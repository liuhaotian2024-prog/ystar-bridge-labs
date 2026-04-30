#!/usr/bin/env python3
"""Build the L7.4 Labs Office legacy team integration layer."""

from __future__ import annotations

import html
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from discover_ystar_bridge_labs_team import DEFAULT_LEGACY_REPO, discover, main as run_discovery  # noqa: E402


CURRENT_REPO = Path(__file__).resolve().parents[2]
LEGACY_REPO = DEFAULT_LEGACY_REPO
OUT = CURRENT_REPO / "l7_labs_office_legacy_integration"
GENERATED_AT = "2026-04-30T00:00:00Z"


POLICY_REFS = {
    "policy_ref": "policy/action_capability_registry.json",
    "revenue_policy_ref": "policy/revenue_action_policy.json",
    "discovery_policy_ref": "policy/discovery_policy.json",
    "approval_state_machine_ref": "policy/approval_state_machine.json",
    "writeback_policy_ref": "policy/writeback_policy.json",
    "secret_scanning_policy_ref": "policy/secret_scanning_policy.json",
}


RESPONSIBILITIES = {
    "haotian_board_founder": ["set direction", "approve Level 3 decisions", "hold company accountable"],
    "aiden_ceo": ["command synthesis", "directive decomposition", "delegation", "Board reporting"],
    "ethan_cto": ["architecture", "engineering coordination", "tests", "technical review"],
    "sofia_cmo": ["content", "growth narrative", "marketing positioning", "case-study drafts"],
    "marco_cfo": ["pricing", "finance", "source-backed numbers", "financial honesty"],
    "zara_cso": ["sales planning", "patents", "commercialization", "lead qualification"],
    "samantha_secretary": ["archive", "indexing", "DNA consistency", "audit consistency"],
    "leo_engineer": ["kernel", "compiler", "contract parsing", "session correctness"],
    "maya_engineer": ["governance", "CIEU", "omission", "Path A/B", "causal systems"],
    "ryan_engineer": ["platform", "hooks", "CLI", "integrations", "QA"],
    "jordan_engineer": ["domains", "templates", "OpenClaw", "policy packs"],
    "jinjin_k9_scout": ["research", "external observation", "cross-model scouting", "cost-efficient collection"],
}


REPORTS_TO = {
    "haotian_board_founder": "none",
    "aiden_ceo": "haotian_board_founder",
    "ethan_cto": "aiden_ceo",
    "sofia_cmo": "aiden_ceo",
    "marco_cfo": "aiden_ceo",
    "zara_cso": "aiden_ceo",
    "samantha_secretary": "aiden_ceo / Board for archive duties",
    "leo_engineer": "ethan_cto",
    "maya_engineer": "ethan_cto",
    "ryan_engineer": "ethan_cto",
    "jordan_engineer": "ethan_cto",
    "jinjin_k9_scout": "aiden_ceo",
}


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


def ensure_legacy_repo() -> dict[str, Any]:
    cloned_now = False
    pull_skipped_to_preserve_read_only_clone = False
    if not (LEGACY_REPO / ".git").exists():
        LEGACY_REPO.parent.mkdir(parents=True, exist_ok=True)
        result = run(["gh", "repo", "clone", "liuhaotian2024-prog/ystar-bridge-labs", str(LEGACY_REPO)], LEGACY_REPO.parent)
        if result.returncode != 0:
            result = run(["git", "clone", "https://github.com/liuhaotian2024-prog/ystar-bridge-labs.git", str(LEGACY_REPO)], LEGACY_REPO.parent)
        cloned_now = result.returncode == 0
    else:
        pull_skipped_to_preserve_read_only_clone = True
    status = run(["git", "status", "--short"], LEGACY_REPO)
    head = run(["git", "rev-parse", "--short", "HEAD"], LEGACY_REPO)
    return {
        "legacy_repo_path": str(LEGACY_REPO),
        "legacy_repo_available": (LEGACY_REPO / ".git").exists(),
        "cloned_now": cloned_now,
        "pull_skipped_to_preserve_read_only_clone": pull_skipped_to_preserve_read_only_clone,
        "legacy_repo_head": head.stdout.strip(),
        "legacy_repo_status_short": [line for line in status.stdout.splitlines() if line.strip()],
        "legacy_repo_modified_by_builder": False,
    }


