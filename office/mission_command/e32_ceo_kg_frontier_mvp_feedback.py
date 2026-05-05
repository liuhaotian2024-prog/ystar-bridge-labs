from __future__ import annotations

from typing import Any

from .e32_base_reconciliation import KG_FEEDBACK, get_kg_edges, get_kg_nodes

def build_ceo_kg_frontier_mvp_feedback() -> dict[str, Any]:
    return dict(KG_FEEDBACK)

def build_ceo_kg_nodes_delta() -> list[dict[str, Any]]:
    return get_kg_nodes()

def build_ceo_kg_edges_delta() -> list[dict[str, Any]]:
    return get_kg_edges()
