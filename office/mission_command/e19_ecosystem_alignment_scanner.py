from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPO_ROOTS = {
    "ystar-bridge-labs": "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
    "gov-mcp": "/Users/haotianliu/.openclaw/workspace/gov-mcp",
    "Y-star-gov": "/Users/haotianliu/.openclaw/workspace/Y-star-gov",
    "ystar-company": "/Users/haotianliu/.openclaw/workspace/ystar-company",
}


@dataclass(frozen=True)
class E19RepoAlignment:
    repo_name: str
    repo_path: str
    exists: bool
    branch: str
    head: str
    relevant_file_groups_found: List[str]
    commercial_runtime_relevance: str
    governance_relevance: str
    provider_boundary_relevance: str
    historical_asset_relevance: str
    direct_dependency_on_e18: str
    modification_needed: str
    risk_if_not_modified: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _git(repo: Path, args: List[str]) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(repo), *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _any_exists(root: Path, rels: Iterable[str]) -> bool:
    return any((root / rel).exists() for rel in rels)


def _find_keyword_hits(root: Path, keywords: List[str], limit: int = 12) -> List[str]:
    if not root.exists():
        return []
    hits: List[str] = []
    for path in sorted(root.rglob("*")):
        if len(hits) >= limit:
            break
        if ".git" in path.parts or "__pycache__" in path.parts or not path.is_file():
            continue
        if path.suffix.lower() not in {".py", ".md", ".json", ".toml", ".yaml", ".yml", ".txt"}:
            continue
        text = ""
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")[:20000].lower()
        except Exception:
            continue
        if any(keyword.lower() in text for keyword in keywords):
            hits.append(str(path.relative_to(root)))
    return hits


def scan_repo(repo_name: str, repo_path: str) -> E19RepoAlignment:
    root = Path(repo_path)
    exists = root.exists()
    branch = _git(root, ["branch", "--show-current"]) if exists else ""
    head = _git(root, ["rev-parse", "HEAD"]) if exists else ""
    groups: List[str] = []
    commercial = "not_applicable"
    governance = "not_applicable"
    provider = "not_applicable"
    historical = "not_applicable"
    direct_dependency = "none"
    modification_needed = "no_change_needed"
    risk = "low"

    if repo_name == "ystar-bridge-labs" and exists:
        if _any_exists(root, ["operations/external_validation/e18_revenue_validation_batch.json", "office/mission_command/e18_route_decision.py"]):
            groups.append("e18_revenue_validation_runtime")
            commercial = "canonical_company_runtime_owner"
            direct_dependency = "direct_source_of_e19_control_room"
            modification_needed = "bridge_labs_update_only"
    elif repo_name == "gov-mcp" and exists:
        if _any_exists(root, ["gov_mcp/outbound/models.py", "gov_mcp/outbound/adapter_contract.py", "tests/test_outbound_models.py"]):
            groups.append("canonical_outbound_no_send_adapter")
            provider = "canonical_provider_boundary_owner"
            governance = "execution_receipt_boundary"
            modification_needed = "no_change_needed"
            risk = "medium_if_real_send_requested_without_provider_implementation"
    elif repo_name == "Y-star-gov" and exists:
        hits = _find_keyword_hits(root, ["IntentContract", "CIEU", "check()", "enforce", "CZL", "DelegationChain"], limit=8)
        if hits:
            groups.append("deterministic_governance_kernel")
            governance = "canonical_governance_contract_cieu_czl_owner"
            modification_needed = "no_change_needed"
            risk = "medium_if_bridge_labs_claims_canonical_writeback_without_Y_star_gov_contract"
    elif repo_name == "ystar-company" and exists:
        hits = _find_keyword_hits(root, ["revenue_execution_enabled", "outreach_enabled", "buyer pain", "offer", "customer"], limit=8)
        if hits:
            groups.append("historical_incubated_commercial_assets")
            historical = "historical_assets_with_revenue_outreach_disabled_by_default"
            modification_needed = "future_ystar_company_migration_required"
            risk = "low_now_medium_if_old_assets_are_treated_as_current_authority"

    return E19RepoAlignment(
        repo_name=repo_name,
        repo_path=repo_path,
        exists=exists,
        branch=branch,
        head=head,
        relevant_file_groups_found=groups,
        commercial_runtime_relevance=commercial,
        governance_relevance=governance,
        provider_boundary_relevance=provider,
        historical_asset_relevance=historical,
        direct_dependency_on_e18=direct_dependency,
        modification_needed=modification_needed,
        risk_if_not_modified=risk,
    )


def build_ecosystem_alignment_scan(repo_roots: Dict[str, str] | None = None) -> Dict[str, Any]:
    roots = repo_roots or REPO_ROOTS
    repos = [scan_repo(name, path).to_dict() for name, path in roots.items()]
    available = [repo for repo in repos if repo["exists"]]
    status = "aligned_partial_followups_required"
    if len(available) == 4 and all(repo["modification_needed"] in {"no_change_needed", "bridge_labs_update_only", "future_ystar_company_migration_required"} for repo in repos):
        status = "ecosystem_aligned_with_documented_followups"
    return {
        "artifact_id": "e19_ecosystem_alignment_scan",
        "alignment_status": status,
        "repos_checked_count": len(repos),
        "repos_available_count": len(available),
        "repos": repos,
        "read_only_scan": True,
        "external_action_executed": False,
    }


def render_ecosystem_alignment_scan(scan: Dict[str, Any]) -> str:
    lines = [
        "# E19 Ecosystem Alignment Scan",
        "",
        f"- alignment_status: {scan['alignment_status']}",
        f"- repos_checked_count: {scan['repos_checked_count']}",
        f"- repos_available_count: {scan['repos_available_count']}",
        "- read_only_scan: true",
        "- external_action_executed: false",
        "",
        "| repo | exists | branch | modification_needed | relevance |",
        "| --- | --- | --- | --- | --- |",
    ]
    for repo in scan["repos"]:
        relevance = repo["commercial_runtime_relevance"] or repo["governance_relevance"] or repo["provider_boundary_relevance"] or repo["historical_asset_relevance"]
        lines.append(f"| {repo['repo_name']} | {str(repo['exists']).lower()} | {repo['branch']} | {repo['modification_needed']} | {relevance} |")
    return "\n".join(lines).rstrip() + "\n"