def packet(packet_type: str) -> dict[str, Any]:
    return {
        "schema_version": "v0",
        "milestone_id": "L7.4",
        "milestone_name": "Y*Bridge Labs Legacy Team Recovery & Office Integration Sprint",
        "packet_type": packet_type,
        "generated_at_utc": GENERATED_AT,
        **POLICY_REFS,
    }


def write_json(relative_path: str, data: Any) -> None:
    path = OUT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(relative_path: str, text: str) -> None:
    path = OUT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def registry_from_discovery(discovery: dict[str, Any]) -> list[dict[str, Any]]:
    registry = []
    for agent in discovery["agents"]:
        agent_id = agent["legacy_agent_id"]
        registry.append(
            {
                "agent_id": agent_id,
                "display_name": agent["display_name"],
                "legacy_role": agent["role"],
                "role_description": agent["evidence_excerpt_short"] if agent["evidence_excerpt_short"] != "not found" else "needs_review",
                "source_evidence": agent["evidence_items"][:5],
                "known_responsibilities": RESPONSIBILITIES.get(agent_id, ["needs_review"]),
                "known_incidents_or_history": known_history(agent_id),
                "brain_profile_refs": agent["brain_profile_refs"],
                "memory_or_dna_refs": agent["dna_memory_refs"],
                "current_status": "integrated_from_legacy_evidence" if agent["safe_to_integrate"] else "needs_review",
                "integration_notes": "Legacy identity preserved; mapped to current runtime capability without renaming.",
                "reports_to": REPORTS_TO.get(agent_id, "needs_review"),
                "delegates_to": delegates_to(agent_id),
                "can_accept_tasks": agent_id != "haotian_board_founder",
                "can_self_work": agent_id != "haotian_board_founder",
                "approval_required_for": [
                    "outreach",
                    "publication",
                    "payment",
                    "account creation",
                    "form submission",
                    "grant/RFP submission",
                    "customer contact",
                    "MCP/live behavior",
                    "actual memory/brain/canonical/CIEU DB writeback",
                ],
            }
        )
    return registry


def delegates_to(agent_id: str) -> list[str]:
    if agent_id == "aiden_ceo":
        return [
            "ethan_cto",
            "sofia_cmo",
            "marco_cfo",
            "zara_cso",
            "samantha_secretary",
            "jinjin_k9_scout",
        ]
    if agent_id == "ethan_cto":
        return ["leo_engineer", "maya_engineer", "ryan_engineer", "jordan_engineer"]
    return []


def known_history(agent_id: str) -> list[str]:
    return {
        "sofia_cmo": ["CASE-001 CMO fabrication incident documented in README and cases."],
        "marco_cfo": ["CASE-002 CFO fabrication incident documented in README and cases."],
        "zara_cso": ["README states three US provisional patents filed under Sales & Patents function."],
        "samantha_secretary": ["Owns DNA_LOG and BOARD_CHARTER_AMENDMENTS per README and secretary definitions."],
        "jinjin_k9_scout": ["Cross-model MiniMax/OpenClaw research scout documented in README and AGENTS."],
        "ethan_cto": ["README states CTO caught and recorded three own mistakes under intent verification."],
    }.get(agent_id, ["unknown_or_needs_review"])


