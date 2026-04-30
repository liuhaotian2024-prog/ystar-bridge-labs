#!/usr/bin/env python3
"""Initialize and load the selected L8 first cash path."""

from __future__ import annotations

from typing import Any

from .first_cash_path_model import SELECTED_CASH_PATH_ID, default_first_cash_path, get_packet, write_packet


def initialize_first_cash_path(force: bool = False) -> dict[str, Any]:
    existing = get_packet("first_cash_paths", SELECTED_CASH_PATH_ID)
    if existing and not force:
        return existing
    return write_packet("first_cash_paths", SELECTED_CASH_PATH_ID, default_first_cash_path())


def first_cash_path_status() -> dict[str, Any]:
    path = initialize_first_cash_path()
    return {
        "ok": True,
        "first_cash_path": path,
        "selected_offer": path["selected_offer"],
        "current_stage": path["current_stage"],
        "next_recommended_action": path["next_recommended_action"],
        "grant_rfp_path_created_by_default": False,
        "external_side_effects": False,
        "core_writeback": False,
    }

