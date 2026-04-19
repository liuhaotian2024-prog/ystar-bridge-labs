# Lesson: 性能诊断必跑 profile，不凭直觉锁定（2026-04-18 misdiagnosis postmortem）

**Date**: 2026-04-18
**Author**: Aiden (CEO)
**Trigger**: Board catch — hook 14s 慢的根因不是我以为的 "policy compile 每 call"，是 daemon socket fast path 死了导致 Python 冷启+重 import 每 call。
**Audience**: future CEO (must profile before designing fix); CTO Ethan (technical validation of perf claims); future engineers proposing cache-as-answer.

**Research basis**: Empirical sequence this evening:
1. CEO measured hook wall time: 15.828s (user 5.38s + sys 8.12s).
2. CEO inferred root cause = "every call recompiles AGENTS.md 3000-line regex" based on observed "Multi-agent Policy: 5 roles loaded from AGENTS.md" print + reading Policy.from_agents_md code path.
3. CEO proposed OPA Bundle Persistence pattern; Board approved; Ethan + CEO-proxy shell both landed cache module + wired session.py.
4. Benchmark with cache ON: 13.4s / 20.1s / 13.6s — identical to baseline. Cache worked (tests 3/3 pass) but saved only ~2s of the 14s.
5. CEO then started hook_daemon — benchmark via daemon fast path: **0.299s (50x speedup)**.
6. True root cause: hook_client_labs.sh fast path via `/tmp/ystar_hook.sock` had been broken since CEO's pkill that morning. Every call fell through to slow path = cold Python start (~2s) + ystar import of large module tree (~5s) + check_hook main (~5s) + policy compile (~2s). Cache only addresses the last 2s.

**Synthesis**: CEO's intuition pointed to the most visible cause (the noisy "Policy loaded" print on every call) without profiling. The true dominant cost was process startup + import, invisible to the code-path intuition because it happens before any print. Profile-driven diagnosis would have caught this on the first `time python3 -c "import ystar"` (which alone takes several seconds) compared to `time python3 -c "from ystar.session import Policy; Policy.from_agents_md('AGENTS.md')"`. The diff isolates compile-cost from import-cost.

## Hard constraint for future CEO (perf-diagnosis)

Before proposing any "cache / memoize / rewrite" performance fix, CEO MUST:

1. **Decompose the wall time**. Time the smallest suspected sub-operation in isolation (e.g., `time python3 -c "import X"`). Compare vs end-to-end. The dominant sub-op is the real target.
2. **Verify the hypothesis with A/B benchmark BEFORE landing fix code**. In today's case, a 2-line test of "empty Python vs compile-only" would have shown compile is <20 % of the 14s.
3. **Check operational primitives first**: is the existing daemon / cache / fast-path actually running? `ps aux | grep daemon` + `ls -l /tmp/*.sock` is cheaper than writing a new cache module.
4. **Prefer restart-known-component over new-code**. Daemon restart was 1 line; cache module was ~130 lines + wiring + tests. Restart was the right first move; I inverted priorities.
5. **Industry precedent scan** (already codified as separate lesson `industry_precedent_scan_first_20260418.md`) complements profiling — cite precedent + quantify which sub-op the precedent actually addresses.

## Today's action trail (what was landed)

- `Y-star-gov/ystar/kernel/_policy_bundle_cache.py` — OPA-pattern cache module (KEEP as future slow-path fallback; inert when `YSTAR_POLICY_CACHE=1` env is unset, which is the default).
- `Y-star-gov/tests/kernel/test_policy_bundle_cache.py` — 3 tests (KEEP; validates the module's correctness).
- `Y-star-gov/ystar/session.py` — wire added then REVERTED via `reports/ceo/revert_policy_cache_wire.sh`. Rationale: daemon fast path is the real solution; wire gave false appearance that caching alone fixed the symptom.
- hook_daemon (PID per `ps aux | grep _hook_daemon`) restarted. `/tmp/ystar_hook.sock` active. Benchmark 0.299s confirmed.

## Related memory / artifacts

- `knowledge/ceo/lessons/industry_precedent_scan_first_20260418.md` — the complementary "scan external before proposing" habit; today's lesson adds the "profile internal before scanning external".
- `knowledge/shared/rules_first_team_norm_20260418.md` — rule-doc check-first; today's misdiagnosis would ALSO have been avoided if CEO had grep'd `hook_client_labs.sh` for the fast path FIRST.
- `reports/ceo/four_goals_verification_20260418.md` — today's 4-goal verification; this perf unlock is the practical enabler for Goal 2 (agents no longer 空转 waiting 14s per tool).

## Takeaway principle

"Profile the symptom, verify the hypothesis, check the primitives first. Only write new code when the existing primitive is proven insufficient by measurement."
