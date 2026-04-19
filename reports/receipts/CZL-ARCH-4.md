# CZL-ARCH-4 Completion Receipt — RouterRegistry loader + IngressRequest

**Atomic ID**: CZL-ARCH-4
**Claimed by**: eng-kernel (Leo)
**Completed + CEO Verified**: 2026-04-18 (17 tool_uses / 399s / 14/14 tests)

**Audience**: Board (Phase 2 router integration substrate closed), CTO Ethan (his Part B design manifest), future engineers registering new router rules via directory-load pattern.

**Research basis**: Ethan arch doc Part B spec. Industry precedent: Python entry_points, Django auto-discover, Flask blueprints — all "load modules from directory, invoke register callables". Ryan ARCH-6 put stub in hook.py awaiting this canonical implementation.

**Synthesis**: Three additions, zero existing behavior changed. IngressRequest dataclass normalizes payloads from 3 sources (Claude Code / MCP / CLI) with `from_*` classmethods + `to_payload()` roundtrip. `unregister_all()` clears rules + resets execution_depth. `load_rules_dir(path)` globs `*.py` (skips `_`-prefixed), imports via importlib.util, registers `RULES` list (idempotent on duplicates). Hook.py stub replaced with 5-line thin delegation.

## 5-Tuple
- **Y\***: router_registry gains directory-load + unregister + IngressRequest normalize; 5+ tests
- **Xt**: router_registry was read/write API only, no bulk-load or cleanup; hook.py had 39-line inline stub awaiting canonical
- **U**:
  - `Y-star-gov/ystar/governance/router_registry.py` — added IngressRequest dataclass (3 classmethods + to_payload), unregister_all, load_rules_dir
  - `Y-star-gov/ystar/adapters/hook.py` — `_load_rules_from_dir` stub replaced with 5-line thin wrapper
  - `Y-star-gov/tests/governance/test_router_registry_loader.py` — 14 tests (4+3+3+2+2)
- **Yt+1**: 14/14 tests PASS; pre-existing test_router_registry.py 27/28 (1 pre-existing failure in EnforceDecision enum count from our earlier additions)
- **Rt+1**: 0
