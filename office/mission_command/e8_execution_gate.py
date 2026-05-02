from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List

from .e8_external_action_preflight import E8ExternalValidationAction, E8PreflightResult
from .e8_risk_controlled_action_model import RiskTier


@dataclass(frozen=True)
class ExecutionGateResult:
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


class ExternalValidationProvider:
    provider_name = "external_validation_provider"

    def available(self) -> bool:
        return False

    def send_validation_message(self, action: E8ExternalValidationAction) -> Dict[str, Any]:
        return {"sent": False, "error": "provider_not_implemented", "action_id": action.action_id}

    def publish_landing_page(self, action: E8ExternalValidationAction) -> Dict[str, Any]:
        return {"published": False, "error": "provider_not_implemented", "action_id": action.action_id}

    def publish_post(self, action: E8ExternalValidationAction) -> Dict[str, Any]:
        return {"published": False, "error": "provider_not_implemented", "action_id": action.action_id}


class DisabledExternalValidationProvider(ExternalValidationProvider):
    provider_name = "disabled_external_validation_provider"


class DeterministicFakeExternalValidationProvider(ExternalValidationProvider):
    provider_name = "deterministic_fake_external_validation_provider_tests_only"

    def available(self) -> bool:
        return True

    def send_validation_message(self, action: E8ExternalValidationAction) -> Dict[str, Any]:
        return {"sent": True, "action_id": action.action_id, "test_only": True}


def build_owner_operated_handoff_packet(action: E8ExternalValidationAction, repo_root: Path) -> Path:
    path = repo_root / "reports" / "integration" / "e8_owner_operated_handoff_packet.md"
    lines = [
        "# E8 Owner-Operated Handoff Packet",
        "",
        "- external_action_executed_by_aiden: false",
        "- customer_contact_occurred_by_aiden: false",
        f"- action_id: {action.action_id}",
        f"- target_id: {action.target_id}",
        f"- channel: {action.channel}",
        f"- draft_id: {action.draft_id}",
        f"- draft_hash: {action.draft_hash}",
        f"- risk_tier: {action.risk_tier}",
        "",
        "## Stop Conditions",
    ]
    lines.extend(f"- {item}" for item in action.stop_conditions)
    lines.extend(["", "Owner must execute manually only after creating a valid manifest and target seed registry."])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_e8_execution_gate(
    action: E8ExternalValidationAction,
    preflight: E8PreflightResult,
    repo_root: Path,
    provider: ExternalValidationProvider | None = None,
    execution_mode: str = "dry_run_only",
) -> ExecutionGateResult:
    provider = provider or DisabledExternalValidationProvider()
    reports = repo_root / "reports" / "integration"
    reports.mkdir(parents=True, exist_ok=True)
    if action.risk_tier == RiskTier.TIER_4_COMMERCIAL_LEGAL_PRODUCTION_HIGH_RISK:
        return ExecutionGateResult(execution_mode, provider.provider_name, provider.available(), False, False, "tier4_blocked", "", "", False, False, False, ["tier4_blocked"])
    if execution_mode == "owner_operated_handoff":
        handoff = build_owner_operated_handoff_packet(action, repo_root)
        return ExecutionGateResult(execution_mode, provider.provider_name, provider.available(), False, True, "", "", str(handoff), False, False, False)
    if not preflight.allowed:
        return ExecutionGateResult(execution_mode, provider.provider_name, provider.available(), False, False, "preflight_not_allowed", "", "", False, False, False, [preflight.blocked_reason])
    if execution_mode == "dry_run_only":
        return ExecutionGateResult(execution_mode, provider.provider_name, provider.available(), False, False, "dry_run_only", "", "", False, False, False)
    if not provider.available():
        return ExecutionGateResult(execution_mode, provider.provider_name, False, False, False, "blocked_missing_provider", "", "", False, False, False)
    result = provider.send_validation_message(action)
    if not result.get("sent"):
        return ExecutionGateResult(execution_mode, provider.provider_name, True, False, False, str(result.get("error", "send_failed")), "", "", False, False, False)
    ledger = reports / "e8_external_action_ledger.md"
    ledger.write_text(
        "\n".join(
            [
                "# E8 External Action Ledger",
                "",
                f"- action_id: {action.action_id}",
                f"- provider_name: {provider.provider_name}",
                "- external_action_executed: true",
                "- customer_contact_occurred: true",
                "- publication_occurred: false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return ExecutionGateResult(execution_mode, provider.provider_name, True, True, False, "", str(ledger), "", True, True, False)


def render_e8_execution_gate_report(result: ExecutionGateResult) -> str:
    lines = ["# E8 Execution Gate Report", ""]
    for key, value in result.to_dict().items():
        rendered = "none" if value == "" or value is None else value
        lines.append(f"- {key}: {rendered}")
    return "\n".join(lines)
