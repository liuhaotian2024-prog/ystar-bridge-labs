# Loader Policy

## Allowed Source Files

The loader may read only curated files:

- `console_read_model/*.json`
- `console_read_model/*.md`
- `console_read_model/validation/*.json`
- `agent_brains/team_capsule_map.json`
- `agent_brains/Aiden-CEO/brain_profile.json`
- `agent_brains/Ethan-CTO/brain_profile.json`
- `agent_brains/Samantha-Secretary/brain_profile.json`
- `agent_brains/Ethan-CTO/execution_channels.json`
- `agent_brains/schema/*.json`
- `runtime_artifact_quarantine/quarantine_index.json`
- `runtime_artifact_quarantine/generated/runtime_artifact_manifest.json`

## Forbidden Sources

The loader must not read:

- `.db`, `.db-wal`, `.db-shm`
- `scripts/.logs`
- `__pycache__`
- active-agent markers
- `.pid`
- daemon state
- raw runtime report directories

## Outputs

- `console_read_model/generated/team_console_snapshot.json`
- `console_read_model/generated/team_console_snapshot.md`
- `console_read_model/generated/agent_cards_compiled.json`
- `console_read_model/generated/readiness_summary.json`
- `console_read_model/generated/quarantine_summary.json`
- `console_read_model/generated/generation_manifest.json`

## Why This Is Still Not Runtime

The loader creates a static snapshot from curated read-model files. It does not
observe live runtime state, query DBs, run daemons, call hooks, or validate
Y-star-gov behavior.
The quarantine integration reads only the quarantine framework index and
path-level generated manifest. It never follows artifact paths.
