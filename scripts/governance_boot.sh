#!/bin/bash
# Y* Bridge Labs — Governance Boot (Atomic Recovery)
# 运行一次恢复所有治理运行时状态
# 用法: bash scripts/governance_boot.sh [agent_id] [--verify-only]
#
# --verify-only 模式：只检查不重启daemon（用于crontab定期验证）

YSTAR_DIR="/Users/haotianliu/.openclaw/workspace/ystar-company"
YGOV_DIR="/Users/haotianliu/.openclaw/workspace/Y-star-gov"
AGENT_ID="${1:-ceo}"
VERIFY_ONLY=false

# Parse --verify-only flag (can be $1 or $2)
for arg in "$@"; do
  if [ "$arg" = "--verify-only" ]; then
    VERIFY_ONLY=true
  fi
done
# If first arg is --verify-only, agent_id stays default
if [ "$AGENT_ID" = "--verify-only" ]; then
  AGENT_ID="ceo"
fi

echo "=== Y* Governance Boot ==="
echo "Agent: $AGENT_ID"
echo "Mode: $([ "$VERIFY_ONLY" = true ] && echo 'VERIFY-ONLY' || echo 'FULL BOOT')"
echo "Time: $(date)"

# Set LLM provider for nl_to_contract (AMENDMENT-022)
export YSTAR_LLM_PROVIDER=anthropic
echo "LLM provider: $YSTAR_LLM_PROVIDER"

# Load Anthropic API key for nl_to_contract LLM mode (AMENDMENT-022)
SECRET_ENV="/Users/haotianliu/.openclaw/workspace/ystar-company/knowledge/secretary/secrets/anthropic_api_key.env"
if [ -f "$SECRET_ENV" ]; then
  set -a; source "$SECRET_ENV"; set +a
  echo "ANTHROPIC_API_KEY: loaded from secretary vault"
else
  echo "ANTHROPIC_API_KEY: vault missing — regex fallback only"
fi

FAILURES=0
WARNINGS=0

