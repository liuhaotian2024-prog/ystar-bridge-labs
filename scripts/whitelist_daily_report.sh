#!/usr/bin/env bash
# whitelist_daily_report.sh — A018 Phase 1 cron entry for daily whitelist coverage
#
# Schedule: 00:00 UTC daily
# Action:
#   1. Run whitelist_coverage.py for last 24h
#   2. If coverage < 60%, emit WHITELIST_GAP CIEU
#   3. Append result to reports/whitelist_daily/{date}.md
#
# Created: 2026-04-13 by Maya Patel (eng-platform)
# DO NOT install to crontab yet — CEO will install

set -euo pipefail

# --- Config ---
REPO_ROOT="/Users/haotianliu/.openclaw/workspace/ystar-company"
SCRIPT_DIR="${REPO_ROOT}/scripts"
REPORT_DIR="${REPO_ROOT}/reports/whitelist_daily"
DB_PATH="${REPO_ROOT}/.ystar_cieu.db"
WHITELIST_DIR="${REPO_ROOT}/governance/whitelist"

# --- Ensure report directory exists ---
mkdir -p "${REPORT_DIR}"

# --- Calculate time window (last 24h) ---
END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S")
START_TIME=$(date -u -v-24H +"%Y-%m-%dT%H:%M:%S")  # macOS date -v flag
DATE_TAG=$(date -u +"%Y-%m-%d")

# --- Run coverage script ---
echo "[$(date -u +"%Y-%m-%d %H:%M:%S UTC")] Running whitelist coverage for ${START_TIME} → ${END_TIME}" | tee -a "${REPORT_DIR}/${DATE_TAG}.md"

COVERAGE_OUTPUT=$(python3 "${SCRIPT_DIR}/whitelist_coverage.py" \
    --db-path "${DB_PATH}" \
    --whitelist-dir "${WHITELIST_DIR}" \
    --start-time "${START_TIME}" \
    --end-time "${END_TIME}" \
    --emit-gap \
    --verbose 2>&1)

EXIT_CODE=$?

# --- Append to daily report ---
cat >> "${REPORT_DIR}/${DATE_TAG}.md" <<EOF

## Whitelist Coverage Report — ${DATE_TAG}

\`\`\`
${COVERAGE_OUTPUT}
\`\`\`

**Exit Code**: ${EXIT_CODE} (0 = coverage ≥ 60%, 1 = coverage < 60%)

---

EOF

# --- Log to CIEU ---
if [ ${EXIT_CODE} -eq 0 ]; then
    echo "[OK] Whitelist coverage ≥ 60%. No action required."
else
    echo "[ALERT] Whitelist coverage < 60%. WHITELIST_GAP emitted to CIEU."
fi

exit ${EXIT_CODE}
