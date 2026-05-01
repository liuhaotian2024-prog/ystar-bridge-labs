from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

from .e4_market_research_plan import build_e4_market_research_request
from .tier1_public_research import (
    DisabledTier1ResearchProvider,
    Tier1ResearchProvider,
    validate_receipt,
)
from .tier1_research_mission_packet import build_tier1_research_mission_packet


@dataclass(frozen=True)
class Tier1ResearchCapabilityResolution:
    mode: str
    live_read_only_available: bool
    fixture_demo_available: bool
    architecture_available: bool
    configured_live_explicitly_enabled: bool
    budget_requested: Dict[str, int]
    missing_config_actions: List[str]
    enablement_packet: Dict[str, Any]
    live_research_executed: bool
    external_action_executed: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _safe_contains(path: Path, needle: str) -> bool:
    if not path.exists() or not path.is_file():
        return False
    return needle.lower() in path.read_text(encoding="utf-8", errors="replace").lower()


def resolve_tier1_research_capability(repo_root: Path) -> Dict[str, Any]:
    workspace = repo_root.parent
    company_root = workspace / "ystar-company"
    l10_root = company_root / "l10_delegated_live_meta_development_runtime"
    executor = l10_root / "controlled_research_executor.py"
    planner = l10_root / "controlled_research_planner.py"
    budget = l10_root / "research_budget_model.py"
    stdlib_contract = company_root / "controlled_public_page_read_adapter" / "stdlib_public_http_safety_contract.json"
    backend_contract = company_root / "controlled_backend_configuration_policy" / "backend_env_var_contract.json"

    architecture_available = all(path.exists() for path in (executor, planner, budget))
    fixture_demo_available = _safe_contains(executor, "run_fixture_research_demo")
    configured_live_disabled = _safe_contains(executor, "configured_live_read_only_available\": False") or _safe_contains(
        executor,
        "disabled_unless_explicitly_configured_and_safe",
    )
    live_available = architecture_available and not configured_live_disabled
    packet = build_tier1_research_mission_packet()
    missing = []
    if not live_available:
        missing.extend(
            [
                "Owner must explicitly approve a Tier 1 live read-only evidence mission.",
                "Controlled search/page-read provider must be configured without exposing secret values.",
                "Research budget must be accepted before execution.",
                "Budget receipt writer must record queries, pages, domains, and stop reason.",
            ]
        )
    if not stdlib_contract.exists():
        missing.append("stdlib public HTTP/page-read safety contract is not present in ystar-company.")
    if not backend_contract.exists():
        missing.append("backend env-var contract is not present in ystar-company.")

    mode = "live_read_only_configured" if live_available else ("fixture_demo" if fixture_demo_available else "blocked_missing_config")
    if mode == "fixture_demo":
        # Fixture mode is useful for testing plumbing, but it is not live market evidence.
        mode = "blocked_missing_config"

    resolution = Tier1ResearchCapabilityResolution(
        mode=mode,
        live_read_only_available=live_available,
        fixture_demo_available=fixture_demo_available,
        architecture_available=architecture_available,
        configured_live_explicitly_enabled=live_available,
        budget_requested={
            "max_search_queries": int(packet["max_search_queries"]),
            "max_pages_read": int(packet["max_pages_read"]),
            "max_domains": int(packet["max_domains"]),
        },
        missing_config_actions=missing,
        enablement_packet={
            "packet_type": "tier1_live_read_only_enablement",
            "recommended_owner_decision": "approve_or_revise_tier1_live_read_only_research",
            "missing_config_actions": missing,
            "budget_requested": {
                "max_search_queries": packet["max_search_queries"],
                "max_pages_read": packet["max_pages_read"],
                "max_domains": packet["max_domains"],
            },
            "allowed_source_categories": packet["source_categories"],
            "stop_conditions": packet["stop_conditions"],
            "boundary": {
                "no_login": True,
                "no_contact": True,
                "no_form_submit": True,
                "no_payment": True,
                "no_publication": True,
                "no_file_upload": True,
                "no_customer_contact": True,
            },
            "approval_options": packet["owner_approval_options"],
        },
        live_research_executed=False,
        external_action_executed=False,
    )
    return resolution.to_dict()


