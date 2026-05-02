from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Dict, List

from .repository_delivery_status import RepositoryDeliveryAssessment


@dataclass(frozen=True)
class RepositoryDeliveryCZL:
    y_star: List[str]
    xt: Dict[str, object]
    u: List[str]
    y_t1: Dict[str, object]
    rt1: int
    status: str
    blocked_reason: str
    next_allowed_action: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


REPOSITORY_DELIVERY_Y_STAR = [
    "expected_branch_checked",
    "local_head_checked",
    "worktree_clean_checked",
    "remote_url_checked",
    "github_connectivity_checked",
    "remote_head_compared_to_local_head",
    "repository_delivery_rt1_zero_only_on_remote_match",
    "owner_handoff_generated_if_blocked",
]


def build_repository_delivery_czl(assessment: RepositoryDeliveryAssessment) -> RepositoryDeliveryCZL:
    y_t1 = {
        "expected_branch_checked": bool(assessment.branch),
        "local_head_checked": bool(assessment.local_head),
        "worktree_clean_checked": assessment.preflight.worktree_clean,
        "remote_url_checked": assessment.preflight.remote_url_present,
        "github_connectivity_checked": assessment.connectivity.attempted,
        "remote_head_compared_to_local_head": assessment.remote_confirmation.attempted,
        "repository_delivery_rt1_zero_only_on_remote_match": (
            assessment.repository_delivery_rt1 == 0
            and assessment.remote_confirmation.confirmed
            and assessment.remote_head == assessment.local_head
        )
        or assessment.repository_delivery_rt1 > 0,
        "owner_handoff_generated_if_blocked": assessment.repository_delivery_rt1 == 0 or bool(assessment.owner_handoff),
    }
    residuals = [criterion for criterion in REPOSITORY_DELIVERY_Y_STAR if not y_t1.get(criterion)]
    rt1 = 0 if assessment.repository_delivery_rt1 == 0 and not residuals else max(1, len(residuals))
    status = "complete_repository_delivery_confirmed" if rt1 == 0 else "BLOCKED_REPOSITORY_DELIVERY_NOT_CONFIRMED"
    return RepositoryDeliveryCZL(
        y_star=REPOSITORY_DELIVERY_Y_STAR,
        xt={
            "branch": assessment.branch,
            "expected_branch": assessment.expected_branch,
            "local_head": assessment.local_head,
            "expected_head": assessment.expected_head,
            "remote_head": assessment.remote_head or "unavailable",
            "worktree_clean": assessment.preflight.worktree_clean,
        },
        u=[
            "checked local branch, local head, worktree cleanliness, and remote URL",
            "checked GitHub connectivity with git ls-remote",
            "compared remote branch SHA to local HEAD",
            "generated owner handoff when remote closure was not confirmed",
        ],
        y_t1=y_t1,
        rt1=rt1,
        status=status,
        blocked_reason="" if rt1 == 0 else assessment.failure_code,
        next_allowed_action="enter_next_milestone" if rt1 == 0 else "stop_and_complete_repository_delivery_handoff",
    )


def render_repository_delivery_czl(czl: RepositoryDeliveryCZL) -> str:
    lines = [
        "# Repository Delivery CZL",
        "",
        f"- status: {czl.status}",
        f"- repository_delivery_rt1: {czl.rt1}",
        f"- blocked_reason: {czl.blocked_reason or 'none'}",
        f"- next_allowed_action: {czl.next_allowed_action}",
        "",
        "## Y*",
    ]
    lines.extend(f"- {item}" for item in czl.y_star)
    lines.extend(["", "## Xt"])
    lines.extend(f"- {key}: {value}" for key, value in czl.xt.items())
    lines.extend(["", "## U"])
    lines.extend(f"- {item}" for item in czl.u)
    lines.extend(["", "## Yt+1"])
    lines.extend(f"- {key}: {value}" for key, value in czl.y_t1.items())
    return "\n".join(lines)
