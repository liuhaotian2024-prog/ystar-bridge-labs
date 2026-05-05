from __future__ import annotations

import re
from typing import Any

from .e35_one_brain_integration_guard import get_artifact

SUPPORT_CONFIDENCE = {"strong": 0.92, "medium": 0.72, "weak": 0.42, "contradiction": 0.35, "context only": 0.25}


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def normalize_e38_evidence(receipts_data: dict[str, Any], claims_data: dict[str, Any], cluster_data: dict[str, Any], ranking_data: dict[str, Any], scan_data: dict[str, Any], gap_data: dict[str, Any], backlog_data: dict[str, Any]) -> dict[str, Any]:
    receipt_rows = receipts_data.get("receipts", [])
    claim_rows = claims_data.get("claims", [])
    cluster_rows = cluster_data.get("cluster_updates", [])
    receipts_by_id = {r["receipt_id"]: r for r in receipt_rows}
    missing_fields: list[dict[str, str]] = []
    sources: list[dict[str, Any]] = []
    for receipt in receipt_rows:
        for field in ["receipt_id", "cluster", "source_title", "source_url", "source_type", "direct_support_level"]:
            if field not in receipt:
                missing_fields.append({"record": receipt.get("receipt_id", "<unknown>"), "missing_field": field})
        sources.append({
            "source_id": "source_" + receipt["receipt_id"],
            "receipt_id": receipt["receipt_id"],
            "cluster": receipt["cluster"],
            "title": receipt["source_title"],
            "url": receipt["source_url"],
            "source_type": receipt["source_type"],
            "publisher": receipt.get("publisher", ""),
            "support_level": receipt.get("direct_support_level", "context only"),
            "confidence": SUPPORT_CONFIDENCE.get(receipt.get("direct_support_level"), 0.25),
            "limitations": receipt.get("limitation", ""),
            "evidence_boundary": "public_observation_only",
            "not_customer_validation": receipt.get("not_customer_validation") is True,
            "not_paid_signal": receipt.get("not_paid_signal") is True,
        })
    normalized_claims: list[dict[str, Any]] = []
    for claim in claim_rows:
        for field in ["claim_id", "cluster", "source_receipt_id", "support_level", "claim_text"]:
            if field not in claim:
                missing_fields.append({"record": claim.get("claim_id", "<unknown>"), "missing_field": field})
        receipt = receipts_by_id.get(claim.get("source_receipt_id", ""), {})
        normalized_claims.append({
            "claim_id": claim["claim_id"],
            "cluster": claim["cluster"],
            "source_receipt_id": claim["source_receipt_id"],
            "source_url": receipt.get("source_url", ""),
            "claim_category": claim.get("claim_category", ""),
            "claim_text": claim.get("claim_text", ""),
            "support_level": claim.get("support_level", "context only"),
            "confidence": SUPPORT_CONFIDENCE.get(claim.get("support_level"), 0.25),
            "contradiction": claim.get("contradiction") is True,
            "inference_required": claim.get("inference_required") is True,
            "allowed_in_buyer_facing_copy": claim.get("allowed_in_buyer_facing_copy") is True,
            "limitations": claim.get("limitations", ""),
            "what_cannot_be_claimed": claim.get("what_cannot_be_claimed", []),
            "evidence_boundary": "public_observation_only",
            "not_customer_validation": claim.get("public_observation_only") is True,
            "not_paid_signal": True,
        })
    ranking_by_cluster = {row["cluster"]: row for row in ranking_data.get("ranking", [])}
    clusters = [{
        "cluster": row["cluster"],
        "sources_collected": row.get("sources_collected", 0),
        "claims_extracted": row.get("claims_extracted", 0),
        "contradictions_found": row.get("contradictions_found", 0),
        "evidence_level_before_E38": row.get("evidence_level_before_E38"),
        "evidence_level_after_E38": row.get("evidence_level_after_E38"),
        "route_implication": row.get("route_implication", ""),
        "confidence_change": row.get("confidence_change", ""),
        "weakest_assumption": row.get("weakest_assumption", ""),
        "ranking": ranking_by_cluster.get(row["cluster"], {}),
        "evidence_boundary": "public_observation_only",
    } for row in cluster_rows]
    issues: list[str] = []
    if len(receipt_rows) != receipts_data.get("receipt_count"):
        issues.append("receipt_count_mismatch")
    if len(claim_rows) != claims_data.get("claim_count"):
        issues.append("claim_count_mismatch")
    if any(not s["url"].startswith("https://") for s in sources):
        issues.append("non_https_source_url")
    return {
        "artifact_id": "e39_e38_evidence_ingestion_manifest",
        "input_artifacts": ["e38_public_evidence_receipts", "e38_claim_extraction_evidence_grading", "e38_cluster_evidence_update", "e38_comparative_cluster_ranking", "e38_frontier_capability_import_scan", "e38_ceo_capability_gap_mapping", "e38_frontier_capability_import_backlog"],
        "normalized_source_count": len(sources),
        "normalized_claim_count": len(normalized_claims),
        "normalized_cluster_count": len(clusters),
        "frontier_capabilities_consumed": scan_data.get("capability_count", 0),
        "frontier_backlog_items_consumed": backlog_data.get("item_count", 0),
        "sources": sources,
        "claims": normalized_claims,
        "clusters": clusters,
        "unsupported_claims_removed_or_downgraded": claims_data.get("unsupported_claims_removed_or_downgraded", []),
        "missing_fields": missing_fields,
        "data_quality_issues": issues,
        "graph_construction_can_proceed": not missing_fields and not issues,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "external_execution_occurred": False,
    }


def build_e38_evidence_ingestion_manifest() -> dict[str, Any]:
    return normalize_e38_evidence(
        get_artifact("e38_public_evidence_receipts"),
        get_artifact("e38_claim_extraction_evidence_grading"),
        get_artifact("e38_cluster_evidence_update"),
        get_artifact("e38_comparative_cluster_ranking"),
        get_artifact("e38_frontier_capability_import_scan"),
        get_artifact("e38_ceo_capability_gap_mapping"),
        get_artifact("e38_frontier_capability_import_backlog"),
    )
