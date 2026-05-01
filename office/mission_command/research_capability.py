from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from office.aiden_meeting_room.company_context_loader import SAFE_CONTEXT_FILES, load_company_context


FORBIDDEN_MARKERS = (
    ".env",
    "secret",
    ".db",
    ".db-wal",
    ".db-shm",
    ".log",
    "active_agent",
    ".ystar_active_agent",
)


@dataclass(frozen=True)
class ResearchCapabilityAudit:
    internal_research_verdict: str
    external_research_verdict: str
    plan_confidence_allowed: str
    internal_capability: Dict[str, Any]
    external_capability: Dict[str, Any]
    governance_support: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "internal_research_verdict": self.internal_research_verdict,
            "external_research_verdict": self.external_research_verdict,
            "plan_confidence_allowed": self.plan_confidence_allowed,
            "internal_capability": self.internal_capability,
            "external_capability": self.external_capability,
            "governance_support": self.governance_support,
        }


def _safe_exists(path: Path) -> bool:
    lowered = str(path).lower()
    return not any(marker in lowered for marker in FORBIDDEN_MARKERS) and path.exists()


def _file_contains(path: Path, needle: str) -> bool:
    if not _safe_exists(path) or not path.is_file():
        return False
    return needle.lower() in path.read_text(encoding="utf-8", errors="replace").lower()


def _ystar_company_root(repo_root: Path) -> Path:
    return repo_root.parent / "ystar-company"


def audit_research_capability(repo_root: Path) -> ResearchCapabilityAudit:
    ctx = load_company_context(repo_root)
    safe_context_loaded = [rel for rel in SAFE_CONTEXT_FILES if rel in ctx.source_texts]
    required = {
        "README.md",
        "AGENTS.md",
        "OPERATIONS.md",
        "DIRECTIVE_TRACKER.md",
        "governance/ACTIVE_OPERATING_CHARTER.md",
        "knowledge/ceo/wisdom/M_TRIANGLE.md",
        "knowledge/ceo/wisdom/WORK_METHODOLOGY.md",
    }
    internal_ready = required.issubset(set(safe_context_loaded)) and (repo_root / "directive_retriage.json").exists()

    scannable_dirs = {
        "sales": _safe_exists(repo_root / "sales"),
        "content": _safe_exists(repo_root / "content"),
        "reports/integration": _safe_exists(repo_root / "reports" / "integration"),
        "knowledge/ceo/wisdom": _safe_exists(repo_root / "knowledge" / "ceo" / "wisdom"),
        "office/aiden_meeting_room": _safe_exists(repo_root / "office" / "aiden_meeting_room"),
        "office/mission_command": _safe_exists(repo_root / "office" / "mission_command"),
    }

    company_root = _ystar_company_root(repo_root)
    l10_executor = company_root / "l10_delegated_live_meta_development_runtime" / "controlled_research_executor.py"
    l10_budget = company_root / "l10_delegated_live_meta_development_runtime" / "research_budget_model.py"
    l10_planner = company_root / "l10_delegated_live_meta_development_runtime" / "controlled_research_planner.py"
    stdlib_contract = company_root / "controlled_public_page_read_adapter" / "stdlib_public_http_safety_contract.json"
    backend_contract = company_root / "controlled_backend_configuration_policy" / "backend_env_var_contract.json"

    fixture_available = _file_contains(l10_executor, "run_fixture_research_demo")
    configured_live_disabled = _file_contains(l10_executor, "configured_live_read_only_available\": False") or _file_contains(
        l10_executor, "disabled_unless_explicitly_configured_and_safe"
    )
    stdlib_contract_available = _safe_exists(stdlib_contract)
    backend_contract_available = _safe_exists(backend_contract)
    l10_architecture_available = all(_safe_exists(path) for path in (l10_executor, l10_budget, l10_planner))

    if not l10_architecture_available:
        external_verdict = "NOT_READY"
        plan_confidence = "internal_only_preliminary"
    elif configured_live_disabled:
        external_verdict = "ARCHITECTURE_ONLY"
        plan_confidence = "internal_only_preliminary"
    elif fixture_available:
        external_verdict = "FIXTURE_ONLY"
        plan_confidence = "evidence_backed_with_fixture_only"
    else:
        external_verdict = "NOT_READY"
        plan_confidence = "internal_only_preliminary"

    ystar_gov_root = repo_root.parent / "Y-star-gov"
    gov_mcp_root = repo_root.parent / "gov-mcp"
    gov_mcp_tools = gov_mcp_root / "gov_mcp" / "company_runtime_tools.py"
    ystar_action_classifier = ystar_gov_root / "ystar" / "domains" / "company_runtime" / "company_action_classifier.py"
    gov_mcp_distinguishes_read_only_from_contact = (
        _file_contains(gov_mcp_tools, "gov_company_action_preflight")
        and _file_contains(ystar_action_classifier, "read-only research")
        and (_file_contains(ystar_action_classifier, "customer contact") or _file_contains(ystar_action_classifier, "email"))
    )
    governance_support = {
        "ystar_gov_company_runtime_policy_present": _safe_exists(ystar_gov_root / "ystar" / "domains" / "company_runtime" / "company_runtime_policy.py"),
        "ystar_gov_tier1_read_only_supported": _file_contains(ystar_gov_root / "ystar" / "domains" / "company_runtime" / "permission_tiers.py", "read-only external research"),
        "gov_mcp_company_preflight_present": _safe_exists(gov_mcp_tools),
        "gov_mcp_distinguishes_read_only_from_contact": gov_mcp_distinguishes_read_only_from_contact,
    }

    return ResearchCapabilityAudit(
        internal_research_verdict="INTERNAL_RESEARCH_READY" if internal_ready else "PARTIAL",
        external_research_verdict=external_verdict,
        plan_confidence_allowed=plan_confidence,
        internal_capability={
            "safe_context_loaded": safe_context_loaded,
            "directive_retriage_loaded": (repo_root / "directive_retriage.json").exists(),
            "scannable_dirs": scannable_dirs,
            "can_identify_active_vs_historical": bool(ctx.operations_findings and ctx.directive_findings),
            "can_map_internal_assets_to_money_paths": True,
        },
        external_capability={
            "ystar_company_l10_architecture_available": l10_architecture_available,
            "fixture_demo_available": fixture_available,
            "configured_live_read_only_available": False if configured_live_disabled else None,
            "stdlib_public_http_contract_available": stdlib_contract_available,
            "backend_env_var_contract_available": backend_contract_available,
            "tavily_config_currently_verified": False,
            "live_research_executed": False,
            "missing_for_live_research": [
                "explicit live read-only enablement in the active mission/config",
                "current safe provider/search backend verification without reading secret values",
                "budget receipt from a live read-only run",
                "fresh source summaries from bounded public page reads",
            ],
        },
        governance_support=governance_support,
    )


