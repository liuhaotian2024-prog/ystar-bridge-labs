#!/usr/bin/env python3
"""Load and select local Labs work items for autonomous scheduler runs."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from .capability_classifier import classify_work_item


ROOT = Path(__file__).resolve().parents[1]
OFFICE_WEB_DIR = ROOT / "scripts/l7_labs_office_web"
if str(OFFICE_WEB_DIR) not in sys.path:
    sys.path.insert(0, str(OFFICE_WEB_DIR))

from whiteboard_store import PACKET_ROOT, load_work_items  # noqa: E402


PENDING_STATUSES = {"Inbox", "Interpreting", "Assigned", "In Progress"}


def pending_work_items(packet_root: Path = PACKET_ROOT) -> list[dict[str, Any]]:
    return [item for item in load_work_items(packet_root) if item.get("status", "Inbox") in PENDING_STATUSES]


def classify_pending_items(packet_root: Path = PACKET_ROOT) -> list[dict[str, Any]]:
    classified = []
    for item in pending_work_items(packet_root):
        classified.append({"work_item": item, "classification": classify_work_item(item)})
    return classified


def select_eligible_work_items(packet_root: Path = PACKET_ROOT, limit: int = 3) -> list[dict[str, Any]]:
    eligible = []
    for entry in classify_pending_items(packet_root):
        if entry["classification"]["classification"] == "autonomous_internal_allowed":
            eligible.append(entry["work_item"])
        if len(eligible) >= limit:
            break
    return eligible


def first_pending_item(packet_root: Path = PACKET_ROOT) -> dict[str, Any] | None:
    items = pending_work_items(packet_root)
    return items[0] if items else None

