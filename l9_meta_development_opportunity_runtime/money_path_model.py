#!/usr/bin/env python3
"""Money path model helpers."""

from __future__ import annotations

from typing import Any

from .opportunity_model import get_packet, load_packets, now_iso, write_packet


def list_money_paths(status: str | None = None) -> list[dict[str, Any]]:
    paths = load_packets("money_path_candidates")
    if status:
        return [path for path in paths if path.get("status") == status]
    return paths


def get_money_path(money_path_id: str) -> dict[str, Any]:
    path = get_packet("money_path_candidates", money_path_id)
    if not path:
        raise ValueError(f"Unknown money path: {money_path_id}")
    return path


def save_money_path(path: dict[str, Any]) -> dict[str, Any]:
    path["updated_at"] = now_iso()
    return write_packet("money_path_candidates", path["money_path_id"], path)

