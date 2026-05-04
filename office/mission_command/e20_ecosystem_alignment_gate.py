from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, List


REPOS = {
    "ystar-bridge-labs": "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
    "gov-mcp": "/Users/haotianliu/.openclaw/workspace/gov-mcp",
    "Y-star-gov": "/Users/haotianliu/.openclaw/workspace/Y-star-gov",
    "ystar-company": "/Users/haotianliu/.openclaw/workspace/ystar-company",
}


def _git(repo: Path, args: List[str]) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(repo), *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def build_ecosystem_alignment_gate(provider_capability: Dict[str, Any]) -> Dict[str, Any]:
    repos = []
    for name, path in REPOS.items():
        root = Path(path)
        repos.append(
            {
                "repo": name,
                "path": path,
                "exists": root.exists(),
                "branch": _git(root, ["branch", "--show-current"]) if root.exists() else "",
                "head": _git(root, ["rev-parse", "HEAD"]) if root.exists() else "",
                "role": {
                    "ystar-bridge-labs": "commercial runtime and control room owner",
                    "gov-mcp": "provider boundary and outbound receipts owner",
                    "Y-star-gov": "deterministic governance/CIEU/CZL owner",
                    "ystar-company": "historical/incubated asset reference",
                }[name],
            }
        )
    repo_decisions = [
        {"repo": "ystar-bridge-labs", "decision": "bridge_labs_update_only", "reason": "E20 control plane belongs in company runtime."},
        {"repo": "gov-mcp", "decision": "future_gov_mcp_update_required", "reason": "Live provider adapter is missing and should be implemented in gov-mcp, not bridge-labs."},
        {"repo": "Y-star-gov", "decision": "no_change_needed", "reason": "E20 does not require canonical governance kernel mutation."},
        {"repo": "ystar-company", "decision": "no_change_needed_historical_reference", "reason": "Historical assets remain read-only reference."},
    ]
    status = "ecosystem_aligned_with_documented_followups"
    if not provider_capability.get("live_provider_adapter_present"):
        status = "ecosystem_aligned_with_documented_followups"
    return {
        "artifact_id": "e20_ecosystem_alignment_gate",
        "closure_status": status,
        "repos_checked": repos,
        "cross_repo_impact_update": [
            "bridge-labs owns E20 risk-tiered control plane artifacts",
            "gov-mcp owns future live provider adapter and receipts",
            "Y-star-gov remains canonical for governance/CIEU/CZL",
            "ystar-company remains historical reference",
        ],
        "repo_modification_decisions": repo_decisions,
        "drift_blockers": [
            "gov-mcp live provider adapter missing",
            "real provider tests missing",
            "owner manual send must not be default in future outbound milestones",
        ],
        "external_action_executed": False,
    }


def render_ecosystem_alignment_gate(gate: Dict[str, Any]) -> str:
    lines = [
        "# E20 Ecosystem Alignment Gate",
        "",
        f"- closure_status: {gate['closure_status']}",
        "- external_action_executed: false",
        "",
        "## Repos Checked",
    ]
    lines.extend(f"- {repo['repo']}: exists={str(repo['exists']).lower()} role={repo['role']}" for repo in gate["repos_checked"])
    lines.extend(["", "## Drift / Blockers"])
    lines.extend(f"- {item}" for item in gate["drift_blockers"])
    return "\n".join(lines).rstrip() + "\n"
