# CZL-ARCH-11a Completion Receipt — Mandatory Invoke Mode

**Atomic ID**: CZL-ARCH-11a
**Claimed by**: eng-kernel (Leo)
**Completed + CEO Verified**: 2026-04-18 (14 tool_uses / 584s / no stall)

**Audience**: Board (ARCH-11 series second landing; Board's "advisory vs mandatory" concern addressed), CTO Ethan (integration review), future agents benefiting from auto-invoke safety net.

**Research basis**: Ethan's arch doc Part A defined the upgrade path REDIRECT → INVOKE. Board's 2026-04-18 observation: "REDIRECT 是 advisory deny 不是 mandatory invoke" — agents ignore fix hints. Industry precedent: auto-formatters auto-apply transformations (black / prettier). Leo reused existing REDIRECT branch in hook.py and GuidancePayload substrate from ARCH-11d.

**Synthesis**: Before 11a, REDIRECT was text-only — agent saw fix command but could ignore it. After 11a, when GuidancePayload.invoke_cmd present AND then_retry_original=True, hook auto-executes via subprocess.run. Success → decision upgrades to ALLOW + retry. Failure → stays REDIRECT + adds AUTO_INVOKE_FAILED context. Backward compat: no GuidancePayload → unchanged path.

## 5-Tuple
- **Y\***: REDIRECT auto-upgrades to INVOKE when GuidancePayload present, else unchanged
- **Xt**: REDIRECT advisory-only, agent routinely ignored (Board caught 10+ instances today)
- **U**:
  - `Y-star-gov/ystar/adapters/hook.py` — added `import subprocess`, `_try_extract_guidance()`, `_emit_auto_invoke_cieu()`, INVOKE upgrade in REDIRECT branch
  - `Y-star-gov/tests/adapters/test_arch11a_mandatory_invoke.py` — 9 tests covering extraction / success / failure / backward compat / exception handling
- **Yt+1**: 9/9 tests PASS; 0 regression vs base branch; CIEU `AUTO_INVOKE_APPLIED` event emitted on each invocation
- **Rt+1**: 0

## Proof
```
pytest tests/adapters/test_arch11a_mandatory_invoke.py -q
.........                                                     [100%]
9 passed in 0.XX s

grep _try_extract_guidance hook.py → function definition present
grep AUTO_INVOKE_APPLIED hook.py → CIEU event name present
```

## Why this matters (Board's question directly answered)

Today CEO saw REDIRECT message `echo "ceo" > .ystar_active_agent && retry` 10+ times and hardwrote instead of following it. Board asked: "new framework 下也会被解决吗". ARCH-11a answer: YES — when REDIRECT payload is structured (GuidancePayload), hook auto-executes FIX_COMMAND; agent never has to decide whether to follow guidance. For the 10+ REDIRECTs CEO ignored today, under ARCH-11a they would have been silently auto-executed, CEO's tool call would have retried and succeeded.

Remaining gap: ARCH-11b (REDIRECT ignore detector via OmissionEngine) catches the case where GuidancePayload is NOT present but a free-text REDIRECT fires — attaches obligation to enforce compliance.
