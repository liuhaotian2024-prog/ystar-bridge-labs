#!/bin/bash
# Audience: Board (Haotian Liu) to run via `!` shell. Also: future CEO/CTO
# sessions reading the post-mortem of this misdiagnosis.
#
# Research basis: Empirical benchmark 2026-04-18 20:07 (CEO-authored script
# apply_policy_cache_wire.sh output) showed policy-cache wiring active
# but hook wall time remained ~14s, identical to no-cache baseline. Later
# benchmark with daemon fast path (hook_client_labs.sh via
# /tmp/ystar_hook.sock) showed 0.299s — 50x faster. The true root cause
# was daemon offline forcing every tool call through a cold Python
# process start + ystar import; policy compile was only ~2s of the 14s.
#
# Synthesis: The policy-cache wiring is architecturally redundant with
# the daemon fast path. It was a mis-diagnosis. However the cache module
# itself (OPA Bundle Persistence pattern) is sound and remains useful as
# a slow-path fallback if the daemon dies again. This script reverts ONLY
# the wire in session.py (keep cache module as future-optional tool).
#
# Rollback of revert: re-run apply_policy_cache_wire.sh to re-wire.
#
# Audience note for future engineers: the cache module
# `Y-star-gov/ystar/kernel/_policy_bundle_cache.py` stays; when daemon
# fast path is operational the cache is bypassed by design; the wire is
# removed because it gave the misleading appearance that caching alone
# fixed the 14s symptom — which the benchmarks disproved.

set -e

YGOV=/Users/haotianliu/.openclaw/workspace/Y-star-gov
SESSION_PY=$YGOV/ystar/session.py

echo "=== STEP 1: check if wire is present ==="
if ! grep -q "_policy_bundle_cache" "$SESSION_PY"; then
    echo "Wire not present. Nothing to revert."
    exit 0
fi

echo "=== STEP 2: remove wire + restore original Policy.from_agents_md ==="
python3 << 'PYEOF'
from pathlib import Path

p = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/session.py")
src = p.read_text()

# Locate and remove the inserted block + restore original signature.
# The inserted pattern added a wrapper classmethod + renamed underlying to
# _from_agents_md_uncached. We undo by:
#   1. rename _from_agents_md_uncached back to from_agents_md
#   2. delete the wrapper classmethod block

wrapper_start = 'def from_agents_md(cls, agents_md_path: str, confirm: bool = True):\n        # CZL-ARCH-PERF-1'
if wrapper_start not in src:
    raise SystemExit("ERROR: wrapper-start marker not found — cannot safely revert")

# Find end of wrapper (just before the renamed classmethod decl).
marker_end = '\n    @classmethod\n    def _from_agents_md_uncached(cls, agents_md_path: str, confirm: bool = True)'
idx_start = src.find(wrapper_start)
idx_end = src.find(marker_end, idx_start)
if idx_end < 0:
    raise SystemExit("ERROR: wrapper-end marker not found")

# Remove wrapper block, keep the @classmethod decorator+def that follows
# but rename _from_agents_md_uncached -> from_agents_md.
before = src[:idx_start]
after_block = src[idx_end + len(marker_end):]
# Rebuild: before + original signature of `def from_agents_md...` + after
restored = before + 'def from_agents_md(cls, agents_md_path: str, confirm: bool = True)' + after_block

# Final sanity: only one from_agents_md remains.
if restored.count('def from_agents_md(cls') != 1:
    raise SystemExit("ERROR: final sanity check failed — expected 1 from_agents_md, got {}".format(
        restored.count('def from_agents_md(cls')))
if '_from_agents_md_uncached' in restored:
    raise SystemExit("ERROR: _from_agents_md_uncached still present after revert")

p.write_text(restored)
print(f"Reverted {p}: {len(src) - len(restored)} bytes removed")
PYEOF

echo ""
echo "=== STEP 3: verify syntax ==="
cd $YGOV && python3 -c "import ast; ast.parse(open('ystar/session.py').read()); print('session.py SYNTAX OK')"

echo ""
echo "=== STEP 4: pytest sanity ==="
cd $YGOV && python3 -m pytest tests/kernel/test_policy_bundle_cache.py tests/adapters/test_identity_arch1.py -q 2>&1 | tail -5

echo ""
echo "=== DONE: wire removed, cache module retained as future-optional ==="
echo "Cache module still at: Y-star-gov/ystar/kernel/_policy_bundle_cache.py"
echo "Tests still at:        Y-star-gov/tests/kernel/test_policy_bundle_cache.py"
