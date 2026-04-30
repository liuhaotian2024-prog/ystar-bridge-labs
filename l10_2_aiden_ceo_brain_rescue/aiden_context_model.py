"""Shared local paths and constants for Aiden's context-grounded chat layer."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "l10_2_aiden_ceo_brain_rescue"
PACKET_ROOT = OUT / "runtime_packets"
PACKET_DIRS = {
    "context": PACKET_ROOT / "aiden_context_snapshots",
    "memory": PACKET_ROOT / "aiden_meeting_memory",
    "responses": PACKET_ROOT / "aiden_responses",
    "diagnostics": PACKET_ROOT / "aiden_diagnostics",
    "manifests": PACKET_ROOT / "manifests",
}

FORBIDDEN_ACTIONS = [
    "external outreach",
    "email sending",
    "customer contact",
    "publication",
    "payment",
    "form submission",
    "account creation",
    "grant/RFP submission",
    "MCP/live behavior",
    "actual memory/brain/canonical/CIEU DB writeback",
    "Y-star-gov modification",
    "gov-mcp modification",
    "ystar-bridge-labs modification",
    "secret/env reading",
    "DB/WAL/SHM/log/active-agent marker content reading",
]

TEAM_ROSTER = [
    {"agent_id": "haotian_board_founder", "display_name": "Haotian Liu", "role": "Board / Founder"},
    {"agent_id": "aiden_ceo", "display_name": "Aiden Liu", "role": "CEO"},
    {"agent_id": "ethan_cto", "display_name": "Ethan Wright", "role": "CTO"},
    {"agent_id": "sofia_cmo", "display_name": "Sofia Blake", "role": "CMO"},
    {"agent_id": "marco_cfo", "display_name": "Marco Rivera", "role": "CFO"},
    {"agent_id": "zara_cso", "display_name": "Zara Johnson", "role": "CSO"},
    {"agent_id": "samantha_secretary", "display_name": "Samantha Lin", "role": "Secretary"},
    {"agent_id": "leo_engineer", "display_name": "Leo", "role": "Engineer"},
    {"agent_id": "maya_engineer", "display_name": "Maya", "role": "Engineer"},
    {"agent_id": "ryan_engineer", "display_name": "Ryan", "role": "Engineer"},
    {"agent_id": "jordan_engineer", "display_name": "Jordan", "role": "Engineer"},
    {"agent_id": "jinjin_k9_scout", "display_name": "Jinjin / K9 Scout", "role": "Research"},
]


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def timestamp_id(prefix: str) -> str:
    return f"{prefix}_{time.strftime('%Y%m%dT%H%M%SZ', time.gmtime())}_{time.time_ns() % 1_000_000:06d}"


def ensure_dirs() -> None:
    for path in PACKET_DIRS.values():
        path.mkdir(parents=True, exist_ok=True)
        gitkeep = path / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.write_text("local Aiden runtime packet directory\n", encoding="utf-8")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))
