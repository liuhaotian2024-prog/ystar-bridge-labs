from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List

from .mission_model import MissionCommandResult, TeamTask


OWNER_BY_AGENT = {
    "Aiden Liu": "ceo",
    "Ethan Wright": "cto",
    "Sofia Blake": "cmo",
    "Marco Rivera": "cfo",
    "Zara Johnson": "cso",
    "Samantha Lin": "secretary",
    "Jinjin / K9 Scout": "ceo",
    "Leo / Maya / Ryan / Jordan": "cto",
}


@dataclass(frozen=True)
class ObligationDraft:
    owner: str
    entity_id: str
    rule_id: str
    rule_name: str
    description: str
    due_secs: int
    severity: str
    required_event: str
    source_mission_id: str
    owner_review_required: bool
    registration_allowed: bool
    registration_command_preview: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _slug(text: str, limit: int = 36) -> str:
    slug = "".join(ch.lower() if ch.isascii() and ch.isalnum() else "_" for ch in text).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return (slug or "mission_task")[:limit]


def _draft(
    owner: str,
    entity_id: str,
    rule_id: str,
    rule_name: str,
    description: str,
    source_mission_id: str,
    due_secs: int = 172800,
    severity: str = "medium",
    required_event: str = "completion_event",
) -> ObligationDraft:
    preview = (
        "python3.11 scripts/gov_order.py --dry-run "
        f"\"{owner} {rule_name}: {description}\""
    )
    return ObligationDraft(
        owner=owner,
        entity_id=entity_id,
        rule_id=rule_id,
        rule_name=rule_name,
        description=description,
        due_secs=due_secs,
        severity=severity,
        required_event=required_event,
        source_mission_id=source_mission_id,
        owner_review_required=True,
        registration_allowed=False,
        registration_command_preview=preview,
    )


def build_obligation_draft_from_mission(mission_result: MissionCommandResult) -> Dict[str, Any]:
    mission = mission_result.mission
    draft = _draft(
        owner="ceo",
        entity_id="BOARD-2026-05-01-001",
        rule_id="e1_4_mission_owner_decision",
        rule_name="Mission owner decision brief",
        description=(
            "Prepare the owner-review decision brief, including counterfactual risks, approval-needed actions, "
            "and the next executable U. Do not register this obligation without owner review."
        ),
        source_mission_id=mission.mission_id,
        due_secs=172800,
        severity="medium",
    )
    return draft.to_dict()


def build_team_obligation_drafts(team_tasks: Iterable[TeamTask], source_mission_id: str = "mission") -> List[Dict[str, Any]]:
    drafts: List[Dict[str, Any]] = []
    for index, task in enumerate(team_tasks, start=1):
        owner = OWNER_BY_AGENT.get(task.agent, "ceo")
        drafts.append(
            _draft(
                owner=owner,
                entity_id=f"BOARD-2026-05-01-{100 + index:03d}",
                rule_id=f"{_slug(task.agent)}_{_slug(task.function, 18)}_{index:02d}",
                rule_name=f"{task.agent} mission task",
                description=f"{task.task} Expected output: {task.output}.",
                source_mission_id=source_mission_id,
                due_secs=172800 if task.permission_tier == 0 else 259200,
                severity="medium",
            ).to_dict()
        )
    return drafts


def render_obligation_drafts_markdown(drafts: List[Dict[str, Any]]) -> str:
    lines = ["## Obligation Drafts"]
    for draft in drafts:
        lines.extend(
            [
                f"### {draft['rule_name']}",
                f"- owner: {draft['owner']}",
                f"- entity_id: {draft['entity_id']}",
                f"- rule_id: {draft['rule_id']}",
                f"- due_secs: {draft['due_secs']}",
                f"- severity: {draft['severity']}",
                f"- required_event: {draft['required_event']}",
                f"- owner_review_required: {draft['owner_review_required']}",
                f"- registration_allowed: {draft['registration_allowed']}",
                f"- registration_command_preview: `{draft['registration_command_preview']}`",
            ]
        )
    return "\n".join(lines)
