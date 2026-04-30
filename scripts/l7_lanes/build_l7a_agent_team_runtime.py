#!/usr/bin/env python3
"""Build L7A agent team runtime scaffold artifacts."""

from __future__ import annotations

from common import base_no_action_receipt, lane_summary, simple_md, write_json, write_text


LANE_ID = "L7A"
LANE_NAME = "Agent Team Runtime"
OUTPUT_DIR = "l7_agent_team_runtime"

AGENTS = [
    {
        "role_id": "CEO",
        "mission": "Set owner-facing priorities, delegate lane work, and preserve decision boundaries.",
        "responsibilities": ["prioritize commercial work", "delegate to lanes", "escalate risks"],
        "allowed_actions": ["internal planning", "work order delegation", "review packet synthesis"],
        "revenue_contribution_role": "turn evidence and opportunity packets into owner decisions",
        "reporting_target": "Owner",
    },
    {
        "role_id": "Researcher",
        "mission": "Turn approved questions into controlled evidence and source-quality context.",
        "responsibilities": ["evidence planning", "source triage", "claim boundary support"],
        "allowed_actions": ["read-only observation proposals", "evidence packet review"],
        "revenue_contribution_role": "reduce uncertainty around commercial opportunities",
        "reporting_target": "CEO",
    },
    {
        "role_id": "Operator/COO",
        "mission": "Convert approved plans into safe operating steps and handoff packets.",
        "responsibilities": ["execution planning", "process design", "risk sequencing"],
        "allowed_actions": ["internal runbooks", "draft-only action packets"],
        "revenue_contribution_role": "make commercial work operationally executable after approval",
        "reporting_target": "CEO",
    },
    {
        "role_id": "Engineer/CTO",
        "mission": "Close tool and capability gaps needed for governed commercial execution.",
        "responsibilities": ["tool gap diagnosis", "adapter design", "runtime safety"],
        "allowed_actions": ["scaffold tools", "write tests", "produce validation receipts"],
        "revenue_contribution_role": "turn commercial needs into safe capability upgrades",
        "reporting_target": "CEO",
    },
    {
        "role_id": "Secretary",
        "mission": "Maintain archive, configuration presence checks, and owner-facing status hygiene.",
        "responsibilities": ["archive packets", "secret presence checks", "status summaries"],
        "allowed_actions": ["repo-local summaries", "presence-only config receipts"],
        "revenue_contribution_role": "keep the commercial operating system legible to the owner",
        "reporting_target": "CEO",
    },
    {
        "role_id": "Auditor",
        "mission": "Review boundaries, receipts, and evidence trace integrity before action.",
        "responsibilities": [
            "external side-effect review",
            "core writeback review",
            "secret handling review",
            "approval gate compliance",
        ],
        "allowed_actions": ["audit packets", "no-action receipts", "blocker reports"],
        "revenue_contribution_role": "prevent commercial acceleration from bypassing governance",
        "reporting_target": "Owner and CEO",
    },
    {
        "role_id": "Revenue Scout",
        "mission": "Find and structure revenue opportunity hypotheses under read-only constraints.",
        "responsibilities": ["opportunity scan", "customer pain hypotheses", "revenue pathway mapping"],
        "allowed_actions": ["offline opportunity packets", "read-only radar proposals"],
        "revenue_contribution_role": "identify the next money-making hypothesis for review",
        "reporting_target": "CEO",
    },
]

FORBIDDEN = [
    "external outreach",
    "publication",
    "payment",
    "account creation",
    "form submission",
    "MCP/live behavior",
    "CIEU DB write",
    "brain/memory writeback",
    "canonical strategy mutation",
    "direct Y* mutation",
]


def agent_profile(agent: dict[str, object]) -> dict[str, object]:
    role_id = str(agent["role_id"])
    return {
        "schema_version": "v0",
        "role_id": role_id,
        "mission": agent["mission"],
        "responsibilities": agent["responsibilities"],
        "allowed_actions": agent["allowed_actions"],
        "forbidden_actions": FORBIDDEN,
        "input_packet_schema": {
            "packet_id": "string",
            "mission_context": "string",
            "evidence_refs": "array",
            "approval_state": "blocked|draft|approved",
        },
        "output_packet_schema": {
            "packet_id": "string",
            "role_id": role_id,
            "summary": "string",
            "evidence_refs": "array",
            "no_action_receipt": "object",
        },
        "reporting_target": agent["reporting_target"],
        "escalation_conditions": [
            "external action requested",
            "secret value exposure risk",
            "core writeback requested",
            "evidence conflict or unsupported claim",
        ],
        "no_side_effect_boundary": True,
        "revenue_contribution_role": agent["revenue_contribution_role"],
    }


