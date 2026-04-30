#!/usr/bin/env python3
"""Evidence basis packets for L9 opportunities."""

from __future__ import annotations

from typing import Any

from .opportunity_model import base_packet, write_packet


def build_evidence_basis(opportunity_id: str, source_refs: list[str], summary: str, confidence: str = "medium") -> dict[str, Any]:
    evidence_id = f"evidence_{opportunity_id}"
    packet = {
        **base_packet("evidence_basis"),
        "evidence_basis_id": evidence_id,
        "source_type": "local_artifact_and_internal_asset_synthesis",
        "source_refs": source_refs,
        "summary": summary,
        "confidence": confidence,
        "unresolved_questions": [
            "Which buyer segment responds fastest?",
            "What proof asset best reduces trust barrier?",
            "What exact price point creates paid signal?",
        ],
        "external_observation_needed": "optional_controlled_read_only_planning_only",
        "owner_review_needed": True,
        "uncontrolled_external_search_run": False,
    }
    return write_packet("evidence_basis", evidence_id, packet)

