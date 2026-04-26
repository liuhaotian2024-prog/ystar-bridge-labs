# Aiden-CEO Pre-U Counterfactual Packet

This directory defines the Aiden-CEO Pre-U Counterfactual Packet reference layer.
It is not executable runtime yet.

The packet describes what Aiden should eventually produce before taking action
`U`: a structured comparison of possible actions, predicted next states
`Yt+1`, predicted residuals `Rt+1`, and the selected path expected to bring
`Rt+1` closest to `0`.

This layer connects:

- `agent_brain_capsule/` as the generic Brain Capsule reference model.
- `agent_brains/Aiden-CEO/` as Aiden's per-agent brain capsule.
- Aiden's ontology and cognitive-policy references.
- Y* Field / mission-field grounding.
- CZL residual-closure semantics.
- CIEU nutrition and prediction-error learning.
- Governance and hook boundaries.

The purpose is action imagination, not free-form fantasy. Candidate actions must
be tied to a declared `Y*`, current-state summary `Xt`, evidence references,
field alignment, and CZL closure logic.

Pre-U Counterfactual Imagination is not a replacement for Y-star-gov governance.
It is a labs-side cognitive artifact that Y-star-gov/hook layers may later
validate.

Architectural boundary:

- `ystar-company` / labs thinks.
- Y-star-gov judges.
- Hook layer enforces.
- CIEU teaches.

No DB contents are opened here. No runtime hook or validator is implemented here.
