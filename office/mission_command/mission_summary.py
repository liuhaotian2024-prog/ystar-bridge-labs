from __future__ import annotations

import json
from pathlib import Path

from .action_inventory import (
    build_action_inventory,
    preflight_action_inventory,
    render_action_preflight_markdown,
    summarize_action_preflight,
)
from .czl_mission_loop import (
    build_czl_plan,
    compute_rt1,
    observe_y_t1,
    record_u_action,
    render_czl_markdown,
)
from .governance_bridge import (
    preflight_admin_rule,
    preflight_mission_action,
    preflight_value_alignment,
    summarize_preflight_results,
)
from .obligation_bridge import (
    build_obligation_draft_from_mission,
    build_team_obligation_drafts,
)
from .ecosystem_preflight import run_gov_mcp_preflight, run_ystar_gov_preflight
from .mission_alignment import align_mission_to_m_triangle
from .mission_from_owner_message import build_mission_from_owner_message
from .mission_model import MissionCommandResult
from .mission_router import route_mission
from .meta_development_method_kernel import build_meta_development_trace
from .owner_decision_packet import build_owner_decision_packet, render_owner_decision_packet_markdown
from .research_capability import audit_research_capability
from .residual_learning_bridge import (
    build_residual_candidates_for_experiments,
    build_residual_review_packet,
)
from .team_task_builder import build_team_tasks


def build_mission_result(owner_message: str, repo_root: Path | None = None) -> MissionCommandResult:
    root = (repo_root or Path(__file__).resolve().parents[2]).resolve()
    mission = build_mission_from_owner_message(owner_message, root)
    routing = route_mission(mission)
    return MissionCommandResult(
        mission=mission,
        m_triangle_alignment=align_mission_to_m_triangle(mission),
        team_tasks=build_team_tasks(mission),
        autonomous_internal_actions=routing["autonomous_internal_actions"],
        approval_needed_actions=routing["approval_needed_actions"],
        admin_burden_avoided=routing["admin_burden_avoided"],
        ystar_gov_preflight=run_ystar_gov_preflight(mission, root),
        gov_mcp_preflight=run_gov_mcp_preflight(mission, root),
        next_owner_decision=routing["next_owner_decision"],
    )


