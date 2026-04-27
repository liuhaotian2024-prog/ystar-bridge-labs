# Refresh Loop Policy

The refresh loop may read only curated generated/read-model sources already produced by prior milestones.

Allowed behavior:

- Load generated mission, dashboard, observation, bridge, and console summaries.
- Normalize prior dashboard state into a bounded previous snapshot.
- Normalize current generated evidence into a bounded observation input.
- Produce refreshed generated artifacts under `mission_dashboard_refresh_loop/generated`.
- Emit dry-run CIEU-compatible event and residual delta fixtures.

Forbidden behavior:

- Scheduler or daemon activation.
- Live or external action execution.
- Network calls or external communication.
- Git push or GitHub issue/PR creation.
- CIEU persistence.
- Direct brain writeback or memory ingestion.
- Candidate approval or semantic truth scoring.

