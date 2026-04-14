#!/bin/bash
# fix_hook_immutable_enforcement_v2
#
# ROOT CAUSE (found after deep debug):
#   .ystar_session.json's `immutable_paths` was a FLAT LIST
#   ["override_roles","AGENTS.md","patterns"] — the previous fix script
#   append-pushed the dict *keys themselves* as list entries.
#
#   boundary_enforcer.py::_get_immutable_config() expects a DICT:
#       { "patterns": [...], "override_roles": [...] }
#   It does:
#       immutable = cfg.get("immutable_paths", {})
#       patterns  = immutable.get("patterns", [...])   # AttributeError on list!
#
#   When that raised, check_hook() caught the exception upstream and the
#   daemon returned `{}` — i.e. NO governance verdict, NO DENY. The test
#   payload got `raw hook response: {}` which Claude Code treats as "allow".
#
#   Symptom: AGENTS.md writes bypass immutable enforcement despite the file
#   being "in" immutable_paths, because the config was structurally broken
#   and silently collapsed to defaults (and then further broke on the
#   .get() call on a list).
#
# FIX:
#   1. Normalize immutable_paths to the expected dict schema.
#   2. Restart the hook daemon so it reloads session config.
#   3. Restart gov-mcp (separate script) for CIEU persistence patch.
#   4. Test payload end-to-end: AGENTS.md Write must return action=block.

set -u
YSTAR_DIR="/Users/haotianliu/.openclaw/workspace/ystar-company"
SESSION_JSON="$YSTAR_DIR/.ystar_session.json"
DAEMON_PY="/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/_hook_daemon.py"
SOCK="/tmp/ystar_hook.sock"

echo "=== fix_hook_immutable_enforcement_v2 ==="

# ── Step 1: Normalize immutable_paths to dict schema ──────────────────
python3 <<'PY'
import json, shutil, time, os
p = "/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_session.json"
backup = p + f".bak.{int(time.time())}"
shutil.copy(p, backup)
print(f"Backup: {backup}")

with open(p) as f:
    s = json.load(f)

old = s.get("immutable_paths")
print(f"BEFORE: immutable_paths = {old!r} (type={type(old).__name__})")

# Rebuild canonical dict schema expected by boundary_enforcer.py
# Patterns: ending with "/" = directory prefix; no slash = filename exact match.
new = {
    "patterns": [
        "AGENTS.md",
        ".claude/agents/",
        "CLAUDE.md",
    ],
    "override_roles": [
        "secretary",
    ],
}

# If old WAS a dict with valid patterns/override_roles, merge them in.
if isinstance(old, dict):
    if isinstance(old.get("patterns"), list):
        for pat in old["patterns"]:
            if isinstance(pat, str) and pat and pat not in new["patterns"]:
                new["patterns"].append(pat)
    if isinstance(old.get("override_roles"), list):
        for r in old["override_roles"]:
            if isinstance(r, str) and r and r not in new["override_roles"]:
                new["override_roles"].append(r)
elif isinstance(old, list):
    # Pull genuine path-ish strings out of the broken list
    # (skip the schema-key noise: "patterns", "override_roles")
    for item in old:
        if not isinstance(item, str): continue
        if item in ("patterns", "override_roles"): continue
        if item and item not in new["patterns"]:
            new["patterns"].append(item)

s["immutable_paths"] = new

with open(p, "w") as f:
    json.dump(s, f, indent=2, ensure_ascii=False)

print(f"AFTER:  immutable_paths = {json.dumps(new, ensure_ascii=False)}")
PY

# ── Step 2: Validate JSON still loads ─────────────────────────────────
python3 -c "import json; json.load(open('$SESSION_JSON')); print('session.json valid JSON')" || {
    echo "FAIL: session.json became invalid, check backup"; exit 1;
}

# ── Step 3: Restart hook daemon ───────────────────────────────────────
echo ""
echo "--- restart hook daemon ---"
DPIDS=$(ps aux | grep -E 'python.*_hook_daemon\.py' | grep -v grep | awk '{print $2}')
if [ -n "$DPIDS" ]; then
    echo "Killing daemon PIDs: $DPIDS"
    kill $DPIDS 2>/dev/null
    sleep 1
    for p in $DPIDS; do kill -0 "$p" 2>/dev/null && kill -9 "$p" 2>/dev/null; done
fi
rm -f "$SOCK"

# Relaunch daemon (matches ps aux command)
PYBIN="/opt/homebrew/Cellar/python@3.11/3.11.14_3/Frameworks/Python.framework/Versions/3.11/bin/python3.11"
export PYTHONPATH="/Users/haotianliu/.openclaw/workspace/Y-star-gov:${PYTHONPATH:-}"
nohup "$PYBIN" "$DAEMON_PY" >> "$YSTAR_DIR/scripts/hook_daemon.log" 2>&1 &
NEW_PID=$!
disown
echo "daemon pid=$NEW_PID"

# Wait for socket
for i in 1 2 3 4 5 6 7 8 9 10; do
    if [ -S "$SOCK" ]; then
        echo "daemon socket ready after ${i}s"
        break
    fi
    sleep 1
done

if [ ! -S "$SOCK" ]; then
    echo "FAIL: daemon socket $SOCK not appearing"
    tail -40 "$YSTAR_DIR/scripts/hook_daemon.log" 2>/dev/null
    exit 1
fi

# ── Step 4: End-to-end test on AGENTS.md ──────────────────────────────
echo ""
echo "--- E2E test: Write AGENTS.md must be blocked ---"
RESULT=$(echo '{"tool_name":"Write","tool_input":{"file_path":"/Users/haotianliu/.openclaw/workspace/ystar-company/AGENTS.md","content":"test"},"hook_event_name":"PreToolUse"}' \
    | bash "$YSTAR_DIR/scripts/hook_client_labs.sh" 2>&1)
echo "hook response: $RESULT"

if echo "$RESULT" | grep -q '"action"\s*:\s*"block"'; then
    echo ""
    echo "PASS: AGENTS.md write is now DENIED by immutable_paths enforcement."
else
    echo ""
    echo "FAIL: AGENTS.md write was NOT blocked. Response above."
    echo "Check: tail $YSTAR_DIR/scripts/hook_debug.log"
    exit 1
fi

# ── Step 5: Negative test — regular file should NOT be blocked ────────
echo ""
echo "--- negative test: Write random file should NOT be blocked ---"
RESULT2=$(echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/_ystar_negtest.md","content":"x"},"hook_event_name":"PreToolUse"}' \
    | bash "$YSTAR_DIR/scripts/hook_client_labs.sh" 2>&1)
echo "hook response: $RESULT2"
if echo "$RESULT2" | grep -q '"action"\s*:\s*"block"'; then
    echo "FAIL: unrelated file was blocked — over-enforcement."
    exit 1
else
    echo "PASS: unrelated file not blocked."
fi

echo ""
echo "=== fix_hook_immutable_enforcement_v2 COMPLETE ==="
