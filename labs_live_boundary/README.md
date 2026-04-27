# Labs Live Boundary Harness

This directory contains the L3.9 minimal live boundary harness.

The harness defines the boundaries required before any future minimal live loop:

- operator approval gate placeholder
- action sandbox contract placeholder
- rollback and abort policy
- CIEU writer boundary placeholder
- no brain or memory writeback rule
- live transition guard

The harness is disabled by default. It does not execute actions, activate hooks,
write CIEU records, ingest memory, write brain state, approve candidates, or
read raw runtime artifacts.

Build the generated boundary manifest from curated generated inputs only:

```bash
python3 labs_live_boundary/tools/build_live_boundary_manifest.py
```

The expected answer for L3.9 is:

- `live_boundary_defined`: true
- `live_action_execution_enabled`: false
- `cieu_write_enabled`: false
- `brain_writeback_enabled`: false
- `memory_ingestion_enabled`: false
- `minimal_live_loop_ready`: false
- `blocked_reason`: `required_live_gates_defined_but_disabled`
