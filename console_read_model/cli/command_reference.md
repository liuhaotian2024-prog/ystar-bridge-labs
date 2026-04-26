# Command Reference

Run commands from the repository root:

```bash
python3 console_read_model/cli/team_console.py <command>
```

## Commands

- `summary`: Prints model status, agents included, readiness summary, governance
  summary, and warnings.
- `agents`: Lists agent id, role, readiness/status, and primary focus.
- `agent <agent_id>`: Prints detailed card for `Aiden-CEO`, `Ethan-CTO`, or
  `Samantha-Secretary`.
- `readiness`: Prints ready now, not ready, recommended next steps, blockers,
  and safety boundaries.
- `capabilities`: Prints capability matrix summary.
- `governance`: Prints the governance boundary: labs thinks, Y-star-gov judges,
  hook enforces, CIEU records/teaches, brain learns, console reads snapshots.
- `gaps`: Prints open gaps from snapshot and readiness.
- `sources`: Prints generated manifest source files and unsafe sources not read.
- `warnings`: Prints snapshot/generator warnings.
- `validate-local`: Checks generated JSON files exist, load successfully, include
  required agents, and manifest sources avoid unsafe patterns.

Invalid commands exit with code `1`.
