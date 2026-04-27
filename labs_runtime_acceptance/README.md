# Labs Runtime Governance Acceptance

This directory contains the L3.6 dry-run acceptance pack for the labs-side
runtime governance stack.

The acceptance command is:

```bash
python3 labs_runtime_acceptance/tools/run_labs_runtime_acceptance.py
```

It rebuilds and validates the current governed read-model chain:

- runtime artifact quarantine manifest
- bounded safe-mining candidates
- candidate review queue
- backlog disposition index
- structural evidence review and hint routing
- multi-role Pre-U packet generation
- hook envelope generation
- Y-star-gov dry-run decisions
- console read model
- local safety wrapper
- targeted acceptance tests

Acceptance means the dry-run governance stack is structurally ready. It does
not mean runtime execution is enabled.

The acceptance pack does not execute actions, write CIEU records, mutate brain
or memory, approve candidates, read DB/log/runtime contents, or ingest raw
runtime artifacts.

L3.7 pairs this labs acceptance result with the independent Y-star-gov endpoint
acceptance result through `cross_repo_alignment/`. That pairing remains dry-run
only.

L3.8 consumes the acceptance and alignment outputs through
`labs_live_readiness/`. That gate can say dry-run governance is ready, but it
keeps minimal live runtime blocked until required hook, sandbox, CIEU, approval,
rollback, and writeback gates exist.
