# Data Sources

## Safe Curated Sources

- `actual_team_registry/*.json`
- `actual_team_registry/*.md`
- `agent_brains/**/*.json`
- `agent_brains/**/*.md`
- `agent_brain_capsule/*.md`
- `agent_brain_capsule/*.json`
- `brain_index/db_manifest.json`
- `memory_index/memory_manifest.json`
- `governance_refs/boundaries.md`
- `runtime_mechanism_inventory/mechanisms.json`
- `company_state/current_world_state_ref.md`

## Unsafe Direct Sources

- `*.db`
- `*.db-wal`
- `*.db-shm`
- `scripts/.logs/*`
- Active-agent markers.
- Daemon pid/state files.
- `__pycache__`.
- Raw runtime reports unless curated/indexed.

## Rules

- DBs may be referenced by manifest only.
- Logs may be summarized only through future safe adapters.
- Console must not mutate anything.
- Console should never treat raw runtime state as canonical memory.
- Console should prefer curated read models over direct operational stores.
