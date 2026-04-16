#!/usr/bin/env python3
"""
CIEU Emit Helpers — W23 agent_id enforcement
All CIEU emit points MUST import _get_current_agent() instead of hardcoding.
"""
from pathlib import Path

ACTIVE_AGENT_PATH = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_active_agent")


def _get_current_agent() -> str:
    """
    Read current agent identity from .ystar_active_agent.
    NEVER fallback to "unknown" — if file missing/empty, return "system".

    Returns:
        str: Active agent ID (e.g., "Marco-CFO", "ceo", "eng-governance")
    """
    if not ACTIVE_AGENT_PATH.exists():
        return "system"

    agent_id = ACTIVE_AGENT_PATH.read_text().strip()
    return agent_id if agent_id else "system"
