# Cross-Repo Governance Alignment

This directory contains the L3.7 dry-run cross-repo alignment layer between
ystar-company and Y-star-gov.

The main command is:

```bash
python3 cross_repo_alignment/tools/run_cross_repo_alignment_acceptance.py
```

It proves, locally and deterministically, that:

- Y-star-gov endpoint acceptance passes.
- ystar-company labs runtime acceptance passes.
- the labs-to-Y-star-gov dry-run bridge has a valid decision snapshot.
- multi-role Pre-U governance decisions exist for Aiden-CEO, Ethan-CTO, and
  Samantha-Secretary.
- all non-execution safety assertions remain true.

This is not CI, not push, not real hook integration, and not runtime execution.

`labs_live_readiness/` consumes this dry-run alignment status as one input to
the live-readiness gate. Alignment accepted does not enable live execution; it
only proves the dry-run labs and governance endpoints remain compatible.
