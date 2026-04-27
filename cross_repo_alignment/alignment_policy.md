# Cross-Repo Alignment Policy

## Purpose

Cross-repo alignment records whether the independent Y-star-gov governance
endpoint and the ystar-company labs runtime governance stack are both accepted
in dry-run mode.

## Allowed Cross-Repo Reads

The alignment builder may read Y-star-gov HEAD information and run the
Y-star-gov endpoint acceptance command:

```bash
python3 /Users/haotianliu/.openclaw/workspace/Y-star-gov/tools/run_governance_endpoint_acceptance.py
```

It must not modify Y-star-gov source files or stage/commit anything there.

## ystar-company Inputs

The builder may read generated labs acceptance, Labs-Gov bridge, multi-role
Pre-U governance, and console summary JSON files.

## Non-Execution Boundary

The alignment layer does not execute actions, write CIEU records, mutate brain
or memory, approve candidates, or ingest raw runtime artifacts.

## Local Wrapper

The local safety wrapper validates generated alignment JSON and runs a console
smoke command. It does not run the full cross-repo acceptance command to avoid
recursive acceptance checks.

