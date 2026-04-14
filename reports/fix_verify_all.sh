#!/bin/bash
# ============================================================
# FIX-VERIFY-ALL: 3个fix跑完后的综合回归验证
# ============================================================
# 顺序: 先跑3个fix, 再跑verify. 中间有gov-mcp需要重启的点 — 本脚本会打印指示.
#
# 跑法:
#   bash /Users/haotianliu/.openclaw/workspace/ystar-company/reports/fix_verify_all.sh
# ============================================================
set +e
cd /Users/haotianliu/.openclaw/workspace/ystar-company

REPORT_DIR=reports
PASS=0; FAIL=0
ok()   { echo "  [PASS] $1"; PASS=$((PASS+1)); }
bad()  { echo "  [FAIL] $1"; FAIL=$((FAIL+1)); }

echo "============================================================"
echo "Phase 1: apply all 3 fixes"
echo "============================================================"
bash "$REPORT_DIR/fix_cieu_persistence.sh"        && ok "fix_cieu_persistence applied" || bad "fix_cieu_persistence"
bash "$REPORT_DIR/fix_delegation_schema.sh"       && ok "fix_delegation_schema applied" || bad "fix_delegation_schema"
bash "$REPORT_DIR/fix_hook_immutable_enforcement.sh" && ok "fix_hook_immutable_enforcement applied" || bad "fix_hook_immutable_enforcement"

echo ""
echo "============================================================"
echo "Phase 2: schema verify (no gov-mcp restart required)"
echo "============================================================"

# delegations view
python3 - <<'PY' && ok "delegations view queryable" || bad "delegations view missing"
import sqlite3
c = sqlite3.connect(".gov_mcp_state.db")
c.execute("SELECT COUNT(*) FROM delegations").fetchone()
PY

# hook no-longer over-triggers on strftime
RESP=$(echo '{"tool_name":"Bash","tool_input":{"command":"python3 -c \"import sqlite3; c=sqlite3.connect(\\\".ystar_cieu.db\\\"); print(c.execute(\\\"SELECT strftime(%s,now)\\\").fetchone())\""},"hook_event_name":"PreToolUse"}' \
  | YSTAR_AGENT_ID=ceo python3 scripts/hook_wrapper.py 2>&1)
if echo "$RESP" | grep -qi "cannot write to 'strftime"; then
  bad "strftime false-DENY still happening"
else
  ok "strftime no longer false-DENY"
fi

# hook DOES still deny AGENTS.md writes (immutable)
RESP2=$(echo '{"tool_name":"Write","tool_input":{"file_path":"/Users/haotianliu/.openclaw/workspace/ystar-company/AGENTS.md","content":"test"},"hook_event_name":"PreToolUse"}' \
  | YSTAR_AGENT_ID=ceo python3 scripts/hook_wrapper.py 2>&1)
if echo "$RESP2" | grep -qi "deny\|immutable\|denied\|violation"; then
  ok "AGENTS.md write still DENY (immutable enforce live)"
else
  bad "AGENTS.md write NOT denied — immutable enforce broken"
  echo "    raw hook response: $RESP2" | head -3
fi

echo ""
echo "============================================================"
echo "Phase 3: gov-mcp server restart required for CIEU fix"
echo "============================================================"
echo "  Restart gov-mcp process, then run:"
echo "    mcp__gov-mcp__gov_doctor  # expect L1_02_cieu.status == 'active'"
echo ""
echo "============================================================"
echo "Phase 4: full handoff verify"
echo "============================================================"
bash reports/verify_full_handoff.sh

echo ""
echo "============================================================"
echo "SUMMARY: $PASS passed / $FAIL failed (pre-restart checks)"
echo "============================================================"
exit $FAIL