def mapping(registry: list[dict[str, Any]]) -> dict[str, Any]:
    current_map = []
    for row in registry:
        agent_id = row["agent_id"]
        capability = {
            "haotian_board_founder": "Board approval, strategic direction, Level 3 review",
            "aiden_ceo": "CEO command synthesis, delegation, owner cockpit, decision packet routing",
            "ethan_cto": "tooling/capability implementation and technical quality gate",
            "sofia_cmo": "market narrative, content review, proof-language discipline",
            "marco_cfo": "pricing hypotheses, financial claims, source-backed number review",
            "zara_cso": "sales planning, commercialization, patent/customer path analysis",
            "samantha_secretary": "archive/index/DNA consistency and safe office records",
            "leo_engineer": "kernel/compiler/runtime correctness implementation",
            "maya_engineer": "governance/CIEU/omission/conflict and boundary systems",
            "ryan_engineer": "platform/CLI/hooks/integration/QA automation",
            "jordan_engineer": "domain templates, OpenClaw integration, policy packs",
            "jinjin_k9_scout": "read-only scouting, external observation, cost-efficient research",
        }.get(agent_id, "needs_review")
        current_map.append(
            {
                "legacy_agent_id": agent_id,
                "display_name": row["display_name"],
                "legacy_role": row["legacy_role"],
                "current_runtime_capability": capability,
                "identity_preserved": True,
            }
        )
    slots = {
        **packet("new_l7_capability_slots_not_legacy_agents"),
        "slots": [
            {
                "slot_id": "operator_execution_planning",
                "label": "Operator / COO-style execution planning",
                "legacy_identity": None,
                "status": "unfilled_capability_slot_not_legacy_agent",
                "recommended_assignment": "Aiden delegates planning to Ethan/Samantha/Zara depending on task until a real legacy source exists.",
            },
            {
                "slot_id": "revenue_scout",
                "label": "Revenue Scout",
                "legacy_identity": None,
                "status": "capability_slot_not_legacy_agent",
                "recommended_assignment": "Map scouting to Zara CSO and Jinjin K9 Scout, not a new legacy person.",
            },
            {
                "slot_id": "auditor_function",
                "label": "Auditor",
                "legacy_identity": None,
                "status": "governance_function_not_legacy_person",
                "recommended_assignment": "Governance function handled through Maya/Samantha/Aiden review paths.",
            },
        ],
    }
    return {
        **packet("legacy_to_current_runtime_mapping"),
        "mappings": current_map,
        "new_capability_slots": slots["slots"],
    }


def build_office_home(registry: list[dict[str, Any]], mapping_data: dict[str, Any]) -> dict[str, Any]:
    rooms = [f"agent_rooms/{row['agent_id']}_room.md" for row in registry]
    return {
        **packet("labs_office_home"),
        "identity": "Y*Bridge Labs legacy team office grounded in ystar-bridge-labs source evidence",
        "board_founder": "Haotian Liu",
        "ceo": "Aiden Liu",
        "executive_roles": ["Ethan CTO", "Sofia CMO", "Marco CFO", "Zara CSO", "Samantha Secretary"],
        "engineering_team": ["Leo Kernel", "Maya Governance", "Ryan Platform", "Jordan Domains"],
        "research_scout": "Jinjin / K9 Scout",
        "current_ystar_company_runtime_status": "L6/L7 governed observation, money path, approval workflow, and first revenue readiness artifacts exist.",
        "l6_l7_capabilities": [
            "controlled public read-only observation",
            "evidence packets",
            "conflict bounding",
            "human review packet",
            "CEO command brief",
            "offer validation workflow",
            "first revenue readiness lanes",
        ],
        "commercial_path_status": "first revenue readiness prepared; customer contact and payment still blocked until approval",
        "pending_approvals": ["first manual outreach", "recipient selection", "price quote", "payment method"],
        "team_work_queue": "team_work_queue/team_work_queue.md",
        "agent_rooms": rooms,
        "next_one_command_actions": [
            "bash scripts/run_l7_4_labs_office_legacy_integration.sh --mode status",
            "bash scripts/run_l7_4_labs_office_legacy_integration.sh --mode rooms",
        ],
    }


