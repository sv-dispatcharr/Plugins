#!/usr/bin/env bash
# write_report.sh — nightly report writer for the Mixed Lang Bundle plugin.
# Usage: write_report.sh <report_dir>
#
# Bundled as a shell script to exercise the "unscanned language: shell"
# detection path in the CodeQL workflow.

set -euo pipefail

DEST="${1:?report directory required}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPORT="$DEST/channel_report_${TIMESTAMP}.txt"

mkdir -p "$DEST"

echo "Dispatcharr Channel Report — generated at $(date)" > "$REPORT"
echo "=================================================" >> "$REPORT"
echo "" >> "$REPORT"

# Attempt to gather basic stats via the Django management shell if available.
if command -v python3 &>/dev/null && [[ -f /app/manage.py ]]; then
  python3 /app/manage.py shell -c "
from apps.channels.models import Channel, Stream
print(f'Total channels : {Channel.objects.count()}')
print(f'Active streams : {Stream.objects.filter(is_active=True).count()}')
" >> "$REPORT" 2>/dev/null || echo "(stats unavailable)" >> "$REPORT"
else
  echo "(Django environment not detected — skipping stats)" >> "$REPORT"
fi

echo "" >> "$REPORT"
echo "Report complete: $REPORT"
