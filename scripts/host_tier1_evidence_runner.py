#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from office.mission_command.e13_evidence_records import build_evidence_record, validate_evidence_record
from office.mission_command.e13_owner_decision_packet import build_owner_decision_packet, render_owner_decision_packet
from office.mission_command.e13_paid_signal_readiness import build_paid_signal_readiness_report
from office.mission_command.e13_tier1_evidence_mission import (
    build_default_e13_request,
    render_e13_tier1_evidence_mission,
    validate_e13_request,
)


def load_request(path: Path) -> Dict[str, Any]:
    if not path.exists():
        request = build_default_e13_request().to_dict()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return request
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_public_read_only(url: str, max_bytes: int) -> Dict[str, Any]:
    if not url.startswith(("https://", "http://")):
        return {"ok": False, "error": "unsupported_url_scheme", "content": ""}
    request = urllib.request.Request(url, headers={"User-Agent": "YStarBridgeLabs-E13-Tier1-ReadOnly/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            content_type = response.headers.get("Content-Type", "")
            body = response.read(max_bytes)
            text = body.decode("utf-8", errors="replace")
            return {"ok": True, "content_type": content_type, "content": text}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "content": ""}


def render_readiness_markdown(report: Any) -> str:
    lines = [
        "# E13 Paid-Signal Readiness",
        "",
        f"- classification: {report.classification}",
        f"- top_path: {report.top_path}",
        f"- second_best_path: {report.second_best_path}",
        f"- evidence_count: {report.evidence_count}",
        f"- paid_signal_readiness_rt1: {report.paid_signal_readiness_rt1}",
        f"- counterfactual_changed_default: {str(report.counterfactual_changed_default).lower()}",
        "",
        "## Path Results",
    ]
    for item in report.path_results:
        lines.extend(
            [
                f"### {item.opportunity_path}",
                f"- classification: {item.classification}",
                f"- evidence_count: {item.evidence_count}",
                f"- direct_buyer_pain_count: {item.direct_buyer_pain_count}",
                f"- pricing_or_budget_count: {item.pricing_or_budget_count}",
                f"- substitute_count: {item.substitute_count}",
                f"- evidence_router_allows_validation_feedback_claim: {str(item.evidence_router_allows_validation_feedback_claim).lower()}",
                f"- evidence_router_allows_paid_signal_claim: {str(item.evidence_router_allows_paid_signal_claim).lower()}",
                f"- reason: {item.reason}",
                "",
            ]
        )
    lines.extend(["## Limitations"])
    lines.extend(f"- {item}" for item in report.limitations)
    return "\n".join(lines)


def render_czl(request: Dict[str, Any], evidence_count: int, readiness: Any, blocked_reason: str) -> str:
    entry_rt1 = 0 if request.get("entry_repository_delivery_rt1") == 0 else 1
    tier1_rt1 = 0 if request and not validate_e13_request(request) else 1
    readiness_rt1 = readiness.paid_signal_readiness_rt1
    full_rt1 = 0 if entry_rt1 == 0 and tier1_rt1 == 0 and readiness_rt1 == 0 else 1
    return "\n".join(
        [
            "# E13 CZL Closure",
            "",
            f"- E13 entry_rt1: {entry_rt1}",
            f"- E13 tier1_evidence_mission_rt1: {tier1_rt1}",
            f"- E13 paid_signal_readiness_rt1: {readiness_rt1}",
            "- E13 repository_delivery_rt1: pending_host_delivery_runner",
            f"- E13 full_mission_rt1: {full_rt1}",
            f"- blocked_reason: {blocked_reason or 'none'}",
            "",
            "## Interpretation",
            "- Public evidence can support paid-signal readiness only.",
            "- Public evidence is not validation feedback.",
            "- Readiness is not revenue, paid pilot approval, outreach approval, or payment approval.",
            "",
            "## No External Side Effects",
            "- customer_contact: false",
            "- email_or_message_sent: false",
            "- publication: false",
            "- payment: false",
            "- account_creation: false",
            "- form_submission: false",
            "- login: false",
            "- core_brain_cieu_memory_writeback: false",
        ]
    )


def run_evidence_mission(repo_root: Path, request_path: Path) -> Dict[str, Any]:
    request = load_request(request_path)
    errors = validate_e13_request(request)
    budget = request.get("budget", {})
    max_sources = int(budget.get("max_sources", 0) or 0)
    max_bytes = int(budget.get("max_bytes_per_source", 120000) or 120000)
    records = []
    receipts = []
    blocked_reason = ""
    if errors:
        blocked_reason = "invalid_e13_request: " + ", ".join(errors)
    elif not request.get("source_urls"):
        blocked_reason = "blocked_no_evidence: no public source URLs configured for host-side collection"
    else:
        for index, source in enumerate(request.get("source_urls", [])[:max_sources], start=1):
            url = str(source.get("url", ""))
            fetched = fetch_public_read_only(url, max_bytes)
            receipt = {
                "source_id": f"e13_source_{index:03d}",
                "source_url": url,
                "access_mode": "public_read_only_no_login",
                "ok": fetched["ok"],
                "error": fetched.get("error", ""),
            }
            receipts.append(receipt)
            if not fetched["ok"]:
                continue
            paths = source.get("opportunity_paths") or [request.get("default_path")]
            for path in paths:
                record = build_evidence_record(
                    evidence_id=f"e13_ev_{len(records)+1:03d}",
                    opportunity_path=path,
                    source_url_or_ref=url,
                    source_type=str(source.get("source_type", "public_web_page")),
                    content=fetched["content"],
                    query_or_locator=str(source.get("query_or_locator", url)),
                )
                if not validate_evidence_record(record):
                    records.append(record)
        if not records:
            blocked_reason = "blocked_no_evidence: host-side sources were unavailable or invalid"
    readiness = build_paid_signal_readiness_report(records, default_path=request.get("default_path", "Agent Workflow Bottleneck Diagnosis"))
    packet = build_owner_decision_packet(readiness)

    ops = repo_root / "operations" / "external_validation"
    reports = repo_root / "reports" / "integration"
    ops.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    records_json = {"records": [record.to_dict() for record in records]}
    receipts_json = {"receipts": receipts}
    readiness_json = readiness.to_dict()
    owner_packet_json = packet.to_dict()
    (ops / "e13_evidence_records.json").write_text(json.dumps(records_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ops / "e13_evidence_receipts.json").write_text(json.dumps(receipts_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ops / "e13_paid_signal_readiness_report.json").write_text(json.dumps(readiness_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ops / "e13_owner_decision_packet.json").write_text(json.dumps(owner_packet_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (reports / "e13_tier1_evidence_mission.md").write_text(render_e13_tier1_evidence_mission(request, readiness.classification, len(records)) + "\n", encoding="utf-8")
    (reports / "e13_paid_signal_readiness.md").write_text(render_readiness_markdown(readiness) + "\n", encoding="utf-8")
    (reports / "e13_czl_closure.md").write_text(render_czl(request, len(records), readiness, blocked_reason) + "\n", encoding="utf-8")
    (reports / "e13_owner_decision_packet.md").write_text(render_owner_decision_packet(packet) + "\n", encoding="utf-8")
    return {
        "records": len(records),
        "receipts": len(receipts),
        "classification": readiness.classification,
        "blocked_reason": blocked_reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run E13 host-side Tier-1 public read-only evidence mission.")
    parser.add_argument("request", help="Path to E13 evidence request JSON.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_evidence_mission(Path(args.repo_root).resolve(), Path(args.request))
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"E13 evidence mission classification: {result['classification']}")
        print(f"records: {result['records']}")
        if result["blocked_reason"]:
            print(f"blocked_reason: {result['blocked_reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
