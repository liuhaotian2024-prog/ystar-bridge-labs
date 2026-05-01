from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from .internal_world_scan import build_internal_world_scan
from .tier1_research_runtime import resolve_tier1_research_capability


def _packet(packet_id: str, category: str, title: str, evidence_refs: List[str], summary: str) -> Dict[str, Any]:
    return {
        "packet_id": packet_id,
        "category": category,
        "title": title,
        "evidence_refs": evidence_refs,
        "summary": summary,
        "live_market_evidence": False,
        "fixture_or_demo": False,
        "private_or_secret_content_included": False,
    }


def build_internal_evidence_packets(repo_root: Path) -> List[Dict[str, Any]]:
    scan = build_internal_world_scan(repo_root)
    money_paths = scan["money_paths"]  # type: ignore[index]
    packets = [
        _packet(
            "internal_company_assets",
            "internal_assets",
            "Company assets and operating runtime",
            ["README.md", "AGENTS.md", "governance/ACTIVE_OPERATING_CHARTER.md", "office/mission_command"],
            "Y*Bridge Labs has Aiden Meeting Room, Mission Command, M Triangle doctrine, and governance/preflight bridges as current internal assets.",
        ),
        _packet(
            "internal_sales_content_history",
            "commercial_history",
            "Sales/content history and old commercial assets",
            list(scan["old_commercial_assets"])[:8] + list(scan["old_content_assets"])[:8],  # type: ignore[index]
            "Old sales/content assets exist and can inform offer hypotheses, but they are historical evidence rather than current buyer validation.",
        ),
        _packet(
            "internal_directives_governance",
            "directives_governance",
            "Directive retriage and active operating charter",
            ["DIRECTIVE_TRACKER.md", "directive_retriage.json", "governance/ACTIVE_OPERATING_CHARTER.md"],
            "Directive retriage and active charter reduce admin burden and prioritize M-3 value production while preserving M-2 gates.",
        ),
        _packet(
            "internal_y_star_gov_gov_mcp",
            "governance_tools",
            "Y-star-gov and gov-mcp company runtime support",
            ["Y-star-gov/ystar/domains/company_runtime", "gov-mcp/gov_mcp/company_runtime_tools.py"],
            "Related repos provide deterministic permission tiers, mission preflight, admin rationalization, and value alignment checks.",
        ),
        _packet(
            "internal_money_path_map",
            "money_paths",
            "Internal assets mapped to money paths",
            [ref for path in money_paths for ref in path["evidence_refs"]][:20],
            "Internal scan maps current assets to Founder AI Workflow Audit, Agent Workflow Bottleneck Diagnosis, Coding-Agent Governance Audit, Cockpit Setup, Runtime Setup Advisory, and Governance Template Paid Support.",
        ),
    ]
    return packets


def build_external_evidence_packets(repo_root: Path) -> List[Dict[str, Any]]:
    resolution = resolve_tier1_research_capability(repo_root)
    if resolution["live_read_only_available"] and resolution["live_research_executed"]:
        return [
            {
                "packet_id": "external_live_read_only_placeholder",
                "category": "external_live",
                "title": "Live read-only evidence packet",
                "summary": "Live read-only evidence would be recorded here after an explicitly enabled and budgeted run.",
                "live_market_evidence": True,
                "fixture_or_demo": False,
                "budget_receipt": {},
                "private_or_secret_content_included": False,
            }
        ]
    packets = [
        {
            "packet_id": "external_not_available",
            "category": "external_capability",
            "title": "Live external evidence not available",
            "summary": "No live read-only research was executed. Current recommendation remains internal-evidence preliminary.",
            "live_market_evidence": False,
            "fixture_or_demo": False,
            "blocked_reason": "BLOCKED_BY_MISSING_LIVE_RESEARCH_CONFIG",
            "enablement_packet_ref": "reports/integration/e2_live_read_only_enablement_packet.md",
            "private_or_secret_content_included": False,
        }
    ]
    if resolution["fixture_demo_available"]:
        packets.append(
            {
                "packet_id": "external_fixture_demo_available",
                "category": "fixture_demo",
                "title": "Fixture/demo research evidence availability",
                "summary": "ystar-company has fixture-backed research demo plumbing, but fixture evidence is not live market evidence and is not counted for E2 market validation.",
                "live_market_evidence": False,
                "fixture_or_demo": True,
                "private_or_secret_content_included": False,
            }
        )
    return packets


def render_evidence_packets_markdown(title: str, packets: List[Dict[str, Any]]) -> str:
    lines = [f"# {title}", ""]
    for packet in packets:
        lines.extend(
            [
                f"## {packet['title']}",
                f"- packet_id: {packet['packet_id']}",
                f"- category: {packet['category']}",
                f"- live_market_evidence: {packet['live_market_evidence']}",
                f"- fixture_or_demo: {packet.get('fixture_or_demo', False)}",
                f"- private_or_secret_content_included: {packet['private_or_secret_content_included']}",
                f"- summary: {packet['summary']}",
            ]
        )
        refs = packet.get("evidence_refs") or []
        if refs:
            lines.append("- evidence_refs:")
            lines.extend(f"  - {ref}" for ref in refs)
        if packet.get("blocked_reason"):
            lines.append(f"- blocked_reason: {packet['blocked_reason']}")
        if packet.get("enablement_packet_ref"):
            lines.append(f"- enablement_packet_ref: {packet['enablement_packet_ref']}")
        lines.append("")
    lines.append("Safety: evidence packets exclude secrets, private DB/WAL/SHM/log content, and active-agent marker contents.")
    return "\n".join(lines)
