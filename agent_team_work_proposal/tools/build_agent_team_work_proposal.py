#!/usr/bin/env python3
"""Build the L4.6 agent-team work proposal to governed tool bridge pack."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent_team_work_proposal.tools import run_work_proposal_to_bridge as runner


PACK = ROOT / "agent_team_work_proposal"
GENERATED = PACK / "generated"
TOOL_ID = "governed_readonly_observation_tool_v0"
BRIDGE_ID = "governed_tool_invocation_bridge_v0"
NEXT_MILESTONE = "L4.7 First Mission Dashboard Refresh Loop v0"

MISSION_PROFILE = "company_autonomous_work_cycle/generated/mission_profile.json"
MISSION_DASHBOARD = "governed_observation_loop/generated/mission_dashboard_snapshot.json"
COMPANY_DIGEST = "governed_observation_loop/generated/company_state_digest.json"
OBSERVATION_TICK = "governed_observation_loop/generated/observation_tick_001.json"
WORK_CANDIDATES = "governed_observation_loop/generated/observation_to_work_item_candidates.json"
TOOL_BRIDGE_SUMMARY = "governed_tool_invocation_bridge/generated/tool_bridge_readiness_summary.json"
READONLY_TOOL_SUMMARY = "governed_readonly_observation_tool/generated/tool_readiness_summary.json"
LEGACY_TRIAGE_SUMMARY = "legacy_asset_triage/generated/legacy_asset_triage_summary.json"
CONSOLE_SNAPSHOT = "console_read_model/generated/team_console_snapshot.json"

OUTPUTS = {
    "mission_context_snapshot": "mission_context_snapshot.json",
    "agent_team_observation_input": "agent_team_observation_input.json",
    "autonomous_work_proposals": "autonomous_work_proposals.json",
    "selected_agent_work_proposal": "selected_agent_work_proposal.json",
    "role_review_board": "role_review_board.json",
    "tool_need_analysis": "tool_need_analysis.json",
    "generated_tool_request": "generated_tool_request.json",
    "agent_team_work_proposal_summary": "agent_team_work_proposal_summary.json",
}


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected object JSON: {relative_path}")
    return data


def compact_list(value: Any, limit: int = 6) -> list[Any]:
    if isinstance(value, list):
        return value[:limit]
    return []


def build_mission_context(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    mission = inputs["mission"]
    dashboard = inputs["dashboard"]
    digest = inputs["digest"]
    tool = inputs["readonly_tool"]
    bridge = inputs["bridge"]
    triage = inputs["triage"]
    console = inputs["console"]
    observation_sources = inputs["observation_tick"].get("observation_sources_used", [])

    return {
        "schema_name": "ystar.agent_team_work_proposal.generated.mission_context_snapshot",
        "schema_version": "v0",
        "mission_id": mission.get("mission_id"),
        "founder_defined_mission": mission.get("founder_defined_mission"),
        "mission_bounded_autonomy": True,
        "founder_sets_mission_agent_team_drives": True,
        "step_by_step_human_prompting_required": False,
        "current_capability_state": {
            "governed_readonly_tool_ready": tool.get("local_readonly_dry_run_callable"),
            "tool_bridge_ready": bridge.get("tool_invoked_through_bridge"),
            "legacy_assets_scored": triage.get("assets_scored"),
            "console_agents": [agent.get("agent_id") for agent in console.get("agents", [])],
        },
        "current_safe_observation_sources": observation_sources,
        "current_governed_tools": [
            {
                "tool_id": TOOL_ID,
                "status": "callable_for_local_readonly_dry_run",
                "bridge_required": True,
            }
        ],
        "current_blocked_actions": compact_list(digest.get("what_remains_blocked", []), 8),
        "current_top_risks": compact_list(dashboard.get("top_risks", []), 6),
        "current_top_opportunities": compact_list(dashboard.get("top_opportunities", []), 6),
        "evidence_refs": [
            MISSION_PROFILE,
            MISSION_DASHBOARD,
            COMPANY_DIGEST,
            TOOL_BRIDGE_SUMMARY,
            READONLY_TOOL_SUMMARY,
            LEGACY_TRIAGE_SUMMARY,
            CONSOLE_SNAPSHOT,
        ],
    }


def build_observation_input(inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
    mission = inputs["mission"]
    dashboard = inputs["dashboard"]
    digest = inputs["digest"]
    tick = inputs["observation_tick"]
    tool = inputs["readonly_tool"]
    bridge = inputs["bridge"]
    triage = inputs["triage"]

    return {
        "schema_name": "ystar.agent_team_work_proposal.generated.agent_team_observation_input",
        "schema_version": "v0",
        "mission": mission.get("founder_defined_mission"),
        "current_milestone_chain": dashboard.get("current_milestone_chain", []),
        "latest_observation_tick": {
            "tick_id": tick.get("tick_id"),
            "safe_opportunities": tick.get("safe_opportunities", []),
            "blocked_risks": tick.get("blocked_risks", []),
            "work_item_candidates": tick.get("work_item_candidates", []),
        },
        "mission_dashboard": {
            "next_recommended_work": dashboard.get("next_recommended_work"),
            "top_opportunities": dashboard.get("top_opportunities", []),
            "top_risks": dashboard.get("top_risks", []),
        },
        "company_state_digest": {
            "what_the_company_knows_now": digest.get("what_the_company_knows_now"),
            "what_it_can_safely_observe": digest.get("what_it_can_safely_observe"),
            "what_it_can_safely_do_now": digest.get("what_it_can_safely_do_now"),
            "what_remains_blocked": digest.get("what_remains_blocked"),
        },
        "existing_governed_readonly_tool": {
            "defined": tool.get("governed_readonly_observation_tool_defined"),
            "callable": tool.get("local_readonly_dry_run_callable"),
            "next_required_milestone": tool.get("next_required_milestone"),
        },
        "existing_tool_bridge": {
            "defined": bridge.get("governed_tool_invocation_bridge_defined"),
            "tool_invoked_through_bridge": bridge.get("tool_invoked_through_bridge"),
            "next_required_milestone": bridge.get("next_required_milestone"),
        },
        "legacy_asset_triage_summary": {
            "assets_scored": triage.get("assets_scored"),
            "bucket_counts": triage.get("bucket_counts", {}),
            "top_absorption_candidate_count": triage.get("top_absorption_candidate_count"),
        },
        "safe_opportunities": tick.get("safe_opportunities", []),
        "blocked_risks": tick.get("blocked_risks", []),
        "input_policy": "generated_read_model_only",
    }


def build_work_proposals() -> dict[str, Any]:
    proposals = [
        {
            "proposal_id": "agent-work-proposal-001",
            "title": "Refresh company state through governed read-only bridge",
            "description": "Use the existing L4.5 bridge to request a fresh normalized company-state observation.",
            "proposing_agent": "Aiden-CEO",
            "recommended_owner_agent": "Samantha-Secretary",
            "supporting_agents": ["Maya-Governance", "Ryan-Platform"],
            "mission_relevance": "Reduces founder step-by-step prompting by letting the agent team refresh mission context safely.",
            "evidence_refs": [
                "governed_observation_loop/generated/mission_dashboard_snapshot.json",
                "governed_tool_invocation_bridge/generated/tool_bridge_readiness_summary.json",
            ],
            "tool_need": "governed_readonly_observation_tool_v0 via governed_tool_invocation_bridge_v0",
            "expected_business_value": "Creates the first agent-team generated route from observation to governed tool result.",
            "risk_tier": "low",
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "requires_live_action": False,
            "live_enabled": False,
            "external_action_enabled": False,
            "selection_score": 95,
            "selection_reason": "Best advances autonomy while staying local, read-only, and bridge-gated.",
        },
        {
            "proposal_id": "agent-work-proposal-002",
            "title": "Convert top legacy triage candidate into wrapper plan",
            "description": "Turn a high-value legacy asset into a governed wrapper design without absorbing code.",
            "proposing_agent": "Ethan-CTO",
            "recommended_owner_agent": "Ethan-CTO",
            "supporting_agents": ["Maya-Governance", "Leo-Kernel"],
            "mission_relevance": "Improves governed tool coverage while preserving triage-before-absorption.",
            "evidence_refs": ["legacy_asset_triage/generated/top_absorption_candidates.json"],
            "tool_need": "read-only observation to inspect current triage summary",
            "expected_business_value": "Prepares future wrappers for dormant useful assets.",
            "risk_tier": "medium",
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "requires_live_action": False,
            "live_enabled": False,
            "external_action_enabled": False,
            "selection_score": 82,
            "selection_reason": "Valuable but less immediate than proving proposal-to-bridge routing.",
        },
        {
            "proposal_id": "agent-work-proposal-003",
            "title": "Create mission progress dashboard candidate",
            "description": "Summarize autonomy milestones and blocked live capabilities into a dashboard fixture.",
            "proposing_agent": "Samantha-Secretary",
            "recommended_owner_agent": "Samantha-Secretary",
            "supporting_agents": ["Aiden-CEO"],
            "mission_relevance": "Makes company progress easier for the agent team and founder to inspect.",
            "evidence_refs": ["console_read_model/generated/team_console_snapshot.json"],
            "tool_need": "read-only console summary access",
            "expected_business_value": "Improves continuity and reduces operational prompting.",
            "risk_tier": "low",
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "requires_live_action": False,
            "live_enabled": False,
            "external_action_enabled": False,
            "selection_score": 86,
            "selection_reason": "Strong next step after proposal-to-bridge is proven.",
        },
        {
            "proposal_id": "agent-work-proposal-004",
            "title": "Prepare first low-risk real business task candidate",
            "description": "Draft a future candidate for live business work without executing or contacting anyone.",
            "proposing_agent": "Aiden-CEO",
            "recommended_owner_agent": "Maya-Governance",
            "supporting_agents": ["Ryan-Platform", "Leo-Kernel"],
            "mission_relevance": "Moves toward commercial action while keeping live gates blocked.",
            "evidence_refs": ["labs_live_readiness/generated/live_readiness_report.json"],
            "tool_need": "read-only readiness and boundary summaries",
            "expected_business_value": "Clarifies what must be true before future business work.",
            "risk_tier": "medium",
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "requires_live_action": False,
            "live_enabled": False,
            "external_action_enabled": False,
            "selection_score": 74,
            "selection_reason": "Useful but should wait until dashboard refresh loop exists.",
        },
        {
            "proposal_id": "agent-work-proposal-005",
            "title": "Create observation-to-work backlog refinement",
            "description": "Refine observation-derived work candidates into scored governed proposals.",
            "proposing_agent": "Ryan-Platform",
            "recommended_owner_agent": "Ryan-Platform",
            "supporting_agents": ["Samantha-Secretary", "Maya-Governance"],
            "mission_relevance": "Improves the recurring loop from observation to prioritized work.",
            "evidence_refs": ["governed_observation_loop/generated/observation_to_work_item_candidates.json"],
            "tool_need": "read-only generated candidate observation",
            "expected_business_value": "Turns observation ticks into a stronger autonomous work queue.",
            "risk_tier": "low",
            "requires_y_star_gov": True,
            "requires_operator_approval": False,
            "requires_cieu_event": True,
            "requires_live_action": False,
            "live_enabled": False,
            "external_action_enabled": False,
            "selection_score": 84,
            "selection_reason": "Good follow-on once first proposal-to-bridge path is stable.",
        },
    ]
    return {
        "schema_name": "ystar.agent_team_work_proposal.generated.autonomous_work_proposals",
        "schema_version": "v0",
        "proposal_count": len(proposals),
        "proposals": proposals,
    }


def build_selected_proposal(proposals: dict[str, Any]) -> dict[str, Any]:
    selected = proposals["proposals"][0]
    return {
        "schema_name": "ystar.agent_team_work_proposal.generated.selected_agent_work_proposal",
        "schema_version": "v0",
        "selected_proposal_id": selected["proposal_id"],
        "selected_proposal_title": selected["title"],
        "selection_reason": selected["selection_reason"],
        "selected_by_agent": "Aiden-CEO",
        "requires_tool_invocation": True,
        "selected_tool_id": TOOL_ID,
        "selected_bridge_id": BRIDGE_ID,
        "live_enabled": False,
        "external_action_enabled": False,
        "expected_outcome": selected["expected_business_value"],
    }


def build_role_review_board(selected: dict[str, Any]) -> dict[str, Any]:
    common_forbidden = [
        "live action",
        "external action",
        "git push",
        "daemon control",
        "CIEU persistence",
        "brain writeback",
        "memory ingestion",
        "direct tool invocation",
    ]
    reviews = [
        {
            "agent_id": "Aiden-CEO",
            "review_focus": "mission relevance and priority",
            "support_or_concern": "supports selected proposal as the highest-signal next autonomy step",
            "required_constraints": ["keep mission-bounded autonomy local and dry-run"],
            "approved_for_local_readonly_dry_run": True,
            "forbidden_actions": common_forbidden,
            "notes": "Proposal directly advances founder-set mission while reducing step-by-step prompting.",
        },
        {
            "agent_id": "Ethan-CTO",
            "review_focus": "technical feasibility",
            "support_or_concern": "supports because only deterministic builders/runners are used",
            "required_constraints": ["no code execution beyond local deterministic builder/runner"],
            "approved_for_local_readonly_dry_run": True,
            "forbidden_actions": common_forbidden,
            "notes": "No discovered tools, scripts, daemons, or external commands are executed.",
        },
        {
            "agent_id": "Maya-Governance",
            "review_focus": "governance boundary",
            "support_or_concern": "supports only if Pre-U bridge is required",
            "required_constraints": ["Pre-U bridge required", "Y-star-gov posture preserved", "CIEU event remains dry-run"],
            "approved_for_local_readonly_dry_run": True,
            "forbidden_actions": common_forbidden,
            "notes": "Direct tool invocation is forbidden; request must pass through L4.5 bridge.",
        },
        {
            "agent_id": "Ryan-Platform",
            "review_focus": "platform bridge availability",
            "support_or_concern": "supports because governed_tool_invocation_bridge_v0 exists",
            "required_constraints": ["use existing bridge runner", "use existing read-only observation tool"],
            "approved_for_local_readonly_dry_run": True,
            "forbidden_actions": common_forbidden,
            "notes": "Tool bridge exists and can route a local dry-run read-only request.",
        },
        {
            "agent_id": "Samantha-Secretary",
            "review_focus": "read-model continuity",
            "support_or_concern": "supports read-model observation and report continuity",
            "required_constraints": ["read generated summaries only", "write generated L4.6 artifacts only"],
            "approved_for_local_readonly_dry_run": True,
            "forbidden_actions": common_forbidden,
            "notes": "Selected proposal improves continuity by refreshing normalized company-state observation.",
        },
        {
            "agent_id": "Leo-Kernel",
            "review_focus": "kernel/runtime integrity",
            "support_or_concern": "supports because no runtime or kernel mutation is required",
            "required_constraints": ["no kernel/runtime mutation", "no DB/log/runtime artifact read"],
            "approved_for_local_readonly_dry_run": True,
            "forbidden_actions": common_forbidden,
            "notes": "Boundary remains read-only with no daemon, hook, or runtime activation.",
        },
    ]
    return {
        "schema_name": "ystar.agent_team_work_proposal.generated.role_review_board",
        "schema_version": "v0",
        "selected_proposal_id": selected["selected_proposal_id"],
        "review_count": len(reviews),
        "reviews": reviews,
    }


def build_tool_need_analysis(selected: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.agent_team_work_proposal.generated.tool_need_analysis",
        "schema_version": "v0",
        "analysis_id": "tool-need-analysis-001",
        "selected_proposal_id": selected["selected_proposal_id"],
        "tool_needed": True,
        "tool_id": TOOL_ID,
        "bridge_required": True,
        "bridge_id": BRIDGE_ID,
        "why_tool_needed": "The selected work requires a normalized company-state observation from safe generated summaries.",
        "why_direct_invocation_disallowed": "Agent requests must be converted into Pre-U bridge decisions before any tool call.",
        "expected_tool_output": "Normalized observation with read sources and next work candidates.",
        "risk_tier": "low",
        "requires_y_star_gov": True,
        "requires_cieu_event": True,
        "operator_approval_required": False,
        "live_enabled": False,
        "external_action_enabled": False,
    }


def build_generated_tool_request(mission: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.agent_team_work_proposal.generated.generated_tool_request",
        "schema_version": "v0",
        "request_id": "agent-team-generated-tool-request-001",
        "requesting_agent": "Aiden-CEO",
        "supporting_agent": "Samantha-Secretary",
        "mission_id": mission.get("mission_id"),
        "tool_id": TOOL_ID,
        "request_type": "company_state_observation",
        "business_reason": "Selected agent-team work proposal needs a fresh governed observation before next work selection.",
        "declared_intent": "Refresh company state through the governed read-only observation tool via Pre-U bridge.",
        "requested_summary_level": "executive",
        "requested_sources": [
            "mission-dashboard",
            "company-state-digest",
            "observation-loop-summary",
            "legacy-triage-summary",
            "autonomous-cycle-summary",
            "autonomy-inventory-summary",
            "live-boundary-summary",
            "cieu-boundary-summary",
        ],
        "risk_tier": "low",
        "source_work_proposal_ref": runner.SELECTED_REF,
        "role_review_ref": runner.ROLE_REVIEW_REF,
        "tool_need_analysis_ref": runner.TOOL_NEED_REF,
        "live_action_requested": False,
        "external_action_requested": False,
        "brain_writeback_requested": False,
        "memory_ingestion_requested": False,
        "cieu_persistence_requested": False,
    }


def build_summary(runner_payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    trace = runner_payloads["work_proposal_to_bridge_trace"]
    return {
        "schema_name": "ystar.agent_team_work_proposal.generated.agent_team_work_proposal_summary",
        "schema_version": "v0",
        "agent_team_work_proposal_defined": True,
        "mission_context_snapshot_defined": True,
        "agent_team_observation_input_defined": True,
        "autonomous_work_proposals_defined": True,
        "selected_work_proposal_defined": True,
        "role_review_board_defined": True,
        "tool_need_analysis_defined": True,
        "generated_tool_request_defined": True,
        "work_proposal_routed_to_bridge": True,
        "bridge_runner_used": trace.get("bridge_runner_used") is True,
        "direct_tool_invocation_used": False,
        "bridged_tool_result_ref_defined": True,
        "work_proposal_cieu_event_defined": True,
        "work_proposal_residual_delta_defined": True,
        "next_agent_work_recommendations_defined": True,
        "mission_bounded_autonomy_supported": True,
        "founder_sets_mission_agent_team_drives": True,
        "step_by_step_human_prompting_required": False,
        "agent_team_generated_the_work": True,
        "agent_team_selected_governed_tool": True,
        "pre_u_bridge_required": True,
        "pre_u_bridge_satisfied": True,
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
        "network_enabled": False,
        "git_push_enabled": False,
        "daemon_control_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "email_or_external_communication_enabled": False,
        "next_required_milestone": NEXT_MILESTONE,
        "generated_summary": "agent_team_work_proposal/generated/agent_team_work_proposal_summary.json",
        "generated_tool_request": "agent_team_work_proposal/generated/generated_tool_request.json",
        "generated_bridge_trace": runner.TRACE_REF,
        "generated_bridged_result_ref": runner.BRIDGED_RESULT_REF,
        "generated_cieu_event": runner.CIEU_EVENT_REF,
        "warning": "Agent-team work proposal is dry-run only and routes tool use through the L4.5 bridge.",
    }


def render_report(
    mission_context: dict[str, Any],
    proposals: dict[str, Any],
    selected: dict[str, Any],
    role_review: dict[str, Any],
    tool_need: dict[str, Any],
    request: dict[str, Any],
    runner_payloads: dict[str, dict[str, Any]],
    summary: dict[str, Any],
) -> str:
    trace = runner_payloads["work_proposal_to_bridge_trace"]
    bridged = runner_payloads["bridged_tool_result_ref"]
    event = runner_payloads["work_proposal_cieu_event"]
    delta = runner_payloads["work_proposal_residual_delta"]
    recommendations = runner_payloads["next_agent_work_recommendations"]
    lines = [
        "# Agent Team Work Proposal Report",
        "",
        "## Mission Context",
        "",
        f"- mission_id: {mission_context['mission_id']}",
        f"- mission_bounded_autonomy: {mission_context['mission_bounded_autonomy']}",
        f"- step_by_step_human_prompting_required: {mission_context['step_by_step_human_prompting_required']}",
        "",
        "## Autonomous Proposals",
        "",
        f"- proposal_count: {proposals['proposal_count']}",
        f"- selected: {selected['selected_proposal_id']} - {selected['selected_proposal_title']}",
        "",
        "## Role Review",
        "",
        f"- review_count: {role_review['review_count']}",
        "- all roles approved local read-only dry-run: true",
        "",
        "## Tool Need",
        "",
        f"- tool_id: {tool_need['tool_id']}",
        f"- bridge_required: {tool_need['bridge_required']}",
        f"- bridge_id: {tool_need['bridge_id']}",
        "",
        "## Generated Request",
        "",
        f"- request_id: {request['request_id']}",
        f"- requesting_agent: {request['requesting_agent']}",
        f"- supporting_agent: {request['supporting_agent']}",
        "",
        "## Bridge Routing",
        "",
        f"- bridge_runner_used: {trace['bridge_runner_used']}",
        f"- direct_tool_invocation_used: {trace['direct_tool_invocation_used']}",
        f"- pre_u_bridge_satisfied: {trace['pre_u_bridge_satisfied']}",
        f"- bridged_result_status: {bridged['result_status']}",
        f"- read_source_count: {bridged['read_source_count']}",
        "",
        "## CIEU Event And Residual Delta",
        "",
        f"- dry_run_only: {event['dry_run_only']}",
        f"- persistence_enabled: {event['persistence_enabled']}",
        f"- residual_delta_id: {delta['delta_id']}",
        f"- curation_required: {delta['curation_required']}",
        "",
        "## Next Recommendations",
        "",
        f"- recommendation_count: {recommendations['recommendation_count']}",
        f"- top_recommendation: {recommendations['recommendations'][0]['title']}",
        "",
        "## Why No Real Action Occurred",
        "",
        f"- real_action_executed: {summary['real_action_executed']}",
        f"- external_action_executed: {summary['external_action_executed']}",
        f"- live_action_enabled: {summary['live_action_enabled']}",
        f"- cieu_persistence_enabled: {summary['cieu_persistence_enabled']}",
        f"- brain_writeback_enabled: {summary['brain_writeback_enabled']}",
        f"- memory_ingestion_enabled: {summary['memory_ingestion_enabled']}",
        "",
        f"Next required milestone: {summary['next_required_milestone']}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    GENERATED.mkdir(parents=True, exist_ok=True)
    inputs = {
        "mission": load_json(MISSION_PROFILE),
        "dashboard": load_json(MISSION_DASHBOARD),
        "digest": load_json(COMPANY_DIGEST),
        "observation_tick": load_json(OBSERVATION_TICK),
        "work_candidates": load_json(WORK_CANDIDATES),
        "bridge": load_json(TOOL_BRIDGE_SUMMARY),
        "readonly_tool": load_json(READONLY_TOOL_SUMMARY),
        "triage": load_json(LEGACY_TRIAGE_SUMMARY),
        "console": load_json(CONSOLE_SNAPSHOT),
    }

    mission_context = build_mission_context(inputs)
    observation_input = build_observation_input(inputs)
    proposals = build_work_proposals()
    selected = build_selected_proposal(proposals)
    role_review = build_role_review_board(selected)
    tool_need = build_tool_need_analysis(selected)
    request = build_generated_tool_request(inputs["mission"])

    write_json(GENERATED / OUTPUTS["mission_context_snapshot"], mission_context)
    write_json(GENERATED / OUTPUTS["agent_team_observation_input"], observation_input)
    write_json(GENERATED / OUTPUTS["autonomous_work_proposals"], proposals)
    write_json(GENERATED / OUTPUTS["selected_agent_work_proposal"], selected)
    write_json(GENERATED / OUTPUTS["role_review_board"], role_review)
    write_json(GENERATED / OUTPUTS["tool_need_analysis"], tool_need)
    write_json(GENERATED / OUTPUTS["generated_tool_request"], request)

    runner_payloads = runner.run_proposal_to_bridge(request, GENERATED)
    summary = build_summary(runner_payloads)
    write_json(GENERATED / OUTPUTS["agent_team_work_proposal_summary"], summary)
    (GENERATED / "agent_team_work_proposal_report.md").write_text(
        render_report(mission_context, proposals, selected, role_review, tool_need, request, runner_payloads, summary),
        encoding="utf-8",
    )

    print("Agent team work proposal artifacts generated.")
    print(f"proposal_count: {proposals['proposal_count']}")
    print(f"selected_proposal_id: {selected['selected_proposal_id']}")
    print(f"work_proposal_routed_to_bridge: {summary['work_proposal_routed_to_bridge']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
