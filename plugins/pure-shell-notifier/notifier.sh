#!/usr/bin/env bash
# notifier.sh — entry point for the Pure Shell Notifier plugin.
#
# This plugin is intentionally shell-only (no plugin.py) to exercise the
# CodeQL workflow's "skipped + unscanned: shell" detection path.
# Expected workflow result:
#   - detect-langs: found=false, unscanned_langs=shell
#   - CodeQL: skipped
#   - PR comment: "CodeQL analysis was skipped - ... shell"

set -euo pipefail

MODE="${1:-notify}"
MESSAGE="${2:-Dispatcharr event}"

case "$MODE" in
  notify)
    TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    echo "[${TIMESTAMP}] NOTIFY: ${MESSAGE}"
    ;;
  healthcheck)
    echo "OK"
    ;;
  *)
    echo "Unknown mode: $MODE" >&2
    exit 1
    ;;
esac
