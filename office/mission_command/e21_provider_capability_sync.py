from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Any, Dict, Mapping

DEFAULT_GOV_MCP_ROOT = Path("/Users/haotianliu/.openclaw/workspace/gov-mcp")


def load_gov_mcp_provider_manifest(gov_mcp_root: str | Path = DEFAULT_GOV_MCP_ROOT) -> Dict[str, Any]:
    root = Path(gov_mcp_root)
    if not root.exists():
        return {
            "provider_id": "gov_mcp_unavailable",
            "provider_mode": "live_blocked",
            "no_send_available": False,
            "dry_run_available": False,
            "live_scaffold_available": False,
            "live_provider_enabled": False,
            "live_execution_blocked_reason": "gov_mcp_repo_unavailable",
            "external_provider_called": False,
            "real_message_sent": False,
        }
    sys.path.insert(0, str(root))
    try:
        module = importlib.import_module("gov_mcp.outbound.provider_manifest")
        return dict(module.build_provider_capability_manifest())
    except Exception as exc:  # pragma: no cover - fallback preserves reportability if import path is partial.
        outbound = root / "gov_mcp" / "outbound"
        live_scaffold = (outbound / "provider_adapter.py").exists() and (outbound / "provider_manifest.py").exists()
        return {
            "provider_id": "gov_mcp_provider_manifest_import_failed",
            "provider_mode": "live_disabled" if live_scaffold else "live_blocked",
            "no_send_available": (outbound / "adapter_contract.py").exists(),
            "dry_run_available": (outbound / "dry_run_adapter.py").exists(),
            "live_scaffold_available": live_scaffold,
            "live_provider_enabled": False,
            "live_execution_blocked_reason": f"provider_manifest_import_failed:{type(exc).__name__}",
            "external_provider_called": False,
            "real_message_sent": False,
        }
    finally:
        try:
            sys.path.remove(str(root))
        except ValueError:
            pass


def build_provider_capability_sync(
    manifest: Mapping[str, Any] | None = None,
    gov_mcp_root: str | Path = DEFAULT_GOV_MCP_ROOT,
    gov_mcp_commit: str = "3258488c355482eec0fd92f735d9c0ad10c7bfbe",
) -> Dict[str, Any]:
    provider_manifest = dict(manifest or load_gov_mcp_provider_manifest(gov_mcp_root))
    live_enabled = bool(provider_manifest.get("live_provider_enabled"))
    live_scaffold = bool(provider_manifest.get("live_scaffold_available"))
    status = (
        "live_ready"
        if live_enabled
        else "live_provider_scaffolded_but_disabled"
        if live_scaffold
        else "live_provider_missing"
    )
    return {
        "artifact_id": "e21_provider_capability_sync",
        "source_repo": "gov-mcp",
        "source_commit": gov_mcp_commit,
        "provider_manifest_artifact_id": provider_manifest.get("artifact_id", "unknown"),
        "provider_id": provider_manifest.get("provider_id"),
        "provider_mode": provider_manifest.get("provider_mode"),
        "no_send_available": bool(provider_manifest.get("no_send_available")),
        "dry_run_available": bool(provider_manifest.get("dry_run_available")),
        "live_scaffold_available": live_scaffold,
        "live_provider_enabled": live_enabled,
        "provider_tests_passed": bool(provider_manifest.get("provider_tests_passed", False)),
        "rate_limit_guard_present": bool(provider_manifest.get("rate_limit_guard_present", False)),
        "idempotency_guard_present": bool(provider_manifest.get("idempotency_guard_present", False)),
        "suppression_guard_present": bool(provider_manifest.get("suppression_guard_present", False)),
        "audit_receipt_enabled": bool(provider_manifest.get("audit_receipt_enabled", False)),
        "dry_run_and_live_receipts_distinct": bool(provider_manifest.get("dry_run_and_live_receipts_distinct", False)),
        "capability_status": status,
        "live_execution_blocked_reason": provider_manifest.get("live_execution_blocked_reason", "unknown"),
        "policy_note": "Provider absence is a live-capability blocker; low-risk send remains autonomous-eligible when provider becomes live_ready.",
        "external_action_executed": False,
    }


def render_provider_capability_sync(sync: Dict[str, Any]) -> str:
    lines = [
        "# E21 Provider Capability Sync",
        "",
        f"- source_repo: {sync['source_repo']}",
        f"- source_commit: {sync['source_commit']}",
        f"- capability_status: {sync['capability_status']}",
        f"- no_send_available: {str(sync['no_send_available']).lower()}",
        f"- dry_run_available: {str(sync['dry_run_available']).lower()}",
        f"- live_scaffold_available: {str(sync['live_scaffold_available']).lower()}",
        f"- live_provider_enabled: {str(sync['live_provider_enabled']).lower()}",
        f"- live_execution_blocked_reason: {sync['live_execution_blocked_reason']}",
        "- external_action_executed: false",
    ]
    return "\n".join(lines).rstrip() + "\n"
