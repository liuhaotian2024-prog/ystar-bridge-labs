from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def detect_provider_capability(gov_mcp_root: str | Path = "/Users/haotianliu/.openclaw/workspace/gov-mcp") -> Dict[str, Any]:
    root = Path(gov_mcp_root)
    outbound = root / "gov_mcp" / "outbound"
    files = {
        "models": outbound / "models.py",
        "policy": outbound / "policy.py",
        "safety_guards": outbound / "safety_guards.py",
        "adapter_contract": outbound / "adapter_contract.py",
        "dry_run_adapter": outbound / "dry_run_adapter.py",
        "receipts": outbound / "receipts.py",
        "idempotency": outbound / "idempotency.py",
    }
    tests = list((root / "tests").glob("test_outbound_*.py")) if (root / "tests").exists() else []
    live_adapter_candidates = [
        outbound / "live_adapter.py",
        outbound / "provider_adapter.py",
        outbound / "email_provider.py",
        outbound / "message_provider.py",
    ]
    live_adapter = any(path.exists() for path in live_adapter_candidates)
    no_send_adapter = files["adapter_contract"].exists()
    dry_run_adapter = files["dry_run_adapter"].exists()
    return {
        "artifact_id": "e20_provider_capability_detection",
        "repo_path": str(root),
        "outbound_files_present": {key: path.exists() for key, path in files.items()},
        "no_send_adapter_only": no_send_adapter and not live_adapter,
        "dry_run_adapter_only": dry_run_adapter and not live_adapter,
        "live_provider_adapter_present": live_adapter,
        "provider_tests_present": len(tests) >= 7,
        "rate_limit_guard_present": files["safety_guards"].exists(),
        "idempotency_guard_present": files["idempotency"].exists(),
        "suppression_guard_present": files["safety_guards"].exists(),
        "audit_receipt_generator_present": files["receipts"].exists(),
        "rollback_reversal_path_present": False,
        "provider_capability_status": "no_send_and_dry_run_only_provider_capability_missing_for_live_send" if not live_adapter else "live_provider_adapter_present",
        "external_action_executed": False,
    }


def live_ready(capability: Dict[str, Any]) -> bool:
    return bool(
        capability.get("live_provider_adapter_present")
        and capability.get("provider_tests_present")
        and capability.get("rate_limit_guard_present")
        and capability.get("idempotency_guard_present")
        and capability.get("suppression_guard_present")
        and capability.get("audit_receipt_generator_present")
    )


def render_provider_capability_detection(capability: Dict[str, Any]) -> str:
    lines = [
        "# E20 Provider Capability Detection",
        "",
        f"- provider_capability_status: {capability['provider_capability_status']}",
        f"- no_send_adapter_only: {str(capability['no_send_adapter_only']).lower()}",
        f"- dry_run_adapter_only: {str(capability['dry_run_adapter_only']).lower()}",
        f"- live_provider_adapter_present: {str(capability['live_provider_adapter_present']).lower()}",
        f"- provider_tests_present: {str(capability['provider_tests_present']).lower()}",
        f"- external_action_executed: {str(capability['external_action_executed']).lower()}",
    ]
    return "\n".join(lines).rstrip() + "\n"
