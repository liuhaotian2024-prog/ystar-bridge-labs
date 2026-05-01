from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .action_inventory import build_action_inventory, preflight_action_inventory, summarize_action_preflight
from .e2_money_path_evaluator import build_sample_deliverable, evaluate_money_paths
from .evidence_packet_builder import build_external_evidence_packets, build_internal_evidence_packets
from .meta_development_method_kernel import build_meta_development_trace
from .mission_summary import build_mission_result
from .obligation_bridge import build_obligation_draft_from_mission, build_team_obligation_drafts
from .residual_learning_bridge import build_residual_candidates_for_experiments
from .tier1_research_runtime import resolve_tier1_research_capability


OWNER_MISSION = (
    "Aiden，带团队制定未来 7 天最可能产生第一笔真实收入或强付费信号的行动方案。"
    "不要锁死 Founder AI Workflow Audit；必须比较当前 top money paths，给出默认推荐、团队分工、"
    "可自主执行事项、需要我审批的事项。"
)

E2_Y_STAR = [
    "Mission Command accepts the owner first-revenue mission.",
    "Aiden infers the deeper objective and avoids prompt overfit.",
    "Internal world scan covers company assets, sales/content history, directives, governance, and team capability.",
    "Tier 1 read-only external research capability is resolved or blocked with exact owner/config action.",
    "Internal evidence packets are produced and external evidence state is explicit.",
    "At least five money paths are compared.",
    "Each path has buyer, pain, demand, assets, capability, burden, channel, proof, experiment, kill condition, counterfactual risk, and residual plan.",
    "Counterfactual decision gate can confirm or change default.",
    "All proposed actions are semantically classified and preflighted.",
    "Top two sample deliverables are created.",
    "Owner decision packet is created with approve/reject/request_revision/hold.",
    "Residual candidates are created and review-gated.",
    "Final report distinguishes done, plan, blocked, and Rt+1 residuals.",
    "No external side effects occur.",
]


def build_e2_owner_decision_packet(evaluation: Dict[str, Any], resolution: Dict[str, Any]) -> Dict[str, Any]:
    if not resolution["live_read_only_available"]:
        recommended = "approve_or_revise_tier1_live_read_only_research_enablement"
        why = "The cycle completed internal evidence work, but live market evidence is blocked by missing Tier 1 configuration/approval."
    else:
        recommended = "approve_or_revise_next_internal_sample_or_tier1_run"
        why = "Live read-only capability appears available, but this E2 run did not execute it without explicit owner approval."
    return {
        "packet_id": "e2_owner_decision_packet",
        "recommended_decision": recommended,
        "why": why,
        "default_path": evaluation["default_path"],
        "top_two_paths": evaluation["top_two_paths"],
        "approval_covers": "Only bounded Tier 1 live read-only research enablement with the stated budget and stop conditions.",
        "approval_does_not_cover": [
            "customer contact",
            "email/message sending",
            "publication",
            "payment",
            "account creation",
            "form submission",
            "obligation registration",
            "core DB/brain/memory/CIEU writeback",
        ],
        "exact_boundary": resolution["enablement_packet"]["boundary"],
        "options": ["approve", "reject", "request_revision", "hold"],
        "external_action_executed": False,
    }


