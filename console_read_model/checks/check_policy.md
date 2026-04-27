# Check Policy

## Allowed Checks

The wrapper may run only these safe commands:

- `python3 runtime_artifact_quarantine/tools/build_runtime_artifact_manifest.py`
- `python3 console_read_model/loader/build_team_console_snapshot.py`
- `python3 -m json.tool console_read_model/generated/team_console_snapshot.json`
- `python3 -m json.tool console_read_model/generated/quarantine_summary.json`
- `python3 -m json.tool console_read_model/generated/generation_manifest.json`
- `python3 -m json.tool console_read_model/generated/readiness_summary.json`
- `python3 console_read_model/validation/validate_team_read_model.py`
- `python3 console_read_model/cli/team_console.py validate-local`
- `python3 console_read_model/cli/team_console.py quarantine`
- `python3 console_read_model/cli/team_console.py sources`

## Forbidden Reads And Actions

The wrapper must not:

- open SQLite DB contents
- query DBs
- read DB/WAL/SHM contents
- read raw logs
- read active-agent marker contents
- read daemon pid/state contents
- parse raw runtime reports
- run daemon, hook, runtime, boot, governance, or agent scripts
- clean, move, delete, archive, or stage dirty runtime artifacts

## Boundary

The wrapper verifies the local read-model layer only. It does not replace
runtime tests, governance validators, hook enforcement, CIEU correctness checks,
or future DB-safe adapters.
