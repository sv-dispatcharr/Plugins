#!/usr/bin/env bash
# backup.sh — bundled backup script for the Shell Backup Helper plugin.
# Usage: backup.sh <destination_path> <retain_days>
#
# This file is intentionally a shell script to exercise the CodeQL workflow's
# "unscanned language" detection path (shell is not supported by CodeQL).

set -euo pipefail

DEST="${1:?destination path required}"
RETAIN="${2:-7}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ARCHIVE="dispatcharr_backup_${TIMESTAMP}.tar.gz"

mkdir -p "$DEST"

# Locate the Dispatcharr data directory (adjust DATA_DIR if needed).
DATA_DIR="${DISPATCHARR_DATA_DIR:-/app/data}"

if [[ ! -d "$DATA_DIR" ]]; then
  echo "ERROR: data directory not found: $DATA_DIR" >&2
  exit 1
fi

echo "Archiving $DATA_DIR -> $DEST/$ARCHIVE ..."
tar -czf "$DEST/$ARCHIVE" -C "$(dirname "$DATA_DIR")" "$(basename "$DATA_DIR")"

echo "Removing archives older than $RETAIN day(s) ..."
find "$DEST" -name 'dispatcharr_backup_*.tar.gz' -mtime "+${RETAIN}" -delete

echo "Done: $DEST/$ARCHIVE"