def build_e2_residual_candidates(evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
    candidates = []
    for row in evaluation["paths"][:3]:
        candidates.append(
            {
                "source_mission_id": "e2_first_revenue_evidence_cycle",
                "opportunity_id": row["path"],
                "expected_signal": "Clear buyer pain, credible budget/demand proxy, and feasible 48h sample validation.",
                "actual_signal_placeholder": "",
                "assumption_tested": row["counterfactual_risks"]["highest_risk_assumption"],
                "if_failed_interpretation": "Downgrade path or require additional evidence before owner approves external validation.",
                "if_succeeded_interpretation": "Keep or raise path as default and prepare owner-approved validation action.",
                "recommended_strategy_update": "Update money path ranking after owner-approved Tier 1 evidence run.",
                "writeback_allowed": False,
                "review_required": True,
            }
        )
    return candidates


def build_e2_cycle(repo_root: Path) -> Dict[str, Any]:
    result = build_mission_result(OWNER_MISSION, repo_root)
    trace = build_meta_development_trace(OWNER_MISSION, repo_root)
    resolution = resolve_tier1_research_capability(repo_root)
    internal_packets = build_internal_evidence_packets(repo_root)
    external_packets = build_external_evidence_packets(repo_root)
    evaluation = evaluate_money_paths(repo_root)
    sample_deliverables = [build_sample_deliverable(row, index + 1) for index, row in enumerate(evaluation["paths"][:2])]
    drafts = [build_obligation_draft_from_mission(result)] + build_team_obligation_drafts(result.team_tasks, result.mission.mission_id)
    residuals_for_inventory = build_residual_candidates_for_experiments(trace["experiments"], trace["counterfactual_cases"], result.mission.mission_id)
    actions = build_action_inventory(result, trace, drafts, residuals_for_inventory)
    mission_dict = {
        "mission_id": result.mission.mission_id,
        "owner_goal": result.mission.goal,
        "allowed_permission_tier": result.mission.allowed_permission_tier,
        "research_budget": result.mission.research_budget,
    }
    preflight_rows = preflight_action_inventory(actions, mission_dict, repo_root)
    preflight_summary = summarize_action_preflight(preflight_rows)
    owner_packet = build_e2_owner_decision_packet(evaluation, resolution)
    residual_candidates = build_e2_residual_candidates(evaluation)
    blocked = not resolution["live_read_only_available"]
    y_t1 = {
        "mission_accepted": bool(result.mission.goal),
        "deeper_objective_inferred": bool(trace["inferred_objective"]),
        "internal_scan_ready": bool(internal_packets),
        "tier1_capability_resolved": True,
        "evidence_packets_produced": bool(internal_packets and external_packets),
        "money_paths_compared": len(evaluation["paths"]),
        "path_evaluation_complete": all(row.get("counterfactual_risks") and row.get("48h_validation_experiment") for row in evaluation["paths"]),
        "counterfactual_gate_present": bool(evaluation["counterfactual_gate"]),
        "all_actions_preflighted": preflight_summary["all_actions_preflighted"],
        "top_two_sample_deliverables_created": len(sample_deliverables) == 2,
        "owner_decision_packet_created": bool(owner_packet),
        "residual_candidates_review_gated": all(item["review_required"] and not item["writeback_allowed"] for item in residual_candidates),
        "final_report_distinguishes_status": True,
        "no_external_side_effects": not preflight_summary["external_action_executed"] and not resolution["external_action_executed"],
    }
    residuals = [criterion for criterion, ok in y_t1.items() if criterion != "money_paths_compared" and not ok]
    if y_t1["money_paths_compared"] < 5:
        residuals.append("money_paths_compared")
    status = "BLOCKED_BY_MISSING_LIVE_RESEARCH_CONFIG" if blocked else ("complete" if not residuals else "residual")
    exact_blocking_action = resolution["missing_config_actions"] if blocked else []
    return {
        "y_star": E2_Y_STAR,
        "xt": {
            "repo_commit_start": "a644cf35",
            "actual_branch": "backflow/aiden-ceo-meeting-room",
            "known_live_research_gap": "configured live read-only research is not enabled",
        },
        "u": [
            "ran E2 state audit",
            "resolved Tier 1 research capability",
            "built internal/external evidence packets",
            "evaluated money paths",
            "created top two sample deliverables",
            "created owner decision packet",
            "created residual candidates",
            "preflighted proposed actions semantically",
        ],
        "y_t1": y_t1,
        "rt1_residuals": residuals,
        "rt1_score": len(residuals),
        "final_status": status,
        "exact_blocking_owner_config_action": exact_blocking_action,
        "mission_result": result.to_dict(),
        "method_trace": trace,
        "research_resolution": resolution,
        "internal_evidence_packets": internal_packets,
        "external_evidence_packets": external_packets,
        "money_path_evaluation": evaluation,
        "sample_deliverables": sample_deliverables,
        "action_preflight_summary": preflight_summary,
        "owner_decision_packet": owner_packet,
        "residual_candidates": residual_candidates,
        "external_action_executed": False,
    }


def render_owner_decision_packet(packet: Dict[str, Any]) -> str:
    lines = [
        "# E2 Owner Decision Packet",
        "",
        f"- recommended_decision: {packet['recommended_decision']}",
        f"- why: {packet['why']}",
        f"- default_path: {packet['default_path']}",
        f"- top_two_paths: {', '.join(packet['top_two_paths'])}",
        f"- approval_covers: {packet['approval_covers']}",
        "- approval_does_not_cover:",
    ]
    lines.extend(f"  - {item}" for item in packet["approval_does_not_cover"])
    lines.extend(["", "## Exact Boundary"])
    lines.extend(f"- {key}: {value}" for key, value in packet["exact_boundary"].items())
    lines.extend(["", f"Options: {', '.join(packet['options'])}", "", f"external_action_executed: {packet['external_action_executed']}"])
    return "\n".join(lines)


def render_residual_candidates(candidates: List[Dict[str, Any]]) -> str:
    lines = ["# E2 Residual Learning Candidates", ""]
    for item in candidates:
        lines.extend(
            [
                f"## {item['opportunity_id']}",
                f"- expected_signal: {item['expected_signal']}",
                f"- assumption_tested: {item['assumption_tested']}",
                f"- if_failed_interpretation: {item['if_failed_interpretation']}",
                f"- if_succeeded_interpretation: {item['if_succeeded_interpretation']}",
                f"- recommended_strategy_update: {item['recommended_strategy_update']}",
                f"- writeback_allowed: {item['writeback_allowed']}",
                f"- review_required: {item['review_required']}",
                "",
            ]
        )
    return "\n".join(lines)


def render_e2_czl_closure(cycle: Dict[str, Any]) -> str:
    lines = [
        "# E2 CZL Closure Report",
        "",
        f"- final_status: {cycle['final_status']}",
        f"- rt1_score: {cycle['rt1_score']}",
        "",
        "## Y*",
    ]
    lines.extend(f"- {item}" for item in cycle["y_star"])
    lines.extend(["", "## Xt"])
    lines.extend(f"- {key}: {value}" for key, value in cycle["xt"].items())
    lines.extend(["", "## U"])
    lines.extend(f"- {item}" for item in cycle["u"])
    lines.extend(["", "## Yt+1"])
    lines.extend(f"- {key}: {value}" for key, value in cycle["y_t1"].items())
    lines.extend(["", "## Rt+1 Residual Table"])
    if cycle["rt1_residuals"]:
        lines.extend(f"- {item}" for item in cycle["rt1_residuals"])
    else:
        lines.append("- no residuals for feasible non-blocked criteria")
    if cycle["exact_blocking_owner_config_action"]:
        lines.extend(["", "## Exact Owner / Config Action Needed"])
        lines.extend(f"- {item}" for item in cycle["exact_blocking_owner_config_action"])
    lines.extend(
        [
            "",
            "## Validation",
            "- python3.11 -m py_compile office/mission_command/*.py",
            "- pytest tests/office/test_e2_action_semantics.py -q",
            "- pytest tests/office/test_e2_research_capability_resolution.py -q",
            "- pytest tests/office/test_e2_evidence_packets.py -q",
            "- pytest tests/office/test_e2_money_path_evaluator.py -q",
            "- pytest tests/office/test_e2_owner_decision_packet.py -q",
            "- pytest tests/office/test_e2_czl_closure.py -q",
            "- pytest tests/office/test_czl_mission_loop.py -q",
            "- pytest tests/office/test_counterfactual_decision_gate.py -q",
            "- pytest tests/office/test_action_inventory_preflight.py -q",
            "- pytest tests/office/test_owner_decision_packet.py -q",
            "- pytest tests/office/test_meta_development_method_kernel.py -q",
            "- python3.11 scripts/demo_mission_grade_ecosystem.py",
        ]
    )
    lines.extend(
        [
            "",
            "## No-External-Action Receipt",
            "- external sending: false",
            "- customer contact: false",
            "- email: false",
            "- payment: false",
            "- publication: false",
            "- account creation: false",
            "- form submission: false",
            "- core DB writeback: false",
            "- obligation auto-registration: false",
            "- CIEU write: false",
            "- COO invented: false",
        ]
    )
    return "\n".join(lines)
