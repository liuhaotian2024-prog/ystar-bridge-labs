# Legacy Asset Triage Report

Legacy assets were scored from compact generated inventory metadata only.

## Bucket Counts
- A_adopt_now_read_only: 1
- B_wrap_as_governed_tool: 881
- C_rewrite_from_design: 10
- D_quarantine_as_evidence_ore: 8
- E_retire_do_not_use: 0

## Top Absorption Candidates
- asset-0271: console_read_model/cli/team_console.py (A_adopt_now_read_only)
- asset-0294: console_read_model/generated/team_console_snapshot.md (B_wrap_as_governed_tool)
- asset-0553: gov_mcp/server.py (B_wrap_as_governed_tool)
- asset-2412: scripts/build_rag_index.py (B_wrap_as_governed_tool)
- asset-2558: scripts/restart_handoff_verifier.py (B_wrap_as_governed_tool)
- asset-2572: scripts/skill_lifecycle_manager.py (B_wrap_as_governed_tool)
- asset-2948: ystar.bak.20260415_again/cli/impact_cmd.py (B_wrap_as_governed_tool)

## Safety
- blind_absorption_allowed: false
- blanket_rewrite_allowed: false
- live_actions_enabled: false
- no CIEU persistence, memory ingestion, or brain writeback is enabled