def build() -> None:
    artifacts: list[str] = []
    for agent in AGENTS:
        slug = str(agent["role_id"]).lower().replace("/", "_").replace(" ", "_")
        path = f"{OUTPUT_DIR}/agent_role_profiles/{slug}.json"
        write_json(path, agent_profile(agent))
        artifacts.append(path)

    boundaries = {
        "schema_version": "v0",
        "lane_id": LANE_ID,
        "forbidden_actions": FORBIDDEN,
        "auditor_reviews": [
            "external side effects",
            "core writeback attempts",
            "secret handling",
            "evidence trace integrity",
            "approval gate compliance",
        ],
    }
    write_json(f"{OUTPUT_DIR}/agent_responsibility_boundaries/boundary_matrix.json", boundaries)
    artifacts.append(f"{OUTPUT_DIR}/agent_responsibility_boundaries/boundary_matrix.json")

    inbox = {
        "schema_version": "v0",
        "lane_id": LANE_ID,
        "inboxes": [
            {"role_id": agent["role_id"], "path": f"{OUTPUT_DIR}/agent_work_order_inboxes/{agent['role_id'].lower().replace('/', '_').replace(' ', '_')}_inbox.json", "status": "empty_ready"}
            for agent in AGENTS
        ],
    }
    write_json(f"{OUTPUT_DIR}/agent_work_order_inboxes/inbox_index.json", inbox)
    artifacts.append(f"{OUTPUT_DIR}/agent_work_order_inboxes/inbox_index.json")

    handoff = {
        "schema_version": "v0",
        "required_fields": [
            "handoff_id",
            "from_role",
            "to_role",
            "work_order_id",
            "evidence_refs",
            "approval_state",
            "forbidden_actions",
            "no_action_receipt",
        ],
    }
    write_json(f"{OUTPUT_DIR}/agent_handoff_packets/handoff_packet_schema.json", handoff)
    artifacts.append(f"{OUTPUT_DIR}/agent_handoff_packets/handoff_packet_schema.json")

    manifest = {
        "schema_version": "v0",
        "lane_id": LANE_ID,
        "ceo_delegates_to": {
            "Researcher": "evidence/research",
            "Revenue Scout": "opportunity discovery",
            "Operator/COO": "execution planning",
            "Engineer/CTO": "tool/capability gaps",
            "Secretary": "archive/config/secret presence checks",
            "Auditor": "boundary/no-action review",
        },
        "auditor_reviews": boundaries["auditor_reviews"],
    }
    write_json(f"{OUTPUT_DIR}/agent_reporting_lines/team_orchestration_manifest.json", manifest)
    artifacts.append(f"{OUTPUT_DIR}/agent_reporting_lines/team_orchestration_manifest.json")

    status = {
        "schema_version": "v0",
        "lane_id": LANE_ID,
        "agents_created": [agent["role_id"] for agent in AGENTS],
        "status": "ready_for_parallel_lane_assignment",
        "external_actions_blocked": True,
        "core_writebacks_blocked": True,
    }
    write_json(f"{OUTPUT_DIR}/agent_status_snapshots/l7a_agent_team_status.json", status)
    artifacts.append(f"{OUTPUT_DIR}/agent_status_snapshots/l7a_agent_team_status.json")

    receipt = base_no_action_receipt(LANE_ID, LANE_NAME)
    write_json(f"{OUTPUT_DIR}/agent_team_no_action_receipts/no_action_receipt.json", receipt)
    artifacts.append(f"{OUTPUT_DIR}/agent_team_no_action_receipts/no_action_receipt.json")

    summary = lane_summary(
        LANE_ID,
        LANE_NAME,
        OUTPUT_DIR,
        artifacts,
        "assign read-only commercial work orders to role-specific inboxes",
        {"required_agents": [agent["role_id"] for agent in AGENTS], "agent_count": len(AGENTS)},
    )
    write_json(f"{OUTPUT_DIR}/l7a_agent_team_runtime_summary.json", summary)
    write_text(f"{OUTPUT_DIR}/l7a_agent_team_runtime_summary.md", simple_md("L7A Agent Team Runtime", summary))


if __name__ == "__main__":
    build()
