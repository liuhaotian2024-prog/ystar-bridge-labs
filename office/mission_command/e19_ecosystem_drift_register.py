from __future__ import annotations

from typing import Any, Dict, List


def build_ecosystem_drift_register(scan: Dict[str, Any], matrix: Dict[str, Any]) -> Dict[str, Any]:
    blockers: List[Dict[str, Any]] = [
        {
            "blocker_id": "real_provider_send_blocked",
            "category": "missing_provider_implementation",
            "summary": "gov-mcp currently provides no-send/dry-run provider boundary; real provider implementation and tests are still absent.",
            "severity": "high_for_real_send_low_for_manual_owner_send",
            "next_action": "Keep provider send blocked; optionally plan E20 provider adapter preparation.",
        },
        {
            "blocker_id": "missing_feedback_evidence",
            "category": "missing_feedback_evidence",
            "summary": "No owner-imported customer response exists, so paid-signal counts remain placeholders.",
            "severity": "expected",
            "next_action": "Owner may manually send approved candidates and import feedback later.",
        },
        {
            "blocker_id": "ystar_company_historical_assets_not_canonical",
            "category": "stale_historical_assets",
            "summary": "ystar-company includes historical revenue/outreach-disabled assets that should not be treated as current authority.",
            "severity": "medium",
            "next_action": "Future migration milestone may harvest useful patterns.",
        },
        {
            "blocker_id": "canonical_cieu_writeback_blocked",
            "category": "governance_boundary",
            "summary": "Y-star-gov owns canonical CIEU; E19 must not write real-world facts into CIEU/memory.",
            "severity": "high_if_bypassed",
            "next_action": "Keep CIEU/core writeback blocked until explicit governance contract path exists.",
        },
    ]
    return {
        "artifact_id": "e19_ecosystem_drift_register",
        "blockers": blockers,
        "duplicate_capability_risks": [
            "Do not reimplement gov-mcp provider adapter inside bridge-labs.",
            "Do not treat ystar-company historical revenue-disabled artifacts as active commercial runtime.",
        ],
        "repo_modification_required_now": False,
        "next_milestone_recommendation": "E20_real_feedback_import_loop_or_message_revision_before_owner_send",
        "external_action_executed": False,
    }


def render_ecosystem_drift_register(register: Dict[str, Any]) -> str:
    lines = [
        "# E19 Ecosystem Drift Register",
        "",
        f"- repo_modification_required_now: {str(register['repo_modification_required_now']).lower()}",
        f"- next_milestone_recommendation: {register['next_milestone_recommendation']}",
        "- external_action_executed: false",
        "",
        "## Blockers",
    ]
    for item in register["blockers"]:
        lines.extend(
            [
                f"### {item['blocker_id']}",
                f"- category: {item['category']}",
                f"- severity: {item['severity']}",
                f"- summary: {item['summary']}",
                f"- next_action: {item['next_action']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"
