#!/usr/bin/env bash
# Apply Maya fail-closed Edit sequence to scripts/hook_wrapper.py
# 用法 (外部 Terminal, 非 Claude Code, 防 daemon respawn 干扰):
#   bash reports/apply_maya_fail_closed.sh
#
# Source: reports/recovery/maya_hook_wrapper_edits_20260414.json (from Maya subagent JSONL extraction)
# Reason: in-Claude-Code dispatch triggers _hook_daemon.py respawn → file system wipe cycle.
# Board external shell bypasses Claude Code hook entirely.

set -euo pipefail
cd /Users/haotianliu/.openclaw/workspace/ystar-company

ARTIFACT=reports/recovery/maya_hook_wrapper_edits_20260414.json
TARGET=scripts/hook_wrapper.py

[ ! -f "$ARTIFACT" ] && { echo "ERR: artifact missing: $ARTIFACT"; exit 1; }
[ ! -f "$TARGET" ] && { echo "ERR: target missing: $TARGET"; exit 1; }

# Backup
cp "$TARGET" "${TARGET}.bak.$(date +%s)"
echo "BACKUP: ${TARGET}.bak.$(date +%s)"

# Apply each edit via Python (str.replace, idempotent skip if new_string already present)
python3 <<PY
import json
artifact = "$ARTIFACT"
target = "$TARGET"
with open(artifact) as f:
    edits = json.load(f)
with open(target) as f:
    src = f.read()
applied = 0
skipped = 0
for i, e in enumerate(edits, 1):
    old = e.get('full_old', '')
    new = e.get('full_new', '')
    if not old or not new:
        print(f"edit #{i}: SKIP (missing old/new)")
        skipped += 1
        continue
    if new in src:
        print(f"edit #{i}: SKIP (already applied)")
        skipped += 1
        continue
    if old not in src:
        print(f"edit #{i}: SKIP (old_string not found — file drifted)")
        skipped += 1
        continue
    src = src.replace(old, new, 1)
    print(f"edit #{i}: APPLIED")
    applied += 1
with open(target, 'w') as f:
    f.write(src)
print(f"\nTotal: {applied} applied, {skipped} skipped")
PY

echo ""
echo "=== verify FAIL-CLOSED in scripts/hook_wrapper.py ==="
grep -c "FAIL-CLOSED\|GOVERNANCE_FAIL_CLOSED" "$TARGET"

echo ""
echo "=== git status ==="
git status --short scripts/hook_wrapper.py
echo ""
echo "Next: review then 'git add scripts/hook_wrapper.py && git commit'"
