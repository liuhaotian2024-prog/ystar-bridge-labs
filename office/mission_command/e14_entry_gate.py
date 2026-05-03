from __future__ import annotations

import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict


E13R_REMOTE_CLOSED_HEAD = "18e524fabd07fbdb1a3913689b293b87add3ba50"


@dataclass(frozen=True)
class E14EntryDecision:
    allowed: bool
    e13r_paid_signal_ready: bool
    e13r_repository_delivery_rt1: int
    current_head: str
    blocked_reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _current_head(repo_root: Path) -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_root, text=True, capture_output=True, check=False)
    return result.stdout.strip()


def _contains_commit(repo_root: Path, ancestor: str, head: str) -> bool:
    if not ancestor or not head:
        return False
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, head],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def validate_e14_entry(repo_root: Path, expected_e13r_head: str = E13R_REMOTE_CLOSED_HEAD) -> E14EntryDecision:
    readiness_path = repo_root / "operations" / "external_validation" / "e13r_paid_signal_readiness_report.json"
    readiness = json.loads(readiness_path.read_text(encoding="utf-8")) if readiness_path.exists() else {}
    paid_ready = readiness.get("classification") == "paid_signal_ready" and readiness.get("paid_signal_readiness_rt1") == 0
    head = _current_head(repo_root)
    repo_rt1 = 0 if head.startswith(expected_e13r_head[:8]) or _contains_commit(repo_root, expected_e13r_head, head) else 1
    blocked = ""
    if not paid_ready:
        blocked = "E13R_paid_signal_ready_required"
    elif repo_rt1 != 0:
        blocked = "E13R_repository_delivery_rt1_must_be_zero"
    return E14EntryDecision(
        allowed=paid_ready and repo_rt1 == 0,
        e13r_paid_signal_ready=paid_ready,
        e13r_repository_delivery_rt1=repo_rt1,
        current_head=head,
        blocked_reason=blocked,
    )
