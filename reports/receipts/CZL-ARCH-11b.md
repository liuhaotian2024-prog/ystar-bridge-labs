# CZL-ARCH-11b Completion Receipt — REDIRECT Ignore Detector via OmissionEngine

**Atomic ID**: CZL-ARCH-11b
**Claimed by**: eng-governance (Maya)
**Completed + CEO Verified**: 2026-04-18 (14 tool_uses / 669s)

**Audience**: Board (Board's "REDIRECT advisory-only 可被 agent 忽视" concern second-layer closed), CTO Ethan (ARCH-11 series integration), future agents operating under enforced redirect compliance.

**Research basis**: Board 2026-04-18 observation — "REDIRECT 是 advisory deny 不是 mandatory invoke" — CEO today ignored 10+ REDIRECT hints. ARCH-11a (Leo) handled the structured-GuidancePayload case. 11b closes the remaining gap: free-text REDIRECT (no GuidancePayload) must also be enforced. Industry precedent: OS kill-switch after timeout (systemd watchdog) / K8s liveness probe kill-then-restart.

**Synthesis**: 3-layer design. (1) OmissionEngine gains `register_redirect_obligation(agent, redirect_id, ttl_actions)` creating `must_execute_redirect` with TTL=3 tool_uses. (2) ForgetGuard rule `redirect_ignored` (mode=deny) — when obligation expires, next tool call is denied + CIEU `REDIRECT_IGNORED` event. (3) hook.py REDIRECT branch after ARCH-11a attempt calls `register_redirect_obligation` if GuidancePayload absent or invoke failed. Net effect: free-text REDIRECT now has teeth — agent has ≤3 tool calls to comply or face escalating deny.

## 5-Tuple
- **Y\***: free-text REDIRECT tracked by OmissionEngine; ignored → HARD_OVERDUE → deny next call + escalate
- **Xt**: 11a covered structured REDIRECT; free-text REDIRECT still ignorable
- **U**:
  - `Y-star-gov/ystar/governance/omission_models.py` — added `MUST_EXECUTE_REDIRECT` to OmissionType enum
  - `Y-star-gov/ystar/governance/omission_engine.py` — added `register_redirect_obligation()` method
  - `Y-star-gov/ystar/adapters/hook.py` — REDIRECT branch calls `register_redirect_obligation` when GuidancePayload absent/invoke failed
  - `Y-star-gov/ystar/governance/forget_guard_rules.yaml` — added `redirect_ignored` rule (mode=deny)
  - `Y-star-gov/tests/governance/test_arch11b_redirect_ignore.py` — 3 tests
- **Yt+1**: 3/3 tests PASS in 0.06s; 24 pre-existing failures unchanged (0 regressions)
- **Rt+1**: 0

## CEO Empirical Verify
```
pytest tests/governance/test_arch11b_redirect_ignore.py -q
... [100%]  3 passed, 3 warnings in 0.06s
```

## Net effect on Board's REDIRECT concern
Today CEO ignored REDIRECT 10+ times. Under ARCH-11a + 11b combined:
- REDIRECT with structured GuidancePayload → auto-invoked by 11a → agent doesn't decide
- REDIRECT with free-text only → 11b creates obligation → if agent ignores 3 more tool calls, next one is denied + Board-visible CIEU event + OmissionEngine escalation
- Agent effectively CANNOT ignore REDIRECT anymore. Board's concern closed.
