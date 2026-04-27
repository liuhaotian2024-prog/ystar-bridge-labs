#!/usr/bin/env python3
"""Build a mission-bounded autonomous work cycle simulation.

The simulator reads only curated generated summaries. It does not execute
actions, call external systems, persist CIEU, or mutate brain/memory.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "company_autonomous_work_cycle" / "generated"

REQUIRED_ROLES = [
    "Aiden-CEO",
    "Ethan-CTO",
    "Maya-Governance",
    "Ryan-Platform",
    "Samantha-Secretary",
    "Leo-Kernel",
]

MISSION_TEXT = (
    "Build a commercial AI agent self-governed company runtime that can observe "
    "business-relevant resources, understand constraints, select or build tools, "
    "act through governed channels, record outcomes, and improve through curated "
    "CIEU deltas."
)


def load_json(relative_path: str, default: Any | None = None) -> Any:
    path = ROOT / relative_path
    try:
        path.relative_to(ROOT)
    except ValueError as exc:
        raise ValueError(f"refusing path outside repository: {relative_path}") from exc
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(relative_path: str, payload: dict[str, Any]) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def count_by(items: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(field, "unset"))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def build_mission_profile() -> dict[str, Any]:
    return {
        "schema_name": "ystar.company_autonomous_work_cycle.generated.mission_profile",
        "schema_version": "v0",
        "mission_id": "mission-commercial-agent-company-v0",
        "mission_name": "Commercial AI Agent Self-Governed Company Runtime",
        "founder_defined_mission": MISSION_TEXT,
        "mission_constraints": [
            "preserve architecture boundaries",
            "use governed channels for risky actions",
            "keep live execution disabled in this simulator",
            "record learning only through curated CIEU deltas",
        ],
        "mission_priorities": [
            "preserve architecture boundaries",
            "strengthen autonomous observation",
            "strengthen governed action capability",
            "avoid uncontrolled live execution",
            "produce evidence-backed progress",
            "reduce founder step-by-step operational burden",
        ],
        "forbidden_actions": [
            "uncontrolled live execution",
            "external communication without approval",
            "Git push without approval",
            "direct brain writeback",
            "direct memory ingestion",
            "raw runtime artifact ingestion",
            "CIEU DB persistence without boundary enablement",
            "daemon start/stop without approval",
        ],
        "mission_bounded_autonomy": True,
        "step_by_step_human_prompting_required": False,
        "human_sets_mission_agent_team_drives_execution": True,
        "governance_required_for_risky_actions": True,
        "cieu_required_for_learning": True,
    }


def build_observation_snapshot(inputs: dict[str, Any]) -> dict[str, Any]:
    observation_channels = inputs["observation"].get("channels", [])
    resources = inputs["resources"].get("resources", [])
    actions = inputs["actions"].get("actions", [])
    tools = inputs["tools"].get("candidates", [])
    blocked_actions = [
        action["action_id"]
        for action in actions
        if action.get("current_status") in {"blocked", "candidate_disabled"} and action.get("live_enabled") is False
    ]
    return {
        "schema_name": "ystar.company_autonomous_work_cycle.generated.company_observation_snapshot",
        "schema_version": "v0",
        "committed_milestone_chain": [
            "L3.8 live-readiness gate",
            "L3.9 live-boundary harness",
            "L4.0 CIEU runtime event boundary",
            "L4.1 company autonomy inventory",
        ],
        "live_readiness_status": {
            "dry_run_governance_ready": inputs["live_readiness"].get("dry_run_governance_ready"),
            "minimal_live_loop_ready": inputs["live_readiness"].get("minimal_live_loop_ready"),
        },
        "live_boundary_status": {
            "live_boundary_defined": inputs["live_boundary"].get("live_boundary_defined"),
            "live_action_execution_enabled": inputs["live_boundary"].get("live_action_execution_enabled"),
        },
        "cieu_boundary_status": {
            "cieu_runtime_boundary_defined": inputs["cieu_boundary"].get("cieu_runtime_boundary_defined"),
            "persistence_enabled": inputs["cieu_boundary"].get("persistence_enabled"),
        },
        "autonomy_inventory_status": {
            "repo_archaeology_completed": inputs["inventory_summary"].get("repo_archaeology_completed"),
            "governance_only_runtime": inputs["inventory_summary"].get("governance_only_runtime"),
            "size_guard_safe": inputs["size_guard"].get("generated_inventory_safe_for_read_model"),
        },
        "observation_capability_counts": count_by(observation_channels, "current_status"),
        "resource_sensing_count": len(resources),
        "action_capability_counts": count_by(actions, "current_status"),
        "governed_tool_candidate_counts": count_by(tools, "readiness"),
        "key_gaps": [
            "governed read-only observation loop not yet implemented",
            "tool registry candidates are not approved or live-enabled",
            "CIEU persistence remains disabled",
            "external action surfaces remain blocked",
        ],
        "key_blocked_actions": blocked_actions,
        "strongest_near_term_safe_action_surface": "generated read-model observation and mission dashboard simulation",
        "live_external_observation_performed": False,
        "network_used": False,
    }


def build_backlog() -> dict[str, Any]:
    items = [
        (
            "work-001",
            "Create governed read-only mission dashboard from generated read-models",
            "Aiden-CEO",
            "Ethan-CTO",
            ["Samantha-Secretary", "Ryan-Platform", "Maya-Governance"],
            "low",
            96,
        ),
        (
            "work-002",
            "Define autonomous observation loop from generated company summaries",
            "Aiden-CEO",
            "Ryan-Platform",
            ["Ethan-CTO", "Maya-Governance"],
            "medium",
            91,
        ),
        (
            "work-003",
            "Wrap compact inventory into a governed read-only tool contract",
            "Ethan-CTO",
            "Ryan-Platform",
            ["Maya-Governance", "Leo-Kernel"],
            "medium",
            88,
        ),
        (
            "work-004",
            "Create tool registry wrapper contract for disabled action candidates",
            "Maya-Governance",
            "Leo-Kernel",
            ["Ryan-Platform", "Ethan-CTO"],
            "medium",
            84,
        ),
        (
            "work-005",
            "Prepare controlled real business task candidate without enabling execution",
            "Aiden-CEO",
            "Samantha-Secretary",
            ["Maya-Governance"],
            "medium",
            76,
        ),
        (
            "work-006",
            "Simulate first company task lifecycle through Pre-U and CIEU fixture",
            "Aiden-CEO",
            "Ethan-CTO",
            ["Leo-Kernel", "Maya-Governance"],
            "low",
            82,
        ),
    ]
    work_items = []
    for work_id, title, proposer, owner, support, risk, score in items:
        work_items.append(
            {
                "work_item_id": work_id,
                "title": title,
                "description": f"Mission-bounded simulator work item: {title}.",
                "mission_relevance": "advances self-directed company operation without live execution",
                "proposing_agent": proposer,
                "recommended_owner_agent": owner,
                "supporting_agents": support,
                "risk_tier": risk,
                "requires_y_star_gov": risk != "low",
                "requires_operator_approval": risk != "low",
                "requires_cieu_event": True,
                "requires_live_action": False,
                "live_enabled": False,
                "expected_outcome": "a safer next dry-run autonomy capability",
                "selection_score": score,
                "selection_reason": "prioritizes mission progress while keeping all live/external/writeback behavior disabled",
            }
        )
    return {
        "schema_name": "ystar.company_autonomous_work_cycle.generated.autonomous_work_backlog",
        "schema_version": "v0",
        "work_items": work_items,
    }


def build_selected_work_item(backlog: dict[str, Any]) -> dict[str, Any]:
    selected = sorted(backlog["work_items"], key=lambda item: (-item["selection_score"], item["work_item_id"]))[0]
    return {
        "schema_name": "ystar.company_autonomous_work_cycle.generated.selected_work_item",
        "schema_version": "v0",
        "selected_work_item": selected,
        "selection_method": "highest deterministic mission relevance score with live action disabled",
        "rejected_high_risk_actions": [
            "Git push",
            "daemon control",
            "external communication",
            "brain writeback",
            "memory ingestion",
            "CIEU persistence",
        ],
    }


def build_role_delegation(selected: dict[str, Any]) -> dict[str, Any]:
    work_id = selected["selected_work_item"]["work_item_id"]
    responsibilities = {
        "Aiden-CEO": "Own mission framing and priority selection for the simulated work cycle.",
        "Ethan-CTO": "Assess technical feasibility of generated read-model dashboard surfaces.",
        "Maya-Governance": "Review boundaries and ensure no live/external/writeback path is enabled.",
        "Ryan-Platform": "Map disabled governed tool candidates to future read-only wrappers.",
        "Samantha-Secretary": "Prepare continuity summary and report/read-model handoff shape.",
        "Leo-Kernel": "Review runtime and kernel integrity implications of the simulated loop.",
    }
    delegations = []
    for agent_id in REQUIRED_ROLES:
        delegations.append(
            {
                "agent_id": agent_id,
                "assigned_responsibility": responsibilities[agent_id],
                "input_refs": [
                    "company_autonomy_inventory/generated/company_autonomy_readiness_summary.json",
                    "company_autonomous_work_cycle/generated/selected_work_item.json",
                ],
                "expected_output": "dry-run analysis contribution only",
                "forbidden_actions": [
                    "real action execution",
                    "external communication",
                    "CIEU persistence",
                    "brain writeback",
                    "memory ingestion",
                ],
                "governance_notes": "role responsibility is simulated and requires future governance before live execution",
            }
        )
    return {
        "schema_name": "ystar.company_autonomous_work_cycle.generated.role_delegation_plan",
        "schema_version": "v0",
        "work_item_id": work_id,
        "delegations": delegations,
    }


def build_tool_selection(inputs: dict[str, Any]) -> dict[str, Any]:
    candidates = inputs["tools"].get("candidates", [])
    preferred = {"console-read-model-tools", "repo-scan-tools", "docs-report-tools", "local-validation-tools"}
    selected = [
        {
            "tool_id": candidate["tool_id"],
            "tool_name": candidate["tool_name"],
            "readiness": candidate["readiness"],
            "live_enabled": candidate["live_enabled"],
        }
        for candidate in candidates
        if candidate.get("tool_id") in preferred
    ]
    rejected = [
        {
            "tool_id": candidate["tool_id"],
            "reason": "not selected for this low-risk read-only simulator cycle",
        }
        for candidate in candidates
        if candidate.get("tool_id") not in preferred
    ]
    return {
        "schema_name": "ystar.company_autonomous_work_cycle.generated.governed_tool_selection",
        "schema_version": "v0",
        "selection_id": "tool-selection-mission-dashboard-v0",
        "selected_tool_candidates": selected,
        "rejected_tool_candidates": rejected,
        "selection_reason": "selected read-only generated/read-model and validation candidates only",
        "risk_tier": "low",
        "requires_y_star_gov": False,
        "requires_operator_approval": False,
        "requires_cieu_event": True,
        "live_enabled": False,
        "external_action_enabled": False,
        "notes": "no real tool invocation is performed",
    }


def build_pre_u_simulation(selected: dict[str, Any]) -> dict[str, Any]:
    work = selected["selected_work_item"]
    return {
        "schema_name": "ystar.company_autonomous_work_cycle.generated.pre_u_packet_simulation",
        "schema_version": "v0",
        "packet_id": "pre-u-sim-company-cycle-001",
        "agent_id": work["recommended_owner_agent"],
        "work_item_id": work["work_item_id"],
        "Xt": "Dry-run company autonomy stack has generated inventory, boundaries, and read-model summaries.",
        "Y_star": "Mission-bounded autonomous observation loop advances without live execution.",
        "candidate_U": [
            {
                "candidate_u_id": "U1",
                "summary": "Generate a read-only mission dashboard design from generated summaries.",
                "simulated_only": True,
                "live_enabled": False,
            },
            {
                "candidate_u_id": "U2",
                "summary": "Create a governed tool wrapper contract without enabling invocation.",
                "simulated_only": True,
                "live_enabled": False,
            },
            {
                "candidate_u_id": "U3",
                "summary": "Defer all work until live boundary gates are implemented.",
                "simulated_only": True,
                "live_enabled": False,
            },
        ],
        "predicted_Y_t1": "A concrete next read-only observation-loop milestone is selected.",
        "predicted_R_t1": "Residual risk remains around future live enablement and tool wrapper approval.",
        "selected_U": "U1",
        "why_min_residual": "U1 improves autonomous company motion while keeping all live and external effects disabled.",
        "risk_tier": "low",
        "governance_expectations": [
            "simulation only",
            "no external action",
            "no CIEU persistence",
            "no brain or memory writeback",
        ],
        "cieu_link_policy": "dry_run_fixture_only",
    }


def build_governance_decision(pre_u: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.company_autonomous_work_cycle.generated.governance_decision_simulation",
        "schema_version": "v0",
        "decision_id": "gov-sim-company-cycle-001",
        "packet_id": pre_u["packet_id"],
        "decision": "allow_simulation",
        "decision_reason": "all selected actions are simulated or read-only generated-output actions with live effects disabled",
        "allowed_only_as_simulation": True,
        "live_action_allowed": False,
        "external_action_allowed": False,
        "cieu_persistence_allowed": False,
        "brain_writeback_allowed": False,
        "memory_ingestion_allowed": False,
        "operator_approval_required_for_live": True,
        "notes": "not a Y-star-gov live decision and not hook enforcement",
    }


def build_action_plan(selected: dict[str, Any], pre_u: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.company_autonomous_work_cycle.generated.simulated_action_plan",
        "schema_version": "v0",
        "action_plan_id": "sim-action-company-cycle-001",
        "selected_work_item_id": selected["selected_work_item"]["work_item_id"],
        "selected_U": pre_u["selected_U"],
        "simulated_steps": [
            "Read generated console and autonomy summaries.",
            "Sketch mission dashboard sections.",
            "Route role responsibilities for future implementation.",
            "Record dry-run CIEU event fixture.",
        ],
        "real_execution_performed": False,
        "files_would_create_or_update": [
            "future/company_mission_dashboard.md",
            "future/governed_read_only_observation_loop.json",
        ],
        "external_effects": [],
        "rollback_policy_ref": "labs_live_boundary/rollback_policy.md",
        "risk_tier": "low",
        "notes": "no file modifications are performed beyond this L4.2 generated simulator pack",
    }


def build_simulated_cieu_event(pre_u: dict[str, Any], decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.company_autonomous_work_cycle.generated.simulated_cieu_event",
        "schema_version": "v0",
        "event_id": "cieu-sim-company-cycle-001",
        "dry_run_only": True,
        "persistence_enabled": False,
        "Xt": pre_u["Xt"],
        "U": pre_u["selected_U"],
        "Y_star": pre_u["Y_star"],
        "predicted_Y_t1": pre_u["predicted_Y_t1"],
        "predicted_R_t1": pre_u["predicted_R_t1"],
        "actual_Y_t1": "Simulator generated a selected work item, role plan, tool selection, and next task recommendation.",
        "actual_R_t1": "No live execution occurred; future work remains gated.",
        "residual_delta": "residual_reduced_for_planning_only",
        "evidence_refs": [
            "company_autonomy_inventory/generated/company_autonomy_readiness_summary.json",
            "company_autonomous_work_cycle/generated/governance_decision_simulation.json",
        ],
        "governance_decision_ref": decision["decision_id"],
        "write_policy": "dry_run_no_persistence",
        "learning_eligibility": False,
        "curation_required": True,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
        "raw_artifact_ingestion_allowed": False,
    }


def build_residual_delta(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.company_autonomous_work_cycle.generated.residual_delta_simulation",
        "schema_version": "v0",
        "delta_id": "residual-delta-company-cycle-001",
        "event_id": event["event_id"],
        "predicted_vs_actual_summary": "Predicted planning progress occurred as a simulator artifact only.",
        "residual_delta": event["residual_delta"],
        "learning_eligibility": False,
        "curation_required": True,
        "direct_brain_writeback_allowed": False,
        "direct_memory_ingestion_allowed": False,
        "next_review_required": True,
        "notes": "requires future human or validator review before any learning use",
    }


def build_next_tasks() -> dict[str, Any]:
    tasks = [
        (
            "next-001",
            "L4.3 Governed Read-Only Observation Loop v0",
            "Ryan-Platform",
            "medium",
            ["company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json"],
            True,
            True,
            True,
            "turn the simulator observation step into a governed read-only loop",
        ),
        (
            "next-002",
            "Mission dashboard read-model contract",
            "Samantha-Secretary",
            "low",
            ["company_autonomous_work_cycle/generated/selected_work_item.json"],
            False,
            False,
            True,
            "make mission progress legible without live execution",
        ),
        (
            "next-003",
            "Governed tool wrapper input-output contract pack",
            "Ethan-CTO",
            "medium",
            ["company_autonomy_inventory/generated/governed_tool_registry_candidates.json"],
            True,
            True,
            True,
            "prepare disabled candidates for future approval gates",
        ),
    ]
    return {
        "schema_name": "ystar.company_autonomous_work_cycle.generated.next_task_recommendations",
        "schema_version": "v0",
        "recommendations": [
            {
                "next_task_id": task_id,
                "title": title,
                "recommended_owner_agent": owner,
                "risk_tier": risk,
                "depends_on": depends_on,
                "requires_y_star_gov": ystar,
                "requires_operator_approval": approval,
                "requires_cieu_event": cieu,
                "live_enabled": False,
                "rationale": rationale,
            }
            for task_id, title, owner, risk, depends_on, ystar, approval, cieu, rationale in tasks
        ],
    }


def build_summary() -> dict[str, Any]:
    return {
        "schema_name": "ystar.company_autonomous_work_cycle.generated.autonomous_work_cycle_summary",
        "schema_version": "v0",
        "autonomous_work_cycle_defined": True,
        "mission_bounded_autonomy_defined": True,
        "founder_sets_mission_agent_team_drives": True,
        "step_by_step_human_prompting_required": False,
        "observation_snapshot_defined": True,
        "autonomous_work_backlog_defined": True,
        "selected_work_item_defined": True,
        "role_delegation_defined": True,
        "governed_tool_selection_defined": True,
        "pre_u_packet_simulated": True,
        "governance_decision_simulated": True,
        "action_plan_simulated": True,
        "cieu_event_simulated": True,
        "residual_delta_simulated": True,
        "next_task_recommendations_defined": True,
        "real_action_executed": False,
        "external_action_executed": False,
        "live_action_enabled": False,
        "git_push_enabled": False,
        "daemon_control_enabled": False,
        "cieu_persistence_enabled": False,
        "brain_writeback_enabled": False,
        "memory_ingestion_enabled": False,
        "email_or_external_communication_enabled": False,
        "requires_manual_enablement_for_live": True,
        "next_required_milestone": "L4.3 Governed Read-Only Observation Loop v0",
        "generated_report": "company_autonomous_work_cycle/generated/autonomous_work_cycle_report.md",
        "warning": "simulator only; no real action, external effect, CIEU persistence, or writeback occurred",
    }


def render_report(
    mission: dict[str, Any],
    observation: dict[str, Any],
    backlog: dict[str, Any],
    selected: dict[str, Any],
    delegation: dict[str, Any],
    tool_selection: dict[str, Any],
    pre_u: dict[str, Any],
    decision: dict[str, Any],
    action_plan: dict[str, Any],
    event: dict[str, Any],
    delta: dict[str, Any],
    next_tasks: dict[str, Any],
) -> str:
    selected_work = selected["selected_work_item"]
    return "\n".join(
        [
            "# Autonomous Work Cycle Report",
            "",
            f"Mission: {mission['mission_name']}",
            "",
            "## Observation Snapshot",
            "",
            f"- observation counts: {observation['observation_capability_counts']}",
            f"- action counts: {observation['action_capability_counts']}",
            f"- strongest safe surface: {observation['strongest_near_term_safe_action_surface']}",
            "",
            "## Proposed Work",
            "",
            *[f"- {item['work_item_id']}: {item['title']} ({item['selection_score']})" for item in backlog["work_items"]],
            "",
            "## Selected Work Item",
            "",
            f"- {selected_work['work_item_id']}: {selected_work['title']}",
            f"- why: {selected['selection_method']}",
            "",
            "## Role Delegation",
            "",
            *[f"- {item['agent_id']}: {item['assigned_responsibility']}" for item in delegation["delegations"]],
            "",
            "## Governed Tool Selection",
            "",
            *[f"- {item['tool_id']}: live_enabled={item['live_enabled']}" for item in tool_selection["selected_tool_candidates"]],
            "",
            "## Pre-U Simulation",
            "",
            f"- packet: {pre_u['packet_id']}",
            f"- selected_U: {pre_u['selected_U']}",
            f"- why_min_residual: {pre_u['why_min_residual']}",
            "",
            "## Governance Decision Simulation",
            "",
            f"- decision: {decision['decision']}",
            f"- live_action_allowed: {decision['live_action_allowed']}",
            "",
            "## Simulated Action Plan",
            "",
            f"- real_execution_performed: {action_plan['real_execution_performed']}",
            f"- files_would_create_or_update: {', '.join(action_plan['files_would_create_or_update'])}",
            "",
            "## Simulated CIEU Event",
            "",
            f"- event_id: {event['event_id']}",
            f"- persistence_enabled: {event['persistence_enabled']}",
            "",
            "## Residual Delta",
            "",
            f"- residual_delta: {delta['residual_delta']}",
            f"- curation_required: {delta['curation_required']}",
            "",
            "## Next Tasks",
            "",
            *[f"- {item['next_task_id']}: {item['title']}" for item in next_tasks["recommendations"]],
            "",
            "## Remaining Gaps",
            "",
            "- No live execution, CIEU persistence, or writeback is enabled.",
            "- Governed read-only observation loop is still a future implementation.",
            "",
            "No real action was executed because this milestone is a mission-bounded simulator only.",
            "",
        ]
    )


def load_inputs() -> dict[str, Any]:
    return {
        "inventory_summary": load_json("company_autonomy_inventory/generated/company_autonomy_readiness_summary.json", {}),
        "observation": load_json("company_autonomy_inventory/generated/observation_capability_map.json", {"channels": []}),
        "resources": load_json("company_autonomy_inventory/generated/resource_sensing_map.json", {"resources": []}),
        "actions": load_json("company_autonomy_inventory/generated/action_capability_map.json", {"actions": []}),
        "tools": load_json("company_autonomy_inventory/generated/governed_tool_registry_candidates.json", {"candidates": []}),
        "agent_matrix": load_json("company_autonomy_inventory/generated/agent_role_capability_matrix.json", {"agents": []}),
        "size_guard": load_json("company_autonomy_inventory/generated/inventory_size_guard.json", {}),
        "cieu_boundary": load_json("labs_cieu_runtime_boundary/generated/cieu_runtime_boundary_summary.json", {}),
        "sample_cieu_event": load_json("labs_cieu_runtime_boundary/generated/sample_cieu_runtime_event.json", {}),
        "live_boundary": load_json("labs_live_boundary/generated/live_boundary_summary.json", {}),
        "live_readiness": load_json("labs_live_readiness/generated/live_readiness_report.json", {}),
        "labs_acceptance": load_json("labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json", {}),
        "cross_repo_alignment": load_json("cross_repo_alignment/generated/cross_repo_status_manifest.json", {}),
        "console_snapshot": load_json("console_read_model/generated/team_console_snapshot.json", {}),
    }


def main() -> int:
    inputs = load_inputs()
    mission = build_mission_profile()
    observation = build_observation_snapshot(inputs)
    backlog = build_backlog()
    selected = build_selected_work_item(backlog)
    delegation = build_role_delegation(selected)
    tool_selection = build_tool_selection(inputs)
    pre_u = build_pre_u_simulation(selected)
    decision = build_governance_decision(pre_u)
    action_plan = build_action_plan(selected, pre_u)
    event = build_simulated_cieu_event(pre_u, decision)
    delta = build_residual_delta(event)
    next_tasks = build_next_tasks()
    summary = build_summary()
    report = render_report(
        mission,
        observation,
        backlog,
        selected,
        delegation,
        tool_selection,
        pre_u,
        decision,
        action_plan,
        event,
        delta,
        next_tasks,
    )

    GENERATED.mkdir(parents=True, exist_ok=True)
    write_json("company_autonomous_work_cycle/generated/mission_profile.json", mission)
    write_json("company_autonomous_work_cycle/generated/company_observation_snapshot.json", observation)
    write_json("company_autonomous_work_cycle/generated/autonomous_work_backlog.json", backlog)
    write_json("company_autonomous_work_cycle/generated/selected_work_item.json", selected)
    write_json("company_autonomous_work_cycle/generated/role_delegation_plan.json", delegation)
    write_json("company_autonomous_work_cycle/generated/governed_tool_selection.json", tool_selection)
    write_json("company_autonomous_work_cycle/generated/pre_u_packet_simulation.json", pre_u)
    write_json("company_autonomous_work_cycle/generated/governance_decision_simulation.json", decision)
    write_json("company_autonomous_work_cycle/generated/simulated_action_plan.json", action_plan)
    write_json("company_autonomous_work_cycle/generated/simulated_cieu_event.json", event)
    write_json("company_autonomous_work_cycle/generated/residual_delta_simulation.json", delta)
    write_json("company_autonomous_work_cycle/generated/next_task_recommendations.json", next_tasks)
    write_json("company_autonomous_work_cycle/generated/autonomous_work_cycle_summary.json", summary)
    (GENERATED / "autonomous_work_cycle_report.md").write_text(report, encoding="utf-8")

    print("Company Autonomous Work Cycle Simulator: PASS")
    print(f"selected_work_item: {selected['selected_work_item']['work_item_id']}")
    print(f"governance_decision: {decision['decision']}")
    print(f"real_action_executed: {summary['real_action_executed']}")
    print(f"next_required_milestone: {summary['next_required_milestone']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
