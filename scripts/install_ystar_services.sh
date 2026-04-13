#!/bin/bash
# Y* Bridge Labs — Install YStar Services (One-Time Setup)
# AMENDMENT-015 v2 LRS C8: LaunchAgent installation for zero-touch boot
#
# Usage: bash scripts/install_ystar_services.sh

set -e

REPO_ROOT="/Users/haotianliu/.openclaw/workspace/ystar-company"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
MARKER="$REPO_ROOT/.ystar_services_installed"

echo "=== Y* Services Installer ==="
echo ""

# Check if already installed
if [ -f "$MARKER" ]; then
    echo "⚠ Services already installed (marker found: $MARKER)"
    echo "To reinstall, delete the marker file and run again:"
    echo "  rm $MARKER"
    echo "  bash scripts/install_ystar_services.sh"
    exit 0
fi

# ── STEP 1: Install LaunchAgent plists ─────────────────────────────────
echo "[1/4] Installing LaunchAgent plists..."

mkdir -p "$LAUNCHD_DIR"

for plist in hook_daemon gov_mcp crontab_sync; do
    SRC="$REPO_ROOT/scripts/launchagents/com.ystar.$plist.plist"
    DST="$LAUNCHD_DIR/com.ystar.$plist.plist"

    if [ ! -f "$SRC" ]; then
        echo "  ✗ Source plist not found: $SRC"
        exit 1
    fi

    cp "$SRC" "$DST"
    echo "  ✓ Installed com.ystar.$plist.plist"
done

# ── STEP 2: Load LaunchAgents ───────────────────────────────────────────
echo "[2/4] Loading LaunchAgents..."

for plist in hook_daemon gov_mcp crontab_sync; do
    LABEL="com.ystar.$plist"

    # Unload first if already loaded (handles reinstall case)
    launchctl unload "$LAUNCHD_DIR/$LABEL.plist" 2>/dev/null || true

    # Load the agent
    if launchctl load "$LAUNCHD_DIR/$LABEL.plist" 2>&1; then
        echo "  ✓ Loaded $LABEL"
    else
        echo "  ⚠ Failed to load $LABEL (may already be loaded)"
    fi
done

sleep 3  # Give daemons time to start

# ── STEP 3: Verify Services Running ────────────────────────────────────
echo "[3/4] Verifying services..."

VERIFY_FAILED=0

# Check hook daemon
if [ -S /tmp/ystar_hook.sock ]; then
    echo "  ✓ Hook daemon socket exists"
else
    echo "  ✗ Hook daemon socket not found"
    VERIFY_FAILED=1
fi

# Check gov-mcp
if pgrep -f "gov_mcp.*--port 7922" > /dev/null; then
    echo "  ✓ GOV-MCP server running"
else
    echo "  ✗ GOV-MCP server not running"
    VERIFY_FAILED=1
fi

# ── STEP 4: Install Crontab Entries ─────────────────────────────────────
echo "[4/4] Installing crontab entries..."

if bash "$REPO_ROOT/scripts/ensure_crontab.sh"; then
    echo "  ✓ Crontab entries synced"
else
    echo "  ⚠ Crontab sync had warnings (check logs)"
fi

# ── FINAL STEPS ─────────────────────────────────────────────────────────
if [ $VERIFY_FAILED -eq 0 ]; then
    touch "$MARKER"
    echo ""
    echo "=== INSTALLATION COMPLETE ==="
    echo "✓ All services are running"
    echo "✓ LaunchAgents will auto-restart daemons on crash or reboot"
    echo "✓ Crontab entries installed"
    echo ""
    echo "Marker file created: $MARKER"
    echo ""
    echo "From now on, session boot is AUTOMATIC:"
    echo "  • Hook daemon and GOV-MCP will auto-start at system boot"
    echo "  • zero_touch_boot.sh will self-heal on every Claude Code session"
    echo "  • No manual intervention required"
else
    echo ""
    echo "=== INSTALLATION INCOMPLETE ==="
    echo "✗ Some services failed verification"
    echo "Check logs:"
    echo "  /tmp/ystar_hook_daemon_error.log"
    echo "  /tmp/ystar_gov_mcp_error.log"
    echo ""
    echo "Marker NOT created. Fix errors and run again."
    exit 1
fi
