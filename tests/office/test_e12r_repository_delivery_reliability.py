from pathlib import Path
from typing import Sequence

from office.mission_command.repository_delivery_czl import build_repository_delivery_czl, render_repository_delivery_czl
from office.mission_command.repository_delivery_health import render_repository_delivery_health
from office.mission_command.repository_delivery_status import GitCommandResult, assess_repository_delivery


class FakeGit:
    def __init__(self, remote_head: str, ls_remote_error: str = ""):
        self.remote_head = remote_head
        self.ls_remote_error = ls_remote_error

    def __call__(self, repo_root: Path, args: Sequence[str], timeout_seconds: int = 20) -> GitCommandResult:
        if args == ["branch", "--show-current"]:
            return GitCommandResult(list(args), 0, "backflow/aiden-ceo-meeting-room", "")
        if args == ["rev-parse", "HEAD"]:
            return GitCommandResult(list(args), 0, "d8ba7636fd623cd402309c5bfaf3adeabdfbcce3", "")
        if args == ["status", "--porcelain"]:
            return GitCommandResult(list(args), 0, "", "")
        if args == ["remote", "get-url", "origin"]:
            return GitCommandResult(list(args), 0, "https://github.com/example/repo.git", "")
        if args[:2] == ["ls-remote", "origin"]:
            if self.ls_remote_error:
                return GitCommandResult(list(args), 128, "", self.ls_remote_error)
            return GitCommandResult(list(args), 0, f"{self.remote_head}\trefs/heads/{args[2]}", "")
        if args[:2] == ["push", "origin"]:
            return GitCommandResult(list(args), 0, "pushed", "")
        return GitCommandResult(list(args), 99, "", "unexpected fake git call")


def test_health_report_requires_remote_confirmation_for_closure():
    fake = FakeGit(remote_head="d8ba7636fd623cd402309c5bfaf3adeabdfbcce3")
    assessment = assess_repository_delivery(Path("."), "backflow/aiden-ceo-meeting-room", "d8ba7636", runner=fake)
    report = render_repository_delivery_health(assessment)
    assert "repository_delivery_rt1: 0" in report
    assert "remote_confirmation_confirmed: true" in report


def test_health_report_blocks_on_dns_without_faking_remote_closure():
    fake = FakeGit(remote_head="", ls_remote_error="fatal: unable to access x: Could not resolve host: github.com")
    assessment = assess_repository_delivery(Path("."), "backflow/aiden-ceo-meeting-room", "d8ba7636", runner=fake)
    report = render_repository_delivery_health(assessment)
    assert "repository_delivery_rt1: 1" in report
    assert "DNS_GITHUB_UNRESOLVED" in report
    assert "e13_entry_allowed: false" in report


def test_e12r_czl_closes_only_when_remote_head_matches_local_head():
    fake = FakeGit(remote_head="d8ba7636fd623cd402309c5bfaf3adeabdfbcce3")
    assessment = assess_repository_delivery(Path("."), "backflow/aiden-ceo-meeting-room", "d8ba7636", runner=fake)
    czl = build_repository_delivery_czl(assessment)
    rendered = render_repository_delivery_czl(czl)
    assert czl.rt1 == 0
    assert "next_allowed_action: enter_next_milestone" in rendered


def test_e12r_czl_blocks_next_milestone_when_remote_missing():
    fake = FakeGit(remote_head="e780aaf88f51cf83259db81b43def5d1c1c78df8")
    assessment = assess_repository_delivery(Path("."), "backflow/aiden-ceo-meeting-room", "d8ba7636", runner=fake)
    czl = build_repository_delivery_czl(assessment)
    rendered = render_repository_delivery_czl(czl)
    assert czl.rt1 > 0
    assert "next_allowed_action: stop_and_complete_repository_delivery_handoff" in rendered
