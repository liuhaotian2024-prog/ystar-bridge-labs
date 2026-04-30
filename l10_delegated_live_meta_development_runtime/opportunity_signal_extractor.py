#!/usr/bin/env python3
"""Extract opportunity signals from L10 evidence packets."""

from __future__ import annotations

from typing import Any

from .evidence_packet_builder import list_evidence_packets
from .mission_model import base_packet, now_iso, safe_id, write_packet


def extract_opportunity_signals(mission_id: str) -> list[dict[str, Any]]:
    evidence = [item for item in list_evidence_packets() if item["mission_id"] == mission_id]
    signals = []
    for item in evidence:
        title = item["extracted_signal"]
        signal_id = f"signal_{mission_id}_{safe_id(title.lower())}"
        packet = {
            **base_packet("opportunity_signal"),
            "signal_id": signal_id,
            "mission_id": mission_id,
            "signal_title": title,
            "customer_pain": item["summary"],
            "market_context": "AI founder/operator teams need bounded agent-workflow help, clearer proof, and faster cash-path decisions.",
            "possible_offer": title,
            "internal_asset_match": ["L7 Labs Office", "L7.6 scheduler", "L8 action loop", "L9 portfolio runtime"],
            "evidence_refs": [item["evidence_id"]],
            "confidence": "medium_fixture_backed",
            "recommended_money_path": _recommended_path(title),
            "created_at": now_iso(),
        }
        signals.append(write_packet("opportunity_signals", signal_id, packet))
    return signals


def list_opportunity_signals() -> list[dict[str, Any]]:
    from .mission_model import load_packets

    return load_packets("opportunity_signals")


def _recommended_path(title: str) -> str:
    lower = title.lower()
    if "cockpit" in lower:
        return "AI company cockpit setup sprint"
    if "governance" in lower:
        return "coding-agent governance audit"
    return "Founder AI workflow audit and CEO command brief sprint"

