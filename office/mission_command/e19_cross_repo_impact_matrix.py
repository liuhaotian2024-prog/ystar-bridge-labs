from __future__ import annotations

from typing import Any, Dict, List


def build_cross_repo_impact_matrix(scan: Dict[str, Any]) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = [
        {
            "capability_or_artifact": "E18 revenue validation batch runtime",
            "source_repo": "ystar-bridge-labs",
            "consumer_repo": "ystar-bridge-labs",
            "alignment_status": "aligned",
            "evidence_path": "operations/external_validation/e18_revenue_validation_batch.json",
            "required_action": "Use as local commercial runtime source for E19 control room.",
        },
        {
            "capability_or_artifact": "gov-mcp outbound no-send/provider boundary",
            "source_repo": "gov-mcp",
            "consumer_repo": "ystar-bridge-labs",
            "alignment_status": "aligned",
            "evidence_path": "gov_mcp/outbound/adapter_contract.py",
            "required_action": "Keep real provider send blocked; consume boundary semantics only.",
        },
        {
            "capability_or_artifact": "Y-star-gov check/enforce/CIEU/CZL semantics",
            "source_repo": "Y-star-gov",
            "consumer_repo": "ystar-bridge-labs",
            "alignment_status": "partially_aligned",
            "evidence_path": "README.md",
            "required_action": "Do not claim canonical CIEU writeback; future activation needs Y-star-gov contract path.",
        },
        {
            "capability_or_artifact": "historical commercial/revenue disabled assets",
            "source_repo": "ystar-company",
            "consumer_repo": "ystar-bridge-labs",
            "alignment_status": "followup_required",
            "evidence_path": "approval_authority_model/approval_authority_scope_matrix.json",
            "required_action": "Treat as historical reference; future migration can harvest useful patterns.",
        },
        {
            "capability_or_artifact": "E19 owner control room",
            "source_repo": "ystar-bridge-labs",
            "consumer_repo": "owner",
            "alignment_status": "aligned",
            "evidence_path": "operations/external_validation/e19_revenue_validation_control_room.json",
            "required_action": "Owner reviews one surface instead of scattered JSON files.",
        },
    ]
    return {
        "artifact_id": "e19_cross_repo_impact_matrix",
        "alignment_status": scan["alignment_status"],
        "rows": rows,
        "external_action_executed": False,
    }


def render_cross_repo_impact_matrix(matrix: Dict[str, Any]) -> str:
    lines = [
        "# E19 Cross-Repo Impact Matrix",
        "",
        f"- alignment_status: {matrix['alignment_status']}",
        "- external_action_executed: false",
        "",
        "| capability / artifact | source repo | consumer repo | status | required action |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in matrix["rows"]:
        lines.append(f"| {row['capability_or_artifact']} | {row['source_repo']} | {row['consumer_repo']} | {row['alignment_status']} | {row['required_action']} |")
    return "\n".join(lines).rstrip() + "\n"
