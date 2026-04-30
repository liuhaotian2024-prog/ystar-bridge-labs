#!/usr/bin/env python3
"""Source summaries for L10 evidence packets."""

from __future__ import annotations

from typing import Any

from .evidence_packet_builder import list_evidence_packets
from .mission_model import base_packet, now_iso, write_packet


def build_source_summary(mission_id: str) -> dict[str, Any]:
    evidence = [item for item in list_evidence_packets() if item["mission_id"] == mission_id]
    summary_id = f"source_summary_{mission_id}"
    packet = {
        **base_packet("source_summary"),
        "summary_id": summary_id,
        "mission_id": mission_id,
        "source_refs": [item["evidence_id"] for item in evidence],
        "main_findings": [item["summary"] for item in evidence],
        "opportunity_implications": [item["extracted_signal"] for item in evidence],
        "uncertainty": "Fixture evidence is directional; live read-only research remains optional and budgeted.",
        "created_at": now_iso(),
    }
    return write_packet("source_summaries", summary_id, packet)


def list_source_summaries() -> list[dict[str, Any]]:
    from .mission_model import load_packets

    return load_packets("source_summaries")

