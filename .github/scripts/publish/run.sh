#!/bin/bash
set -e

# publish-plugins.sh
# Orchestrates plugin publishing: sets up the releases branch working directory,
# runs each publish phase via subscripts, then commits and pushes.
#
# Usage: publish-plugins.sh <source_branch>
#
# Environment variables required:
#   GITHUB_REPOSITORY - Full repository name (owner/repo)
#   GITHUB_TOKEN      - GitHub token with write access

SOURCE_BRANCH=$1

if [[ -z "$SOURCE_BRANCH" ]]; then
  echo "Usage: $0 <source_branch>"
  exit 1
fi

RELEASES_BRANCH="releases"
MAX_VERSIONED_ZIPS=10
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

export SOURCE_BRANCH RELEASES_BRANCH MAX_VERSIONED_ZIPS

echo "Publishing plugins from $SOURCE_BRANCH to $RELEASES_BRANCH"

# Create temporary working directories
WORK_DIR=$(mktemp -d)
BUILD_META_DIR=$(mktemp -d)
export BUILD_META_DIR
trap 'rm -rf "$WORK_DIR" "$BUILD_META_DIR"' EXIT

echo "Cloning repository..."
git clone --no-checkout "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" "$WORK_DIR/repo"
cd "$WORK_DIR/repo"

# Configure git — use GitHub App bot identity when available, otherwise fall back
# to the generic github-actions[bot] identity.
# NOTE: the email uses the bot *user* ID (not the App ID) — GitHub resolves commit
# authorship by matching this ID+slug[bot]@users.noreply.github.com to the bot account.
if [[ -n "${APP_SLUG:-}" ]]; then
  BOT_USER_ID=$(gh api "/users/${APP_SLUG}%5Bbot%5D" --jq '.id' 2>/dev/null || echo "")
  git config user.name "${APP_SLUG}[bot]"
  if [[ -n "$BOT_USER_ID" ]]; then
    git config user.email "${BOT_USER_ID}+${APP_SLUG}[bot]@users.noreply.github.com"
  else
    # Fallback if the API call fails — avatar may not resolve but commits still work
    git config user.email "${APP_SLUG}[bot]@users.noreply.github.com"
  fi
else
  git config user.name "github-actions[bot]"
  git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
fi

# Checkout or create releases branch
echo "Setting up $RELEASES_BRANCH branch..."
if [[ "${FORCE_REBUILD:-false}" == "true" ]]; then
  echo "Force rebuild requested - resetting $RELEASES_BRANCH to a new orphan commit."
  git checkout --orphan $RELEASES_BRANCH
  git rm -rf . 2>/dev/null || true
  git commit --allow-empty -m "Initialize $RELEASES_BRANCH branch (force rebuild)"
  git push --force "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git" $RELEASES_BRANCH
elif git ls-remote --exit-code --heads origin $RELEASES_BRANCH >/dev/null 2>&1; then
  git checkout $RELEASES_BRANCH
  git pull origin $RELEASES_BRANCH || true
else
  git checkout --orphan $RELEASES_BRANCH
  git rm -rf . 2>/dev/null || true
  git commit --allow-empty -m "Initialize $RELEASES_BRANCH branch"
fi

# Clean old top-level artifacts (regenerated each run)
rm -f manifest.json README.md

# Fetch source branch and copy plugins
echo "Fetching plugins from $SOURCE_BRANCH..."
git fetch origin $SOURCE_BRANCH
git checkout origin/$SOURCE_BRANCH -- plugins

mkdir -p zips

# --- Phases ---
echo ""
echo "=== Building ZIPs ==="
bash "$SCRIPT_DIR/build-zips.sh"

echo ""
echo "=== Cleaning up old releases ==="
bash "$SCRIPT_DIR/cleanup.sh"

echo ""
echo "=== Generating manifests ==="
bash "$SCRIPT_DIR/generate-manifest.sh"

echo ""
echo "=== Generating per-plugin READMEs ==="
bash "$SCRIPT_DIR/plugin-readmes.sh"

echo ""
echo "=== Generating releases README ==="
bash "$SCRIPT_DIR/releases-readme.sh"

