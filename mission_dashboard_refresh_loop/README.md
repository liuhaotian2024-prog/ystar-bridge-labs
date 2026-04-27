# Mission Dashboard Refresh Loop

L4.7 defines the first deterministic mission dashboard refresh loop for the company autonomy stack.

The loop reads curated generated/read-model JSON only. It combines the previous mission dashboard, the current governed read-only observation path, and the agent-team work proposal bridge result into a refreshed mission dashboard, company state delta, refreshed backlog, dry-run CIEU-compatible event, residual delta, and next-loop recommendations.

This is local, manual, and dry-run only. It does not enable a scheduler, daemon, live action, external action, CIEU persistence, brain writeback, or memory ingestion.

