# Team Capsule Generalization Review

## Summary

The Aiden capsule pattern has now been generalized to two additional evidenced
roles:

- Aiden-CEO: orchestration / CEO.
- Ethan-CTO: technical architecture / implementation reasoning.
- Samantha-Secretary: memory continuity / secretary curation.

This tests the Agent Brain Capsule model across orchestration, engineering
architecture, and continuity/curation roles without inventing new roles or
opening DB contents.

## What Generalizes Cleanly

- The shared layer set: DNA, memory, cognitive policy, mission field, CZL, CIEU
  nutrition, lifecycle, and governance.
- Metadata-only brain DB references through `brain_index/db_manifest.json`.
- Memory references through `memory_index/memory_manifest.json`.
- Cross-repo boundary references through `governance_refs/boundaries.md`.
- External Y-star-gov references as governance/kernel boundaries, not company
  runtime ownership.

## What Remains Aiden-Specific

- Aiden's ontology and CEO operating philosophy.
- Aiden's Pre-U Counterfactual Packet layer and boundary alignment.
- Aiden's chain review and packet validator handoff path.

## Role-Specific Specialization Needed

- Ethan needs stronger technical architecture, ruling interpretation,
  implementation feasibility, and engineering handoff semantics.
- Samantha needs stronger memory curation, session continuity, report hygiene,
  and handoff lifecycle semantics.
- Each role will need its own Pre-U packet variant only after shared schema and
  validator interfaces are stable.

## Team Expansion

Next expansion could include governance, platform, finance, or marketing roles
only if their evidence is read from `actual_team_registry/agents.json` and
supporting profiles/boot packages. Do not add roles by business-org assumption.

## Recommendation

Recommended next step:

A. Create a shared per-agent capsule schema to reduce drift across Aiden, Ethan,
and Samantha.

Alternative next steps:

B. Create per-agent Pre-U packet variants.
C. Create Y-star-gov validator implementation skeleton after interface stability.
D. Create console read model for team capsules.

Do not start runtime implementation before the shared schema and validation
boundaries are stable.
