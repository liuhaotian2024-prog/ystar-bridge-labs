#!/usr/bin/env bash
#
# Aiden Cognition Guardian — Disaster Recovery
#
# Board directive 2026-04-12: One-command full recovery from mirror.
#
# Usage:
#   bash scripts/disaster_recovery.sh [--from <mirror_path>] [--verify-only]
#
# Exit codes:
#   0 = Recovery successful (or verify passed)
#   1 = Recovery failed
#   2 = Verification found differences
#   3 = Governance boot failed after recovery

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPANY_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEFAULT_MIRROR="$HOME/.openclaw/mirror/ystar-company-backup"

MIRROR_PATH="$DEFAULT_MIRROR"
VERIFY_ONLY=0

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --from)
            MIRROR_PATH="$2"
            shift 2
            ;;
        --verify-only)
            VERIFY_ONLY=1
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--from <mirror_path>] [--verify-only]"
            exit 1
            ;;
    esac
done

echo "=========================================="
echo "Aiden Cognition Guardian — Disaster Recovery"
echo "=========================================="
echo "Company Root: $COMPANY_ROOT"
echo "Mirror Path: $MIRROR_PATH"
echo ""

# Check mirror exists
if [[ ! -d "$MIRROR_PATH" ]]; then
    echo "ERROR: Mirror directory not found: $MIRROR_PATH"
    exit 1
fi

if [[ ! -f "$MIRROR_PATH/MANIFEST.json" ]]; then
    echo "ERROR: No MANIFEST.json in mirror directory"
    exit 1
fi

# Verify mode
if [[ $VERIFY_ONLY -eq 1 ]]; then
    echo "VERIFY-ONLY mode: comparing mirror vs current state"
    echo ""

    python3 "$SCRIPT_DIR/aiden_cognition_backup.py" \
        --backup-root "$MIRROR_PATH" \
        --verify-only

    exit $?
fi

# Recovery mode
echo "WARNING: This will overwrite current cognition state with mirror backup."
echo "Mirror timestamp: $(jq -r '.timestamp' "$MIRROR_PATH/MANIFEST.json")"
echo ""
read -p "Continue? (yes/no): " confirm

if [[ "$confirm" != "yes" ]]; then
    echo "Recovery cancelled."
    exit 0
fi

echo ""
echo "Starting recovery..."
echo ""

# Read manifest
FILE_COUNT=$(jq -r '.file_count' "$MIRROR_PATH/MANIFEST.json")
TOTAL_BYTES=$(jq -r '.total_bytes' "$MIRROR_PATH/MANIFEST.json")

echo "Files to restore: $FILE_COUNT"
echo "Total size: $(numfmt --to=iec-i --suffix=B $TOTAL_BYTES 2>/dev/null || echo $TOTAL_BYTES bytes)"
echo ""

# Restore each file atomically
recovered=0
failed=0

jq -r '.files | keys[]' "$MIRROR_PATH/MANIFEST.json" | while read -r rel_path; do
    src="$MIRROR_PATH/$rel_path"
    dst="$COMPANY_ROOT/$rel_path"

    if [[ ! -f "$src" ]]; then
        echo "SKIP: Mirror file missing: $rel_path"
        ((failed++)) || true
        continue
    fi

    # Atomic restore: copy to .tmp, then rename
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst.tmp"
    mv "$dst.tmp" "$dst"

    ((recovered++)) || true

    if (( recovered % 100 == 0 )); then
        echo "Restored $recovered / $FILE_COUNT files..."
    fi
done

echo ""
echo "Recovery complete: $recovered files restored"
if (( failed > 0 )); then
    echo "WARNING: $failed files failed to restore"
fi
echo ""

# Verify recovery
echo "Verifying restored state..."
python3 "$SCRIPT_DIR/aiden_cognition_backup.py" \
    --backup-root "$MIRROR_PATH" \
    --verify-only > /tmp/recovery_verify.json

VERIFY_STATUS=$(jq -r '.status' /tmp/recovery_verify.json)
if [[ "$VERIFY_STATUS" != "ok" ]]; then
    echo "WARNING: Verification found differences:"
    jq . /tmp/recovery_verify.json
    echo ""
    echo "Recovery completed but state may be inconsistent."
    exit 2
fi

echo "Verification passed: backup and restored state match."
echo ""

# Run governance boot to verify system integrity
echo "Running governance boot to verify system integrity..."
echo ""

if [[ ! -f "$COMPANY_ROOT/.ystar_active_agent" ]]; then
    echo "ceo" > "$COMPANY_ROOT/.ystar_active_agent"
fi

ACTIVE_AGENT=$(cat "$COMPANY_ROOT/.ystar_active_agent")

bash "$SCRIPT_DIR/governance_boot.sh" "$ACTIVE_AGENT"

BOOT_EXIT=$?
if [[ $BOOT_EXIT -ne 0 ]]; then
    echo ""
    echo "ERROR: Governance boot failed after recovery (exit code $BOOT_EXIT)"
    echo "System may require manual intervention."
    exit 3
fi

echo ""
echo "=========================================="
echo "Disaster recovery complete: ALL SYSTEMS GO"
echo "=========================================="
exit 0