def build_rooms(registry: list[dict[str, Any]]) -> None:
    for row in registry:
        room = {
            **packet("agent_room"),
            "agent_id": row["agent_id"],
            "display_name": row["display_name"],
            "legacy_role": row["legacy_role"],
            "identity_evidence": row["source_evidence"],
            "brain_profile_refs": row["brain_profile_refs"] or ["not found or not safely readable"],
            "dna_memory_refs": row["memory_or_dna_refs"] or ["not found or not safely readable"],
            "current_mapped_responsibilities": row["known_responsibilities"],
            "what_owner_can_ask": owner_prompts(row["agent_id"]),
            "autonomous_work_allowed": [
                "internal analysis",
                "local artifact review",
                "controlled read-only observation if configured",
                "evidence summary",
                "draft-only artifacts",
                "approval request preparation",
                "tool proposal",
                "tests/builders",
                "owner cockpit updates",
            ],
            "requires_owner_approval": row["approval_required_for"],
            "current_inbox": default_inbox(row["agent_id"]),
            "integration_status": row["current_status"],
            "next_suggested_task": next_task(row["agent_id"]),
        }
        write_json(f"agent_rooms/{row['agent_id']}_room.json", room)
        write_md(
            f"agent_rooms/{row['agent_id']}_room.md",
            f"""
# {row['display_name']} Room

**Legacy role:** {row['legacy_role']}

**Evidence:** {row['source_evidence'][0]['excerpt'] if row['source_evidence'] else 'needs review'}

**Brain/profile refs:** {', '.join(room['brain_profile_refs'][:5])}

**Current mapped responsibilities**
{bullets(room['current_mapped_responsibilities'])}

**What you can ask**
{bullets(room['what_owner_can_ask'])}

**Requires owner approval**
{bullets(room['requires_owner_approval'])}

**Current inbox**
{bullets(room['current_inbox'])}

**Next suggested task:** {room['next_suggested_task']}
""",
        )


def owner_prompts(agent_id: str) -> list[str]:
    prompts = {
        "aiden_ceo": ["turn Board direction into tasks", "summarize company status", "decide next safe sprint"],
        "ethan_cto": ["evaluate tool gaps", "design implementation", "review technical claims"],
        "sofia_cmo": ["draft internal narrative", "review market language", "prepare content for approval"],
        "marco_cfo": ["check pricing evidence", "label estimates", "review financial claims"],
        "zara_cso": ["draft sales plan", "review buyer fit", "prepare approved-contact plan"],
        "samantha_secretary": ["find artifacts", "archive summaries", "check DNA consistency"],
        "jinjin_k9_scout": ["run read-only research", "scout public signals", "compare sources"],
    }
    return prompts.get(agent_id, ["accept scoped internal task aligned to legacy role"])


def default_inbox(agent_id: str) -> list[str]:
    if agent_id == "aiden_ceo":
        return ["integrate Labs Office into owner cockpit", "route L7.5 approval preparation"]
    if agent_id == "zara_cso":
        return ["review first outreach approval package", "map buyer fit with no contact"]
    if agent_id == "jinjin_k9_scout":
        return ["prepare read-only scout plan for public buyer signals"]
    if agent_id == "samantha_secretary":
        return ["maintain legacy office registry and room index"]
    return ["review mapped responsibility and identify next safe internal task"]


def next_task(agent_id: str) -> str:
    return {
        "haotian_board_founder": "review whether Labs Office roster matches the original team",
        "aiden_ceo": "delegate L7.5 preparation through original team identities",
        "ethan_cto": "remove or annotate prior invented COO-style assumptions in active L7 artifacts",
        "sofia_cmo": "turn proof pack into internal-review narrative, not publication",
        "marco_cfo": "review price quote policy before any external quote",
        "zara_cso": "prepare approved-contact criteria for first outreach",
        "samantha_secretary": "archive legacy evidence and maintain room index",
        "leo_engineer": "review kernel/runtime capability gaps for office routing",
        "maya_engineer": "review governance boundary for office interactions",
        "ryan_engineer": "wire one-command office status runner",
        "jordan_engineer": "map domain templates to Labs Office rooms",
        "jinjin_k9_scout": "draft read-only target signal observation plan",
    }.get(agent_id, "needs review")


