from __future__ import annotations

from typing import Any, Dict, List


def build_repo_modification_decision_packet(scan: Dict[str, Any]) -> Dict[str, Any]:
    decisions: List[Dict[str, Any]] = []
    for repo in scan["repos"]:
        name = repo["repo_name"]
        if name == "ystar-bridge-labs":
            decision = "bridge_labs_update_only"
            reason = "E19 control room is company runtime and should be delivered in bridge-labs."
        elif name == "gov-mcp":
            decision = "future_gov_mcp_update_required"
            reason = "No immediate mutation; future real provider adapter implementation belongs here."
        elif name == "Y-star-gov":
            decision = "no_change_needed"
            reason = "Governance kernel remains canonical; E19 does not require contract mutation."
        elif name == "ystar-company":
            decision = "future_ystar_company_migration_required"
            reason = "Historical assets can be reviewed later, but should not be active authority now."
        else:
            decision = "no_change_needed"
            reason = "Unknown repo not modified."
        decisions.append({"repo": name, "decision": decision, "reason": reason, "immediate_update_required": decision == "bridge_labs_update_only"})
    return {
        "artifact_id": "e19_repo_modification_decision_packet",
        "decisions": decisions,
        "cross_repo_mutation_performed": False,
        "bridge_labs_only_delivery": True,
        "external_action_executed": False,
    }


def render_repo_modification_decision_packet(packet: Dict[str, Any]) -> str:
    lines = [
        "# E19 Repo Modification Decision Packet",
        "",
        f"- cross_repo_mutation_performed: {str(packet['cross_repo_mutation_performed']).lower()}",
        f"- bridge_labs_only_delivery: {str(packet['bridge_labs_only_delivery']).lower()}",
        "- external_action_executed: false",
        "",
        "| repo | decision | reason |",
        "| --- | --- | --- |",
    ]
    for item in packet["decisions"]:
        lines.append(f"| {item['repo']} | {item['decision']} | {item['reason']} |")
    return "\n".join(lines).rstrip() + "\n"
