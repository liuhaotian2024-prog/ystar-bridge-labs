from __future__ import annotations

from .mission_model import Mission


def align_mission_to_m_triangle(mission: Mission) -> dict:
    text = f"{mission.goal} {mission.recommended_path}".lower()
    m3 = any(keyword in text for keyword in ["收入", "revenue", "first", "cash", "customer", "paid", "客户"])
    m2 = True
    m1 = False
    return {
        "m1": m1,
        "m2": m2,
        "m3": m3,
        "primary": "M-3 Value Production" if m3 else "M-2 Governability",
        "explanation": (
            "The mission is value-production led, with M-2 preserved through preflight and owner approval gates."
            if m3
            else "The mission needs further framing before it clearly advances M-3."
        ),
    }

