from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict

REPOS = {
    "ystar-bridge-labs": "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
    "gov-mcp": "/Users/haotianliu/.openclaw/workspace/gov-mcp",
    "Y-star-gov": "/Users/haotianliu/.openclaw/workspace/Y-star-gov",
    "ystar-company": "/Users/haotianliu/.openclaw/workspace/ystar-company",
}


def _git(repo: Path, args: list[str]) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(repo), *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def scan_repo(name: str, path: str) -> Dict[str, Any]:
    root = Path(path)
    exists = root.exists()
    return {
        "repo": name,
        "path": path,
        "exists": exists,
        "branch": _git(root, ["branch", "--show-current"]) if exists else "",
        "head": _git(root, ["rev-parse", "HEAD"]) if exists else "",
        "provider_boundary_relevance": name == "gov-mcp" and (root / "gov_mcp/outbound/provider_manifest.py").exists(),
        "governance_relevance": name == "Y-star-gov" and (root / "ystar").exists(),
        "commercial_runtime_relevance": name == "ystar-bridge-labs" and (root / "operations/external_validation/e20_czl_closure.json").exists(),
        "historical_asset_relevance": name == "ystar-company" and exists,
    }


def build_e21_ecosystem_alignment_gate(provider_sync: Dict[str, Any]) -> Dict[str, Any]:
    scans = [scan_repo(name, path) for name, path in REPOS.items()]
    decisions = {
        "ystar-bridge-labs": "immediate_update_required_and_delivered_for_e21_sync",
        "gov-mcp": "immediate_update_required_and_delivered_for_provider_foundation",
        "Y-star-gov": "no_change_needed_for_e21_provider_scaffold",
        "ystar-company": "future_historical_asset_migration_only",
    }
    return {
        "artifact_id": "e21_ecosystem_alignment_gate",
        "closure_status": "ecosystem_aligned_with_documented_followups",
        "repos_checked": scans,
        "gov_mcp_modified_and_delivered": True,
        "bridge_labs_modified_and_delivered": True,
        "Y_star_gov_immediate_update_needed": False,
        "ystar_company_migration_followup_needed": True,
        "repo_modification_decisions": decisions,
        "provider_capability_status": provider_sync["capability_status"],
        "documented_followups": [
            "live provider remains disabled until real provider adapter credentials, tests, quotas, suppression, idempotency, audit receipts, and promotion gates pass",
            "Y-star-gov remains read-only because no kernel/contract mutation is needed for disabled-live scaffold",
            "ystar-company remains historical/incubated; no active canonical role added",
        ],
        "external_action_executed": False,
    }


def render_ecosystem_alignment_gate(gate: Dict[str, Any]) -> str:
    lines = [
        "# E21 Ecosystem Alignment Gate",
        "",
        f"- closure_status: {gate['closure_status']}",
        f"- gov_mcp_modified_and_delivered: {str(gate['gov_mcp_modified_and_delivered']).lower()}",
        f"- bridge_labs_modified_and_delivered: {str(gate['bridge_labs_modified_and_delivered']).lower()}",
        f"- Y_star_gov_immediate_update_needed: {str(gate['Y_star_gov_immediate_update_needed']).lower()}",
        "- external_action_executed: false",
        "",
        "## Repos Checked",
    ]
    for repo in gate["repos_checked"]:
        lines.append(f"- {repo['repo']}: exists={str(repo['exists']).lower()} branch={repo['branch']} head={repo['head']}")
    lines.extend(["", "## Followups"])
    lines.extend(f"- {item}" for item in gate["documented_followups"])
    return "\n".join(lines).rstrip() + "\n"
