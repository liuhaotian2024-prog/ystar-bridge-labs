# Bridge Policy

The bridge is the only allowed path for agent-initiated tool invocation in this milestone.

Required sequence:

- Agent produces a tool request.
- Bridge converts it into a Pre-U tool packet.
- Governance decision envelope allows only local read-only dry-run execution.
- Bridge authorization binds allowed sources and denied behaviors.
- Bridge invokes the L4.4 governed read-only observation tool.
- Bridge emits a dry-run CIEU-compatible event and residual delta fixture.

Forbidden shortcuts:

- No direct agent-to-tool invocation.
- No live execution.
- No external action.
- No network.
- No GitHub issue or PR creation.
- No git push.
- No daemon control.
- No CIEU persistence.
- No brain/memory writeback or ingestion.
- No candidate approval.
- No semantic truth scoring.

