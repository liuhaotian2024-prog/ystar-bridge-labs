#!/bin/bash
# field_backfill_cron_install.sh
# Idempotent installer: adds m_functor backfill cron entry to user crontab.
# Schedule: every 15 minutes, 10K rows/run.
# Safe to run multiple times -- deduplicates via grep guard.

set -euo pipefail

WORKSPACE="/Users/haotianliu/.openclaw/workspace/ystar-company"
CRON_COMMENT="# Y* field m_functor backfill every 15 min (Wave-2 coverage climb)"
CRON_LINE="*/15 * * * * cd ${WORKSPACE} && /usr/bin/python3 scripts/y_star_field_validator_run.py --backfill --limit 10000 >> scripts/.logs/field_backfill.log 2>&1"

# Ensure log directory exists
mkdir -p "${WORKSPACE}/scripts/.logs"

# Check if already installed
if crontab -l 2>/dev/null | grep -qF "field_backfill"; then
    echo "[OK] Backfill cron already installed. Skipping."
    crontab -l | grep "field_backfill"
    exit 0
fi

# Append to existing crontab
(crontab -l 2>/dev/null; echo ""; echo "${CRON_COMMENT}"; echo "${CRON_LINE}") | crontab -

echo "[INSTALLED] Backfill cron entry added:"
echo "  Schedule: */15 * * * *"
echo "  Command:  python3 scripts/y_star_field_validator_run.py --backfill --limit 10000"
echo "  Log:      scripts/.logs/field_backfill.log"
echo ""
echo "Verify with: crontab -l | grep field_backfill"
