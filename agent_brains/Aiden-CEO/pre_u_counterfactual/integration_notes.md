# Integration Notes

## ystar-company / Labs

Labs owns packet generation. This includes reading Aiden Brain Capsule
references, forming Y*, imagining bounded candidate actions, comparing predicted
residuals, and explaining why one action path is selected.

Labs does not own deterministic governance judgment.

## Y-star-gov

Y-star-gov owns deterministic validation. Future validation should check packet
schema, Y* declaration, m_functor grounding, role scope, CZL residual logic, and
boundary constraints.

Y-star-gov may later own a packet validator, but this milestone does not modify
that repository.

## Hook Layer

The hook layer owns the pre-action gate. It should not perform complex
counterfactual imagination itself. In a future implementation, hooks should
require a valid Pre-U packet for high-risk actions and call Y-star-gov validators
before allowing the selected action.

## CIEU

CIEU owns actual outcome evidence. Future CIEU events should compare predicted
Yt+1 and Rt+1 against actual Yt+1 and Rt+1, then use prediction error and
residual delta as nutrition for brain learning, writeback, and dream replay.

## Relation to Existing Indexes

- `agent_brain_capsule/`: Generic reference architecture for brain, field, CZL,
  CIEU, lifecycle, and governance.
- `agent_brains/Aiden-CEO/`: Aiden-specific per-agent reference capsule.
- `runtime_mechanism_inventory/`: Existing mechanism inventory for governance,
  field validation, CIEU, brain bridge, hooks, and related systems.
- `governance_refs/`: Cross-repo boundary reference that keeps Y-star-gov as the
  governance kernel.
- `brain_index/`: Metadata-only DB/state index; DB contents remain unopened.
- `memory_index/`: Memory/boot/session reference index for read-model assembly.

This packet layer should remain a reference/design layer until a future
milestone validates generator, validator, hook gate, and CIEU delta wiring.
