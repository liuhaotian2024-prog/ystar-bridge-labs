#!/usr/bin/env python3
"""Research budget model for L10 missions."""

from __future__ import annotations

from typing import Any

from .mission_model import base_packet, now_iso, write_packet


def create_research_budget(
    mission_id: str,
    max_search_queries: int = 20,
    max_pages_read: int = 40,
    max_domains: int = 15,
    max_runtime_seconds: int = 300,
    allow_external_observation: bool = True,
) -> dict[str, Any]:
    budget_id = f"research_budget_{mission_id}"
    budget = {
        **base_packet("research_budget"),
        "budget_id": budget_id,
        "mission_id": mission_id,
        "max_search_queries": max_search_queries,
        "max_pages_read": max_pages_read,
        "max_domains": max_domains,
        "max_runtime_seconds": max_runtime_seconds,
        "allowed_domains": [],
        "disallowed_domains": [],
        "allow_public_page_read": True,
        "allow_search": True,
        "allow_external_observation": allow_external_observation,
        "no_login": True,
        "no_form_submit": True,
        "no_contact": True,
        "no_payment": True,
        "no_publication": True,
        "created_at": now_iso(),
    }
    return write_packet("research_budget_receipts", budget_id, budget)