def render_capability_audit_markdown(audit: ResearchCapabilityAudit) -> str:
    data = audit.to_dict()
    lines = [
        "# E1.2 Research Capability Audit",
        "",
        f"Internal research verdict: {audit.internal_research_verdict}",
        f"External research verdict: {audit.external_research_verdict}",
        f"Plan confidence allowed: {audit.plan_confidence_allowed}",
        "",
        "## Internal Research Capability",
        f"- Safe context loaded: {', '.join(data['internal_capability']['safe_context_loaded'])}",
        f"- directive_retriage.json loaded: {data['internal_capability']['directive_retriage_loaded']}",
        f"- Can identify active vs historical: {data['internal_capability']['can_identify_active_vs_historical']}",
        f"- Can map internal assets to money paths: {data['internal_capability']['can_map_internal_assets_to_money_paths']}",
        "",
        "## Scannable Internal Directories",
    ]
    for name, available in data["internal_capability"]["scannable_dirs"].items():
        lines.append(f"- {name}: {available}")
    lines.extend(
        [
            "",
            "## External Research Capability",
            f"- ystar-company L10 research architecture available: {data['external_capability']['ystar_company_l10_architecture_available']}",
            f"- fixture demo available: {data['external_capability']['fixture_demo_available']}",
            f"- configured live read-only available now: {data['external_capability']['configured_live_read_only_available']}",
            f"- stdlib_public_http contract available: {data['external_capability']['stdlib_public_http_contract_available']}",
            f"- backend env-var contract available: {data['external_capability']['backend_env_var_contract_available']}",
            f"- Tavily/current provider verified without reading secrets: {data['external_capability']['tavily_config_currently_verified']}",
            f"- live research executed: {data['external_capability']['live_research_executed']}",
            "",
            "## Missing For Fully Evidence-Backed Live Plan",
        ]
    )
    lines.extend(f"- {item}" for item in data["external_capability"]["missing_for_live_research"])
    lines.extend(
        [
            "",
            "## Y-star-gov / gov-mcp Support",
            f"- Y-star-gov company_runtime policy present: {data['governance_support']['ystar_gov_company_runtime_policy_present']}",
            f"- Y-star-gov Tier 1 read-only supported: {data['governance_support']['ystar_gov_tier1_read_only_supported']}",
            f"- gov-mcp company preflight present: {data['governance_support']['gov_mcp_company_preflight_present']}",
            f"- gov-mcp distinguishes read-only from contact: {data['governance_support']['gov_mcp_distinguishes_read_only_from_contact']}",
            "",
            "## Verdict",
            "Aiden can produce an internal-evidence preliminary plan now. It must not claim a fully live-market-evidence-backed 7-day plan until configured live read-only research is explicitly enabled, budgeted, run, and recorded.",
            "",
            "Safety: no external sending, customer contact, email, payment, publication, or core DB writeback occurred.",
        ]
    )
    return "\n".join(lines)
