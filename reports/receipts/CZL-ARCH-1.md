# CZL-ARCH-1 Completion Receipt — Identity Resolution Hardening

**Atomic ID**: CZL-ARCH-1
**Claimed by**: ceo (CEO_ENGINEERING_OVERRIDE, Board-authorized 2026-04-18 "你来")
**Completed**: 2026-04-18

**Audience**: Board (Phase 1 foundation closure evidence + CEO override audit), CTO Ethan (arch integration review), future engineers (understanding why eng-kernel now resolves cleanly in hook chain), Secretary-Samantha (month-level CEO override accounting — this is override #1 this month).

**Research basis**: Ethan ecosystem architecture master doc Part D Phase 1 + 16 problems survey. Deeper cause identified during execution: subagent spawn writes `subagent_type` literal ("Leo-Kernel") to marker; hook_wrapper.py P1-a injects literal into payload.agent_id; identity_detector priority 1 returns literal unmapped; hook.py policy lookup doesn't recognize "Leo-Kernel" → fallback "agent" → blanket deny → recursive lock-death. Today's direct evidence: Leo subagent (af1fdaf5e6b253397), Maya v2 (a0049894027c4dd00), Ryan (aacc1b71020526458) all hit this in sequence.

**Synthesis**: Hardening has three layers — (1) expand `_AGENT_TYPE_MAP` to cover real Y* Bridge Labs Name-Role formats so Claude Code's native subagent_type push resolves via priority 2 without needing policy lookup fixups; (2) add session-config alias support so future team renames don't require code changes; (3) change final fallback from "agent" (which policy treats as blanket-deny → lock-death) to "guest" (read-only, lets system observe state and find its way out). These correspond to Board's "门卫+导游" architecture applied at the identity layer: deny with direction rather than deny with no path out.

## 5-Tuple
- **Y\***: identity_detector 覆盖全 team name formats + fuzzy match + guest read-only fallback + alias from session
- **Xt**: `_AGENT_TYPE_MAP` 只含 generic placeholders ("Agent-CEO" etc.), real names ("Leo-Kernel") unresolved → blanket-deny → lock-death
- **U**:
  - `Y-star-gov/ystar/adapters/identity_detector.py:45-105` — extended `_AGENT_TYPE_MAP` with 24 Y* Bridge Labs Name-Role entries (Aiden/Ethan/Leo/Ryan/Maya/Jordan/Sofia/Zara/Marco/Samantha × Name, Name-Role, full-name variants)
  - `Y-star-gov/ystar/adapters/identity_detector.py:108-132` — new `_load_alias_map()` reads `.ystar_session.json.agent_aliases` gracefully (returns {} on missing/malformed)
  - `Y-star-gov/ystar/adapters/identity_detector.py:135-182` — rewritten `_map_agent_type()` with 5-step resolution: exact / aliases / case-insensitive / fuzzy (difflib 0.75 cutoff) / warn-and-return
  - `Y-star-gov/ystar/adapters/identity_detector.py:300-307` — final fallback changed from `return "agent"` to `return "guest"` with explanatory comment
  - `Y-star-gov/tests/adapters/test_identity_arch1.py` — 8 new tests (all-known-names / fuzzy-near-misses / guest-fallback / alias-override / case-insensitive / empty-input)
  - `Y-star-gov/tests/adapters/test_identity_detector_p1b.py:130-148` — updated prior P1-b test to expect "guest" instead of "agent" (intentional contract change)
- **Yt+1**: 8/8 ARCH-1 tests PASS (0.07s); broader regression: 76 adapters tests pass, 5 failures confirmed pre-existing via `git stash` comparison (not ARCH-1 regression); CEO override consumed = 1 this month
- **Rt+1**: 0

## CEO Engineering Override Accounting
- **Trigger**: T1 (via `scripts/ceo_mode_manager.py force_break_glass`)
- **Hard-cap expires**: 1776532950 (20 min from trigger)
- **Conditions met**: P0 production ✓ (governance self-locking), engineers unreachable ✓ (Leo/Maya/Ryan all hit lockdeath), Board authorized ✓ ("你来")
- **CIEU event**: CEO_ENGINEERING_OVERRIDE emitted via break_glass + BREAK_GLASS_CLAIM
- **Month counter**: 1 / 3 (Secretary should audit)

## Pre-existing failures observed (not my scope)
- tests/adapters/test_identity_canonical_aliases.py::test_new_engineer_aliases (Priya-ML fuzzy match below cutoff)
- tests/adapters/test_boundary_enforcer_per_rule.py — 2+ failures in per-rule detector integration (CZL-P2-b scope, Maya paused)
- tests/adapters/hooks/test_czl_gate_hook.py — 2 failures in CZL gate (CZL-P2-c scope, Maya paused)

## Next per Ethan roadmap
ARCH-2 (dead code cleanup in `_result_to_response`, 15 uses), ARCH-3 (boundary_enforcer reverse dep removal, 60 uses), ARCH-4 (router rules loader, 45 uses), ARCH-5 (YSTAR_BREAK_GLASS env var, 35 uses), ARCH-6 (thin hook adapter, 80 uses depends on ARCH-4).
