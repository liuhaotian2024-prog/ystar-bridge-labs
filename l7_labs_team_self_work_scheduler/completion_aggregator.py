#!/usr/bin/env python3
"""Aggregate completion reports for L7.6 autonomous self-work runs."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OFFICE_WEB_DIR = ROOT / "scripts/l7_labs_office_web"
if str(OFFICE_WEB_DIR) not in sys.path:
    sys.path.insert(0, str(OFFICE_WEB_DIR))

from whiteboard_store import PACKET_ROOT, atomic_write_json, create_completion_report, load_agent_replies  # noqa: E402


def aggregate_completion(work_item: dict[str, Any], packet_root: Path = PACKET_ROOT) -> dict[str, Any]:
    replies = load_agent_replies(packet_root)
    report = create_completion_report(work_item, replies, packet_root)
    report["summary"] = f"L7.6 autonomous scheduler completed bounded internal work for: {work_item['title']}"
    report["next_owner_action"] = "Review the local completion report; approve separately only if an external action is proposed."
    atomic_write_json(packet_root / "completion_reports" / f"{report['completion_report_id']}.json", report)
    return report
