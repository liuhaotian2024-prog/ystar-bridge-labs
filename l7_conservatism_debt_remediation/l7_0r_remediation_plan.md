
# L7.0R Remediation Plan

This sprint uses the L7.0Q2 migration map rather than rescanning the repo.

## Strategy
- Replace disabled/not_configured dead ends with staged policy states.
- Allow discovery, read-only analysis, drafting, planning, and approval requests.
- Keep external side effects and permanent writeback blocked until approval.
- Preserve hard boundaries for secrets, payment, outreach, publication, raw DB/WAL/SHM, logs, active-agent marker content, Y-star-gov, and gov-mcp.

## Patched Active P0 Files
- `scripts/aiden_dream.py`: converted disabled scheduling language into staged dry-run/writeback policy decisions
- `scripts/hook_wrapper.py`: converted hook v2 dead switch into blocked_pending_evidence resolver gate
- `scripts/session_health_watchdog.py`: converted board disabled override into blocked_pending_human_review pause with auto-detect available
- `scripts/governance_boot.sh`: added policy registry visibility and converted override disabled language into staged gate state
- `scripts/memory_consistency_check.py`: converted not_configured status into blocked_pending_config and added runtime/writeback policy refs
- `scripts/linkedin_auth.py`: added explicit policy gate that blocks unapproved social posting while preserving human-supervised login/setup

## Patched L7.0P Policy Semantics
- `l7_revenue_opportunity_radar/l7b_revenue_opportunity_radar_summary.json`: added L7.0R staged revenue policy remediation fields
- `l7_revenue_opportunity_radar/opportunity_packets/opportunity_packet_001.json`: added read-only revenue work and draft/planning allowed fields
- `l7_owner_runtime_cockpit/owner_cockpit.json`: added owner burden replacement and staged execution/writeback policy fields
