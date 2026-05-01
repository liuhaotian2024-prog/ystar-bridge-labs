# E1.5 CZL Plan

## Y* — Owner-Defined Completion Standard

Rt+1 may be 0 only if all ten criteria are satisfied:

1. Aiden Mission Command explicitly defines Y*, Xt, U, Yt+1, and Rt+1 for a mission.
2. Counterfactual reasoning is a decision gate, not just a report section.
3. Counterfactual gate can confirm or change the default recommendation.
4. All proposed mission actions are inventoried and passed through governance preflight.
5. Obligation drafts use dynamic, collision-safe identifiers and remain dry-run only.
6. Residual candidates can be updated with actual signal placeholders and remain review-gated.
7. A clear owner decision packet is generated.
8. Mission output distinguishes plan, executable U, observed Yt+1, and remaining Rt+1.
9. No external side effects occur.
10. Tests and unseen smoke checks verify behavior.

## Xt — Current State Before E1.5 Actions

- Branch: `backflow/aiden-ceo-meeting-room`.
- Latest commit before E1.5: `6bbc091b0fe8106f008459e8fbfe9172f191827b`.
- Working tree before E1.5 contains one unrelated untracked file: `reports/integration/post_push_quality_audit.md`; it is intentionally excluded.
- Existing Mission Command has method trace, opportunity synthesis, counterfactual report sections, obligation dry-run drafts, governance bridge, and residual candidates.
- Gap: Mission Command does not yet define a CZL tuple for each mission.
- Gap: counterfactual reasoning confirms the default with a hardcoded boolean and is not a real decision gate.
- Gap: governance preflight covers sample actions, not every proposed mission action.
- Gap: obligation IDs are still date-block/static, not mission-derived collision-safe identifiers.
- Gap: residual candidates cannot be updated with actual signal placeholders.
- Gap: owner decision packet is not first-class.
- Gap: mission output does not prove Rt+1 = 0 against owner-defined Y*.

## Planned U Actions

1. Add CZL mission loop model and renderer.
2. Add counterfactual decision gate that can confirm or change default recommendations.
3. Add action inventory and action-wide governance preflight.
4. Update obligation bridge to use dynamic, collision-safe dry-run identifiers.
5. Add residual update and review packet helpers.
6. Add owner decision packet builder.
7. Integrate CZL, decision gate, action-wide preflight, owner packet, and residual review into Mission Command and reports.
8. Add E1.5 tests and unseen smoke checks.
9. Generate closure report only after observing Yt+1 and computing Rt+1.

## Completion Rule

Completion may be claimed only when `e1_5_czl_closure_report.md` shows Rt+1 = 0 and every Y* criterion is marked satisfied. If any criterion remains unsatisfied, the status must be BLOCKED or a bounded correction U must be run before commit.

## Safety Boundary

No external sending, customer contact, email, publication, payment, account creation, form submission, obligation registration, CIEU write, or core DB/brain/memory writeback is allowed in this sprint.

## Implementation U Trace

- u_001: Implemented CZL mission loop model and renderer.
- u_002: Implemented counterfactual decision gate and connected it to method trace.
- u_003: Inventoried all mission actions and preflighted every action.
- u_004: Made obligation drafts dynamic, collision-safe, and dry-run only.
- u_005: Added residual update/review packet scaffold with no core writeback.
- u_006: Generated owner decision packet for Tier 1 read-only evidence mission.
- u_007: Ran tests and unseen smoke checks.

## Planned Closure Criteria

Rt+1 will be computed in `e1_5_czl_closure_report.md` after validation.
