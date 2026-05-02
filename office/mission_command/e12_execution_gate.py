from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .e12_action_packet import E12ValidationActionPacket


E12_ACTION_LEDGER_PATH = Path("reports/integration/e12_external_action_ledger.md")


class E12ExternalValidationProvider:
    provider_name = "abstract_e12_provider"

    def available(self) -> bool:
        return False

    def send_validation_message(self, packet: E12ValidationActionPacket) -> Dict[str, Any]:
        raise NotImplementedError


class DisabledE12ExternalValidationProvider(E12ExternalValidationProvider):
    provider_name = "disabled_e12_provider"

    def available(self) -> bool:
        return False

    def send_validation_message(self, packet: E12ValidationActionPacket) -> Dict[str, Any]:
        return {"sent": False, "blocked_reason": "provider_disabled"}


class DeterministicFakeE12ProviderForTestsOnly(E12ExternalValidationProvider):
    provider_name = "deterministic_fake_e12_provider_for_tests_only"

    def available(self) -> bool:
        return True

    def send_validation_message(self, packet: E12ValidationActionPacket) -> Dict[str, Any]:
        return {"sent": True, "provider_reference": f"fake_send_{packet.action_id}"}


@dataclass(frozen=True)
class E12ExecutionResult:
    execution_status: str
    external_validation_ran: bool
    aiden_sent_anything: bool
    customer_contact_occurred: bool
    publication_occurred: bool
    action_ledger_path: str
    handoff_packet_path: str
    blocked_reason: str
    exact_unblock_action: str
    executed_actions: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def render_e12_owner_operated_handoff_packet(packets: List[E12ValidationActionPacket], active: bool = False) -> str:
    lines = [
        "# E12 Owner-Operated Handoff Packet",
        "",
        f"- handoff_active: {str(active).lower()}",
        "- aiden_sent_anything: false",
        "- customer_contact_occurred_by_aiden: false",
        "- DRAFT ONLY / NOT SENT / OWNER APPROVAL REQUIRED",
        "",
        "## Use",
        "- Owner may use this only after approving E12 manifest/targets/channel/draft/stop conditions.",
        "- Owner should record any resulting feedback in `operations/external_validation/e12_feedback_events.json`.",
        "",
    ]
    for packet in packets:
        lines.extend(
            [
                f"## {packet.target_id}: {packet.target_label}",
                f"- channel: {packet.channel}",
                f"- draft_hash: {packet.draft_hash}",
                f"- approval_reference: {packet.owner_approval_reference}",
                "",
                "### Draft",
                packet.ai_transparency_statement,
                "",
                "I'm checking whether a 48h AI Ops Operating Room Blueprint would be useful for AI consultants/agencies that need a governance layer around implementation work.",
                "",
                "The quick ask: would this kind of blueprint help you scope safer AI workflow implementation, or would you need implementation support instead of a blueprint?",
                "",
                packet.opt_out_language,
                "",
            ]
        )
    return "\n".join(lines).rstrip()


