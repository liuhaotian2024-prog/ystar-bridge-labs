from pathlib import Path
from typing import Sequence

from office.mission_command.repository_delivery_status import (
    DeliveryFailureCode,
    GitCommandResult,
    assess_repository_delivery,
    attempt_push_with_confirmation,
    build_owner_handoff,
    classify_git_failure,
    e13_entry_allowed,
    run_delivery_preflight,
    unsafe_dirty_paths,
)


class FakeGit:
    def __init__(
        self,
        branch: str = "backflow/aiden-ceo-meeting-room",
        head: str = "d8ba7636fd623cd402309c5bfaf3adeabdfbcce3",
        status: str = "",
        remote_url: str = "https://github.com/example/repo.git",
        remote_head: str = "d8ba7636fd623cd402309c5bfaf3adeabdfbcce3",
        ls_remote_error: str = "",
        push_error: str = "",
    ):
        self.branch = branch
        self.head = head
        self.status = status
        self.remote_url = remote_url
        self.remote_head = remote_head
        self.ls_remote_error = ls_remote_error
        self.push_error = push_error
        self.calls = []

    def __call__(self, repo_root: Path, args: Sequence[str], timeout_seconds: int = 20) -> GitCommandResult:
        self.calls.append(list(args))
        if args == ["branch", "--show-current"]:
            return GitCommandResult(list(args), 0, self.branch, "")
        if args == ["rev-parse", "HEAD"]:
            return GitCommandResult(list(args), 0, self.head, "")
        if args == ["status", "--porcelain"]:
            return GitCommandResult(list(args), 0, self.status, "")
        if args == ["remote", "get-url", "origin"]:
            if self.remote_url:
                return GitCommandResult(list(args), 0, self.remote_url, "")
            return GitCommandResult(list(args), 2, "", "No such remote")
        if args[:2] == ["ls-remote", "origin"]:
            if self.ls_remote_error:
                return GitCommandResult(list(args), 128, "", self.ls_remote_error)
            return GitCommandResult(list(args), 0, f"{self.remote_head}\trefs/heads/{args[2]}", "")
        if args[:2] == ["push", "origin"]:
            if self.push_error:
                return GitCommandResult(list(args), 1, "", self.push_error)
            return GitCommandResult(list(args), 0, "pushed", "")
        return GitCommandResult(list(args), 99, "", "unexpected fake git call")


def test_clean_worktree_passes_preflight():
    fake = FakeGit()
    preflight = run_delivery_preflight(Path("."), "backflow/aiden-ceo-meeting-room", "d8ba7636", runner=fake)
    assert preflight.push_allowed is True
    assert preflight.worktree_clean is True


def test_dirty_worktree_blocks_push():
    fake = FakeGit(status=" M reports/integration/mission_grade_ecosystem_demo.md\n")
    preflight = run_delivery_preflight(Path("."), "backflow/aiden-ceo-meeting-room", "d8ba7636", runner=fake)
    assert preflight.push_allowed is False
    assert preflight.failure_code == DeliveryFailureCode.WORKTREE_DIRTY


def test_wrong_branch_blocks_push():
    fake = FakeGit(branch="main")
    preflight = run_delivery_preflight(Path("."), "backflow/aiden-ceo-meeting-room", "d8ba7636", runner=fake)
    assert preflight.push_allowed is False
    assert preflight.failure_code == DeliveryFailureCode.WRONG_BRANCH


def test_local_ahead_remote_missing_produces_residual():
    fake = FakeGit(remote_head="e780aaf88f51cf83259db81b43def5d1c1c78df8")
    assessment = assess_repository_delivery(Path("."), "backflow/aiden-ceo-meeting-room", "d8ba7636", runner=fake)
    assert assessment.repository_delivery_rt1 > 0
    assert assessment.failure_code == DeliveryFailureCode.LOCAL_AHEAD_REMOTE_MISSING


def test_remote_sha_matching_local_head_produces_rt1_zero():
    fake = FakeGit()
    assessment = assess_repository_delivery(Path("."), "backflow/aiden-ceo-meeting-room", "d8ba7636", runner=fake)
    assert assessment.repository_delivery_rt1 == 0
    assert assessment.next_milestone_allowed is True


def test_dns_failure_is_classified():
    assert classify_git_failure("fatal: Could not resolve host: github.com") == DeliveryFailureCode.DNS_GITHUB_UNRESOLVED


def test_remote_unpack_failure_is_classified():
    text = "remote unpack failed: unable to create temporary object directory"
    assert classify_git_failure(text) == DeliveryFailureCode.REMOTE_OBJECT_DIRECTORY_FAILURE


def test_auth_failure_is_classified_separately():
    assert classify_git_failure("Authentication failed for https://github.com/x/y") == DeliveryFailureCode.AUTHENTICATION_FAILURE


def test_push_success_but_remote_confirmation_mismatch_keeps_residual():
    fake = FakeGit(remote_head="e780aaf88f51cf83259db81b43def5d1c1c78df8")
    assessment = assess_repository_delivery(Path("."), "backflow/aiden-ceo-meeting-room", "d8ba7636", attempt_push=True, runner=fake)
    assert assessment.push_attempt.succeeded is True
    assert assessment.repository_delivery_rt1 > 0


def test_owner_handoff_includes_exact_safe_commands():
    fake = FakeGit(ls_remote_error="fatal: Could not resolve host: github.com")
    preflight = run_delivery_preflight(Path("/repo"), "backflow/aiden-ceo-meeting-room", "d8ba7636", runner=fake)
    handoff = build_owner_handoff(preflight, failure_code=DeliveryFailureCode.DNS_GITHUB_UNRESOLVED)
    assert "git push origin backflow/aiden-ceo-meeting-room" in handoff
    assert "git ls-remote origin backflow/aiden-ceo-meeting-room" in handoff


def test_no_force_push_is_ever_generated():
    fake = FakeGit()
    preflight = run_delivery_preflight(Path("."), "backflow/aiden-ceo-meeting-room", "d8ba7636", runner=fake)
    attempt_push_with_confirmation(Path("."), preflight, runner=fake)
    assert not any("--force" in part or "-f" == part for call in fake.calls for part in call)


def test_pycache_and_demo_drift_are_unsafe_to_commit():
    unsafe = unsafe_dirty_paths(["tests/__pycache__/x.pyc", "reports/integration/mission_grade_ecosystem_demo.md"])
    assert "tests/__pycache__/x.pyc" in unsafe
    assert "reports/integration/mission_grade_ecosystem_demo.md" in unsafe


def test_e13_entry_is_blocked_if_repository_delivery_rt1_nonzero():
    assert e13_entry_allowed(1) is False


def test_e13_entry_is_allowed_only_if_repository_delivery_rt1_zero():
    assert e13_entry_allowed(0) is True
