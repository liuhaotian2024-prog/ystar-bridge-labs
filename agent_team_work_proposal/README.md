# Agent Team Work Proposal

L4.6 moves one step earlier than the governed tool bridge. It starts from
mission and observation evidence, lets the agent team propose work, selects a
safe proposal, reviews it across roles, derives a tool need, and routes the
generated tool request through the L4.5 Pre-U bridge.

This pack is local, deterministic, read-only, and dry-run only. It does not
execute live work, contact external systems, write CIEU records, mutate
brain/memory, or approve candidates.

Run from the repository root:

```bash
python3 agent_team_work_proposal/tools/build_agent_team_work_proposal.py
```

The generated files under `agent_team_work_proposal/generated/` are curated
read-model artifacts for console and validation use.