def render_tier1_research_capability_resolution(resolution: Dict[str, Any]) -> str:
    lines = [
        "# E2 Tier 1 Research Capability Resolution",
        "",
        f"- mode: {resolution['mode']}",
        f"- live_read_only_available: {resolution['live_read_only_available']}",
        f"- fixture_demo_available: {resolution['fixture_demo_available']}",
        f"- architecture_available: {resolution['architecture_available']}",
        f"- configured_live_explicitly_enabled: {resolution['configured_live_explicitly_enabled']}",
        f"- live_research_executed: {resolution['live_research_executed']}",
        f"- external_action_executed: {resolution['external_action_executed']}",
        "",
        "## Budget Requested",
    ]
    for key, value in resolution["budget_requested"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Missing Config / Owner Actions"])
    lines.extend(f"- {item}" for item in resolution["missing_config_actions"])
    lines.extend(["", "## No-Side-Effect Boundary"])
    for key, value in resolution["enablement_packet"]["boundary"].items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def render_live_read_only_enablement_packet(resolution: Dict[str, Any]) -> str:
    packet = resolution["enablement_packet"]
    lines = [
        "# E2 Live Read-Only Enablement Packet",
        "",
        f"- recommended_owner_decision: {packet['recommended_owner_decision']}",
        f"- approval_options: {', '.join(packet['approval_options'])}",
        "",
        "## Missing Config / Approval",
    ]
    lines.extend(f"- {item}" for item in packet["missing_config_actions"])
    lines.extend(["", "## Requested Budget"])
    for key, value in packet["budget_requested"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Allowed Source Categories"])
    lines.extend(f"- {item}" for item in packet["allowed_source_categories"])
    lines.extend(["", "## Stop Conditions"])
    lines.extend(f"- {item}" for item in packet["stop_conditions"])
    lines.extend(["", "## Boundary"])
    for key, value in packet["boundary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "This packet does not execute research. It requests approval/configuration for a future bounded Tier 1 read-only run.",
        ]
    )
    return "\n".join(lines)


def run_e4_tier1_research(
    repo_root: Path,
    provider: Tier1ResearchProvider | None = None,
) -> Dict[str, Any]:
    request = build_e4_market_research_request()
    provider = provider or DisabledTier1ResearchProvider()
    receipt, sources = provider.run(request)
    validation_errors = validate_receipt(receipt, sources)
    live_ok = receipt.live_research_executed and bool(sources) and not validation_errors
    blocker_path = None
    if not live_ok:
        blocker_path = write_e4_research_runtime_blocker(repo_root, receipt.to_dict(), validation_errors)
    return {
        "request": request.to_dict(),
        "provider_name": provider.provider_name,
        "provider_available": provider.available(),
        "receipt": receipt.to_dict(),
        "source_evidence": [source.to_dict() for source in sources],
        "validation_errors": validation_errors,
        "live_research_executed": live_ok,
        "blocker_path": str(blocker_path) if blocker_path else "",
        "external_action_executed": False,
    }


def write_e4_research_runtime_blocker(
    repo_root: Path,
    receipt: Dict[str, Any],
    validation_errors: List[str],
) -> Path:
    path = repo_root / "reports" / "integration" / "e4_research_runtime_blocker.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# E4 Research Runtime Blocker",
        "",
        f"- provider_name: {receipt.get('provider_name')}",
        f"- live_research_executed: {receipt.get('live_research_executed')}",
        f"- stopped_reason: {receipt.get('stopped_reason')}",
        f"- external_action_executed: {receipt.get('external_action_executed')}",
        "",
        "## Missing Runtime / Config",
        "- Safe public search provider is not enabled in bridge-labs.",
        "- ystar-company has GET-only page-read safety components, but its configured-live research executor is disabled.",
        "- No live source summaries and budget receipt can be produced without an enabled provider.",
        "- Therefore full_mission_rt1 must remain nonzero.",
        "",
        "## Exact Owner / Config Action",
        "- Approve and configure a safe Tier 1 public search/page-read provider.",
        "- Keep provider-key handling presence-only; do not print or store secret values.",
        "- Enable budget accounting for queries, pages, domains, and stop reason.",
        "- Re-run E4 research after provider configuration is present.",
        "",
        "## Validation Errors",
    ]
    if validation_errors:
        lines.extend(f"- {item}" for item in validation_errors)
    else:
        lines.append("- provider unavailable")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
