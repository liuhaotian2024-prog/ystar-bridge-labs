#!/bin/bash
# Y* Bridge Labs — Zero-Touch Boot Sequencer
# AMENDMENT-015 v2 LRS C8: Fully automated session recovery
# Target: < 30s from Claude Code start to ALL SYSTEMS GO
#
# Usage: bash scripts/zero_touch_boot.sh

set -e

REPO_ROOT="/Users/haotianliu/.openclaw/workspace/ystar-company"
YGOV_ROOT="/Users/haotianliu/.openclaw/workspace/Y-star-gov"
LOG_FILE="/tmp/zero_touch_boot_$(date +%s).log"

# Redirect all output to log file + stdout
exec > >(tee -a "$LOG_FILE")
exec 2>&1

echo "=== ZERO-TOUCH BOOT SEQUENCER ==="
echo "Started: $(date)"
echo "Log: $LOG_FILE"
echo ""

FAILURES=0
START_TIME=$(date +%s)

# ── STEP 1: Identity Self-Heal ──────────────────────────────────────────
echo "[1/6] Agent Identity Self-Heal"
IDENTITY_FILE="$REPO_ROOT/.ystar_active_agent"

if [ ! -f "$IDENTITY_FILE" ] || [ ! -s "$IDENTITY_FILE" ]; then
    echo "ceo" > "$IDENTITY_FILE"
    echo "  ✓ Reset identity to CEO (file missing/empty)"
elif [ "$(cat "$IDENTITY_FILE")" != "ceo" ]; then
    PREV=$(cat "$IDENTITY_FILE")
    echo "ceo" > "$IDENTITY_FILE"
    echo "  ✓ Reset identity to CEO (was: $PREV)"
else
    echo "  ✓ Identity already CEO"
fi

# ── STEP 2: Hook Daemon Health Check + Auto-Restart ────────────────────
echo "[2/6] Hook Daemon Health"

if [ -S /tmp/ystar_hook.sock ]; then
    # Socket exists, test if it's responsive
    TEST_RESPONSE=$(echo '{"tool_name":"Read","tool_input":{"file_path":"README.md"}}' | \
        bash "$REPO_ROOT/scripts/hook_client_labs.sh" 2>/dev/null || echo "")

    if [ -n "$TEST_RESPONSE" ]; then
        echo "  ✓ Hook daemon RUNNING and RESPONSIVE"
    else
        echo "  ⚠ Hook daemon socket exists but not responsive, restarting..."
        pkill -f "_hook_daemon.py" 2>/dev/null || true
        rm -f /tmp/ystar_hook.sock
        sleep 1
        cd "$REPO_ROOT"
        PYTHONPATH="$YGOV_ROOT:$PYTHONPATH" python3.11 "$YGOV_ROOT/ystar/_hook_daemon.py" &
        sleep 2

        if [ -S /tmp/ystar_hook.sock ]; then
            echo "  ✓ Hook daemon RESTARTED"
        else
            echo "  ✗ Hook daemon FAILED to restart"
            FAILURES=$((FAILURES + 1))
        fi
    fi
else
    echo "  ⚠ Hook daemon not running, starting..."
    cd "$REPO_ROOT"
    PYTHONPATH="$YGOV_ROOT:$PYTHONPATH" python3.11 "$YGOV_ROOT/ystar/_hook_daemon.py" &
    sleep 2

    if [ -S /tmp/ystar_hook.sock ]; then
        echo "  ✓ Hook daemon STARTED"
    else
        echo "  ✗ Hook daemon FAILED to start"
        FAILURES=$((FAILURES + 1))
    fi
fi

# ── STEP 3: GOV-MCP Server Health Check + Auto-Restart ─────────────────
echo "[3/6] GOV-MCP Server Health"

if pgrep -f "gov_mcp.*--port 7922" > /dev/null; then
    # Process running, test if port is listening
    if nc -z 127.0.0.1 7922 2>/dev/null; then
        echo "  ✓ GOV-MCP server RUNNING on port 7922"
    else
        echo "  ⚠ GOV-MCP process exists but port not listening, restarting..."
        pkill -f "gov_mcp.*--port 7922" 2>/dev/null || true
        sleep 1
        python3.11 -m gov_mcp \
            --session-config "$REPO_ROOT/.ystar_session.json" \
            --transport sse \
            --host 0.0.0.0 \
            --port 7922 \
            > /tmp/ystar_gov_mcp.log 2>&1 &
        sleep 2

        if pgrep -f "gov_mcp.*--port 7922" > /dev/null; then
            echo "  ✓ GOV-MCP server RESTARTED"
        else
            echo "  ✗ GOV-MCP server FAILED to restart"
            FAILURES=$((FAILURES + 1))
        fi
    fi
else
    echo "  ⚠ GOV-MCP not running, starting..."
    python3.11 -m gov_mcp \
        --session-config "$REPO_ROOT/.ystar_session.json" \
        --transport sse \
        --host 0.0.0.0 \
        --port 7922 \
        > /tmp/ystar_gov_mcp.log 2>&1 &
    sleep 2

    if pgrep -f "gov_mcp.*--port 7922" > /dev/null; then
        echo "  ✓ GOV-MCP server STARTED"
    else
        echo "  ✗ GOV-MCP server FAILED to start"
        FAILURES=$((FAILURES + 1))
    fi
fi

# ── STEP 4: Crontab Entries (Idempotent) ───────────────────────────────
echo "[4/6] Crontab Entries"

if [ -f "$REPO_ROOT/scripts/ensure_crontab.sh" ]; then
    bash "$REPO_ROOT/scripts/ensure_crontab.sh" | grep -E "✓|ADD" || echo "  (no changes)"
else
    echo "  ⚠ ensure_crontab.sh not found, skipping"
fi

# ── STEP 5: Script Override Grant (Secretary-only restriction bypass) ──
echo "[5/6] Script Override Status"

OVERRIDE_FILE="$REPO_ROOT/.ystar_session.json"
if [ -f "$OVERRIDE_FILE" ]; then
    OVERRIDE_ACTIVE=$(python3 -c "import json; print(json.load(open('$OVERRIDE_FILE')).get('script_override_active', False))" 2>/dev/null || echo "false")

    if [ "$OVERRIDE_ACTIVE" = "True" ] || [ "$OVERRIDE_ACTIVE" = "true" ]; then
        echo "  ✓ Script override ACTIVE (allows .ystar_active_agent writes)"
    else
        echo "  ℹ Script override INACTIVE (default — identity writes restricted to Secretary)"
    fi
else
    echo "  ⚠ .ystar_session.json not found"
    FAILURES=$((FAILURES + 1))
fi

# ── STEP 6: Session Markers ────────────────────────────────────────────
echo "[6/6] Session Markers"

touch "$REPO_ROOT/scripts/.session_booted"
echo "0" > "$REPO_ROOT/scripts/.session_call_count"
echo "  ✓ Created .session_booted and reset call counter"

# ── FINAL REPORT ────────────────────────────────────────────────────────
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""
echo "=== BOOT SUMMARY ==="
echo "Duration: ${DURATION}s"
echo "Failures: $FAILURES"

if [ $FAILURES -eq 0 ]; then
    echo "Status: ✓ ALL SYSTEMS ONLINE"
    exit 0
else
    echo "Status: ✗ $FAILURES COMPONENT(S) FAILED"
    exit 1
fi
