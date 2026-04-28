# Generated Console Snapshots

These files are derived artifacts from curated read-model inputs only.
They do not contain DB contents, raw logs, daemon state, active-agent state,
or live runtime observations.

`quarantine_summary.json` is derived from the runtime artifact quarantine
path-only manifest. It summarizes classes/counts only and does not include
artifact contents.

`safe_mining_summary.json` is derived from bounded Markdown report candidate
indexes. It summarizes candidate counts/classes only; candidates remain
review assets, not brain memory.

`review_queue_summary.json` is derived from generated review queue files.
It summarizes pending review state only; entries are not approved or ingested.

`artifact_disposition_summary.json` is derived from generated backlog
disposition indexes. It summarizes routing/disposition only; it is not ingestion.

`evidence_review_summary.json` is derived from generated evidence review
indexes. It summarizes structural readiness only; it is not approval.

`governance_bridge_summary.json` is derived from the generated Labs-Gov
dry-run decision snapshot. It is not hook execution or CIEU writeback.

`pre_u_governance_summary.json` is derived from generated multi-role
Pre-U dry-run decisions. It is not runtime packet execution.

`labs_acceptance_summary.json` is derived from the generated labs runtime
acceptance report. It is dry-run acceptance only, not runtime execution.

`cross_repo_alignment_summary.json` is derived from the generated cross-repo
alignment manifest. It is dry-run compatibility only, not CI or hook execution.

`live_readiness_summary.json` is derived from the generated live-readiness
report. It identifies blockers and keeps live execution disabled.

`live_boundary_summary.json` is derived from the generated live-boundary
manifest. It confirms boundary definitions remain disabled.

`cieu_boundary_summary.json` is derived from the generated CIEU runtime
boundary manifest. It confirms event fixtures are dry-run only and persistence is disabled.

`autonomy_inventory_summary.json` is derived from the generated company
autonomy inventory. It confirms capability maps and tool candidates exist while live actions remain disabled.

`autonomous_cycle_summary.json` is derived from the mission-bounded
autonomous work cycle simulator. It confirms a full simulated company cycle exists while real actions remain disabled.

`legacy_triage_summary.json` is derived from generated legacy asset
triage outputs. It classifies assets before absorption and enables no actions.

`observation_loop_summary.json` is derived from generated governed
observation loop outputs. It summarizes a read-only tick from safe generated sources.

`readonly_tool_summary.json` is derived from generated governed read-only
observation tool outputs. It confirms the first local read-only wrapper is callable while live action remains disabled.

`tool_bridge_summary.json` is derived from generated governed tool
invocation bridge outputs. It confirms the read-only tool is called only after Pre-U packet, decision, and bridge authorization.

`work_proposal_summary.json` is derived from generated agent-team work
proposal outputs. It confirms mission/observation evidence produced a governed tool request routed through the L4.5 bridge.

`dashboard_refresh_summary.json` is derived from generated mission dashboard
refresh loop outputs. It confirms a manual local refresh loop produced a refreshed dashboard without scheduler or daemon use.

`recurring_loop_summary.json` is derived from generated recurring observation
loop contract outputs. It confirms recurrence is defined but disabled and only one manual local simulated tick exists.

`manual_tick_summary.json` is derived from generated manual recurring
observation tick runner outputs. It confirms one manual local tick ran with a receipt while scheduler, daemon, and recurrence stay disabled.

`field_functional_summary.json` is derived from generated field
functional archaeology outputs. It confirms old field-functional work was searched and mapped into a merge plan without executing old code.

`mission_projection_summary.json` is derived from the L5.1 mission field
projection harness. It confirms layered Y* projection, a Pre-U packet candidate, and a residual fixture exist while action execution remains disabled.

`field_projection_summary.json` is derived from the L5.2 field functional
auto-projection core. It confirms mission-to-behavior Y* projection, a behavior-level Pre-U candidate, and a residual loop fixture exist while behavior execution remains disabled.

`projection_cycle_summary.json` is derived from the L5.3 projection-checked
autonomous work cycle. It confirms behavior-level Y* is consumed as a gate before dry-run work proposal, Pre-U candidate, residual, and review-only learning artifacts.

`shadow_learning_cycle_summary.json` is derived from the L5.4 integrated
review-gated shadow learning cycle. It confirms an L5.3 residual can influence a shadow behavior-level Y* preview and shadow cycle without canonical policy mutation or writeback.

`cross_repo_governance_summary.json` is derived from the L5.5 cross-repo
governance contract proof. It confirms ystar-company remains labs/runtime, Y-star-gov remains the intended governance kernel, and gov-mcp remains a governed interface boundary.

`console_read_model/cli/team_console.py` consumes these generated files as its
only data source.