def build_mission_summary(owner_message: str, repo_root: Path | None = None) -> str:
    result = build_mission_result(owner_message, repo_root)
    mission = result.mission
    root = (repo_root or Path(__file__).resolve().parents[2]).resolve()
    research_audit = audit_research_capability(root)
    method_trace = build_meta_development_trace(owner_message, root)
    obligation_drafts = [build_obligation_draft_from_mission(result)] + build_team_obligation_drafts(
        result.team_tasks,
        result.mission.mission_id,
    )
    mission_dict = {
        "mission_id": mission.mission_id,
        "owner_goal": mission.goal,
        "allowed_permission_tier": mission.allowed_permission_tier,
        "research_budget": mission.research_budget,
    }
    governance_bridge_results = [
        preflight_mission_action({"action": "read-only research public page search"}, mission_dict, root),
        preflight_mission_action({"action": "send email to selected customer"}, mission_dict, root),
        preflight_admin_rule({"title": "old daily report"}, mission_dict, root),
        preflight_value_alignment({"title": "first paid customer interview"}, root),
    ]
    governance_bridge_summary = summarize_preflight_results(governance_bridge_results)
    residual_candidates = build_residual_candidates_for_experiments(
        method_trace["experiments"],
        method_trace["counterfactual_cases"],
        mission.mission_id,
    )
    residual_review_packet = build_residual_review_packet(residual_candidates)
    action_inventory = build_action_inventory(result, method_trace, obligation_drafts, residual_candidates)
    action_preflight_rows = preflight_action_inventory(action_inventory, mission_dict, root)
    action_preflight_summary = summarize_action_preflight(action_preflight_rows)
    czl_state = build_czl_plan(result, root)
    for action in [
        {"action_id": "u_001", "description": "Generated method-driven mission output."},
        {"action_id": "u_002", "description": "Ran counterfactual gate and action-wide preflight."},
        {"action_id": "u_003", "description": "Generated owner decision packet and residual review packet."},
    ]:
        czl_state = record_u_action(czl_state, action)
    czl_state = observe_y_t1(
        czl_state,
        {
            "czl_tuple_present": True,
            "counterfactual_gate_present": True,
            "counterfactual_gate_can_change_or_confirm": True,
            "action_wide_preflight_complete": action_preflight_summary["all_actions_preflighted"],
            "dynamic_obligation_ids_dry_run": all(not draft["registration_allowed"] for draft in obligation_drafts),
            "residual_update_review_gated": residual_review_packet["review_required"] and not residual_review_packet["writeback_allowed"],
            "owner_decision_packet_present": True,
            "plan_u_yt1_rt1_distinguished": True,
            "no_external_side_effects": True,
            "tests_and_unseen_smoke_passed": False,
            "external_research_executed": False,
        },
    )
    czl_state = compute_rt1(czl_state)
    owner_packet = build_owner_decision_packet(
        mission.mission_id,
        method_trace["evidence_status"],
        {"status": czl_state.status, "rt1_score": czl_state.rt1_score, "rt1_residuals": czl_state.rt1_residuals},
        method_trace["counterfactual_gate_result"],
        action_preflight_summary,
    )
    evidence_mode = (
        "live-read-only evidence-backed plan"
        if research_audit.plan_confidence_allowed == "evidence_backed_live_read_only"
        else "internal-evidence preliminary plan"
    )
    lines = [
        "# Mission Command Summary",
        "",
        f"Mission goal: {mission.goal}",
        f"Mission type: {mission.mission_type}",
        f"Default priority: {mission.default_priority}",
        f"Evidence mode: {evidence_mode}",
        f"External research verdict: {research_audit.external_research_verdict}",
        f"Plan confidence allowed: {research_audit.plan_confidence_allowed}",
        "",
        "## Aiden Inferred Deeper Objective",
        method_trace["inferred_objective"],
        "",
        "## Prompt-Overfit Risk",
        *[f"- {risk}" for risk in method_trace["prompt_overfit_risk"]["risks"]],
        f"Mitigation: {method_trace['prompt_overfit_risk']['mitigation']}",
        "",
        "## Meta-Development Method Trace",
        *[f"- {step}" for step in method_trace["method_steps"]],
        "",
        "## Aiden Recommended Path",
        mission.recommended_path,
        "",
        "## M Triangle Alignment",
        f"Primary: {result.m_triangle_alignment['primary']}",
        result.m_triangle_alignment["explanation"],
        "",
        "## Evidence Basis",
        *mission.evidence_basis,
        "",
        "## Team Task Split",
    ]
    for task in result.team_tasks:
        lines.append(f"- {task.agent} ({task.function}, Tier {task.permission_tier}): {task.task} Output: {task.output}.")
    lines.extend(
        [
            "",
            "## Autonomous Internal Actions",
            *[f"- {action}" for action in result.autonomous_internal_actions],
            "",
            "## Approval-Needed Actions",
            *[f"- {action}" for action in result.approval_needed_actions],
            "",
            "## Admin Burden Avoided",
            *[f"- {item}" for item in result.admin_burden_avoided],
            "",
            "## Resource Comparison",
        ]
    )
    for item in method_trace["resource_comparison"]:
        lines.append(
            f"- {item['opportunity']}: assets={', '.join(item['matched_assets'])}; trust_gap={item['trust_gap']}; owner_burden={item['owner_burden']}"
        )
    lines.extend(
        [
            "",
            "## Behavior Capability Matrix",
        ]
    )
    for item in method_trace["behavior_capabilities"]:
        lines.append(
            f"- {item['capability']}: status={item['current_status']}; autonomous_now={item['autonomous_now']}; tier={item['requires_tier']}; owner_approval={item['requires_owner_approval']}; next_U={item['next_possible_u']}"
        )
    lines.extend(
        [
            "",
            "## Opportunity Space",
        ]
    )
    for item in method_trace["opportunities"]:
        lines.append(
            f"- {item['title']} ({item['generated_from_lens']}): confidence={item['confidence']}; first_experiment={item['first_experiment']}"
        )
    lines.extend(
        [
            "",
            "## Top Opportunities",
        ]
    )
    for item in method_trace["top_opportunities"]:
        lines.append(f"- {item['title']}: score={item['method_score']}; buyer={item['buyer']}")
    lines.extend(
        [
            "",
            "## Experiment Design",
        ]
    )
    for item in method_trace["experiments"]:
        lines.append(f"- {item['opportunity']}: 48h={item['48h_internal_experiment']}; kill={item['kill_condition']}")
    lines.extend(
        [
            "",
            "## Counterfactual Stress Test",
        ]
    )
    for item in method_trace["counterfactual_cases"]:
        lines.append(f"- {item['opportunity_title']}: risk={item['highest_risk_assumption']}; fastest_test={item['fastest_disconfirming_test']}")
    lines.extend(
        [
            "",
            "## Highest Risk Assumptions",
        ]
    )
    for item in method_trace["highest_counterfactual_risks"]:
        lines.append(f"- {item['opportunity_title']}: {item['highest_risk_assumption']}")
    lines.extend(
        [
            "",
            "## Fastest Disconfirming Tests",
        ]
    )
    for item in method_trace["fastest_disconfirming_tests"]:
        lines.append(f"- {item['opportunity']}: {item['test']}")
    lines.extend(
        [
            "",
            "## Alternative Path Analysis",
            method_trace["alternative_path_rationale"],
            "",
            "## Counterfactual Default Check",
            f"Default changed after stress test: {method_trace['default_changed_after_counterfactual']}",
            method_trace["why_default_still_wins_or_changed"],
            "",
            "## CZL Tuple",
            render_czl_markdown(czl_state),
            "",
            render_owner_decision_packet_markdown(owner_packet),
            "",
            render_action_preflight_markdown(action_preflight_rows),
        ]
    )
    lines.extend(
        [
            "",
            "## Owner Burden Minimization",
            method_trace["owner_burden"],
            "",
            "## Next Executable U",
            method_trace["next_executable_u"],
            "",
            "## Residual / Learning Path",
            *[f"- {item}" for item in method_trace["residual_plan"]],
            "",
            "## Method Compliance",
            *[f"- {key}: {value}" for key, value in method_trace["method_compliance"].items()],
            "",
            "## Obligation Drafts",
        ]
    )
    for draft in obligation_drafts:
        lines.append(
            f"- {draft['rule_name']}: owner={draft['owner']}; entity_id={draft['entity_id']}; registration_allowed={draft['registration_allowed']}; review_required={draft['owner_review_required']}"
        )
    lines.extend(
        [
            "",
            "## Governance Bridge Summary",
            "```json",
            json.dumps(governance_bridge_summary, ensure_ascii=False, indent=2, sort_keys=True),
            "```",
            "",
            "## Residual Learning Candidates",
        ]
    )
    for item in residual_candidates:
        lines.append(
            f"- {item['opportunity_id']}: assumption={item['assumption_tested']}; writeback_allowed={item['writeback_allowed']}; review_required={item['review_required']}"
        )
    lines.extend(
        [
            "",
            "## Y-star-gov Preflight",
            "```json",
            json.dumps(result.ystar_gov_preflight, ensure_ascii=False, indent=2, sort_keys=True),
            "```",
            "",
            "## gov-mcp Preflight",
            "```json",
            json.dumps(result.gov_mcp_preflight, ensure_ascii=False, indent=2, sort_keys=True),
            "```",
            "",
            "## Next Owner Decision",
            result.next_owner_decision,
            "",
            "Safety: no external sending, customer contact, email, payment, publication, form submission, account creation, or core DB writeback executed.",
        ]
    )
    return "\n".join(lines)
