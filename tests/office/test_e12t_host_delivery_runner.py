import json
import importlib.util
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("host_delivery_runner", ROOT / "scripts" / "host_delivery_runner.py")
runner = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules["host_delivery_runner"] = runner
SPEC.loader.exec_module(runner)


def _request(tmp_path: Path) -> dict:
    return {
        "request_id": "req_test",
        "milestone_id": "E_TEST",
        "repo_root": str(tmp_path),
        "expected_branch": "backflow/aiden-ceo-meeting-room",
        "expected_base_head": "d8ba7636",
        "expected_result_head_optional": "",
        "commit_message": "test: delivery",
        "allowed_files": ["allowed.py"],
        "forbidden_patterns": runner.DEFAULT_FORBIDDEN_PATTERNS,
        "validation_commands": ["python3.11 -m py_compile allowed.py", "pytest tests/office/test_e12r_*.py -q"],
        "push_remote": "origin",
        "push_branch": "backflow/aiden-ceo-meeting-room",
        "remote_confirmation_required": True,
        "created_by": "Codex",
        "created_at": "2026-05-02T00:00:00Z",
        "safety_boundary": {"force_push": False},
        "no_external_side_effects_statement": "No external side effects.",
    }


def test_valid_delivery_request_is_accepted(tmp_path: Path):
    errors = runner.validate_request(_request(tmp_path))
    assert errors == []


def test_arbitrary_shell_injection_in_validation_command_is_rejected(tmp_path: Path):
    request = _request(tmp_path)
    request["validation_commands"] = ["pytest tests/office/test_e12r_*.py -q && git push --force"]
    errors = runner.validate_request(request)
    assert "shell_injection_operator_blocked" in errors


def test_allowed_validation_commands_pass(tmp_path: Path):
    assert runner.validate_command("python3.11 -m py_compile office/mission_command/*.py") == []
    assert runner.validate_command("pytest tests/office/test_e12r_*.py -q") == []


