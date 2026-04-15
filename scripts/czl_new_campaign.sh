#!/usr/bin/env bash
# HiAgent V5: New Campaign Scaffolding
# Archives old .czl_subgoals.json and generates fresh stub for next campaign.
#
# Usage: bash scripts/czl_new_campaign.sh "Campaign Name"

set -e

if [ $# -lt 1 ]; then
  echo "Usage: $0 <campaign_name>"
  echo "Example: $0 'Gemma Phase 2'"
  exit 1
fi

CAMPAIGN_NAME="$1"
YSTAR_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CZL_FILE="$YSTAR_DIR/.czl_subgoals.json"
ARCHIVE_DIR="$YSTAR_DIR/memory/archive"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Step 1: Archive old .czl_subgoals.json if exists
if [ -f "$CZL_FILE" ]; then
  OLD_CAMPAIGN=$(python3 -c "import json; print(json.load(open('$CZL_FILE')).get('campaign', 'unknown'))" 2>/dev/null || echo "unknown")
  ARCHIVE_FILE="$ARCHIVE_DIR/czl_subgoals_${OLD_CAMPAIGN// /_}_$TIMESTAMP.json"

  mkdir -p "$ARCHIVE_DIR"
  cp "$CZL_FILE" "$ARCHIVE_FILE"
  echo "[ARCHIVE] Old campaign saved to: $ARCHIVE_FILE"
else
  echo "[INFO] No existing .czl_subgoals.json — creating fresh campaign"
fi

# Step 2: Find latest priority_brief version
PRIORITY_BRIEF="reports/priority_brief.md"
if [ ! -f "$YSTAR_DIR/$PRIORITY_BRIEF" ]; then
  # Look for versioned brief
  LATEST_BRIEF=$(ls -t "$YSTAR_DIR"/reports/priority_brief*.md 2>/dev/null | head -1 || echo "")
  if [ -n "$LATEST_BRIEF" ]; then
    PRIORITY_BRIEF=$(basename "$LATEST_BRIEF")
  else
    PRIORITY_BRIEF="reports/priority_brief.md (missing — CEO must create)"
  fi
fi

# Step 3: Generate new stub
cat > "$CZL_FILE" <<EOF
{
  "y_star_ref": "$PRIORITY_BRIEF",
  "campaign": "$CAMPAIGN_NAME",
  "y_star_criteria": [],
  "current_subgoal": null,
  "completed": [],
  "remaining": [],
  "rt1_status": "0/0 — new campaign",
  "boot_injection_spec": "HiAgent v0.1 — Y* / current / completed summaries"
}
EOF

echo "[CREATED] New campaign stub: $CZL_FILE"
echo "Campaign: $CAMPAIGN_NAME"
echo "Y* ref: $PRIORITY_BRIEF"
echo ""
echo "Next steps:"
echo "  1. CEO: populate y_star_criteria[] with measurable targets"
echo "  2. CEO: populate remaining[] with subgoals (U1-UN)"
echo "  3. CEO: push first subgoal to current_subgoal"
echo ""

# Step 4: Emit CIEU event
python3 -c "
import sys
sys.path.insert(0, '$YSTAR_DIR/../Y-star-gov')
try:
    from ystar.adapters.cieu_writer import write_cieu_event
    write_cieu_event('CAMPAIGN_STARTED', {'campaign': '$CAMPAIGN_NAME', 'timestamp': '$TIMESTAMP'}, agent_id='ceo')
    print('[CIEU] CAMPAIGN_STARTED event emitted')
except Exception as e:
    print(f'[WARN] CIEU event failed: {e}', file=sys.stderr)
" 2>/dev/null || echo "[WARN] CIEU event skipped (ystar not available)"

echo "[COMPLETE] Campaign '$CAMPAIGN_NAME' scaffolded successfully"
