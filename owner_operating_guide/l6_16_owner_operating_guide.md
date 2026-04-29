# L6.16 Owner Operating Guide

## How do I run the CEO command brief?
- Use the console command `ceo-command-brief-internal-strategy-memo` from the repo root.

## How do I run real observation?
- Use the existing L6.13 real observation scripts only when the repo-external controlled observation environment is configured.
- Do not paste API keys into repo files.

## How do I read the evidence report?
- Start with `ceo_command_brief/l6_16_ceo_command_brief.md` for the owner view.
- Read `internal_strategy_memo/l6_16_internal_strategy_memo.md` for the caveated internal planning direction.
- Use L6.13-L6.15 reports when you need evidence packet details.

## How do I know what is safe to do next?
- The next safe step is: draft internal strategy memo with bounded-conflict caveats.
- Internal analysis is allowed. External action and core writeback remain blocked.

## What should I not ask the agent to do yet?
- Do not ask it to publish, contact customers, submit grants/RFPs, spend money, execute MCP/live behavior, or write brain/memory/canonical state.

## Important files
- `ceo_command_brief/l6_16_ceo_command_brief.md`
- `internal_strategy_memo/l6_16_internal_strategy_memo.md`
- `system_capability_inventory/system_capability_inventory.json`
- `decision_options_matrix/decision_options_matrix.json`
- `next_30_60_90_day_plan/next_30_60_90_day_plan.json`

## One-command workflow
- `python3 console_read_model/cli/team_console.py ceo-command-brief-internal-strategy-memo`
