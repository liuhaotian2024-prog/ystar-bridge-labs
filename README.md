# Y* Bridge Labs

Y* Bridge Labs is the CEO and company behavior center for the Y* agent-company
runtime. It is where the company mission, owner decisions, business artifacts,
mission-command reports, external-validation planning, and CEO runtime sessions
live.

This repository is not the canonical governance engine and it is not the
provider executor. It produces and routes company decisions; Y-star-gov governs
them; gov-mcp carries them to tool/provider boundaries in dry-run or approved
execution modes.

## Current role in the system

The current baseline comes from the full-repository E87R baseline and the E88
runtime binding work. The division of responsibilities is:

| Repository | Canonical role |
| --- | --- |
| `ystar-bridge-labs` | CEO/company behavior center, mission command, business reasoning, owner decisions, reports, pre-action packets, post-action residuals. |
| `Y-star-gov` | Governance reflex center, deterministic validators, runtime hooks, CIEUStore formal governance records. |
| `gov-mcp` | Provider/tool execution boundary, outbound policy, dry-run/no-send receipts, future owner-activated execution preflight. |
| `K9Audit` | Separate stronger hash-chain evidence ledger. It is not currently a write path from this repo. |

## What is implemented here

### CEO behavior center

The existing CEO-facing behavior center lives under:

- `office/aiden_meeting_room/aiden_response_engine.py`
- `office/aiden_meeting_room/company_context_loader.py`
- `office/aiden_meeting_room/aiden_intent_classifier.py`
- `office/aiden_meeting_room/meeting_memory.py`

It reads repository-grounded company context, classifies owner intent, returns a
CEO-level response, and keeps external side effects out of the response path.

### Mission command and runtime bridge

The mission-command layer lives under `office/mission_command/`. It now includes:

- `e84_ystar_gov_ceo_cognitive_os_call_adapter.py` - direct Y-star-gov validator call adapter.
- `e85_ceo_cognitive_os_runtime_bridge.py` - CEO major-action runtime envelope and decision routing.
- `e87_ceo_runtime_session.py` - end-to-end CEO runtime session runner.

The E87/E88 runtime session runner proves this internal chain:

```text
bridge-labs behavior center
-> CEO pre-action packet
-> Y-star-gov validate_and_write_ceo_runtime_envelope(...)
-> formal Y-star-gov CIEUStore pre-action record
-> bridge-labs decision route
-> gov-mcp dry-run receipt when the action is provider/tool-bound
-> post-action residual
-> formal Y-star-gov CIEUStore residual record
-> next-action recommendation
```

### Baseline reports

The canonical baseline reports are under:

- `operations/baseline/e87r_full_repo_baseline/`

Important files include:

- `baseline_summary.json`
- `architecture_evidence_map.json`
- `stable_vocabulary_and_owner_map.json`
- `l5_truth_table.json`
- `final_goal_gap_analysis.json`
- `next_engineering_roadmap.json`
- `current_runtime_status_after_e88_bind_existing_labs_behavior_center_to_runtime_cieu_loop.json`

## Current L5 truth table

Do not describe the project as simply "L5 complete." Use this taxonomy:

| Layer | Current status | Meaning |
| --- | --- | --- |
| L5-A Runtime Foundation | Complete for internal runtime foundation | One internal CEO session can pass through behavior center, Y-star-gov runtime governance, formal CIEUStore writes, gov-mcp dry-run, and post-action residual closure. |
| L5-B CEO Intelligence Loop | Partial | The repo has intelligence artifacts and reports, but still needs a runtime/compiler flow for full repo recall, route generation, counterfactual comparison, commercial sharpness, and learning updates before every major action. |
| L5-C Controlled External Action | Partial dry-run only | gov-mcp dry-run/no-send boundary exists. Live provider execution is not enabled by this milestone. |
| L5-D Revenue/Customer/Payment Loop | Absent or not executed | No customer validation, paid signal, pricing validation, payment loop, or revenue loop is claimed. |

## What this repository does not claim

This repository does not claim:

- live external outreach;
- customer validation;
- paid signal;
- pricing validation;
- compliance or legal proof;
- production deployment;
- live provider execution;
- K9Audit ledger integration;
- complete L5 revenue/customer/payment loop.

## Key validation commands

Useful targeted checks:

```bash
python3 -m py_compile office/mission_command/e87_ceo_runtime_session.py
pytest -q tests/office/test_e87_ceo_runtime_session.py
pytest -q tests/office/test_e85_ceo_cognitive_os_runtime_bridge.py
pytest -q tests/office/test_e87r_full_repo_baseline_reports.py
```

## Delivery model

Changes to this repository are delivered through the host-local repository
delivery bridge when normal push from a sandbox is unavailable:

- `scripts/repository_delivery_bridge_submit.py`
- `scripts/repository_delivery_bridge_worker.py`
- `scripts/repository_delivery_bridge_status.py`

The delivery bridge applies an allowlisted payload, runs targeted validation,
commits, pushes, and records the remote-confirmed hash.

## Next engineering direction

The next major engineering loop should upgrade L5-B: turn the CEO intelligence
loop into a real runtime/compiler path that performs repository and history
recall, candidate route generation, counterfactual comparison, commercial
sharpness, adversarial critique, pre-action CIEU prediction, and next-action
selection before every major action.
