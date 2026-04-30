#!/usr/bin/env python3
"""Simple conflict report builder for delegated research."""

from __future__ import annotations

from typing import Any

from .evidence_packet_builder import list_evidence_packets
from .mission_model import base_packet, now_iso, write_packet


def build_conflict_report(mission_id: str) -> dict[str, Any]:
    refs = [item["evidence_id"] for item in list_evidence_packets() if item["mission_id"] == mission_id]
    packet = {
        **base_packet("conflict_report"),
        "conflict_id": f"conflict_{mission_id}",
        "mission_id": mission_id,
        "conflicting_claims": [
            "Fastest-cash service paths may not compound as strongly as productized support.",
            "Productized support can compound but usually needs more proof before cash.",
        ],
        "source_refs": refs,
        "severity": "medium",
        "resolution_status": "bounded_by_strategy_brief",
        "recommended_next_research": "Validate buyer urgency and proof requirements with owner-approved/manual discovery only.",
        "created_at": now_iso(),
    }
    return write_packet("conflict_reports", packet["conflict_id"], packet)


def list_conflict_reports() -> list[dict[str, Any]]:
    from .mission_model import load_packets

    return load_packets("conflict_reports")

