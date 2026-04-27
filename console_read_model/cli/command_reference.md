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
- `quarantine`: Prints the generated runtime artifact quarantine summary:
  framework status, mining level, class counts, forbidden direct reads, future
  adapter candidates, and safety warning.
- `mining-candidates`: Prints the generated safe-mining candidate summary:
  candidate count, report classes, safety level, ingestion status, generated
  candidate index, and review/writeback warning.
- `review-queue`: Prints the generated candidate review queue summary: review
  count, statuses, intended-use counts, generated queue path, and warning.
- `artifact-disposition`: Prints the generated backlog disposition summary:
  total artifact coverage, disposition counts, deferred adapter counts,
  forbidden direct-read count, and evidence-scoring status.
- `evidence-review`: Prints the generated evidence review summary: candidates
  scored, decision stubs, route counts, automatic approvals, semantic truth
  status, and structural-only warning.
- `governance-bridge`: Prints the generated Labs-Gov bridge summary:
  Y-star-gov dry-run decision, execution booleans, and non-execution warning.
- `pre-u-governance`: Prints the generated multi-role Pre-U governance summary:
  packets generated, roles covered, decisions by role, and dry-run safety flags.
- `labs-acceptance`: Prints the generated labs runtime governance acceptance
  summary: accepted status, check counts, decisions, and dry-run safety flags.
- `cross-repo-alignment`: Prints the generated cross-repo governance alignment
  summary: repo heads, acceptance states, decisions, and safety assertions.
- `live-readiness`: Prints the generated live-readiness gate summary: dry-run
  readiness, live blockers, transition backlog count, and disabled live-write
  flags.
- `live-boundary`: Prints the generated live-boundary harness summary:
  boundary contracts, disabled live execution flags, manual enablement, and
  transition checklist counts.
- `cieu-boundary`: Prints the generated CIEU runtime boundary summary:
  runtime event schema status, prediction-delta fixture status, persistence
  disabled flags, and required manual enablement.
- `autonomy-inventory`: Prints the generated company autonomy inventory
  summary: repo archaeology status, observation/resource/action maps, governed
  tool candidates, agent role matrix, disabled live/external actions, and the
  next required autonomy simulator milestone.
- `autonomous-cycle`: Prints the generated mission-bounded autonomous work
  cycle summary: mission-bounded autonomy, observation, backlog, selected work,
  role delegation, governed tool selection, Pre-U simulation, governance
  decision simulation, CIEU fixture, residual delta, disabled live flags, and
  the L4.3 recommendation.
- `legacy-triage`: Prints the generated legacy asset triage summary: assets
  scored, absorption buckets, top candidates, governed backlog, disabled live
  flags, and the L4.4 recommendation.
- `observation-loop`: Prints the generated governed observation loop summary:
  read-only source registry, observation tick, mission dashboard, company
  digest, work candidates, disabled live flags, and the L4.4 recommendation.
- `gaps`: Prints open gaps from snapshot and readiness.
- `sources`: Prints generated manifest source files and unsafe sources not read.
- `warnings`: Prints snapshot/generator warnings.
- `validate-local`: Checks generated JSON files exist, load successfully, include
  required agents, and manifest sources avoid unsafe patterns.

Invalid commands exit with code `1`.
