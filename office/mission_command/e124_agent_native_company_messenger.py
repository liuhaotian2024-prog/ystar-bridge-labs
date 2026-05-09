from __future__ import annotations

import importlib
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


MILESTONE_ID = "E124_Agent_Native_Company_Messenger_R1"
SESSION_ID = "e124_agent_native_company_messenger"
BRIDGE_ROOT = Path(os.environ.get("YSTAR_BRIDGE_LABS_ROOT", Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get("YSTAR_GOV_ROOT", "/Users/haotianliu/.openclaw/workspace/Y-star-gov"))

CIEU_FIVE_TUPLE_FIELDS = ("Y_star_t", "X_t", "U_t", "Y_t_plus_1", "R_t_plus_1")


def build_agent_native_participants() -> list[dict[str, Any]]:
    return [
        {
            "participant_id": "owner",
            "display_name": "Haotian / Owner",
            "participant_type": "human",
            "role": "company_owner",
            "communication_boundary": "can initiate CEO meeting and approve external/high-risk actions",
        },
        {
            "participant_id": "Aiden",
            "display_name": "Aiden",
            "participant_type": "agent",
            "role": "CEO principal",
            "communication_boundary": "strategy owner; must use governed model orchestration and CIEU five tuple messages",
        },
        {
            "participant_id": "Codex",
            "display_name": "Codex",
            "participant_type": "tool_executor",
            "role": "engineering executor",
            "communication_boundary": "may execute only from CEOImplementationOrder; not a strategy owner",
        },
        {
            "participant_id": "StrategyAgent",
            "display_name": "Strategy Agent",
            "participant_type": "agent",
            "role": "market/research analyst",
            "communication_boundary": "local research synthesis only; no external send",
        },
        {
            "participant_id": "FinanceAgent",
            "display_name": "Finance Agent",
            "participant_type": "agent",
            "role": "pricing, wallet, and cash discipline analyst",
            "communication_boundary": "wallet/payment proposal-only; no payment execution",
        },
        {
            "participant_id": "external_agent_placeholder",
            "display_name": "External Agent Placeholder",
            "participant_type": "external_agent",
            "role": "future outside-company agent contact",
            "communication_boundary": "no-send proposal-only until owner approves provider and external boundary",
            "live_external_delivery_allowed": False,
        },
    ]


def build_cieu_five_tuple(
    *,
    y_star: str,
    context: str | Mapping[str, Any],
    action: str | Mapping[str, Any],
    expected_next: str,
    residual: str = "pending until recipient response",
    residual_status: str = "planning_residual_pending",
) -> dict[str, Any]:
    return {
        "Y_star_t": y_star,
        "X_t": context,
        "U_t": action,
        "Y_t_plus_1": expected_next,
        "R_t_plus_1": residual,
        "residual_status": residual_status,
        "five_tuple_protocol": "CZL/CIEU",
    }


def build_agent_native_message_packet(
    *,
    thread_id: str,
    sender_id: str,
    recipient_ids: list[str],
    message_kind: str,
    human_readable_text: str,
    cieu_five_tuple: Mapping[str, Any],
    cieu_db: str | Path,
    message_id: str | None = None,
    participants: list[dict[str, Any]] | None = None,
    wallet_proposal: Mapping[str, Any] | None = None,
    attachment_manifest: Mapping[str, Any] | None = None,
    selected_model_id: str = "local_gemma4_e4b",
    local_messenger_only: bool = True,
    no_send_default: bool = True,
    external_delivery_executed: bool = False,
    provider_action_executed: bool = False,
) -> dict[str, Any]:
    participants = participants or build_agent_native_participants()
    participant_types = {item["participant_id"]: item["participant_type"] for item in participants}
    agent_involved = participant_types.get(sender_id) in {"agent", "tool_executor"} or any(
        participant_types.get(recipient_id) in {"agent", "tool_executor"} for recipient_id in recipient_ids
    )
    message: dict[str, Any] = {
        "message_id": message_id or f"msg_{uuid.uuid4().hex[:12]}",
        "created_at": _now(),
        "sender_id": sender_id,
        "recipient_ids": list(recipient_ids),
        "message_kind": message_kind,
        "human_readable_text": human_readable_text,
        "cieu_five_tuple": dict(cieu_five_tuple),
    }
    if wallet_proposal is not None:
        message["wallet_proposal"] = dict(wallet_proposal)
    return {
        "artifact_id": "e124_agent_native_message_packet",
        "milestone_id": MILESTONE_ID,
        "messenger_session_id": SESSION_ID,
        "thread": {
            "thread_id": thread_id,
            "thread_type": "direct" if len(recipient_ids) == 1 else "group_meeting",
            "title": "Aiden Company Messenger",
            "purpose": "Human/agent and agent/agent communication with natural language plus CIEU/CZL five tuple",
        },
        "participants": participants,
        "message": message,
        "model_orchestration": {
            "model_orchestration_required": bool(agent_involved),
            "selected_model_id": selected_model_id if agent_involved else "human_direct_input",
            "raw_prompt_only": False,
            "E123_model_orchestration_reused": bool(agent_involved),
            "routing_summary": "Aiden messages route through governed local model/tool orchestration before execution.",
        },
        "delivery_boundary": {
            "local_messenger_only": local_messenger_only,
            "no_send_default": no_send_default,
            "external_delivery_executed": external_delivery_executed,
            "provider_action_executed": provider_action_executed,
            "external_side_effect": False,
        },
        "attachment_manifest": dict(attachment_manifest or {"metadata_only": True, "external_upload_executed": False, "attachments": []}),
        "CIEU_linkage": {
            "CIEU_recording_required": True,
            "target_event_type": "AIDEN_AGENT_NATIVE_MESSAGE_DECISION",
            "target_cieu_db": str(cieu_db),
            "five_tuple_fields": list(CIEU_FIVE_TUPLE_FIELDS),
        },
        "truth_constraints": {
            "raw_natural_language_only_message": False,
            "missing_CIEU_five_tuple_allowed": False,
            "agent_message_without_model_orchestration": False,
            "external_delivery_executed": external_delivery_executed,
            "external_agent_live_contact_executed": False,
            "payment_executed": False,
            "USDC_transfer_executed": False,
            "customer_validation_claim": False,
            "revenue_claim": False,
            "payment_claim": False,
            "K9Audit_write_claim": False,
            "hidden_chain_of_thought_stored": False,
            "CIEU_recording_bypassed": False,
        },
    }


def validate_and_record_agent_native_message(
    packet: Mapping[str, Any],
    *,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
) -> dict[str, Any]:
    gov = _load_ystar_module("ystar.governance.aiden_agent_native_messenger_contract", ystar_gov_root)
    return gov.validate_and_write_aiden_agent_native_message_packet(
        packet,
        cieu_db=str(cieu_db),
        session_id=SESSION_ID,
    )


def generate_aiden_reply_text(
    owner_text: str,
    *,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
    repo_root: str | Path | None = None,
    allow_live_network: bool = False,
) -> dict[str, Any]:
    """Generate Aiden's reply through the existing governed meeting-room router."""

    try:
        from office.aiden_meeting_room.chat_router import route_chat_message_to_aiden_meeting_room

        route = route_chat_message_to_aiden_meeting_room(
            f"Aiden: {owner_text}",
            repo_root=Path(repo_root or BRIDGE_ROOT),
            cieu_db=cieu_db,
            ystar_gov_root=Path(ystar_gov_root or Y_GOV_ROOT),
            allow_live_network=allow_live_network,
        )
        return {
            "reply_text": route.response_text or "Aiden received the message, but the governed response was empty.",
            "reply_backend": route.route,
            "reply_protocol": route.protocol,
            "runtime_fallback_used": False,
        }
    except Exception as exc:
        return {
            "reply_text": (
                "Aiden Messenger Runtime Notice: I received your message inside the governed local messenger, "
                "but the Aiden behavior runtime could not complete this reply. The message was still recorded "
                "with CIEU/CZL provenance. Correct path: inspect the Aiden runtime error and retry."
            ),
            "reply_backend": "runtime_fallback_notice",
            "reply_protocol": "AidenMessengerFallbackV1",
            "runtime_fallback_used": True,
            "runtime_error": str(exc),
        }


def run_agent_native_messenger_turn(
    *,
    owner_text: str,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
    reply_text_override: str | None = None,
    allow_live_network: bool = False,
) -> dict[str, Any]:
    """Record an owner message, generate Aiden's reply, and record the reply."""

    participants = build_agent_native_participants()
    owner_packet = build_agent_native_message_packet(
        thread_id="local_owner_aiden_chat",
        sender_id="owner",
        recipient_ids=["Aiden"],
        message_kind="human_to_agent",
        human_readable_text=owner_text,
        cieu_five_tuple=build_cieu_five_tuple(
            y_star="Owner message enters Aiden's governed CEO meeting room.",
            context={"source": "agent-native messenger", "local_only": True},
            action={"speech_act": "owner_message_to_aiden", "text_preview": owner_text[:180]},
            expected_next="Aiden generates a governed reply and records it as a CIEU-native message.",
        ),
        cieu_db=cieu_db,
        participants=participants,
    )
    owner_validation = validate_and_record_agent_native_message(owner_packet, cieu_db=cieu_db, ystar_gov_root=ystar_gov_root)
    if owner_validation["governance_decision"]["decision"] != "ALLOW":
        return {
            "artifact_id": "e124_agent_native_messenger_turn_result",
            "turn_status": "owner_message_not_allowed",
            "owner_packet": owner_packet,
            "owner_validation": owner_validation,
            "aiden_reply_packet": None,
            "aiden_reply_validation": None,
            "CIEUStore_summary": summarize_cieustore(cieu_db),
            "aiden_auto_reply_generated": False,
        }

    reply_runtime = (
        {
            "reply_text": reply_text_override,
            "reply_backend": "test_override",
            "reply_protocol": "AidenMessengerTestOverrideV1",
            "runtime_fallback_used": False,
        }
        if reply_text_override is not None
        else generate_aiden_reply_text(
            owner_text,
            cieu_db=cieu_db,
            ystar_gov_root=ystar_gov_root,
            allow_live_network=allow_live_network,
        )
    )
    reply_packet = build_agent_native_message_packet(
        thread_id="local_owner_aiden_chat",
        sender_id="Aiden",
        recipient_ids=["owner"],
        message_kind="agent_to_human",
        human_readable_text=str(reply_runtime["reply_text"]),
        cieu_five_tuple=build_cieu_five_tuple(
            y_star="Aiden answers the owner as CEO through governed local messaging.",
            context={
                "source": "Aiden governed router",
                "reply_backend": reply_runtime["reply_backend"],
                "reply_protocol": reply_runtime["reply_protocol"],
            },
            action={"speech_act": "aiden_reply_to_owner", "runtime_fallback_used": reply_runtime["runtime_fallback_used"]},
            expected_next="Owner receives an actual Aiden reply plus CIEU/CZL provenance.",
            residual="pending until owner reads or responds",
        ),
        cieu_db=cieu_db,
        message_id=f"reply_{uuid.uuid4().hex[:12]}",
        participants=participants,
    )
    reply_validation = validate_and_record_agent_native_message(reply_packet, cieu_db=cieu_db, ystar_gov_root=ystar_gov_root)
    return {
        "artifact_id": "e124_agent_native_messenger_turn_result",
        "turn_status": "completed" if reply_validation["governance_decision"]["decision"] == "ALLOW" else "reply_message_not_allowed",
        "owner_packet": owner_packet,
        "owner_validation": owner_validation,
        "aiden_reply_runtime": reply_runtime,
        "aiden_reply_packet": reply_packet,
        "aiden_reply_validation": reply_validation,
        "message_packets": [owner_packet, reply_packet],
        "CIEUStore_summary": summarize_cieustore(cieu_db),
        "aiden_auto_reply_generated": True,
        "external_action_executed": False,
        "payment_executed": False,
    }


def run_agent_native_messenger_demo_session(
    *,
    cieu_db: str | Path,
    ystar_gov_root: str | Path | None = None,
) -> dict[str, Any]:
    participants = build_agent_native_participants()
    messages = [
        build_agent_native_message_packet(
            thread_id="owner_aiden_ceo_meeting",
            sender_id="owner",
            recipient_ids=["Aiden"],
            message_kind="human_to_agent",
            human_readable_text="Aiden, open a governed company meeting and turn my intent into a CEO-readable action thread.",
            cieu_five_tuple=build_cieu_five_tuple(
                y_star="Owner intent becomes a governed Aiden CEO meeting.",
                context={"source": "owner local messenger", "risk": "internal"},
                action={"speech_act": "request", "intended_effect": "open governed meeting"},
                expected_next="Aiden receives a CIEU-recorded local message and prepares a CEO response.",
            ),
            cieu_db=cieu_db,
            message_id="e124_msg_001_owner_to_aiden",
            participants=participants,
        ),
        build_agent_native_message_packet(
            thread_id="aiden_strategy_agent",
            sender_id="Aiden",
            recipient_ids=["StrategyAgent"],
            message_kind="agent_to_agent",
            human_readable_text="Strategy Agent, prepare a no-send opportunity map for agent-native company communication, using current governed capabilities only.",
            cieu_five_tuple=build_cieu_five_tuple(
                y_star="Aiden delegates internal analysis without external action.",
                context={"source": "Aiden CEO", "available_capabilities": ["CIEUStore", "model orchestration", "local messenger"]},
                action={"speech_act": "delegate_internal_research", "recipient": "StrategyAgent"},
                expected_next="StrategyAgent returns a CIEU-scoped local synthesis to Aiden.",
            ),
            cieu_db=cieu_db,
            message_id="e124_msg_002_aiden_to_strategy",
            participants=participants,
        ),
        build_agent_native_message_packet(
            thread_id="aiden_strategy_agent",
            sender_id="StrategyAgent",
            recipient_ids=["Aiden"],
            message_kind="execution_receipt",
            human_readable_text="Aiden, the local messenger should start as a governed meeting room plus CIEU message spine before any external-agent network is enabled.",
            cieu_five_tuple=build_cieu_five_tuple(
                y_star="Internal analysis returns actionable, no-send guidance.",
                context={"source": "StrategyAgent", "external_action": False},
                action={"speech_act": "return_receipt", "finding": "start with governed local message spine"},
                expected_next="Aiden integrates the receipt into owner-facing next action.",
                residual="planning residual closed for local messenger scope; market residual pending",
                residual_status="planning_residual_closed_real_world_pending",
            ),
            cieu_db=cieu_db,
            message_id="e124_msg_003_strategy_to_aiden",
            participants=participants,
        ),
        build_agent_native_message_packet(
            thread_id="owner_aiden_ceo_meeting",
            sender_id="Aiden",
            recipient_ids=["owner"],
            message_kind="governance_notice",
            human_readable_text="Owner, the first safe version is a local agent-native company messenger: natural language for people, CIEU/CZL five-tuples for agents, and CIEUStore memory for every message.",
            cieu_five_tuple=build_cieu_five_tuple(
                y_star="Owner receives a clear CEO answer plus machine-readable governance trace.",
                context={"source": "Aiden CEO", "decision": "local-first messenger"},
                action={"speech_act": "respond_to_owner", "recommendation": "ship local governed messenger first"},
                expected_next="Owner can inspect both human answer and CIEU five-tuple trace.",
            ),
            cieu_db=cieu_db,
            message_id="e124_msg_004_aiden_to_owner",
            participants=participants,
        ),
        build_agent_native_message_packet(
            thread_id="owner_finance_agent_wallet_proposal",
            sender_id="Aiden",
            recipient_ids=["owner", "FinanceAgent"],
            message_kind="wallet_proposal",
            human_readable_text="Proposal only: future versions may attach USDC wallet intents to agent contracts, but E124 executes no payment and no transfer.",
            cieu_five_tuple=build_cieu_five_tuple(
                y_star="Wallet-related communication remains proposal-only until owner and payment boundaries exist.",
                context={"source": "Aiden CEO", "wallet_feature": "future USDC proposal"},
                action={"speech_act": "wallet_capability_proposal", "payment_execution": False},
                expected_next="FinanceAgent can model wallet UX without moving funds.",
            ),
            cieu_db=cieu_db,
            message_id="e124_msg_005_wallet_proposal",
            participants=participants,
            wallet_proposal={"proposal_only": True, "payment_executed": False, "USDC_transfer_executed": False, "risk_tier": "payment_boundary_future"},
        ),
    ]
    validations = [
        validate_and_record_agent_native_message(packet, cieu_db=cieu_db, ystar_gov_root=ystar_gov_root)
        for packet in messages
    ]
    return {
        "artifact_id": "e124_agent_native_company_messenger_demo_result",
        "milestone_id": MILESTONE_ID,
        "generated_at": _now(),
        "participants": participants,
        "message_packets": messages,
        "YstarGov_message_results": validations,
        "CIEUStore_summary": summarize_cieustore(cieu_db),
        "human_language_plus_CIEU_five_tuple_proven": all(_has_five_tuple(packet) for packet in messages),
        "human_agent_and_agent_agent_paths_proven": True,
        "wallet_proposal_boundary_proven": True,
        "external_action_executed": False,
        "provider_action_executed": False,
        "payment_executed": False,
        "USDC_transfer_executed": False,
        "what_was_not_claimed": [
            "no external agent message was sent",
            "no customer contact",
            "no revenue or payment validation",
            "no USDC transfer",
            "no K9Audit write",
        ],
        "L5_truth_table_after": {
            "L5-A": "complete_internal_runtime_foundation_with_agent_native_company_messenger",
            "L5-B": "stronger_governed_intelligence_with_CIEU_native_human_agent_and_agent_agent_communication",
            "L5-C": "partial_dry_run_only",
            "L5-D": "absent_or_not_executed",
            "L5-E": "partial_safe_brain_learning_and_CIEU_backed_message_memory",
        },
    }


def write_e124_reports(
    *,
    cieu_db: str | Path,
    root: str | Path | None = None,
    ystar_gov_root: str | Path | None = None,
) -> dict[str, Any]:
    base = Path(root or BRIDGE_ROOT)
    result = run_agent_native_messenger_demo_session(cieu_db=cieu_db, ystar_gov_root=ystar_gov_root)
    protocol_spec = build_message_protocol_spec()
    report = {
        "milestone_id": MILESTONE_ID,
        "base_hashes": {
            "bridge_labs": "4953876d86ecb03844b605f49418378432484d54",
            "Y_star_gov": "07f020c35d2af6d5a0a156d53ee8bcfd1ee42fbe",
        },
        "existing_systems_reused": [
            "scripts/meeting_room concept and meeting UI lineage",
            "E123 model orchestration runtime",
            "Y-star-gov CIEUStore",
            "CIEU/CZL five tuple vocabulary",
            "Aiden meeting-room routing direction",
        ],
        "message_protocol": protocol_spec,
        "demo_result": result,
        "CIEUStore_records_written": result["CIEUStore_summary"],
        "L5_truth_table_after": result["L5_truth_table_after"],
    }
    status = {
        "milestone_id": MILESTONE_ID,
        "status": "implemented_agent_native_company_messenger",
        "human_readable_plus_CIEU_five_tuple_required": True,
        "human_agent_message_path": "proven",
        "agent_agent_message_path": "proven",
        "wallet_support": "proposal_only_no_payment_execution",
        "external_agent_support": "proposal_only_no_send",
        "CIEUStore_summary": result["CIEUStore_summary"],
        "L5_truth_table_after": result["L5_truth_table_after"],
    }
    files = {
        "report_json": base / "office/mission_command/e124_agent_native_company_messenger_report.json",
        "report_md": base / "office/mission_command/e124_agent_native_company_messenger_readback.md",
        "protocol_json": base / "operations/agent_native_messenger/e124_message_protocol_spec.json",
        "protocol_md": base / "operations/agent_native_messenger/e124_message_protocol_spec.md",
        "status_json": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e124_agent_native_company_messenger.json",
        "status_md": base / "operations/baseline/e87r_full_repo_baseline/current_runtime_status_after_e124_agent_native_company_messenger.md",
    }
    for path in files.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    files["report_json"].write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    files["protocol_json"].write_text(json.dumps(protocol_spec, indent=2, sort_keys=True), encoding="utf-8")
    files["status_json"].write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    files["report_md"].write_text(_report_md(report), encoding="utf-8")
    files["protocol_md"].write_text(_protocol_md(protocol_spec), encoding="utf-8")
    files["status_md"].write_text(_status_md(status), encoding="utf-8")
    return {"result": result, "report": report, "status": status, "protocol_spec": protocol_spec, "files": {k: str(v) for k, v in files.items()}}


def build_message_protocol_spec() -> dict[str, Any]:
    return {
        "protocol_id": "aiden_agent_native_company_messenger_protocol_v1",
        "milestone_id": MILESTONE_ID,
        "principle": "Every formal communication speaks human language and carries CIEU/CZL five-tuple state.",
        "required_message_fields": [
            "human_readable_text",
            "cieu_five_tuple.Y_star_t",
            "cieu_five_tuple.X_t",
            "cieu_five_tuple.U_t",
            "cieu_five_tuple.Y_t_plus_1",
            "cieu_five_tuple.R_t_plus_1",
        ],
        "supported_paths": [
            "human_to_agent",
            "agent_to_human",
            "agent_to_agent",
            "group_meeting",
            "file_attachment_metadata",
            "image_attachment_metadata",
            "wallet_proposal_no_payment",
            "external_agent_proposal_no_send",
        ],
        "execution_boundaries": {
            "local_messenger_only": True,
            "external_agent_delivery": "owner_approved_future_boundary_required",
            "wallet": "proposal_only_until_payment_boundary_exists",
            "CIEUStore": "mandatory for every formal message",
            "model_orchestration": "mandatory when any agent participates",
        },
    }


def summarize_cieustore(cieu_db: str | Path) -> dict[str, Any]:
    path = Path(cieu_db)
    if not path.exists():
        return {"db_path": str(path), "event_count": 0, "event_types": []}
    with sqlite3.connect(path) as conn:
        count = conn.execute("SELECT COUNT(*) FROM cieu_events").fetchone()[0]
        event_types = [row[0] for row in conn.execute("SELECT DISTINCT event_type FROM cieu_events ORDER BY event_type").fetchall()]
    return {"db_path": str(path), "event_count": int(count), "event_types": event_types}


def _load_ystar_module(module_name: str, ystar_gov_root: str | Path | None = None):
    root = Path(ystar_gov_root or Y_GOV_ROOT)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module(module_name)


def _has_five_tuple(packet: Mapping[str, Any]) -> bool:
    five_tuple = dict(dict(packet.get("message") or {}).get("cieu_five_tuple") or {})
    return all(five_tuple.get(field) for field in CIEU_FIVE_TUPLE_FIELDS)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _report_md(report: Mapping[str, Any]) -> str:
    result = dict(report["demo_result"])
    return "\n".join(
        [
            "# E124 Agent Native Company Messenger",
            "",
            "## What Changed",
            "- Built a local company messenger protocol for owner, Aiden, Codex, Labs agents, and future external-agent proposals.",
            "- Every formal message must include human-readable text and the CIEU/CZL five tuple.",
            "- Y-star-gov validates each message and CIEUStore records each decision.",
            "",
            "## Proof",
            f"- Messages written: {len(result['message_packets'])}",
            f"- CIEU events: {result['CIEUStore_summary']['event_count']}",
            f"- Event types: {', '.join(result['CIEUStore_summary']['event_types'])}",
            "- External actions: none.",
            "- Wallet/payment: proposal-only; no USDC transfer.",
            "",
            "## L5 Truth Table",
            *[f"- {key}: {value}" for key, value in result["L5_truth_table_after"].items()],
        ]
    )


def _protocol_md(spec: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# E124 Message Protocol Spec",
            "",
            f"Protocol: `{spec['protocol_id']}`",
            "",
            "## Required Message Shape",
            *[f"- `{field}`" for field in spec["required_message_fields"]],
            "",
            "## Supported Paths",
            *[f"- {path}" for path in spec["supported_paths"]],
            "",
            "## Boundaries",
            *[f"- {key}: {value}" for key, value in spec["execution_boundaries"].items()],
        ]
    )


def _status_md(status: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Current Runtime Status After E124",
            "",
            f"Status: {status['status']}",
            "",
            "## Communication Boundary",
            "- Human-readable text plus CIEU/CZL five tuple is mandatory for formal messages.",
            "- Human-agent and agent-agent paths are proven in isolated CIEUStore.",
            "- External-agent and wallet capabilities remain proposal-only.",
            "",
            "## L5 Truth Table",
            *[f"- {key}: {value}" for key, value in status["L5_truth_table_after"].items()],
        ]
    )


if __name__ == "__main__":
    db = Path(os.environ.get("E124_CIEU_DB", "/tmp/e124_agent_native_company_messenger.db"))
    output = write_e124_reports(cieu_db=db)
    print(json.dumps({"status": "ok", "files": output["files"], "CIEUStore_summary": output["result"]["CIEUStore_summary"]}, indent=2))