def build_protocol() -> None:
    schemas = {
        "owner_to_agent_message_schema": ["message_id", "target_agent_id", "owner_intent", "scope", "approval_boundary"],
        "team_message_schema": ["message_id", "from_agent_id", "to_agent_ids", "topic", "artifact_refs"],
        "agent_reply_schema": ["message_id", "agent_id", "summary", "evidence_refs", "next_safe_action"],
        "ceo_delegation_schema": ["delegation_id", "from_aiden_ceo", "to_agent_id", "task", "acceptance_criteria"],
        "agent_handoff_schema": ["handoff_id", "from_agent_id", "to_agent_id", "artifact", "risk_boundary"],
        "auditor_review_schema": ["review_id", "review_function", "artifact", "boundary_check", "decision"],
    }
    for name, fields in schemas.items():
        write_json(
            f"interaction_protocol/{name}.json",
            {**packet(name), "fields": fields, "legacy_identity_safe": True},
        )
    write_md(
        "interaction_protocol/interaction_protocol.md",
        """
# Labs Office Interaction Protocol

The owner may talk to one legacy agent or the whole team. Board direction routes to Aiden CEO; Aiden delegates to the original team: Ethan for technical/tooling, Sofia for narrative, Marco for pricing and financial claims, Zara for sales/commercialization, Samantha for archive/DNA consistency, Leo/Maya/Ryan/Jordan for engineering specialties, and Jinjin for read-only scouting.

Auditor is represented as a governance function, not an invented legacy person.
""",
    )


def build_queue(registry: list[dict[str, Any]]) -> None:
    queue = {
        **packet("team_work_queue"),
        "work_items": [
            {"work_id": "office_001", "owner": "samantha_secretary", "task": "maintain legacy team registry"},
            {"work_id": "office_002", "owner": "aiden_ceo", "task": "route next revenue sprint through original team"},
            {"work_id": "office_003", "owner": "zara_cso", "task": "prepare no-contact buyer-fit review"},
            {"work_id": "office_004", "owner": "ethan_cto", "task": "review invented-role drift in active artifacts"},
        ],
    }
    write_json("team_work_queue/team_work_queue.json", queue)
    write_md("team_work_queue/team_work_queue.md", "# Team Work Queue\n\n" + bullets([item["task"] for item in queue["work_items"]]))
    for row in registry:
        write_json(
            f"team_work_queue/agent_inboxes/{row['agent_id']}_inbox.json",
            {**packet("agent_inbox"), "agent_id": row["agent_id"], "items": default_inbox(row["agent_id"])},
        )
    write_json(
        "team_work_queue/delegation_rules.json",
        {
            **packet("delegation_rules"),
            "rules": [
                "Board directs Aiden CEO",
                "Aiden delegates executive work to original legacy roles",
                "Ethan delegates engineering work to Leo/Maya/Ryan/Jordan",
                "Jinjin scouts/researches; factual claims are verified before use",
            ],
        },
    )
    write_json(
        "team_work_queue/safe_self_work_policy.json",
        {
            **packet("safe_self_work_policy"),
            "safe_autonomous_work": [
                "internal analysis",
                "local artifact review",
                "controlled read-only observation if configured",
                "evidence summary",
                "market/revenue opportunity analysis",
                "draft-only artifacts",
                "approval request preparation",
                "tool proposal",
                "tests/builders",
                "owner cockpit updates",
            ],
        },
    )
    write_json(
        "team_work_queue/approval_required_policy.json",
        {
            **packet("approval_required_policy"),
            "approval_required": [
                "outreach",
                "publication",
                "payment",
                "account creation",
                "form submission",
                "grant/RFP submission",
                "customer contact",
                "MCP/live behavior",
                "actual memory/brain/canonical/CIEU DB writeback",
            ],
        },
    )