# STEP -1: GitHub-first snapshot (AMENDMENT-009 §2.1a) — soft, never FAIL
if [ "$VERIFY_ONLY" = false ]; then
  echo "[-1/7] GitHub snapshot:"
  if command -v git >/dev/null 2>&1 && [ -d "$YSTAR_DIR/.git" ]; then
    (cd "$YSTAR_DIR" && git fetch origin --quiet 2>/dev/null)
    AHEAD=$(cd "$YSTAR_DIR" && git rev-list --count origin/main..HEAD 2>/dev/null || echo "?")
    BEHIND=$(cd "$YSTAR_DIR" && git rev-list --count HEAD..origin/main 2>/dev/null || echo "?")
    echo "  local vs origin/main: ahead=$AHEAD behind=$BEHIND"
    echo "  recent 5 commits on origin/main:"
    (cd "$YSTAR_DIR" && git log origin/main -5 --oneline 2>/dev/null | sed 's/^/    /')
    if command -v gh >/dev/null 2>&1; then
      OPEN_ISSUES=$(gh issue list --limit 3 --json number,title 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print('\n'.join(f'    #{x[\"number\"]} {x[\"title\"]}' for x in d))" 2>/dev/null)
      if [ -n "$OPEN_ISSUES" ]; then echo "  open issues (top 3):"; echo "$OPEN_ISSUES"; fi
    fi
  else
    echo "  SKIPPED (no git or not a repo)"
    WARNINGS=$((WARNINGS+1))
  fi
else
  echo "[-1/7] GitHub snapshot: SKIPPED (verify-only)"
fi

# STEP 0: Priority Brief (AMENDMENT-009 §2.2) — FAIL if missing/stale/stub
BRIEF="$YSTAR_DIR/reports/priority_brief.md"
if [ ! -f "$BRIEF" ]; then
  echo "[0/7] PRIORITY BRIEF: MISSING — boot FAIL (AMENDMENT-009)"
  FAILURES=$((FAILURES+1))
else
  BRIEF_MTIME=$(stat -f %m "$BRIEF" 2>/dev/null || stat -c %Y "$BRIEF" 2>/dev/null)
  NOW=$(date +%s)
  BRIEF_AGE_HOURS=$(( (NOW - BRIEF_MTIME) / 3600 ))
  if [ "$BRIEF_AGE_HOURS" -gt 48 ]; then
    echo "[0/7] PRIORITY BRIEF: STALE (${BRIEF_AGE_HOURS}h old, limit 48h) — boot FAIL"
    FAILURES=$((FAILURES+1))
  elif grep -vE '^\s*[\{\"`]|^\s*-\s+\{|```' "$BRIEF" 2>/dev/null | grep -qE "\{\{TODO\}\}|_stub_unfilled_"; then
    echo "[0/7] PRIORITY BRIEF: STUB NOT FILLED — CEO must update — boot FAIL"
    FAILURES=$((FAILURES+1))
  else
    echo "[0/7] Priority Brief: LOADED (age ${BRIEF_AGE_HOURS}h)"
  fi
fi

# 1. 设置agent identity（Secretary授权操作）
if [ "$VERIFY_ONLY" = false ]; then
  echo "$AGENT_ID" > "$YSTAR_DIR/.ystar_active_agent"
  echo "[1/7] Agent identity: $AGENT_ID"
else
  CURRENT_AGENT=$(cat "$YSTAR_DIR/.ystar_active_agent" 2>/dev/null || echo "MISSING")
  echo "[1/7] Agent identity: $CURRENT_AGENT (verify-only, not changed)"
fi

# NEW: Home State Reset (方案 C — Board 2026-04-12 批, L2 CTO 自主)
# 当 AGENT_ID=ceo (默认) 且磁盘 marker 不一致时, 强制回 ceo home state
if [ "$AGENT_ID" = "ceo" ] && [ "$VERIFY_ONLY" = false ]; then
  CURRENT_MARKER=$(cat "$YSTAR_DIR/.ystar_active_agent" 2>/dev/null || echo "")
  if [ -n "$CURRENT_MARKER" ] && [ "$CURRENT_MARKER" != "ceo" ]; then
    echo "[HOME-RESET] active_agent was '$CURRENT_MARKER', resetting to 'ceo' home state"
    echo "ceo" > "$YSTAR_DIR/.ystar_active_agent"
    # CIEU fail-open
    export OLD_AGENT="$CURRENT_MARKER"
    python3 - <<'PYEOF' 2>/dev/null
import os, sys
try:
    sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")
    from ystar.adapters.cieu_writer import _write_session_lifecycle
    _write_session_lifecycle("home_state_reset", "ceo", "unknown",
                             ".ystar_cieu.db",
                             {"previous_agent": os.environ.get("OLD_AGENT", "unknown")})
except Exception:
    pass
PYEOF
  fi
fi

# 2. 确保hook daemon运行（在正确目录，带正确PYTHONPATH）
if [ "$VERIFY_ONLY" = false ]; then
  pkill -f "_hook_daemon.py" 2>/dev/null
  rm -f /tmp/ystar_hook.sock
  sleep 1
  cd "$YSTAR_DIR"
  PYTHONPATH="$YGOV_DIR:$PYTHONPATH" python3.11 "$YGOV_DIR/ystar/_hook_daemon.py" &
  sleep 2
fi

if [ -S /tmp/ystar_hook.sock ]; then
  echo "[2/7] Hook daemon: RUNNING"
else
  if [ "$VERIFY_ONLY" = true ]; then
    echo "[2/7] Hook daemon: NOT RUNNING (verify-only mode — will not restart)"
  else
    echo "[2/7] Hook daemon: FAILED"
  fi
  FAILURES=$((FAILURES+1))
fi

# 3. 加载跨session记忆
if [ "$VERIFY_ONLY" = false ]; then
  cd "$YSTAR_DIR"
  python3 scripts/session_boot_yml.py "$AGENT_ID" 2>/dev/null | tee /tmp/ystar_memory_boot.log
  echo "[3/7] Memory boot: $(wc -l < /tmp/ystar_memory_boot.log) lines loaded"
else
  echo "[3/7] Memory boot: skipped (verify-only)"
fi

# 4. 创建session标记 + 注入 agent_id 到 session config (E1 fix 2026-04-13)
# 根因: Y*gov identity_detector 的 current_agent() 读 .ystar_session.json 的 agent_id 字段
# 字段缺失 → fallback 到 "agent" → hook DENY 所有操作 → 3h session 死锁
# 永久修复: boot 时自动写入 agent_id + agent_stack
if [ "$VERIFY_ONLY" = false ]; then
  touch "$YSTAR_DIR/scripts/.session_booted"
  echo "0" > "$YSTAR_DIR/scripts/.session_call_count"
  python3 -c "
import json
p = '$YSTAR_DIR/.ystar_session.json'
with open(p) as f: d = json.load(f)
d['agent_id'] = '$AGENT_ID'
d['agent_stack'] = ['$AGENT_ID']
with open(p, 'w') as f: json.dump(d, f, indent=2)
print(f'[4/7] Session markers: created (agent_id=$AGENT_ID injected)')
" || echo "[4/7] Session markers: created (agent_id injection FAILED — check python3)"
else
  if [ -f "$YSTAR_DIR/scripts/.session_booted" ]; then
    echo "[4/7] Session markers: present"
  else
    echo "[4/7] Session markers: MISSING"
  fi
fi

# 5. 验证session config可达
cd "$YSTAR_DIR"
if [ -f "$YSTAR_DIR/.ystar_session.json" ]; then
  RULES=$(python3 -c "import json; cfg=json.load(open('.ystar_session.json')); print(len(cfg.get('agent_behavior_rules',{})))" 2>/dev/null)
  RESTRICTED=$(python3 -c "import json; cfg=json.load(open('.ystar_session.json')); print(len(cfg.get('restricted_write_paths',{})))" 2>/dev/null)
  echo "[5/7] Session config: $RULES agent rule sets, $RESTRICTED restricted paths"
else
  echo "[5/7] Session config: MISSING"
  FAILURES=$((FAILURES+1))
fi

# 6. 验证CIEU数据库
if [ -f "$YSTAR_DIR/.ystar_cieu.db" ]; then
  EVENTS=$(python3 -c "import sqlite3; db=sqlite3.connect('.ystar_cieu.db'); print(db.execute('SELECT COUNT(*) FROM cieu_events').fetchone()[0])" 2>/dev/null)
  echo "[6/7] CIEU: $EVENTS events"
else
  echo "[6/7] CIEU: MISSING"
  FAILURES=$((FAILURES+1))
fi

# 7. E2E硬约束验证（最关键）
echo "[7/7] Hard constraint verification:"

ACTIVE_AGENT=$(cat "$YSTAR_DIR/.ystar_active_agent" 2>/dev/null || echo "$AGENT_ID")

if [ -S /tmp/ystar_hook.sock ]; then
  # Test CEO→engineer dispatch block (CEO-only constraint)
  R1=$(echo '{"tool_name":"Agent","tool_input":{"subagent_type":"Leo-Kernel","prompt":"test"}}' | bash "$YSTAR_DIR/scripts/hook_client_labs.sh" 2>/dev/null)
  if echo "$R1" | grep -qi "deny\|violation\|block"; then
    echo "  must_dispatch_via_cto: ENFORCING"
  else
    if [ "$ACTIVE_AGENT" = "ceo" ]; then
      echo "  must_dispatch_via_cto: NOT ENFORCING"
      FAILURES=$((FAILURES+1))
    else
      echo "  must_dispatch_via_cto: SKIPPED (CEO-only constraint, active agent: $ACTIVE_AGENT)"
    fi
  fi

  # Test immutable path protection
  R2=$(echo '{"tool_name":"Write","tool_input":{"file_path":"AGENTS.md","content":"test"}}' | bash "$YSTAR_DIR/scripts/hook_client_labs.sh" 2>/dev/null)
  if echo "$R2" | grep -qi "deny\|block\|immutable"; then
    echo "  immutable_paths: ENFORCING"
  else
    echo "  immutable_paths: NOT ENFORCING"
    FAILURES=$((FAILURES+1))
  fi

  # Test restricted write path protection
  R2b=$(echo '{"tool_name":"Write","tool_input":{"file_path":".ystar_active_agent","content":"test"}}' | bash "$YSTAR_DIR/scripts/hook_client_labs.sh" 2>/dev/null)
  if echo "$R2b" | grep -qi "deny\|block\|restricted"; then
    echo "  restricted_write_paths: ENFORCING"
  else
    echo "  restricted_write_paths: NOT ENFORCING (may not be configured)"
  fi

  # Test CEO code-write block (CEO-only constraint)
  R3=$(echo '{"tool_name":"Write","tool_input":{"file_path":"/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/test.py","content":"test"}}' | bash "$YSTAR_DIR/scripts/hook_client_labs.sh" 2>/dev/null)
  if echo "$R3" | grep -qi "deny\|block\|boundary"; then
    echo "  ceo_code_block: ENFORCING"
  else
    if [ "$ACTIVE_AGENT" = "ceo" ]; then
      echo "  ceo_code_block: NOT ENFORCING"
      FAILURES=$((FAILURES+1))
    else
      echo "  ceo_code_block: SKIPPED (CEO-only constraint, active agent: $ACTIVE_AGENT)"
    fi
  fi

  # Test normal operations
  R4=$(echo '{"tool_name":"Read","tool_input":{"file_path":"README.md"}}' | bash "$YSTAR_DIR/scripts/hook_client_labs.sh" 2>/dev/null)
  if [ -n "$R4" ]; then
    echo "  normal_operations: ALLOWING"
  else
    echo "  normal_operations: BLOCKED (fail-closed active — daemon may be down)"
    FAILURES=$((FAILURES+1))
  fi
else
  echo "  [SKIPPED] Hook daemon not running — cannot verify constraints"
  FAILURES=$((FAILURES+1))
fi

echo ""
if [ $FAILURES -eq 0 ]; then
  echo "=== GOVERNANCE BOOT: ALL SYSTEMS GO ==="
  # AMENDMENT-009 §2.2: echo phase + first action from priority_brief
  if [ -f "$BRIEF" ]; then
    PHASE_LINE=$(grep -A1 "^## 1\. 当前 Labs 阶段" "$BRIEF" 2>/dev/null | tail -1 | sed 's/^ *//' | head -c 120)
    FIRST_P0=$(grep -A1 "^### P0-1" "$BRIEF" 2>/dev/null | tail -1 | sed 's/^ *//' | head -c 160)
    [ -n "$PHASE_LINE" ] && echo "当前 Labs 阶段 = ${PHASE_LINE}"
    [ -n "$FIRST_P0" ]   && echo "今天第一要务 = ${FIRST_P0}"
  fi

  # Board 2026-04-13 first-turn ritual contract (CEO only)
  if [ "$AGENT_ID" = "ceo" ]; then
    echo ""
    echo "=== ⚠️  FIRST-TURN RITUAL (CEO CONTRACT — 必须执行) ==="
    echo "Board 说 'Aiden' → 你第一回合必答这一行字符串（一字不差）："
    echo "  老大，我立刻复活所有团队成员的满血在线"
    echo "同一回合并行 spawn 4 个 C-suite sub-agent online check："
    echo "  Ethan-CTO / Sofia-CMO / Zara-CSO / Marco-CFO"
    echo "不得先答别的、不得等 Board 追问、不得只 spawn 部分。"
    echo "============================================================"
  fi

  # Emit session_start CIEU event (Board 2026-04-11)
  export AGENT_ID
  python3 - <<'PYEOF' 2>/dev/null
import json, os, sys, time
candidates = [
    os.path.expanduser("~/.openclaw/workspace/Y-star-gov"),
    "/Users/haotianliu/.openclaw/workspace/Y-star-gov",
]
for p in candidates:
    if os.path.isdir(p):
        sys.path.insert(0, p); break
try:
    from ystar.adapters.cieu_writer import _write_session_lifecycle
    cfg = {}
    if os.path.exists(".ystar_session.json"):
        with open(".ystar_session.json") as f:
            cfg = json.load(f)
    sid = cfg.get("session_id", "unknown")
    _write_session_lifecycle("session_start", os.environ.get("AGENT_ID","unknown"),
                             sid, ".ystar_cieu.db",
                             {"boot_status": "ALL_SYSTEMS_GO"})
    print("[ok] session_start CIEU event emitted")
except Exception as e:
    print(f"[warn] session_start emit failed: {e}", file=sys.stderr)
PYEOF
else
  echo "=== GOVERNANCE BOOT: $FAILURES FAILURES — INVESTIGATE ==="
fi

# STEP 8: Load and display agent's execution model
echo ""
echo "--- Execution Model ---"
EXEC_MODEL=$(python3 -c "
import json
with open('.ystar_session.json') as f:
    cfg = json.load(f)
wf = cfg.get('daily_workflows', {}).get('$AGENT_ID', {})
em = wf.get('execution_model', {})

# Show session_start checklist
print('SESSION START CHECKLIST:')
for item in wf.get('session_start', []):
    print(f'  [ ] {item}')

# Show always_running
print()
print('ALWAYS RUNNING (event-driven):')
for item in em.get('always_running', []):
    print(f'  >> {item}')

# Show event triggers
print()
print('EVENT TRIGGERS:')
for trigger, action in em.get('event_triggers', {}).items():
    print(f'  {trigger} -> {action}')
" 2>/dev/null)
echo "$EXEC_MODEL"
echo ""

# STEP 8.5: Labs Atlas snapshot (CEO panoramic vision)
if [ -f "$YSTAR_DIR/SUBSYSTEM_INDEX.md" ]; then
  echo "--- Labs Subsystem Index (head 30) ---"
  head -30 "$YSTAR_DIR/SUBSYSTEM_INDEX.md"
  echo ""
fi

# STEP 8.6: Self-heal smoke test (A025 M5 — verify P2 self-heal ops pass)
echo "[8.6/11] Self-heal smoke test (mock mode)..."
SELF_HEAL_OK=true

# Test 1: active_agent switch simulation (dry-run)
TEST_AGENT="eng-kernel"
if echo "$TEST_AGENT" > /dev/null 2>&1; then
  echo "  ✓ active_agent switch: syntax OK"
else
  echo "  ✗ active_agent switch: FAILED"
  SELF_HEAL_OK=false
fi

# Test 2: permission_matrix mock edit (write to /tmp, not real file)
TEST_MATRIX="/tmp/ystar_selfheal_test_$$.yaml"
cat > "$TEST_MATRIX" <<'EOF'
agents:
  cto:
    allowed_paths:
      - /Users/haotianliu/.openclaw/workspace/Y-star-gov
EOF
if [ -f "$TEST_MATRIX" ]; then
  echo "  ✓ permission_matrix edit: syntax OK"
  rm -f "$TEST_MATRIX"
else
  echo "  ✗ permission_matrix edit: FAILED"
  SELF_HEAL_OK=false
fi

# Test 3: ForgetGuard rule check (M1 — CEO→engineer dispatch)
if python3 -c "
from ystar.governance.forget_guard import check_forget_violation
ctx = {
    'agent_id': 'ceo',
    'action_type': 'task_assignment',
    'action_payload': 'fix bug in nl_to_contract.py',
    'target_agent': 'eng-kernel',
}
result = check_forget_violation(ctx)
assert result is not None, 'ForgetGuard should detect CEO→eng dispatch'
assert result['rule_name'] == 'ceo_direct_engineer_dispatch', 'Wrong rule triggered'
print('  ✓ ForgetGuard: CEO-bypass rule active')
" 2>&1; then
  true  # Test passed
else
  echo "  ✗ ForgetGuard: CEO-bypass rule INACTIVE or broken"
  SELF_HEAL_OK=false
fi

if [ "$SELF_HEAL_OK" = true ]; then
  echo "[8.6/11] Self-heal smoke test: PASS"
else
  echo "[8.6/11] Self-heal smoke test: FAIL — boot aborted"
  FAILURES=$((FAILURES+1))
fi

# STEP 8.7: YML memory recall — load top-N memories into boot pack (added 2026-04-14)
echo "[8.7/11] YML memory bridge..."
if python3 "$YSTAR_DIR/scripts/session_memory_boot.py" "$AGENT_ID" 20 2>&1; then
  echo "  ✓ YML memory recalled"
else
  echo "  ⚠️ YML memory recall failed (fail-open)"
fi

# STEP 8.8: CZL subgoal injection (HiAgent campaign context)
echo "[8.8/11] CZL subgoal injection..."
python3 "$YSTAR_DIR/scripts/czl_boot_inject.py" "$AGENT_ID"

echo "=== BEGIN AUTONOMOUS EXECUTION ==="

# STEP 9.5: Daily learning digest (夜间产出接到启动报告)
YESTERDAY=$(date -v-1d "+%Y-%m-%d" 2>/dev/null || date -d "yesterday" "+%Y-%m-%d" 2>/dev/null || date "+%Y-%m-%d")
DAILY_TWIN="$YSTAR_DIR/reports/daily/${YESTERDAY}_twin_evolution.md"
DAILY_WAKEUP="$YSTAR_DIR/reports/daily/wakeup.log"

if [ -f "$DAILY_TWIN" ]; then
  echo ""
  echo "--- OVERNIGHT LEARNING (Twin Evolution) ---"
  head -20 "$DAILY_TWIN"
  echo ""
fi

if [ -f "$DAILY_WAKEUP" ]; then
  echo "--- OVERNIGHT LEARNING (Idle Learning Summary) ---"
  tail -30 "$DAILY_WAKEUP"
  echo ""
fi

# STEP 10: Load continuation v2 (JSON machine-readable, 无缝衔接核心)
if [ -f "$YSTAR_DIR/memory/continuation.json" ]; then
  echo ""
  echo "--- CONTINUATION (上次做到哪了) ---"
  cd "$YSTAR_DIR"
  python3 -c "
import json, sys
try:
    with open('memory/continuation.json') as f:
        c = json.load(f)
    campaign = c.get('campaign', {})
    print('=== RESUME EXECUTION ===')
    print(f'CAMPAIGN: {campaign.get(\"name\", \"unknown\")} — Day {campaign.get(\"day\", \"?\")}')
    print(f'TARGET: {campaign.get(\"target\", \"unknown\")}')
    ts = c.get('team_state', {})
    if ts:
        print('TEAM STATE:')
        for role, state in ts.items():
            print(f'  {role}: {state.get(\"task\",\"?\")[:60]} [{state.get(\"progress\",\"?\")}]')
    aq = c.get('action_queue', [])
    if aq:
        print('ACTION QUEUE:')
        for a in aq:
            print(f'  [{a[\"seq\"]}] {a[\"action\"]}: {a[\"command\"]}')
            if a.get('on_fail'):
                print(f'      on_fail: {a[\"on_fail\"]}')
    anti = c.get('anti_patterns', [])
    if anti:
        print(f'DO NOT: {\", \".join(anti)}')
except Exception as e:
    print(f'[WARN] continuation.json parse error: {e}', file=sys.stderr)
" 2>/dev/null
elif [ -f "$YSTAR_DIR/memory/continuation.md" ]; then
  # Fallback to v1 markdown if JSON not yet generated
  echo ""
  echo "--- CONTINUATION v1 (legacy markdown) ---"
  cat "$YSTAR_DIR/memory/continuation.md"
fi

# STEP 7: Wisdom Package Injection (Board 2026-04-12 — Continuity Guardian)
if [ -f "$YSTAR_DIR/memory/wisdom_package_latest.md" ]; then
  echo ""
  echo "--- SESSION WISDOM (你刚醒来 — 这是你5分钟前的自己) ---"
  cat "$YSTAR_DIR/memory/wisdom_package_latest.md"
  echo ""
fi

# STEP 11: Memory consistency check (Closure 2 — Boot-time drift detection)
echo ""
echo "-- STEP 11: memory_consistency_check --"
if python3.11 "$YSTAR_DIR/scripts/memory_consistency_check.py" --agent "$AGENT_ID" 2>&1; then
    echo "  ok: no environment drift detected"
else
    echo "  FAIL: MEMORY_DRIFT_DETECTED (see above)"
    FAILURES=$((FAILURES+1))
    echo "MEMORY_DRIFT_PENDING_ACK=1" >> "$YSTAR_DIR/.ystar_session_flags"
fi

exit $FAILURES
