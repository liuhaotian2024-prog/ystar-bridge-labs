from __future__ import annotations

from typing import Any

from .e35_one_brain_integration_guard import get_artifact


def build_expert_review_rubric() -> dict[str, Any]:
    return get_artifact("e40_expert_review_rubric")


def build_feedback_capture_schema() -> dict[str, Any]:
    return get_artifact("e40_feedback_capture_schema")
