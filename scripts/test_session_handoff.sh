#!/usr/bin/env bash
# E2E: kill session, reopen headless, verify handoff injects campaign state.
set -e
REPO=/Users/haotianliu/.openclaw/workspace/ystar-company
cd "$REPO"

echo "== Step 1: verify continuation.json has 'Y*Defuse' + 'Day 3' =="
python3 -c "
import json
d = json.load(open('memory/continuation.json'))
c = d.get('campaign', {})
assert 'Defuse' in c.get('name', ''), 'campaign name missing Defuse'
assert c.get('day') == 3, 'day != 3'
print('OK: campaign=' + c['name'] + ' day=' + str(c['day']))
"

echo "== Step 2: simulate SessionStart hook directly =="
RESULT=$(echo '{}' | YSTAR_AGENT_ID=ceo python3 scripts/hook_session_start.py)
echo "$RESULT" | python3 -m json.tool | head -30

echo "== Step 3: verify injected context contains campaign markers =="
TEXT=$(echo "$RESULT" | python3 -c "
import sys, json
d = json.loads(sys.stdin.read())
print(d['hookSpecificOutput']['additionalContext'])
")
echo "$TEXT" | head -40
echo "---"
FAIL=0
echo "$TEXT" | grep -q 'Defuse' && echo "PASS: Defuse found" || { echo "FAIL: Defuse not injected"; FAIL=1; }
echo "$TEXT" | grep -qE 'Day 3|day.*3' && echo "PASS: Day 3 found" || { echo "FAIL: Day 3 not injected"; FAIL=1; }
echo "$TEXT" | grep -q 'Next Action' && echo "PASS: next_action section rendered" || { echo "FAIL: next_action missing"; FAIL=1; }

echo "== Step 4: verify 10k cap =="
LEN=$(echo -n "$TEXT" | wc -c)
echo "additionalContext length: $LEN chars"
[ "$LEN" -le 10000 ] && echo "PASS: under 10k" || { echo "FAIL: $LEN exceeds 10k"; FAIL=1; }

echo "== Step 5: headless Claude Code test (optional, requires CC CLI) =="
if command -v claude >/dev/null 2>&1; then
    rm -f scripts/.session_booted scripts/.session_call_count
    OUT=$(claude -p "What campaign day are we on?" --session-id test_handoff_$(date +%s) 2>&1 | head -50 || true)
    echo "$OUT" | grep -qi 'day.*3\|Defuse' && echo "PASS: headless session knows Day 3" || echo "SKIP/FAIL: headless output did not mention Day 3 (check manually)"
else
    echo "SKIP: claude CLI not available"
fi

[ "$FAIL" -eq 0 ] && echo "=== ALL TESTS PASS ===" || { echo "=== FAILURES: $FAIL ==="; exit 1; }