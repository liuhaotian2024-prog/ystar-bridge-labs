#!/usr/bin/env python3
"""Fixture-safe evidence packet builder for L10 delegated research."""

from __future__ import annotations

from typing import Any

from .mission_model import base_packet, now_iso, write_packet


FIXTURE_SOURCES = [
    ("demo://founder-ai-workflow-bottleneck", "Founder workflow bottleneck notes", "demo.fixture", "Founder/operators need sharper decision loops, evidence, and reliable agent workflow boundaries.", "Founder workflow audit / CEO command brief"),
    ("demo://coding-agent-governance", "Coding-agent governance pain notes", "demo.fixture", "Teams adopting coding agents need review gates, audit trails, and safe execution policies.", "Coding-agent governance audit"),
    ("demo://ai-company-cockpit", "AI company cockpit setup notes", "demo.fixture", "Small AI teams struggle to see agent tasks, approvals, and revenue-loop state in one place.", "AI company cockpit setup"),
]


def build_fixture_evidence_packets(mission_id: str) -> list[dict[str, Any]]:
    packets = []
    for index, (url, title, domain, summary, signal) in enumerate(FIXTURE_SOURCES, start=1):
        evidence_id = f"evidence_{mission_id}_{index}"
        packet = {
            **base_packet("research_evidence_packet"),
            "evidence_id": evidence_id,
            "mission_id": mission_id,
            "source_url": url,
            "source_title": title,
            "source_domain": domain,
            "source_type": "demo_fixture",
            "summary": summary,
            "extracted_signal": signal,
            "relevance_score": 4,
            "credibility_score": 3,
            "conflict_notes": "Fixture evidence for safe local demo; live read-only research requires explicit configuration.",
            "captured_at": now_iso(),
        }
        packets.append(write_packet("research_evidence_packets", evidence_id, packet))
    return packets


def list_evidence_packets() -> list[dict[str, Any]]:
    from .mission_model import load_packets

    return load_packets("research_evidence_packets")