def execute_e12_validation(
    repo_root: Path,
    packets: List[E12ValidationActionPacket],
    approval_status: Any,
    *,
    provider: E12ExternalValidationProvider | None = None,
) -> E12ExecutionResult:
    provider = provider or DisabledE12ExternalValidationProvider()
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    handoff_path = reports / "e12_owner_operated_handoff_packet.md"
    handoff_path.write_text(render_e12_owner_operated_handoff_packet(packets, active=approval_status.execution_mode == "owner_operated_handoff" and approval_status.approval_valid) + "\n", encoding="utf-8")

    if not approval_status.approval_valid:
        return E12ExecutionResult(
            execution_status="blocked_missing_or_invalid_approval",
            external_validation_ran=False,
            aiden_sent_anything=False,
            customer_contact_occurred=False,
            publication_occurred=False,
            action_ledger_path="",
            handoff_packet_path="reports/integration/e12_owner_operated_handoff_packet.md",
            blocked_reason="missing_or_invalid_E12_owner_approval",
            exact_unblock_action="Owner must approve operations/external_validation/e12_owner_approval.request.json and materialize e12_target_seeds.json, or provide owner-entered feedback events.",
        )
    if approval_status.execution_mode == "owner_operated_handoff":
        return E12ExecutionResult(
            execution_status="owner_operated_handoff_ready",
            external_validation_ran=False,
            aiden_sent_anything=False,
            customer_contact_occurred=False,
            publication_occurred=False,
            action_ledger_path="",
            handoff_packet_path="reports/integration/e12_owner_operated_handoff_packet.md",
            blocked_reason="awaiting_owner_operated_feedback_events",
            exact_unblock_action="Owner manually executes approved handoff and records valid events in operations/external_validation/e12_feedback_events.json.",
        )
    if approval_status.execution_mode == "dry_run_only":
        return E12ExecutionResult(
            execution_status="dry_run_only",
            external_validation_ran=False,
            aiden_sent_anything=False,
            customer_contact_occurred=False,
            publication_occurred=False,
            action_ledger_path="",
            handoff_packet_path="reports/integration/e12_owner_operated_handoff_packet.md",
            blocked_reason="approval_mode_is_dry_run_only",
            exact_unblock_action="Owner must choose owner_operated_handoff or aiden_executes_if_provider_available for validation execution.",
        )
    if not provider.available():
        return E12ExecutionResult(
            execution_status="blocked_missing_safe_provider",
            external_validation_ran=False,
            aiden_sent_anything=False,
            customer_contact_occurred=False,
            publication_occurred=False,
            action_ledger_path="",
            handoff_packet_path="reports/integration/e12_owner_operated_handoff_packet.md",
            blocked_reason="missing_safe_E12_execution_provider",
            exact_unblock_action="Provide a safe E12 provider or switch approval to owner_operated_handoff and record owner-entered feedback events.",
        )
    executable = [packet for packet in packets if packet.action_authorization_allowed and not packet.packet_errors]
    if not executable:
        return E12ExecutionResult(
            execution_status="blocked_preflight_failure",
            external_validation_ran=False,
            aiden_sent_anything=False,
            customer_contact_occurred=False,
            publication_occurred=False,
            action_ledger_path="",
            handoff_packet_path="reports/integration/e12_owner_operated_handoff_packet.md",
            blocked_reason="no_packets_passed_router_preflight",
            exact_unblock_action="Fix approval, target, draft, channel, and action authorization router failures.",
        )
    executed = []
    for packet in executable[: approval_status.max_external_messages]:
        executed.append({"packet": packet.to_dict(), "provider_result": provider.send_validation_message(packet)})
    ledger_path = repo_root / E12_ACTION_LEDGER_PATH
    ledger_lines = [
        "# E12 External Action Ledger",
        "",
        "- approved_external_sending: true",
        f"- approved_external_action_count: {len(executed)}",
        f"- provider: {provider.provider_name}",
        "",
        "```json",
        json.dumps(executed, indent=2, ensure_ascii=False),
        "```",
    ]
    ledger_path.write_text("\n".join(ledger_lines) + "\n", encoding="utf-8")
    return E12ExecutionResult(
        execution_status="aiden_executed_with_ledger",
        external_validation_ran=True,
        aiden_sent_anything=True,
        customer_contact_occurred=True,
        publication_occurred=False,
        action_ledger_path=str(E12_ACTION_LEDGER_PATH),
        handoff_packet_path="reports/integration/e12_owner_operated_handoff_packet.md",
        blocked_reason="",
        exact_unblock_action="Capture resulting feedback events; do not infer success without feedback.",
        executed_actions=executed,
    )


def render_e12_execution_report(result: E12ExecutionResult) -> str:
    lines = [
        "# E12 Execution Report",
        "",
        f"- execution_status: {result.execution_status}",
        f"- external_validation_ran: {str(result.external_validation_ran).lower()}",
        f"- aiden_sent_anything: {str(result.aiden_sent_anything).lower()}",
        f"- customer_contact_occurred: {str(result.customer_contact_occurred).lower()}",
        f"- publication_occurred: {str(result.publication_occurred).lower()}",
        f"- action_ledger_path: {result.action_ledger_path or 'none'}",
        f"- handoff_packet_path: {result.handoff_packet_path or 'none'}",
        f"- blocked_reason: {result.blocked_reason or 'none'}",
        f"- exact_unblock_action: {result.exact_unblock_action or 'none'}",
    ]
    return "\n".join(lines)
