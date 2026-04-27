# Live Boundary Policy

The live boundary harness is a contract layer, not a runtime layer.

Rules:

- Boundaries may be defined and validated locally.
- All live capabilities remain disabled by default.
- Manual enablement is required before any future live loop.
- Action execution remains forbidden.
- CIEU writing remains forbidden.
- Brain and memory writeback remain forbidden.
- Candidate auto-approval remains forbidden.
- Raw artifact ingestion remains forbidden.

The harness may read only curated generated readiness, acceptance, bridge, and
console summaries. It must not read database sidecars, logs, active-agent
markers, raw reports, runtime state, or memory files.
