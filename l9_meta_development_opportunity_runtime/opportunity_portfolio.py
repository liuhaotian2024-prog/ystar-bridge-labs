#!/usr/bin/env python3
"""Opportunity portfolio storage helpers."""

from __future__ import annotations

from typing import Any

from .opportunity_model import get_packet, load_packets, now_iso, write_packet


def list_opportunities(status: str | None = None) -> list[dict[str, Any]]:
    opportunities = load_packets("opportunity_candidates")
    if status:
        return [item for item in opportunities if item.get("current_status") == status]
    return opportunities


def get_opportunity(opportunity_id: str) -> dict[str, Any]:
    packet = get_packet("opportunity_candidates", opportunity_id)
    if not packet:
        raise ValueError(f"Unknown opportunity: {opportunity_id}")
    return packet


def save_opportunity(opportunity: dict[str, Any]) -> dict[str, Any]:
    opportunity["updated_at"] = now_iso()
    return write_packet("opportunity_candidates", opportunity["opportunity_id"], opportunity)