# --- Commit and push via Git Data API (produces a server-signed commit) ---
echo ""
echo "=== Committing ==="
rm -rf plugins
git rm -rf --cached plugins 2>/dev/null || true

# Collect the files that will form the release commit tree
PUBLISH_FILES=(zips manifest.json README.md)

# Build the commit message
source_commit=$(git rev-parse --short origin/$SOURCE_BRANCH)
plugin_list=""
if [[ -s changed_plugins.txt ]]; then
  plugin_list="$(printf '\n\n')$(sed 's/^/- /' changed_plugins.txt)"
fi
COMMIT_MSG="Publish plugin updates from $SOURCE_BRANCH

Source commit: $source_commit${plugin_list}

[skip ci]"

# Get the current tip of the releases branch (the parent commit)
PARENT_SHA=$(gh api "repos/${GITHUB_REPOSITORY}/git/refs/heads/${RELEASES_BRANCH}" \
  --jq '.object.sha')
BASE_TREE_SHA=$(gh api "repos/${GITHUB_REPOSITORY}/git/commits/${PARENT_SHA}" \
  --jq '.tree.sha')

# Create blobs for every file under the publish dirs and collect tree entries
TREE_ENTRIES="[]"

add_blob() {
  local path="$1"
  local content_b64
  content_b64=$(base64 -w 0 "$path")
  local blob_sha
  blob_sha=$(gh api "repos/${GITHUB_REPOSITORY}/git/blobs" \
    -X POST \
    -f encoding="base64" \
    -f content="$content_b64" \
    --jq '.sha')
  TREE_ENTRIES=$(echo "$TREE_ENTRIES" | jq \
    --arg p "$path" --arg s "$blob_sha" \
    '. + [{"path": $p, "mode": "100644", "type": "blob", "sha": $s}]')
}

for entry in "${PUBLISH_FILES[@]}"; do
  if [[ -f "$entry" ]]; then
    add_blob "$entry"
  elif [[ -d "$entry" ]]; then
    while IFS= read -r -d '' file; do
      add_blob "$file"
    done < <(find "$entry" -type f -print0)
  fi
done

# Create the new tree, rooted on the current base tree
NEW_TREE_SHA=$(gh api "repos/${GITHUB_REPOSITORY}/git/trees" \
  -X POST \
  -f "base_tree=${BASE_TREE_SHA}" \
  --field "tree=$(echo "$TREE_ENTRIES")" \
  --jq '.sha')

# Bail out early if nothing changed
if [[ "$NEW_TREE_SHA" == "$BASE_TREE_SHA" ]]; then
  echo "No changes to commit."
else
  # Resolve the author identity (mirrors the git config block above)
  if [[ -n "${APP_SLUG:-}" ]]; then
    AUTHOR_NAME="${APP_SLUG}[bot]"
    AUTHOR_EMAIL=$(git config user.email)  # set from API user-ID lookup earlier
  else
    AUTHOR_NAME="github-actions[bot]"
    AUTHOR_EMAIL="41898282+github-actions[bot]@users.noreply.github.com"
  fi

  NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  # Create the commit via the API — GitHub signs it server-side
  NEW_COMMIT_SHA=$(gh api "repos/${GITHUB_REPOSITORY}/git/commits" \
    -X POST \
    -f "message=${COMMIT_MSG}" \
    -f "tree=${NEW_TREE_SHA}" \
    -f "parents[]=${PARENT_SHA}" \
    --field "author[name]=${AUTHOR_NAME}" \
    --field "author[email]=${AUTHOR_EMAIL}" \
    --field "author[date]=${NOW}" \
    --jq '.sha')

  # Fast-forward the branch ref to the new commit
  gh api "repos/${GITHUB_REPOSITORY}/git/refs/heads/${RELEASES_BRANCH}" \
    -X PATCH \
    -f "sha=${NEW_COMMIT_SHA}" \
    -F force=false

  echo "Successfully published to ${RELEASES_BRANCH} (commit ${NEW_COMMIT_SHA:0:7})"
fi
