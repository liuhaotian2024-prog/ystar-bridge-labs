#!/bin/bash
# [L2->L3] WIP Auto-Commit — Prevent work-in-flight evaporation
# Cron: */10 * * * * (every 10 minutes)
# CZL-WIP-AUTOCOMMIT-RESUSCITATE: minimal viable version
# - Only operates when active_agent is ceo or cto
# - Logs to scripts/.logs/wip.log
# - Detects hash changes (dry-run echo, no actual git add/commit yet)
# - Full auto-commit logic is deferred to CZL-AUTO-COMMIT-PUSH-IMPL

WORKSPACE="/Users/haotianliu/.openclaw/workspace/ystar-company"
LOG_DIR="$WORKSPACE/scripts/.logs"
LOG_FILE="$LOG_DIR/wip.log"
HASH_FILE="$LOG_DIR/.wip_last_hash"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

# Check active agent — only ceo/cto may auto-commit
ACTIVE_AGENT=""
for marker in "$WORKSPACE/scripts/.ystar_active_agent" "$WORKSPACE/.ystar_active_agent"; do
    if [ -f "$marker" ]; then
        ACTIVE_AGENT=$(cat "$marker" 2>/dev/null | tr -d '[:space:]')
        break
    fi
done

if [ -z "$ACTIVE_AGENT" ]; then
    log "SKIP: no active_agent marker found"
    exit 0
fi

case "$ACTIVE_AGENT" in
    ceo|cto|Aiden-CEO|Ethan-CTO)
        ;;
    *)
        log "SKIP: active_agent='$ACTIVE_AGENT' is not ceo/cto, no auto-commit"
        exit 0
        ;;
esac

# Change detection: hash of porcelain status for governance-critical dirs
cd "$WORKSPACE" || { log "ERROR: cannot cd to workspace"; exit 1; }
CURRENT_HASH=$(git status --porcelain scripts/ governance/ .claude/ 2>/dev/null | sha256sum | cut -d' ' -f1)

if [ -f "$HASH_FILE" ]; then
    LAST_HASH=$(cat "$HASH_FILE" 2>/dev/null)
else
    LAST_HASH=""
fi

if [ "$CURRENT_HASH" = "$LAST_HASH" ]; then
    log "NO_CHANGE: hash unchanged ($ACTIVE_AGENT)"
    exit 0
fi

# Hash changed — record it
echo "$CURRENT_HASH" > "$HASH_FILE"

# Count changed files
CHANGED_COUNT=$(git status --porcelain scripts/ governance/ .claude/ 2>/dev/null | wc -l | tr -d ' ')

if [ "$CHANGED_COUNT" = "0" ]; then
    log "CLEAN: no uncommitted changes in governance dirs ($ACTIVE_AGENT)"
    exit 0
fi

# DRY-RUN detection (actual commit deferred to CZL-AUTO-COMMIT-PUSH-IMPL)
log "DETECTED: $CHANGED_COUNT files changed in governance dirs (agent=$ACTIVE_AGENT, hash=$CURRENT_HASH)"
log "DRY_RUN: would auto-commit $CHANGED_COUNT files (actual commit not yet implemented)"
