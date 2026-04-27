# Review Queue Policy

All safe-mining candidates require explicit review before any future use.

Allowed review actions:

- `approve_for_capsule_hint`
- `approve_for_governance_gap_hint`
- `approve_for_packet_hint`
- `approve_for_cieu_delta_hint`
- `reject`
- `needs_more_context`

Forbidden actions:

- `direct_brain_writeback`
- `direct_memory_ingestion`
- `direct_cieu_write`
- `runtime_recovery`

Queue entries do not approve anything automatically. Approval, rejection, and escalation workflows are future work. This layer only creates deterministic pending review records from already generated safe candidates.
