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

FAILURES=0

# 1. 设置agent identity（Secretary授权操作）
if [ "$VERIFY_ONLY" = false ]; then
  echo "$AGENT_ID" > "$YSTAR_DIR/.ystar_active_agent"
  echo "[1/7] Agent identity: $AGENT_ID"
else
  CURRENT_AGENT=$(cat "$YSTAR_DIR/.ystar_active_agent" 2>/dev/null || echo "MISSING")
  echo "[1/7] Agent identity: $CURRENT_AGENT (verify-only, not changed)"
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

# 4. 创建session标记
if [ "$VERIFY_ONLY" = false ]; then
  touch "$YSTAR_DIR/scripts/.session_booted"
  echo "0" > "$YSTAR_DIR/scripts/.session_call_count"
  echo "[4/7] Session markers: created"
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
echo "=== BEGIN AUTONOMOUS EXECUTION ==="

# STEP 9: Surface active obligations (认知恢复核心)
echo ""
echo "--- ACTIVE OBLIGATIONS (你在打什么仗) ---"
cd "$YSTAR_DIR"
python3 -c "
import sqlite3
db = sqlite3.connect('.ystar_memory.db')
obs = db.execute(\"SELECT content, created_at FROM memories WHERE memory_type='obligation' ORDER BY created_at DESC\").fetchall()
if obs:
    for content, ts in obs:
        print(f'  [OBLIGATION] {content[:200]}')
else:
    print('  (no obligations found)')

# Also show active lessons (top 5 by access)
lessons = db.execute(\"SELECT content FROM memories WHERE memory_type='lesson' ORDER BY access_count DESC LIMIT 5\").fetchall()
if lessons:
    print()
    print('TOP LESSONS:')
    for (content,) in lessons:
        print(f'  [LESSON] {content[:150]}')
db.close()
" 2>/dev/null

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