def test_validation_globs_are_expanded_without_shell(tmp_path: Path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg/a.py").write_text("x = 1\n", encoding="utf-8")
    assert runner.expand_validation_args(tmp_path, ["python3.11", "-m", "py_compile", "pkg/*.py"]) == [
        "python3.11",
        "-m",
        "py_compile",
        "pkg/a.py",
    ]


def test_unexpected_dirty_file_is_rejected():
    errors = runner.reject_unexpected_dirty(["other.py"], ["allowed.py"], runner.DEFAULT_FORBIDDEN_PATTERNS)
    assert "unexpected_dirty_file: other.py" in errors


def test_pycache_is_rejected():
    errors = runner.reject_unexpected_dirty(["tests/__pycache__/x.pyc"], ["allowed.py"], runner.DEFAULT_FORBIDDEN_PATTERNS)
    assert "forbidden_file_present: tests/__pycache__/x.pyc" in errors


def test_db_wal_shm_files_are_rejected():
    errors = runner.reject_unexpected_dirty(
        ["state.db", "state.db-wal", "state.db-shm", "runtime.sqlite"],
        ["allowed.py"],
        runner.DEFAULT_FORBIDDEN_PATTERNS,
    )
    assert any("state.db" in error for error in errors)
    assert any("state.db-wal" in error for error in errors)
    assert any("state.db-shm" in error for error in errors)
    assert any("runtime.sqlite" in error for error in errors)


def test_push_failure_is_classified():
    assert runner.classify_git_failure("fatal: Could not resolve host: github.com") == "PUSH_DNS_FAILED"
    assert runner.classify_git_failure("Authentication failed") == "PUSH_AUTH_FAILED"
    assert runner.classify_git_failure("remote unpack failed: unable to create temporary object directory") == "PUSH_REMOTE_OBJECT_FAILURE"


def test_delivery_report_includes_czl(tmp_path: Path):
    result = runner.HostDeliveryResult(
        request_id="req",
        milestone_id="E",
        status="DELIVERY_SUCCEEDED",
        failure_code="DELIVERY_SUCCEEDED",
        repo_root=str(tmp_path),
        expected_branch="branch",
        repository_delivery_rt1=0,
    )
    text = runner.report_text(result)
    assert "## CZL" in text
    assert "Rt+1: 0" in text


def test_host_runner_reusable_for_future_milestones(tmp_path: Path):
    request = _request(tmp_path)
    request["request_id"] = "future_request"
    request["milestone_id"] = "E99_future"
    assert runner.validate_request(request) == []


class FakeRunner:
    def __init__(self, branch="backflow/aiden-ceo-meeting-room", head="d8ba7636abc", status=" M allowed.py\n"):
        self.branch = branch
        self.head = head
        self.status = status
        self.calls = []

    def __call__(self, repo_root: Path, args: Sequence[str], timeout: int = 120, env=None):
        self.calls.append(list(args))
        if args == ["git", "branch", "--show-current"]:
            return runner.CommandResult(list(args), 0, self.branch, "")
        if args == ["git", "rev-parse", "HEAD"]:
            return runner.CommandResult(list(args), 0, self.head, "")
        if args == ["git", "status", "--porcelain"]:
            return runner.CommandResult(list(args), 0, self.status, "")
        if args[:2] == ["git", "add"]:
            return runner.CommandResult(list(args), 0, "", "")
        if args == ["git", "diff", "--cached", "--name-only"]:
            return runner.CommandResult(list(args), 0, "allowed.py", "")
        if args[:2] == ["git", "commit"]:
            return runner.CommandResult(list(args), 0, "[x] commit", "")
        if args[:2] == ["git", "push"]:
            return runner.CommandResult(list(args), 0, "pushed", "")
        if args[:2] == ["git", "ls-remote"]:
            return runner.CommandResult(list(args), 0, "newhead\trefs/heads/backflow/aiden-ceo-meeting-room", "")
        if args and args[0] in {"python3.11", "pytest"}:
            return runner.CommandResult(list(args), 0, "", "")
        return runner.CommandResult(list(args), 99, "", "unexpected")


def _write_request(tmp_path: Path, request: dict) -> Path:
    request_path = tmp_path / "request.json"
    request_path.write_text(json.dumps(request), encoding="utf-8")
    (tmp_path / ".git").mkdir()
    return request_path


def test_wrong_branch_is_rejected(tmp_path: Path, monkeypatch):
    request_path = _write_request(tmp_path, _request(tmp_path))
    monkeypatch.setattr(runner, "run", FakeRunner(branch="main"))
    result = runner.execute_delivery(request_path)
    assert result.failure_code == "WRONG_BRANCH"


def test_base_head_mismatch_is_rejected(tmp_path: Path, monkeypatch):
    request_path = _write_request(tmp_path, _request(tmp_path))
    monkeypatch.setattr(runner, "run", FakeRunner(head="abc123"))
    result = runner.execute_delivery(request_path)
    assert result.failure_code == "BASE_HEAD_MISMATCH"


def test_only_allowed_files_are_staged(tmp_path: Path, monkeypatch):
    fake = FakeRunner()
    request_path = _write_request(tmp_path, _request(tmp_path))
    monkeypatch.setattr(runner, "run", fake)
    result = runner.execute_delivery(request_path)
    assert result.failure_code == "REMOTE_CONFIRMATION_FAILED"
    assert ["git", "add", "--", "allowed.py"] in fake.calls


def test_force_push_is_never_generated(tmp_path: Path, monkeypatch):
    fake = FakeRunner()
    request_path = _write_request(tmp_path, _request(tmp_path))
    monkeypatch.setattr(runner, "run", fake)
    runner.execute_delivery(request_path)
    assert not any("--force" in part or part == "-f" for call in fake.calls for part in call)


def test_failed_validation_blocks_commit(tmp_path: Path, monkeypatch):
    class FailingValidation(FakeRunner):
        def __call__(self, repo_root: Path, args: Sequence[str], timeout: int = 120, env=None):
            if args and args[0] == "python3.11":
                return runner.CommandResult(list(args), 1, "", "compile failed")
            return super().__call__(repo_root, args, timeout, env)

    request_path = _write_request(tmp_path, _request(tmp_path))
    monkeypatch.setattr(runner, "run", FailingValidation())
    result = runner.execute_delivery(request_path)
    assert result.failure_code == "VALIDATION_FAILED"


def test_remote_sha_mismatch_blocks_closure(tmp_path: Path, monkeypatch):
    request_path = _write_request(tmp_path, _request(tmp_path))
    monkeypatch.setattr(runner, "run", FakeRunner())
    result = runner.execute_delivery(request_path)
    assert result.failure_code == "REMOTE_CONFIRMATION_FAILED"
    assert result.repository_delivery_rt1 > 0


def test_remote_sha_match_sets_repository_delivery_rt1_zero(tmp_path: Path, monkeypatch):
    class MatchingRemote(FakeRunner):
        def __call__(self, repo_root: Path, args: Sequence[str], timeout: int = 120, env=None):
            if args == ["git", "rev-parse", "HEAD"]:
                return runner.CommandResult(list(args), 0, "d8ba7636abc", "")
            if args[:2] == ["git", "ls-remote"]:
                return runner.CommandResult(list(args), 0, "d8ba7636abc\trefs/heads/backflow/aiden-ceo-meeting-room", "")
            return super().__call__(repo_root, args, timeout, env)

    request_path = _write_request(tmp_path, _request(tmp_path))
    monkeypatch.setattr(runner, "run", MatchingRemote())
    result = runner.execute_delivery(request_path)
    assert result.repository_delivery_rt1 == 0
    assert result.failure_code == "DELIVERY_SUCCEEDED"
