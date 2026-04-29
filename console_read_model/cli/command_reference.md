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
- `readonly-tool`: Prints the generated governed read-only observation tool
  summary: contract, allowed source registry, sample invocation/result,
  unsafe request rejection, disabled live/persistence flags, and the L4.5
  recommendation.
- `tool-bridge`: Prints the generated governed tool invocation bridge summary:
  Pre-U packet, governance decision, bridge authorization, bridged read-only
  tool result, rejection fixtures, disabled live/persistence flags, and the
  L4.6 recommendation.
- `work-proposal`: Prints the generated agent-team work proposal summary:
  mission context, observation input, autonomous proposals, role review, tool
  need, generated tool request, bridge routing, CIEU fixture, disabled live
  flags, and the L4.7 recommendation.
- `dashboard-refresh`: Prints the generated mission dashboard refresh loop
  summary: previous dashboard snapshot, current observation input, refreshed
  dashboard, company state delta, refreshed backlog, CIEU fixture, disabled
  scheduler/live/persistence flags, and the L4.8 recommendation.
- `recurring-loop`: Prints the generated governed recurring observation loop
  contract summary: recurrence policy, allowed sources, tick governance gate,
  simulated tick, CIEU fixture, residual delta, stop/abort and escalation
  conditions, disabled scheduler/live/persistence flags, and the L4.9
  recommendation.
- `manual-tick`: Prints the generated manual recurring observation tick runner
  summary: one manual tick request, preflight, source validation, governance
  decision, tick result, receipt, history index, disabled scheduler/live flags,
  and the L5.0 recommendation.
- `field-functional`: Prints the generated field functional archaeology
  summary: repositories/assets scanned, merge decision counts, mission
  projection merge-plan status, disabled live/persistence flags, and the L5.1
  recommendation.
- `mission-projection`: Prints the generated L5.1 mission field projection
  harness summary: projection contract, layered trace, Pre-U adapter candidate,
  residual delta fixture, disabled live/writeback/persistence flags, and the
  L5.2 recommendation.
- `field-projection`: Prints the generated L5.2 field functional
  auto-projection core summary: mission-to-behavior Y* projection, behavior Y*
  candidate, Pre-U packet candidate, residual loop fixture, learning stub, and
  disabled live/writeback/persistence/behavior-execution flags.
- `projection-cycle`: Prints the generated L5.3 projection-checked autonomous
  work cycle summary: behavior-level Y* consumption, projection gate, Pre-U
  packet candidate, dry-run result, CIEU-like fixture, residual delta, review
  learning candidate, and disabled live/writeback/persistence/behavior-execution
  flags.
- `shadow-learning-cycle`: Prints the generated L5.4 integrated review-gated
  shadow learning cycle summary: L5.3 residual consumption, deterministic
  review gate, learning target classification, shadow policy patch, shadow
  behavior-level Y* preview, shadow cycle, original-vs-shadow comparison, and
  disabled live/writeback/persistence/canonical-mutation flags.
- `cross-repo-governance`: Prints the generated L5.5 cross-repo governance
  contract proof summary: Y-star-gov and gov-mcp read-only inventories,
  ystar-company to governance-kernel alignment, governed MCP boundary
  invariants, bypass risks, and disabled live/MCP/writeback/persistence flags.
- `governed-mcp-adapter`: Prints the generated L5.6 governed MCP dry-run
  adapter summary: behavior-level Y* consumption, MCP request intent, MCP
  Pre-U packet candidate, dry-run governance decision, bridge receipt, blocked
  real MCP execution, CIEU-like fixture, residual delta, review-only learning
  candidate, and disabled live/MCP/writeback/persistence flags.
- `controlled-canonical-learning`: Prints the generated L5.7 controlled
  canonical learning design summary: Y* non-mutation invariant, learning target
  registry, promotion evidence, promotion gate, canonical update package
  candidate, versioned patch plan, rollback/audit plan, validation plan, dry-run
  promotion fixture, and blocked approval/application/writeback/direct-Y* state.
- `approved-sandbox-update`: Prints the generated L5.8 approved canonical
  update sandbox summary: sandbox approval, sandbox baseline, sandbox patch
  application, post-update validation, behavior-level Y* reprojection, governed
  MCP preview, CIEU-like residual, rollback validation, comparison, and blocked
  real approval/application/writeback/direct-Y*/MCP/live state.
