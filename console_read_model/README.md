# Console Read Model

Future CEO/team console work should read the index files created in this architecture recovery layer, not raw DBs, logs, or mutable runtime state.

Preferred inputs:
- `actual_team_registry/agents.json`
- `actual_team_registry/system_functions.json`
- `brain_index/db_manifest.json`
- `memory_index/memory_manifest.json`
- `runtime_mechanism_inventory/mechanisms.json`
- `governance_refs/boundaries.md`
- `company_state/current_world_state_ref.md`

Avoid direct console reads from:
- `.ystar_cieu.db`
- `.ystar_memory.db`
- `*_brain.db`
- `.ystar_session.json`
- `.ystar_ceo_mode.json`
- daemon logs
- active-agent marker files

Reason: those files are runtime state or evidence stores. The console should consume stable indexed state unless a future reviewed adapter is explicitly designed for safe access.
