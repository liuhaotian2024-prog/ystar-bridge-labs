from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


REQUIRED_SCOPE_FIELDS = [
    "target_scope",
    "channel_scope",
    "draft_scope",
    "count_scope",
    "time_scope",
    "followup_scope",
    "data_scope",
    "feedback_scope",
]


@dataclass(frozen=True)
class E9ActionScope:
    action_id: str
    target_scope: str
    channel_scope: str
    draft_scope: str
    count_scope: str
    time_scope: str
    followup_scope: str
    data_scope: str
    feedback_scope: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def validate_e9_action_scope(scope: E9ActionScope | Dict[str, Any]) -> List[str]:
    item = scope if isinstance(scope, E9ActionScope) else E9ActionScope(**scope)
    errors: List[str] = []
    for field_name in REQUIRED_SCOPE_FIELDS:
        if not str(getattr(item, field_name, "")).strip():
            errors.append(f"missing_{field_name}")
    if "unbounded" in item.count_scope.lower():
        errors.append("unbounded_count_scope")
    if "any" in item.channel_scope.lower():
        errors.append("overbroad_channel_scope")
    return errors


def build_standard_e9_action_scope(action_id: str = "e9_action_001") -> E9ActionScope:
    return E9ActionScope(
        action_id=action_id,
        target_scope="owner-provided targets only",
        channel_scope="owner-selected channel only",
        draft_scope="frozen draft hash only",
        count_scope="max 3 validation messages unless owner manifest says less",
        time_scope="expires at manifest expiry",
        followup_scope="no automated follow-up unless explicitly approved",
        data_scope="no sensitive/private data; no scraped leads",
        feedback_scope="owner-entered or real reply events only; no invented feedback",
    )


def render_e9_scope_minimization_report(scope: E9ActionScope) -> str:
    errors = validate_e9_action_scope(scope)
    lines = ["# E9 Scope Minimization Report", "", f"- action_id: {scope.action_id}", f"- scope_valid: {not errors}", f"- validation_errors: {', '.join(errors) or 'none'}", ""]
    for key, value in scope.to_dict().items():
        if key != "action_id":
            lines.append(f"- {key}: {value}")
    return "\n".join(lines)
