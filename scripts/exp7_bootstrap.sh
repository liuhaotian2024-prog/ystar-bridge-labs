#!/usr/bin/env bash
# AMENDMENT-016 Rule Mirror Sync Pilot — Test Workspace Bootstrap
# Maya-Governance, 2026-04-14
#
# Creates isolated test environment for rule-mirror-sync experiment:
# - rsync prod to ystar-company-test/
# - Isolate hook socket path (/tmp/ystar_hook_exp7.sock)
# - Isolate CIEU db (.ystar_cieu_exp7.db)
# - Safety: NEVER modify production workspace

set -euo pipefail

PROD_ROOT="/Users/haotianliu/.openclaw/workspace/ystar-company"
TEST_ROOT="/Users/haotianliu/.openclaw/workspace/ystar-company-test"

echo "=== AMENDMENT-016 EXP7 Bootstrap ==="
echo "Prod: $PROD_ROOT"
echo "Test: $TEST_ROOT"

# Safety check: confirm we're in prod workspace
if [[ "$PWD" != "$PROD_ROOT" ]]; then
    echo "ERROR: Must run from production workspace: $PROD_ROOT"
    exit 1
fi

# Remove old test workspace if exists
if [[ -d "$TEST_ROOT" ]]; then
    echo "Removing existing test workspace..."
    rm -rf "$TEST_ROOT"
fi

# rsync production to test (exclude git history, runtime artifacts, venv)
echo "Syncing production → test..."
rsync -a \
    --exclude='.git/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.venv/' \
    --exclude='venv/' \
    --exclude='node_modules/' \
    --exclude='.ystar_cieu.db*' \
    --exclude='.ystar_session.json' \
    --exclude='scripts/.session_booted' \
    --exclude='scripts/.session_call_count' \
    --exclude='scripts/.k9_last_read' \
    "$PROD_ROOT/" "$TEST_ROOT/"

echo "Test workspace created at: $TEST_ROOT"

# Create experiment-specific config
echo "Configuring test workspace isolation..."
cd "$TEST_ROOT"

# Isolate hook socket path
cat > .exp7_config.sh <<'EOF'
# EXP7 runtime config — source this before starting hook daemon
export YSTAR_HOOK_SOCKET="/tmp/ystar_hook_exp7.sock"
export YSTAR_CIEU_DB="$PWD/.ystar_cieu_exp7.db"
export YSTAR_SESSION_JSON="$PWD/.ystar_session_exp7.json"

# Safety reminder
echo "EXP7 isolated environment active:"
echo "  Hook socket: $YSTAR_HOOK_SOCKET"
echo "  CIEU DB:     $YSTAR_CIEU_DB"
echo "  Session:     $YSTAR_SESSION_JSON"
EOF

# Create minimal session.json for test
cat > .ystar_session_exp7.json <<'EOF'
{
  "active_agent": "eng-governance",
  "session_id": "exp7-rule-mirror-test",
  "workspace": "/Users/haotianliu/.openclaw/workspace/ystar-company-test",
  "governance_contract": "AGENTS.md",
  "hook_socket": "/tmp/ystar_hook_exp7.sock",
  "cieu_db": ".ystar_cieu_exp7.db"
}
EOF

echo ""
echo "✅ Bootstrap complete"
echo ""
echo "Next steps (IN TEST WORKSPACE):"
echo "  cd $TEST_ROOT"
echo "  source .exp7_config.sh"
echo "  # Start hook daemon with isolated socket"
echo "  # Implement watcher prototype"
echo ""
echo "⚠️  NEVER modify production workspace during experiment"
echo "⚠️  Use 'pkill -9 -f hook_daemon && rm -f /tmp/ystar_hook_exp7.sock' to reset"
