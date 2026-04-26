# Version Notes

## Canonical artifacts

- `AIDEN_ONTOLOGY.md`: identity and counterfactual operating style.
- `CZL.md`: concise CZL definition.
- `charter_amendment_014_closed_loop_cieu_residual_engine.md`: residual-loop extension of CZL/CIEU.
- `Y_STAR_FIELD_THEORY_SPEC.md`: Mission Field spec, with Section 11 correction binding.
- `CZL-BRAIN-3LOOP-FINAL-ruling.md`: binding 3-loop brain architecture ruling.
- `CZL-BRAIN-BIPARTITE-ruling.md`: binding separation of Hebbian and bipartite/evaluative learning.
- `CZL-BRAIN-BIPARTITE-P2-ALGO-ruling.md`: binding algorithm constraints for bipartite learning.
- `CZL-BRAIN-L3-GUARD-RAILS-ruling.md`: binding L3 guardrail design.

## Adjacent artifacts

- `team_dna.md`: older team operating DNA; valuable, but may conflict with newer registry.
- `MEMORY_AND_DEGRADATION_STRATEGY.md`: memory/degradation strategy; useful for memory layer framing.
- `WORLD_STATE.md` and `session_handoff.md`: runtime-state references, not immutable specs.

## Implementation artifacts

- `cieu_brain_bridge.py`
- `cieu_brain_streamer.py`
- `cieu_brain_learning.py`
- `brain_auto_ingest.py`
- `brain_dream_scheduler.py`
- `y_star_field_validator.py`

These should stay kernel-side in Y-star-gov and be referenced, not copied into company docs.

## Superseded ideas

- LLM judge for field validation is superseded by `Y_STAR_FIELD_THEORY_SPEC.md` Section 11, which restores deterministic governance and separates governance from operations.
- Pattern D full auto-generation is postponed beyond v1 in the 3-loop architecture; D-LITE observability is the safe first step.
- Naive positive-only Hebbian reinforcement is superseded by outcome-weighted Hebbian in the 3-loop rulings.

## Unresolved version conflicts

- Current L2 writeback live status needs validation after the partial receipt.
- RLE live implementation status is unclear.
- Some lifecycle-continuity ideas live in `ystar-company-test` and should remain reference-only until reviewed.
- Exact multi-agent extension beyond Aiden requires a later pass.
