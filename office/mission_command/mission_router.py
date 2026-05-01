from __future__ import annotations

from .mission_model import Mission


def route_mission(mission: Mission) -> dict:
    return {
        "recommended_path": mission.recommended_path,
        "autonomous_internal_actions": [
            "Build a 7-day first-revenue decision brief.",
            "Compare top money paths using repo evidence and current capabilities.",
            "Draft buyer archetypes and offer language for owner review.",
            "Prepare read-only research plan within budget.",
            "Create approval packet for any external action, but do not execute it.",
        ],
        "approval_needed_actions": [
            "customer contact / select exact external recipient",
            "send email/message",
            "publish public content",
            "quote price externally",
            "create payment path",
            "write to core DB/brain/memory/CIEU",
        ],
        "admin_burden_avoided": [
            "old daily/weekly/nightly report ceremony",
            "old HN/LinkedIn calendar obedience",
            "old enterprise sales phase without current evidence",
            "treating every old directive as active by default",
        ],
        "next_owner_decision": (
            "Approve the team to run this as a Tier 1 read-only evidence mission, or request_revision on the target path."
        ),
    }
