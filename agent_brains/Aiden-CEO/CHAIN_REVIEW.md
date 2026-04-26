# Aiden Brain Chain Review

## Current Chain Status

The current Aiden brain chain is a committed reference chain, not executable
runtime. It now runs from labs-side architecture indexes through generic Agent
Brain Capsule references, Aiden-specific capsule references, Pre-U
Counterfactual Packet references, and boundary-alignment references for labs,
Y-star-gov, hook, CIEU, and brain learning.

Primary evidence files:

- `actual_team_registry/agents.json`
- `agent_brain_capsule/README.md`
- `agent_brain_capsule/runtime_layers.md`
- `agent_brains/Aiden-CEO/brain_profile.json`
- `agent_brains/Aiden-CEO/pre_u_counterfactual/packet_schema.json`
- `agent_brains/Aiden-CEO/pre_u_counterfactual/boundary_alignment/boundary_map.json`

## What Exists Now

- L1 runtime architecture indexes identify ystar-company as the labs/company
  host and Y-star-gov as the governance kernel.
- `agent_brain_capsule/` defines the generic reference wrapper for DNA, memory,
  field, CZL, CIEU nutrition, lifecycle, and governance boundaries.
- `agent_brains/Aiden-CEO/` instantiates that wrapper for Aiden-CEO as a
  reference-only capsule.
- `agent_brains/Aiden-CEO/pre_u_counterfactual/` defines the future packet
  shape for bounded action imagination before U.
- `agent_brains/Aiden-CEO/pre_u_counterfactual/boundary_alignment/` makes the
  cross-layer responsibilities explicit.

## What Each Layer Is Responsible For

- Runtime architecture indexes: map repositories, mechanisms, memory/brain
  assets, and boundaries.
- Generic Agent Brain Capsule: define the shared brain-capsule reference layers.
- Aiden Brain Capsule: bind those layers to Aiden-specific evidence refs.
- Pre-U Counterfactual Packet: structure candidate U actions, predicted Yt+1,
  predicted Rt+1, and residual-minimizing selection.
- Boundary alignment: define who generates, validates, gates, records, teaches,
  and learns.
- Future Y-star-gov validator: validate packet schema, Y*, m_functor grounding,
  role scope, and residual logic.
- Future hook gate: require and enforce packet validation for risk-tiered action.
- Future CIEU feedback: record actual outcome and compare predicted vs actual.
- Future brain writeback/dream: learn from evidence-backed CIEU deltas.

## What Each Layer Must Not Do

- Labs must not become deterministic judge.
- Aiden Brain Capsule must not open DB contents or execute runtime behavior.
- Pre-U packet must not claim actual outcome before action.
- Y-star-gov must not become subjective brain or candidate-action generator.
- Hook must not become a reasoning engine.
- CIEU must not treat prediction as actual evidence.
- Brain must not learn from unaudited fantasy alone.
- Console/read-model layers must not mutate raw DB/log/runtime state.

## Aiden Capsule to Pre-U Counterfactual Imagination

Aiden's capsule supplies the read-model context for future Pre-U packet
generation: identity, ontology, memory refs, field refs, CZL refs, CIEU
nutrition refs, lifecycle refs, and governance refs. The packet layer uses that
context to structure action imagination around Y*, Xt, candidate U, predicted
Yt+1, predicted Rt+1, and selected residual-minimizing action.

The packet is not a replacement for Aiden's brain DB. It is a structured
pre-action artifact that a future labs runtime may generate from the capsule
context.

## Pre-U Packet to Y-star-gov / Hook / CIEU / Brain

The intended handoff is:

1. Labs generates a packet.
2. Y-star-gov validates schema, Y*, m_functor grounding, role scope, and
   residual logic.
3. Hook enforces the validator result before high-risk action.
4. CIEU records post-action actual outcome and compares predicted vs actual.
5. Brain writeback/dream learns from CIEU deltas, not from speculation alone.

This preserves the boundary: labs thinks, Y-star-gov judges, hook enforces,
CIEU records and teaches, brain learns.

## Why DB Contents and Runtime State Remain Outside This Chain

This chain is documentation/reference only. DBs, WAL/SHM files, logs,
active-agent state, and runtime session files are high-risk local state. Existing
indexes such as `brain_index/db_manifest.json` and `memory_index/memory_manifest.json`
reference them by metadata only. The chain review does not inspect, migrate, or
mutate DB contents.

## Ready for Future Runtime Implementation

- Packet schema shape is ready for interface discussion.
- Boundary map is ready as an implementation guardrail.
- Risk-tier policy is defined at reference level.
- CIEU feedback and brain learning contracts are ready for schema/interface work.
- Aiden capsule can serve as a future read-model source.

## Not Ready Yet

- No Y-star-gov packet validator exists.
- Hook does not require Pre-U packets.
- CIEU prediction-delta event schema is not implemented.
- Brain writeback from packet deltas is not validated.
- Aiden packet generator does not exist.
- RLE live status remains unclear.
- Multi-agent generalization is not complete.

## Recommended Next Branch

Recommended next branch depends on direction:

- A. Ethan/Samantha capsule generalization: best if the next goal is team-scale
  proof that the capsule pattern is not Aiden-only.
- B. Y-star-gov packet validator interface spec: best if the next goal is
  governance-path implementation readiness.
- C. Hook gate policy implementation design: best after the validator interface
  is stable.
- D. CIEU prediction-delta event schema: best if the next goal is learning
  feedback and brain nutrition.

Default recommendation: choose either B or A. Choose B for governance execution
path; choose A for team-generalization path. Do not start runtime implementation
until the validator and event boundaries are stable.
