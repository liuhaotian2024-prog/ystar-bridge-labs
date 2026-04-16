#!/bin/bash
# Y* Bridge Labs — PreToolUse Hook Client
#
# THIS is the single entry point for ALL governance enforcement.
# It combines Y*gov core (check_hook) + Labs-specific rules (hook_wrapper.py).
#
# Architecture:
#   FAST PATH: daemon socket → check_hook() (Y*gov core only, ~5ms)
#   SLOW PATH: python3 hook_wrapper.py (Y*gov core + Labs rules, ~1.4s)
#   FALLBACK: if both fail → DENY (fail-closed, not fail-open)
#
# Why fail-closed: Board铁律 — 宁可多拦一次，不可漏放一次。
# If governance can't verify a tool call, the safe default is DENY.

YSTAR_DIR="/Users/haotianliu/.openclaw/workspace/ystar-company"
YGOV_DIR="/Users/haotianliu/.openclaw/workspace/Y-star-gov"
SOCK="${YSTAR_HOOK_SOCK:-/tmp/ystar_hook.sock}"
PAYLOAD=$(cat)

# AMENDMENT-025 P2: Self-heal whitelist (always-allow regardless of governance state)
# Rationale: when governance brick'd self, these commands MUST be allowed to recover
case "$PAYLOAD" in
    *"pkill"*"hook_daemon"*|*"pkill"*"hook_wrapper"*|*"rm "*"/tmp/ystar_hook.sock"*)
        echo '{"action":"allow","message":"[A025-P2] self-heal: daemon kill bypass"}'
        exit 0;;
    *"echo"*"> /Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_active_agent"*|*"echo"*"> .ystar_active_agent"*)
        echo '{"action":"allow","message":"[A025-P2] self-heal: active_agent restore bypass"}'
        exit 0;;
    *"governance_boot.sh"*)
        echo '{"action":"allow","message":"[A025-P2] self-heal: governance reboot bypass"}'
        exit 0;;
esac

# ── FAST PATH: daemon running ──────────────────────────────────────────
if [ -S "$SOCK" ]; then
    if command -v socat &>/dev/null; then
        RESULT=$(echo "$PAYLOAD" | socat - UNIX-CONNECT:"$SOCK" 2>/dev/null)
    else
        RESULT=$(python3.11 -c "
import socket,sys,json
s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
s.connect('$SOCK')
s.sendall(sys.stdin.buffer.read())
s.shutdown(socket.SHUT_WR)
d=b''
while True:
    c=s.recv(65536)
    if not c:break
    d+=c
s.close()
sys.stdout.write(d.decode())
" <<< "$PAYLOAD" 2>/dev/null)
    fi

    # If daemon returned a valid result, output it
    if [ -n "$RESULT" ]; then
        # Emit HOOK_PRE_CALL (canonical event, k9_audit_v3 requirement)
        python3.11 -c "import sys,time,uuid,json; from ystar.governance.cieu_store import CIEUStore; CIEUStore('.ystar_cieu.db').write_dict({'event_id':str(uuid.uuid4()),'session_id':'hook_chain','agent_id':'governance','event_type':'HOOK_PRE_CALL','decision':'info','evidence_grade':'ops','created_at':time.time(),'seq_global':time.time_ns()//1000,'params':{'hook':'PreToolUse','daemon_path':'$SOCK'},'violations':[],'drift_detected':False,'human_initiator':'system'})" 2>/dev/null &

        # AMENDMENT-018 sync A: emit WHITELIST event (async, fail-open)
        echo "$PAYLOAD" | python3.11 "$YSTAR_DIR/scripts/whitelist_emit.py" 2>/dev/null &

        # AMENDMENT-020 v2: ForgetGuard sync deny
        GUARD_OUT=$(echo "$PAYLOAD" | python3.11 "$YSTAR_DIR/scripts/forget_guard.py" 2>>/tmp/ystar_forget_guard.log)
        GUARD_ACTION=$(echo "$GUARD_OUT" | python3.11 -c "import sys,json;d=json.load(sys.stdin);print(d.get('action','allow'))" 2>/dev/null || echo "allow")
        if [ "$GUARD_ACTION" = "deny" ]; then echo "$GUARD_OUT"; exit 0; fi

        # Emit HOOK_POST_CALL (canonical event, k9_audit_v3 requirement)
        python3.11 -c "import sys,time,uuid,json; from ystar.governance.cieu_store import CIEUStore; CIEUStore('.ystar_cieu.db').write_dict({'event_id':str(uuid.uuid4()),'session_id':'hook_chain','agent_id':'governance','event_type':'HOOK_POST_CALL','decision':'info','evidence_grade':'ops','created_at':time.time(),'seq_global':time.time_ns()//1000,'params':{'hook':'PreToolUse','guard_action':'$GUARD_ACTION'},'violations':[],'drift_detected':False,'human_initiator':'system'})" 2>/dev/null &

        echo "$RESULT"
        exit 0
    fi
    # If daemon returned empty (error), fall through to slow path
fi

# ── SLOW PATH: Labs hook_wrapper.py (includes check_hook + Labs rules) ──
if [ -f "$YSTAR_DIR/scripts/hook_wrapper.py" ]; then
    RESULT=$(echo "$PAYLOAD" | PYTHONPATH="$YGOV_DIR:$PYTHONPATH" python3.11 "$YSTAR_DIR/scripts/hook_wrapper.py" 2>/dev/null)
    if [ -n "$RESULT" ]; then
        echo "$RESULT"
        exit 0
    fi
fi

# ── FALLBACK: fail-closed ──────────────────────────────────────────────
# If neither daemon nor slow path produced a result, DENY the tool call.
# This prevents silent governance bypass on infrastructure failure.
echo '{"action":"block","message":"[Y*gov FAIL-CLOSED] Governance enforcement unavailable. Tool call denied for safety. Check hook daemon: ls /tmp/ystar_hook.sock"}'
