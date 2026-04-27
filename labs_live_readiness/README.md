# Labs Live Readiness

This directory contains the L3.8 live-readiness gate for the labs runtime.

The gate answers whether the current dry-run governance stack is ready and what
still blocks any minimal live governed loop.

The command is:

```bash
python3 labs_live_readiness/tools/build_live_readiness_report.py
```

The answer for this milestone is intentionally conservative:

- `dry_run_governance_ready`: true when acceptance/alignment reports pass.
- `minimal_live_loop_ready`: false.
- `live_action_execution_allowed`: false.
- `live_cieu_write_allowed`: false.
- `live_brain_writeback_allowed`: false.
- `live_memory_ingestion_allowed`: false.

This pack does not enable runtime execution. It creates a transition backlog for
future live boundary harness work.

