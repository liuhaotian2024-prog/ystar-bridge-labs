#!/usr/bin/env python3
"""Build multi-lens rankings for L9 money paths."""

from __future__ import annotations

from typing import Any

from .money_path_generator import generate_money_paths
from .opportunity_model import LENSES, base_packet, now_iso, write_packet
from .opportunity_scoring import score_money_path


def build_rankings(force: bool = False) -> dict[str, Any]:
    paths = generate_money_paths(force=force)["money_paths"]
    rankings = []
    for lens in LENSES:
        scored = [score_money_path(path, lens) for path in paths]
        ranked = sorted(scored, key=lambda item: item["total_score"], reverse=True)
        ranking = {
            **base_packet("opportunity_ranking"),
            "ranking_id": f"ranking_{lens}",
            "lens": lens,
            "ranked_items": ranked,
            "top_recommendation": ranked[0] if ranked else None,
            "explanation": f"Ranking lens `{lens}` is deterministic and includes risk penalties; it is not a claim of certainty.",
            "created_at": now_iso(),
        }
        rankings.append(write_packet("opportunity_rankings", ranking["ranking_id"], ranking))
    return {"ok": True, "rankings": rankings, "ranking_count": len(rankings)}


def list_rankings() -> list[dict[str, Any]]:
    from .opportunity_model import load_packets

    return load_packets("opportunity_rankings")