def build_gap_report(discovery_data: dict[str, Any], registry: list[dict[str, Any]], mapping_data: dict[str, Any]) -> dict[str, Any]:
    report = {
        **packet("integration_gap_report"),
        "legacy_agents_found_but_not_integrated": [],
        "missing_brain_profile_references": [
            row["agent_id"] for row in registry if not row["brain_profile_refs"]
        ],
        "conflicting_role_definitions": [
            "Additional .claude/agents engineering capability definitions exist and need review before being treated as core legacy identities."
        ],
        "new_l7_roles_that_do_not_map_to_legacy_identities": [
            "Operator/COO",
            "Revenue Scout",
            "Auditor as person",
        ],
        "old_team_functions_missing_in_new_architecture": [
            "Sofia CMO narrative ownership",
            "Marco CFO source-backed pricing/finance review",
            "Zara CSO sales/patent/commercialization planning",
            "Jinjin K9 Scout cross-model research",
        ],
        "new_architecture_functions_missing_in_old_team": [
            "approval execution pipeline",
            "controlled observation backend/page-read adapter",
            "first revenue readiness cockpit",
        ],
        "recommended_integration_fixes": [
            "Route revenue work through Zara CSO + Marco CFO + Sofia CMO + Jinjin Scout instead of invented Revenue Scout identity.",
            "Represent Operator/COO as unfilled capability slot unless source evidence appears.",
            "Represent Auditor as governance function handled by Maya/Samantha/Aiden review paths.",
            "Update active L7 artifacts that mention COO as legacy identity.",
        ],
        "previous_mistake_class": "new L7 role assumptions must not override original Y*Bridge Labs team identities",
        "next_sprint_recommendations": [
            "L7.5 Legacy-Team-Grounded First Outreach Approval Preparation",
            "Patch active L7.0P-L7.4 artifacts that hardcode invented roles",
        ],
        "additional_agent_definitions_need_review": discovery_data["additional_agent_definitions"],
        "new_capability_slots": mapping_data["new_capability_slots"],
    }
    write_json("integration_gap_report/integration_gap_report.json", report)
    write_md(
        "integration_gap_report/integration_gap_report.md",
        """
# Integration Gap Report

The previous mistake class is explicit: **new L7 role assumptions must not override original Y*Bridge Labs team identities**.

COO/Operator, Revenue Scout, and Auditor-as-person are not integrated as legacy identities. They remain capability slots or governance functions unless source evidence proves otherwise.
""",
    )
    return report


