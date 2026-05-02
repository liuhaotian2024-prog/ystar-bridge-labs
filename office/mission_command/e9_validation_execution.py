from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .e9_action_plan import E9ValidationActionPlan
from .e9_external_action_preflight import E9PreflightResult


@dataclass(frozen=True)
class E9ExecutionResult:
    execution_mode: str
    provider_name: str
    provider_available: bool
    executed: bool
    owner_operated_handoff_ready: bool
    blocked_reason: str
    action_ledger_path: str
    handoff_packet_path: str
    external_action_executed: bool
    customer_contact_occurred: bool
    publication_occurred: bool
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class E9ExternalValidationProvider:
    provider_name = "disabled_e9_external_validation_provider"

    def available(self) -> bool:
        return False

    def send_validation_message(self, plan: E9ValidationActionPlan) -> Dict[str, Any]:
        return {"sent": False, "error": "provider_not_available"}


class E9DeterministicFakeProvider(E9ExternalValidationProvider):
    provider_name = "deterministic_fake_e9_provider_tests_only"

    def available(self) -> bool:
        return True

    def send_validation_message(self, plan: E9ValidationActionPlan) -> Dict[str, Any]:
        return {"sent": True, "plan_id": plan.plan_id, "test_only": True}


def write_e9_owner_operated_handoff_packet(repo_root: Path, plan: E9ValidationActionPlan) -> Path:
    path = repo_root / "reports" / "integration" / "e9_owner_operated_handoff_packet.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E9 Owner-Operated Handoff Packet",
        "",
        "- external_action_executed_by_aiden: false",
        "- customer_contact_occurred_by_aiden: false",
        "- publication_occurred_by_aiden: false",
        f"- plan_id: {plan.plan_id}",
        f"- top_offer: {plan.top_offer}",
        f"- draft_id: {plan.draft_id}",
        f"- draft_hash: {plan.draft_hash}",
        f"- channel: {plan.channel}",
        f"- target_ids: {', '.join(plan.target_ids)}",
        "",
        "## Owner Instructions",
        "- This packet is not approval and does not send anything.",
        "- Owner must first create valid E9 manifest and target seeds.",
        "- Owner may then manually execute the frozen, AI-disclosed message only within the approved count/channel/target scope.",
        "",
        "## Stop Conditions",
    ]
    lines.extend(f"- {item}" for item in plan.stop_conditions)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_e9_validation_execution(
    repo_root: Path,
    plan: E9ValidationActionPlan,
    preflight: E9PreflightResult,
    provider: E9ExternalValidationProvider | None = None,
    execution_mode: str = "owner_operated_handoff",
) -> E9ExecutionResult:
    provider = provider or E9ExternalValidationProvider()
    if execution_mode == "owner_operated_handoff":
        handoff = write_e9_owner_operated_handoff_packet(repo_root, plan)
        return E9ExecutionResult(execution_mode, provider.provider_name, provider.available(), False, True, "", "", str(handoff), False, False, False)
    if not preflight.allowed:
        return E9ExecutionResult(execution_mode, provider.provider_name, provider.available(), False, False, "preflight_not_allowed", "", "", False, False, False, [preflight.blocked_reason])
    if not provider.available():
        return E9ExecutionResult(execution_mode, provider.provider_name, False, False, False, "blocked_missing_provider", "", "", False, False, False)
    result = provider.send_validation_message(plan)
    if not result.get("sent"):
        return E9ExecutionResult(execution_mode, provider.provider_name, True, False, False, str(result.get("error", "send_failed")), "", "", False, False, False)
    ledger = repo_root / "reports" / "integration" / "e9_external_action_ledger.md"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text(
        "\n".join(
            [
                "# E9 External Action Ledger",
                "",
                f"- plan_id: {plan.plan_id}",
                f"- provider_name: {provider.provider_name}",
                "- external_action_executed: true",
                "- customer_contact_occurred: true",
                "- publication_occurred: false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return E9ExecutionResult(execution_mode, provider.provider_name, True, True, False, "", str(ledger), "", True, True, False)


def render_e9_execution_report(result: E9ExecutionResult) -> str:
    lines = ["# E9 Execution Report", ""]
    for key, value in result.to_dict().items():
        lines.append(f"- {key}: {value if value not in ['', None] else 'none'}")
    return "\n".join(lines)
