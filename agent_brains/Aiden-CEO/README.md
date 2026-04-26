# Aiden-CEO Brain Capsule v0

This directory is the first concrete per-agent Agent Brain Capsule for `Aiden-CEO`.
It is a reference capsule, not the brain database itself and not a new theory.

The capsule instantiates the generic `agent_brain_capsule/` reference layer for
Aiden by pointing to existing Y* artifacts: ontology, DNA, memory, CZL, Mission
Field, CIEU nutrition, lifecycle, and governance boundary references.

This capsule does not open, copy, migrate, or summarize SQLite database contents.
Database assets are referenced only through existing metadata indexes such as
`brain_index/db_manifest.json`.

Intended future use:

- L0 boot: read Aiden identity, memory references, and continuity state.
- L1 pre-action cognition: assemble ontology, cognitive policy, field, and CZL context.
- L2 post-action nutrition: route CIEU/residual evidence into writeback-ready references.
- L3 dream/writeback: guide offline consolidation without bypassing governance.
- CZL closure: keep task completion tied to explicit residual closure rather than narrative completion.

This is v0 and remains reference-only until a later milestone validates live wiring.