def write_office_home(home: dict[str, Any], registry: list[dict[str, Any]]) -> None:
    write_json("office_home/labs_office_home.json", home)
    roster = "\n".join(f"- {row['display_name']} — {row['legacy_role']}" for row in registry)
    write_md(
        "office_home/labs_office_home.md",
        f"""
# Y*Bridge Labs Office

This office is grounded in the original `ystar-bridge-labs` repository, not invented L7 role assumptions.

## Team
{roster}

## Current Runtime Status
{home['current_ystar_company_runtime_status']}

## Commercial Path Status
{home['commercial_path_status']}

## Pending Approvals
{bullets(home['pending_approvals'])}

## Next One-Command Actions
{bullets(home['next_one_command_actions'])}
""",
    )
    cards = "\n".join(
        f"<li><a href='../agent_rooms/{row['agent_id']}_room.md'>{html.escape(row['display_name'])}</a> — {html.escape(row['legacy_role'])}</li>"
        for row in registry
    )
    (OUT / "office_home").mkdir(parents=True, exist_ok=True)
    (OUT / "office_home/labs_office_home.html").write_text(
        f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Y*Bridge Labs Office</title></head>
<body>
<h1>Y*Bridge Labs Office</h1>
<p>Legacy-team-grounded office for the real historical Y*Bridge Labs team.</p>
<h2>Team Rooms</h2>
<ul>{cards}</ul>
<h2>Next Command</h2>
<code>bash scripts/run_l7_4_labs_office_legacy_integration.sh --mode status</code>
</body>
</html>
""",
        encoding="utf-8",
    )


def no_action_receipt(repo_status: dict[str, Any]) -> dict[str, Any]:
    return {
        **packet("l7_4_labs_office_no_action_receipt"),
        "ask_user_url_occurred": False,
        "external_side_effects_occurred": False,
        "customer_contacted": False,
        "email_sent": False,
        "form_submitted": False,
        "payment_occurred": False,
        "publication_occurred": False,
        "core_writeback_occurred": False,
        "secret_printed_stored_in_repo": False,
        "ystar_bridge_labs_modified": repo_status["legacy_repo_modified_by_builder"],
        "ystar_bridge_labs_status_short_at_build": repo_status["legacy_repo_status_short"],
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "db_log_wal_shm_active_agent_marker_content_read": False,
    }


def build() -> dict[str, Any]:
    repo_status = ensure_legacy_repo()
    run_discovery()
    discovery_data = discover(LEGACY_REPO)
    registry = registry_from_discovery(discovery_data)
    mapping_data = mapping(registry)
    home = build_office_home(registry, mapping_data)
    build_rooms(registry)
    build_protocol()
    build_queue(registry)
    gap = build_gap_report(discovery_data, registry, mapping_data)
    write_office_home(home, registry)

    write_json("original_team_registry/original_team_registry.json", {**packet("original_team_registry"), "agents": registry})
    write_md(
        "original_team_registry/original_team_registry.md",
        "# Original Team Registry\n\n" + "\n".join(f"- **{r['display_name']}** — {r['legacy_role']}" for r in registry),
    )
    write_json("legacy_to_current_mapping/legacy_to_current_runtime_mapping.json", mapping_data)
    write_md(
        "legacy_to_current_mapping/legacy_to_current_runtime_mapping.md",
        "# Legacy To Current Runtime Mapping\n\n"
        + "\n".join(
            f"- {row['display_name']} → {row['current_runtime_capability']}" for row in mapping_data["mappings"]
        ),
    )
    write_json(
        "legacy_to_current_mapping/new_l7_capability_slots_not_legacy_agents.json",
        {**packet("new_l7_capability_slots_not_legacy_agents"), "slots": mapping_data["new_capability_slots"]},
    )
    receipt = no_action_receipt(repo_status)
    write_json("l7_4_labs_office_no_action_receipt.json", receipt)
    summary = {
        **packet("l7_4_labs_office_summary"),
        "original_repo_available": repo_status["legacy_repo_available"],
        "original_repo_path": repo_status["legacy_repo_path"],
        "original_repo_modified": bool(repo_status["legacy_repo_status_short"]),
        "legacy_agents_discovered": len(registry),
        "original_team_members_integrated": len([row for row in registry if row["current_status"] == "integrated_from_legacy_evidence"]),
        "new_l7_capability_slots_separated_from_legacy_identities": True,
        "coo_invented_as_legacy_member": False,
        "agents_with_brain_profile_refs": len([row for row in registry if row["brain_profile_refs"]]),
        "office_home_path": "l7_labs_office_legacy_integration/office_home/labs_office_home.md",
        "static_html_page_path": "l7_labs_office_legacy_integration/office_home/labs_office_home.html",
        "agent_rooms_generated": len(registry),
        "interaction_protocol_generated": True,
        "work_queue_generated": True,
        "integration_gap_report_path": "l7_labs_office_legacy_integration/integration_gap_report/integration_gap_report.md",
        "next_one_command_action": "bash scripts/run_l7_4_labs_office_legacy_integration.sh --mode status",
        "ask_user_url_occurred": False,
        "external_side_effects_occurred": False,
        "customer_contacted": False,
        "email_sent": False,
        "form_submitted": False,
        "payment_occurred": False,
        "publication_occurred": False,
        "core_writeback_occurred": False,
        "secret_printed_stored_in_repo": False,
        "ystar_bridge_labs_modified": repo_status["legacy_repo_modified_by_builder"],
        "ystar_bridge_labs_status_short_at_build": repo_status["legacy_repo_status_short"],
        "y_star_gov_modified": False,
        "gov_mcp_modified": False,
        "db_log_wal_shm_active_agent_marker_content_read": False,
        "gap_report_highlight": gap["previous_mistake_class"],
    }
    write_json("l7_4_labs_office_summary.json", summary)
    write_md(
        "l7_4_labs_office_summary.md",
        f"""
# L7.4 Labs Office Legacy Integration Summary

**Legacy agents discovered:** {summary['legacy_agents_discovered']}

**Original team members integrated:** {summary['original_team_members_integrated']}

**COO invented as legacy member:** no

**Office home:** `{summary['office_home_path']}`

**Static HTML:** `{summary['static_html_page_path']}`

**Next command:** `{summary['next_one_command_action']}`
""",
    )
    return summary


def main() -> None:
    summary = build()
    print(f"office_home_path: {summary['office_home_path']}")
    print(f"legacy_agents_discovered: {summary['legacy_agents_discovered']}")
    print(f"original_team_members_integrated: {summary['original_team_members_integrated']}")
    print(f"agent_rooms_generated: {summary['agent_rooms_generated']}")
    print(f"next_command: {summary['next_one_command_action']}")


if __name__ == "__main__":
    main()
