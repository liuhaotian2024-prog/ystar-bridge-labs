#!/bin/bash
# Session Graceful Restart — Save Chain Orchestrator
# Board-approved 2026-04-12 as part of Aiden Continuity Guardian
#
# Executes complete state save before session restart:
# 1. session_close_yml.py (memory distillation)
# 2. twin_evolution.py --mode all (values/genes extraction)
# 3. learning_report.py (lessons learned)
# 4. session_wisdom_extractor.py (NEW: session essence)
# 5. aiden_cognition_backup.py --full (full cognitive mirror)
# 6. git commit + push (precise file add, no -A)
# 7. continuation.json snapshot
# 8. Write /tmp/ystar_ready_for_restart signal
#
# Usage:
#   bash scripts/session_graceful_restart.sh [agent_id]
#
# Defaults to 'ceo' if no agent_id provided.

YSTAR_DIR="/Users/haotianliu/.openclaw/workspace/ystar-company"
AGENT_ID="${1:-ceo}"
DATE=$(date +%Y-%m-%d)
TIME=$(date +%H:%M:%S)

echo "=== Session Graceful Restart: Save Chain ==="
echo "Agent: $AGENT_ID"
echo "Time: $DATE $TIME"
echo ""

cd "$YSTAR_DIR" || exit 1

FAILURES=0

# === STEP 1: Session Close (YML memory distillation) ===
echo "[1/8] Running session_close_yml.py..."
if [ -f scripts/session_close_yml.py ]; then
  python3 scripts/session_close_yml.py "$AGENT_ID" "Graceful restart: health threshold reached" 2>&1
  if [ $? -eq 0 ]; then
    echo "  ✓ Session close completed"
  else
    echo "  ✗ Session close failed (non-fatal)"
    FAILURES=$((FAILURES+1))
  fi
else
  echo "  ✗ session_close_yml.py not found"
  FAILURES=$((FAILURES+1))
fi
echo ""

# === STEP 2: Twin Evolution (values/genes extraction) ===
echo "[2/8] Running twin_evolution.py..."
if [ -f scripts/twin_evolution.py ]; then
  python3.11 scripts/twin_evolution.py --mode all 2>&1
  if [ $? -eq 0 ]; then
    echo "  ✓ Twin evolution completed"
  else
    echo "  ✗ Twin evolution failed (non-fatal)"
    FAILURES=$((FAILURES+1))
  fi
else
  echo "  ✗ twin_evolution.py not found"
fi
echo ""

# === STEP 3: Learning Report (lessons distillation) ===
echo "[3/8] Running learning_report.py..."
if [ -f scripts/learning_report.py ]; then
  python3 scripts/learning_report.py > "reports/daily/${DATE}_learning.md" 2>&1
  if [ $? -eq 0 ]; then
    echo "  ✓ Learning report completed"
  else
    echo "  ✗ Learning report failed (non-fatal)"
  fi
else
  echo "  ✗ learning_report.py not found"
fi
echo ""

# === STEP 4: Session Wisdom Extraction (NEW) ===
echo "[4/8] Running session_wisdom_extractor.py..."
if [ -f scripts/session_wisdom_extractor.py ]; then
  python3 scripts/session_wisdom_extractor.py 2>&1
  if [ $? -eq 0 ]; then
    echo "  ✓ Wisdom extraction completed"
  else
    echo "  ✗ Wisdom extraction failed (non-fatal)"
    FAILURES=$((FAILURES+1))
  fi
else
  echo "  ✗ session_wisdom_extractor.py not found"
  FAILURES=$((FAILURES+1))
fi
echo ""

# === STEP 5: Aiden Cognition Backup (full mirror) ===
echo "[5/8] Running aiden_cognition_backup.py..."
if [ -f scripts/aiden_cognition_backup.py ]; then
  python3 scripts/aiden_cognition_backup.py --full 2>&1
  if [ $? -eq 0 ]; then
    echo "  ✓ Cognition backup completed"
  else
    echo "  ✗ Cognition backup failed (non-fatal)"
  fi
else
  echo "  ⚠  aiden_cognition_backup.py not found (skipping)"
fi
echo ""

# === STEP 6: Git Commit + Push (precise file add) ===
echo "[6/8] Git commit + push..."

# Precise file add (no git add -A)
FILES_TO_ADD=(
  "memory/session_handoff.md"
  "memory/continuation.json"
  "memory/wisdom_package_*.md"
  ".ystar_memory.db"
  ".ystar_cieu.db"
  ".ystar_omission.db"
  ".ystar_session.json"
  "reports/daily/${DATE}_learning.md"
  "knowledge/*/twin_dna_*.json"
  "knowledge/*/active_task.json"
)

echo "  Adding files..."
for pattern in "${FILES_TO_ADD[@]}"; do
  # Use find to expand patterns (glob doesn't work in bash array)
  for file in $pattern; do
    if [ -e "$file" ]; then
      git add "$file" 2>/dev/null && echo "    + $file"
    fi
  done
done

# Commit with template message (pre-whitelisted)
COMMIT_MSG="infra: session state saved before graceful restart [$TIME]

Health threshold reached. Save chain executed:
- Memory distillation (session_close_yml)
- Values extraction (twin_evolution)
- Learning report
- Wisdom package (NEW)
- Cognition backup
- Continuation snapshot

Next session will inject wisdom package for seamless continuity.

Co-Authored-By: Ryan Park (Platform Engineer) <noreply@ystar.com>"

git commit -m "$COMMIT_MSG" 2>&1
if [ $? -eq 0 ]; then
  echo "  ✓ Commit created"

  # Push to remote
  git push 2>&1
  if [ $? -eq 0 ]; then
    echo "  ✓ Pushed to remote"
  else
    echo "  ✗ Push failed (non-fatal)"
  fi
else
  echo "  ⚠  Nothing to commit (or commit failed)"
fi
echo ""

# === STEP 7: Continuation Snapshot ===
echo "[7/8] Verifying continuation.json..."
if [ -f "memory/continuation.json" ]; then
  CONTINUATION_SIZE=$(wc -c < "memory/continuation.json")
  echo "  ✓ Continuation snapshot: $CONTINUATION_SIZE bytes"
else
  echo "  ✗ continuation.json not found"
  FAILURES=$((FAILURES+1))
fi
echo ""

# === STEP 8: Clean Session Markers ===
echo "[8/8] Cleaning session markers..."
rm -f scripts/.session_booted scripts/.session_call_count
echo "  ✓ Session markers cleaned"
echo ""

# === Write Ready Signal ===
if [ $FAILURES -eq 0 ]; then
  echo "=== SAVE CHAIN COMPLETE ==="
  echo "All steps completed successfully."
  echo ""

  # Write restart signal
  RESTART_REASON=$(cat /tmp/ystar_health_yellow 2>/dev/null || echo "{}")
  echo "$RESTART_REASON" > /tmp/ystar_ready_for_restart
  echo "Last restart: $(date)" > /tmp/ystar_last_restart_reason

  echo "Signal written: /tmp/ystar_ready_for_restart"
  echo "Wrapper will now restart Claude Code process."
  echo ""
  exit 0
else
  echo "=== SAVE CHAIN PARTIAL ==="
  echo "Some steps failed ($FAILURES failures), but continuing."
  echo "Data may be incomplete. Review logs above."
  echo ""

  # Still write signal (fail-open)
  echo "{\"partial_failure\": true, \"failures\": $FAILURES}" > /tmp/ystar_ready_for_restart
  echo "Last restart: $(date) [partial]" > /tmp/ystar_last_restart_reason
  exit 1
fi
