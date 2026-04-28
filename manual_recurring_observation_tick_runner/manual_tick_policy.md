# Manual Tick Policy

The manual tick runner is a one-shot local tool for proving the recurring loop contract without enabling recurrence.

Allowed now:
- Accept a generated manual tick request.
- Validate the L4.8 contract, allowed source registry, gate, stop/abort conditions, and escalation conditions.
- Read only allowed generated/read-model JSON sources.
- Produce L4.9 generated artifacts under this pack.

Forbidden now:
- Scheduler activation.
- Daemon activation.
- Automatic recurrence or auto-run.
- Live action or external action.
- CIEU persistence, brain writeback, or memory ingestion.
- Candidate approval or semantic truth scoring.

