#!/bin/bash
# Audience: Board (Haotian Liu) to run via `!` shell as the 2nd half of the
# policy-cache rollout. First half (apply_policy_cache.sh) shipped the
# cache module + tests; this half wires it into Policy.from_agents_md so
# the 14s overhead is actually saved at runtime.
#
# Research basis: Step 3 pytest in prior run proved the cache module works
# in isolation (3/3 pass). Step 4 benchmark confirmed 15.828s baseline.
# Without wiring, the cache module is dead code — the runtime still calls
# the uncached compile path. This script performs the one-idempotent edit
# needed to flip the live path to cache-aware, guarded by env flag.
#
# Synthesis: session.py Policy.from_agents_md top adds a 4-line env check:
# when YSTAR_POLICY_CACHE=1, delegate to get_cached_policy with the
# existing compile path as the fallback callable. When env unset = zero
# behavior change. Benchmarks then run twice with the flag on — warm cache
# miss first call, hit second call — to capture actual savings.
#
# Rollback: `git diff` of session.py + revert the added block; or simply
# unset YSTAR_POLICY_CACHE (the added block is env-gated).
#
# CEO authored 2026-04-18 as follow-up to apply_policy_cache.sh.

set -e

YGOV=/Users/haotianliu/.openclaw/workspace/Y-star-gov
SESSION_PY=$YGOV/ystar/session.py

echo "=== STEP 1: check if already wired ==="
if grep -q "_policy_bundle_cache" "$SESSION_PY"; then
    echo "Already wired. Skipping edit."
else
    echo "=== STEP 2: wire cache into Policy.from_agents_md ==="
    python3 << 'PYEOF'
import re
from pathlib import Path

p = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/session.py")
src = p.read_text()

# Target: inside Policy.from_agents_md classmethod, right after the def
# line, insert an env-gated delegation to get_cached_policy. The actual
# compile work is whatever the body already does — we wrap it in a nested
# closure so the cached_fn calls back into the original logic.

marker = "def from_agents_md(cls, agents_md_path: str, confirm: bool = True)"
new_call = '''def from_agents_md(cls, agents_md_path: str, confirm: bool = True):
        # CZL-ARCH-PERF-1 (2026-04-18): OPA-style on-disk policy cache.
        # Env flag YSTAR_POLICY_CACHE=1 opt-in. Default = existing behavior.
        import os as _os_arch_perf_1
        if _os_arch_perf_1.environ.get("YSTAR_POLICY_CACHE", "").strip() in ("1", "true", "yes", "on"):
            try:
                from ystar.kernel._policy_bundle_cache import get_cached_policy as _gcp
                return _gcp(agents_md_path, lambda p: cls._from_agents_md_uncached(p, confirm))
            except Exception as _cache_exc:
                import logging as _log_mod
                _log_mod.getLogger("ystar.policy_cache_wire").warning(
                    "policy cache wire failed, falling back: %s", _cache_exc)
        return cls._from_agents_md_uncached(agents_md_path, confirm)

    @classmethod
    def _from_agents_md_uncached(cls, agents_md_path: str, confirm: bool = True)'''

if marker not in src:
    raise SystemExit("ERROR: expected marker '{}' not found in session.py".format(marker))

# Also replace the signature-only line with the full wrap. Match flexible
# leading spaces.
pattern = r'def from_agents_md\(cls, agents_md_path: str, confirm: bool = True\)'
if not re.search(pattern, src):
    raise SystemExit("ERROR: regex marker not found")

src_new = re.sub(pattern, new_call, src, count=1)

p.write_text(src_new)
print(f"Wired {p} ({len(src_new) - len(src)} bytes added)")
PYEOF
fi

echo ""
echo "=== STEP 3: verify syntax ==="
cd $YGOV && python3 -c "import ast; ast.parse(open('ystar/session.py').read()); print('session.py SYNTAX OK')"

echo ""
echo "=== STEP 4: pytest regression (identity + kernel) ==="
cd $YGOV && python3 -m pytest tests/kernel/test_policy_bundle_cache.py tests/adapters/test_identity_arch1.py -q 2>&1 | tail -5

echo ""
echo "=== STEP 5: benchmark with cache ON ==="
cd /Users/haotianliu/.openclaw/workspace/ystar-company

echo "--- call 1 (cold, should compile + store) ---"
export YSTAR_POLICY_CACHE=1
{ time (echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/x"},"agent_id":"","agent_type":""}' | python3 scripts/hook_wrapper.py 2>/dev/null > /dev/null); } 2>&1 | tail -3

echo ""
echo "--- call 2 (warm, should hit cache) ---"
{ time (echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/x"},"agent_id":"","agent_type":""}' | python3 scripts/hook_wrapper.py 2>/dev/null > /dev/null); } 2>&1 | tail -3

echo ""
echo "--- call 3 (warm, should hit cache) ---"
{ time (echo '{"tool_name":"Read","tool_input":{"file_path":"/tmp/x"},"agent_id":"","agent_type":""}' | python3 scripts/hook_wrapper.py 2>/dev/null > /dev/null); } 2>&1 | tail -3

echo ""
echo "=== DONE: compare real-time of call 2/3 vs 15.8s baseline ==="
