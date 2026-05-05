from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_no_send_message_drafts() -> dict[str, Any]:
    return get_artifact("e40_no_send_message_drafts")


def build_five_minute_walkthroughs() -> dict[str, Any]:
    return get_artifact("e40_five_minute_walkthroughs")
