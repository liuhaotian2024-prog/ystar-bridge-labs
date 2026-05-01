from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True)
class Mission:
    mission_id: str
    owner_message: str
    goal: str
    mission_type: str
    default_priority: str
    allowed_permission_tier: int
    research_budget: Dict[str, Any]
    recommended_path: str
    evidence_basis: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TeamTask:
    agent: str
    function: str
    task: str
    permission_tier: int
    output: str
    status: str = "planned"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MissionCommandResult:
    mission: Mission
    m_triangle_alignment: Dict[str, Any]
    team_tasks: List[TeamTask]
    autonomous_internal_actions: List[str]
    approval_needed_actions: List[str]
    admin_burden_avoided: List[str]
    ystar_gov_preflight: Dict[str, Any]
    gov_mcp_preflight: Dict[str, Any]
    next_owner_decision: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission": self.mission.to_dict(),
            "m_triangle_alignment": self.m_triangle_alignment,
            "team_tasks": [task.to_dict() for task in self.team_tasks],
            "autonomous_internal_actions": self.autonomous_internal_actions,
            "approval_needed_actions": self.approval_needed_actions,
            "admin_burden_avoided": self.admin_burden_avoided,
            "ystar_gov_preflight": self.ystar_gov_preflight,
            "gov_mcp_preflight": self.gov_mcp_preflight,
            "next_owner_decision": self.next_owner_decision,
        }

