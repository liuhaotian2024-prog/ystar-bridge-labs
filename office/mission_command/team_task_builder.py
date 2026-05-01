from __future__ import annotations

from .mission_model import Mission, TeamTask


def build_team_tasks(mission: Mission) -> list[TeamTask]:
    return [
        TeamTask(
            agent="Aiden Liu",
            function="CEO / Mission Commander",
            task="Frame the owner goal, recommend the default path, and keep all external actions approval-gated.",
            permission_tier=0,
            output="Owner decision brief",
        ),
        TeamTask(
            agent="Sofia Blake",
            function="Market / Positioning",
            task="Turn the first-revenue offer into clear founder/operator language without publication.",
            permission_tier=0,
            output="Review-only positioning and manual message draft",
        ),
        TeamTask(
            agent="Marco Rivera",
            function="Revenue / Pricing",
            task="Compare $750 / $1500 / $3000 diagnostic pricing as hypotheses and define validation signals.",
            permission_tier=0,
            output="Pricing hypothesis and cash-signal criteria",
        ),
        TeamTask(
            agent="Zara Johnson",
            function="Sales Strategy",
            task="Define no-contact buyer archetypes and the approval gate for any later outreach.",
            permission_tier=0,
            output="Buyer archetype review and approval-needed action list",
        ),
        TeamTask(
            agent="Ethan Wright",
            function="Technical Delivery",
            task="Define the audit/brief delivery checklist and what can be delivered manually in 7 days.",
            permission_tier=0,
            output="Delivery checklist and feasibility boundary",
        ),
        TeamTask(
            agent="Jinjin / K9 Scout",
            function="Research / Evidence",
            task="Prepare budgeted read-only research questions and evidence fields; do not contact anyone.",
            permission_tier=1,
            output="Read-only research plan",
        ),
        TeamTask(
            agent="Samantha Lin",
            function="Secretary / Decision Log",
            task="Record mission decisions, avoided admin burden, approval needs, and residual candidates.",
            permission_tier=0,
            output="Mission receipt and decision log",
        ),
        TeamTask(
            agent="Leo / Maya / Ryan / Jordan",
            function="Engineering Support",
            task="Support reusable checklist/tooling only after the offer path is selected.",
            permission_tier=0,
            output="Implementation support notes",
        ),
    ]

