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

from office.mission_command.e13r_buyer_pain_evidence import (
    build_default_e13r_request,
    build_e13r_evidence_record,
    render_buyer_pain_evidence_report,
    validate_e13r_evidence_record,
    validate_e13r_request,
)
from office.mission_command.e13r_offer_revision import (
    diagnose_e13_result,
    generate_revised_offer_candidates,
    render_offer_revision_report,
    write_offer_candidates,
)
from office.mission_command.e13r_owner_decision_packet import build_e13r_owner_decision_packet, render_e13r_owner_decision_packet
from office.mission_command.e13r_readiness_gate import build_e13r_readiness_report, render_e13r_readiness_report


def load_request(path: Path) -> Dict[str, Any]:
    if not path.exists():
        request = build_default_e13r_request().to_dict()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(request, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return request
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_public_read_only(url: str, max_bytes: int) -> Dict[str, Any]:
    if not url.startswith(("https://", "http://")):
        return {"ok": False, "error": "unsupported_url_scheme", "content": ""}
    request = urllib.request.Request(url, headers={"User-Agent": "YStarBridgeLabs-E13R-BuyerPain-ReadOnly/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            body = response.read(max_bytes)
            return {
                "ok": True,
                "content_type": response.headers.get("Content-Type", ""),
                "content": body.decode("utf-8", errors="replace"),
            }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}", "content": ""}


def render_czl(readiness: Any, blocked_reason: str) -> str:
    offer_revision_rt1 = 0
    buyer_pain_rt1 = readiness.buyer_pain_evidence_rt1
    paid_rt1 = readiness.paid_signal_readiness_rt1
    full_rt1 = 0 if offer_revision_rt1 == 0 and buyer_pain_rt1 == 0 and paid_rt1 == 0 else 1
    return "\n".join(
        [
            "# E13R CZL Closure",
            "",
            f"- E13R offer_revision_rt1: {offer_revision_rt1}",
            f"- E13R buyer_pain_evidence_rt1: {buyer_pain_rt1}",
            f"- E13R paid_signal_readiness_rt1: {paid_rt1}",
            "- E13R repository_delivery_rt1: pending_host_delivery_runner",
            f"- E13R full_mission_rt1: {full_rt1}",
            f"- blocked_reason: {blocked_reason or 'none'}",
            "",
            "## Interpretation",
            "- E13R is public read-only evidence rerun, not outreach and not validation feedback.",
            "- Paid-signal readiness is not revenue and does not approve E14 execution by itself.",
            "",
            "## No External Side Effects",
            "- customer_contact: false",
            "- email_or_message: false",
            "- publication: false",
            "- payment: false",
            "- account_creation: false",
            "- form_submission: false",
            "- login: false",
            "- core_brain_cieu_memory_writeback: false",
        ]
    )


def run_e13r_evidence(repo_root: Path, request_path: Path) -> Dict[str, Any]:
    request = load_request(request_path)
    errors = validate_e13r_request(request)
    write_offer_candidates(repo_root)
    diagnosis = diagnose_e13_result(repo_root)
    candidates = generate_revised_offer_candidates()

    budget = request.get("budget", {})
    max_sources = int(budget.get("max_sources", 0) or 0)
    max_bytes = int(budget.get("max_bytes_per_source", 140000) or 140000)
    records = []
    receipts = []
    blocked_reason = ""
    if errors:
        blocked_reason = "invalid_e13r_request: " + ", ".join(errors)
    elif not request.get("source_urls"):
        blocked_reason = "blocked_no_evidence: no E13R source URLs configured"
    else:
        for index, source in enumerate(request.get("source_urls", [])[:max_sources], start=1):
            url = str(source.get("url", ""))
            fetched = fetch_public_read_only(url, max_bytes)
            receipts.append(
                {
                    "source_id": f"e13r_source_{index:03d}",
                    "source_url": url,
                    "source_type": source.get("source_type", "unknown"),
                    "access_mode": "public_read_only_no_login",
                    "ok": fetched["ok"],
                    "error": fetched.get("error", ""),
                    "content_type": fetched.get("content_type", ""),
                }
            )
            if not fetched["ok"]:
                continue
            for offer_id in source.get("offer_ids", []) or request.get("revised_offer_ids", []):
                record = build_e13r_evidence_record(
                    evidence_id=f"e13r_ev_{len(records)+1:03d}",
                    offer_id=offer_id,
                    source_url_or_ref=url,
                    source_type=str(source.get("source_type", "public_buyer_pain_article")),
                    content=fetched["content"],
                    query_or_locator=str(source.get("query_or_locator", url)),
                )
                if not validate_e13r_evidence_record(record):
                    records.append(record)
        if not records:
            blocked_reason = "blocked_no_evidence: host-side sources were unavailable or invalid"
    readiness = build_e13r_readiness_report(records)
    packet = build_e13r_owner_decision_packet(readiness)

    ops = repo_root / "operations" / "external_validation"
    reports = repo_root / "reports" / "integration"
    ops.mkdir(parents=True, exist_ok=True)
    reports.mkdir(parents=True, exist_ok=True)
    (ops / "e13r_evidence_records.json").write_text(json.dumps({"records": [item.to_dict() for item in records]}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ops / "e13r_evidence_receipts.json").write_text(json.dumps({"receipts": receipts}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ops / "e13r_paid_signal_readiness_report.json").write_text(json.dumps(readiness.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ops / "e13r_owner_decision_packet.json").write_text(json.dumps(packet.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (reports / "e13r_offer_revision.md").write_text(render_offer_revision_report(diagnosis, candidates) + "\n", encoding="utf-8")
    (reports / "e13r_buyer_pain_evidence.md").write_text(render_buyer_pain_evidence_report(request, len(records), readiness.classification, blocked_reason) + "\n", encoding="utf-8")
    (reports / "e13r_paid_signal_readiness.md").write_text(render_e13r_readiness_report(readiness) + "\n", encoding="utf-8")
    (reports / "e13r_owner_decision_packet.md").write_text(render_e13r_owner_decision_packet(packet) + "\n", encoding="utf-8")
    (reports / "e13r_czl_closure.md").write_text(render_czl(readiness, blocked_reason) + "\n", encoding="utf-8")
    return {
        "records": len(records),
        "receipts": len(receipts),
        "classification": readiness.classification,
        "top_revised_offer": readiness.top_revised_offer,
        "buyer_pain_evidence_rt1": readiness.buyer_pain_evidence_rt1,
        "paid_signal_readiness_rt1": readiness.paid_signal_readiness_rt1,
        "blocked_reason": blocked_reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run E13R host-side public read-only buyer-pain evidence rerun.")
    parser.add_argument("request", help="Path to E13R buyer-pain evidence request JSON.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run_e13r_evidence(Path(args.repo_root).resolve(), Path(args.request))
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"E13R readiness classification: {result['classification']}")
        print(f"top_revised_offer: {result['top_revised_offer']}")
        print(f"records: {result['records']}")
        if result["blocked_reason"]:
            print(f"blocked_reason: {result['blocked_reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