- `real-approval-boundary`: Prints the generated L5.9 real approval workflow
  boundary summary: authority model, evidence dossier, durable approval record
  contract, decision packet fixture, validity/revocation, snapshot policy, real
  application gate, preflight plan, manual runbook, approval audit fixture, and
  blocked real approval/application/durable-persistence/writeback/direct-Y*
  state.
- `approval-record-sandbox`: Prints the generated L5.10 controlled approval
  record sandbox summary: sandbox record instance, integrity validation,
  validity state replay, invalid-record blocking, valid gate replay, audit
  lineage, CIEU-like residual, and blocked real approval/application/durable
  persistence/writeback/direct-Y*/MCP state.
- `real-release-preflight`: Prints the generated L5.11 controlled real release
  preflight summary: release candidate assembly, scope validation, approval
  record preflight, snapshot/rollback checks, Y* non-mutation and MCP
  non-bypass checks, post-release validation matrix, handoff packet, release
  blocker decision, CIEU-like residual, and blocked real release/application/
  durable-persistence/writeback/direct-Y*/MCP state.
- `release-simulation-sandbox`: Prints the generated L5.12 real release
  simulation sandbox summary: sandbox authority, simulated approval record,
  sandbox snapshot, sandbox release execution, post-release validation,
  projection/MCP preview, rollback drill, CIEU-like residual, and blocked real
  release/application/durable-persistence/writeback/direct-Y*/MCP state.
- `live-boundary-no-go`: Prints the generated L5.13 live boundary no-go
  framework summary: live capability domains, no-go invariants, L5 evidence
  index, live blockers, L6 design-only entry gate, non-execution boundary,
  hardcoding-forbidden policy, system no-go decisions, and blocked live/
  external/network/revenue/persistence/writeback/MCP/release execution state.
- `meta-development-design`: Prints the generated L6.0 meta-development
  generative selection engine summary: self model, unique asset field,
  world-value field, conversion operators, value hypotheses, conversion
  physics, redeemability selection, MVP proof plans, governed experiment
  portfolio, strategic residual loop, hardcoding-forbidden policy, and blocked
  external/network/publication/payment/revenue execution state.
- `meta-development-mvp-artifact-sandbox`: Prints the generated L6.1 MVP
  artifact sandbox summary: selected hypotheses, internal artifact cases,
  artifact generation scope, review gate, structural validation, externalization
  blockers, strategic residual loop, readiness for L6.2 boundary design, and
  blocked external/network/publication/outreach/payment/revenue/MCP/writeback
  execution state.
- `governed-external-observation-boundary`: Prints the generated L6.2 governed
  external observation boundary summary: Pre-Observation packet schema, source
  registry, permission gate, manual import sandbox, observation-to-artifact
  linker, claim boundary policy, no-action receipts, strategic residual loop,
  readiness for L6.3 sandbox design, and blocked network/API/scraping/browser
  fetch/publication/outreach/payment/revenue/MCP/live/writeback execution state.
- `controlled-external-observation-sandbox`: Prints the generated L6.3
  controlled external observation sandbox summary: selected observation cases,
  pre-observation packets, permission replay, static/manual fixtures,
  structural evidence validation, claim/freshness assessment, review packets,
  refinement candidates, no-action receipts, strategic residual loop, readiness
  for L6.4 preflight, and blocked real observation/network/API/scraping/browser
  fetch/publication/outreach/payment/revenue/MCP/live/writeback execution state.
- `real-read-only-observation-preflight`: Prints the generated L6.4 real
  read-only external observation preflight summary: selected future candidates,
  preflight contract, source allowlist/denylist, approval packets, operator
  handoff, network isolation requirements, evidence capture requirements,
  abort/quarantine policy, no-action guarantees, blocked preflight decisions,
  readiness for L6.5 pilot design, and blocked real observation/network/API/
  scraping/browser fetch/publication/outreach/payment/revenue/MCP/live/CIEU DB/
  writeback execution state.
- `gaps`: Prints open gaps from snapshot and readiness.
- `sources`: Prints generated manifest source files and unsafe sources not read.
- `warnings`: Prints snapshot/generator warnings.
- `validate-local`: Checks generated JSON files exist, load successfully, include
  required agents, and manifest sources avoid unsafe patterns.

Invalid commands exit with code `1`.
