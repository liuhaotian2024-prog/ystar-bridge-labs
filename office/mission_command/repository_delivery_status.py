from __future__ import annotations

import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence


class DeliveryFailureCode:
    DNS_GITHUB_UNRESOLVED = "DNS_GITHUB_UNRESOLVED"
    REMOTE_OBJECT_DIRECTORY_FAILURE = "REMOTE_OBJECT_DIRECTORY_FAILURE"
    AUTHENTICATION_FAILURE = "AUTHENTICATION_FAILURE"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    WORKTREE_DIRTY = "WORKTREE_DIRTY"
    WRONG_BRANCH = "WRONG_BRANCH"
    LOCAL_AHEAD_REMOTE_MISSING = "LOCAL_AHEAD_REMOTE_MISSING"
    REMOTE_CONFIRMATION_FAILED = "REMOTE_CONFIRMATION_FAILED"
    PUSH_SUCCEEDED_CONFIRMATION_SUCCEEDED = "PUSH_SUCCEEDED_CONFIRMATION_SUCCEEDED"
    PUSH_SKIPPED_NO_NETWORK = "PUSH_SKIPPED_NO_NETWORK"
    UNKNOWN_PUSH_FAILURE = "UNKNOWN_PUSH_FAILURE"


UNSAFE_COMMIT_PATTERNS = [
    "__pycache__",
    ".pyc",
    ".pyo",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".wal",
    ".shm",
    ".log",
    "active-agent",
    "active_agent",
    "mission_grade_ecosystem_demo.md",
    "e8_external_action_ledger.md",
]


GitRunner = Callable[[Path, Sequence[str], int], "GitCommandResult"]


@dataclass(frozen=True)
class GitCommandResult:
    args: List[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""

    @property
    def combined_output(self) -> str:
        return "\n".join(part for part in [self.stdout, self.stderr] if part)


@dataclass(frozen=True)
class DeliveryPreflight:
    repo_root: str
    expected_branch: str
    current_branch: str
    local_head: str
    expected_head: str
    worktree_clean: bool
    dirty_paths: List[str] = field(default_factory=list)
    unsafe_dirty_paths: List[str] = field(default_factory=list)
    remote_name: str = "origin"
    remote_url_present: bool = False
    remote_url_redacted: str = ""
    branch_ok: bool = False
    head_ok: bool = False
    push_allowed: bool = False
    failure_code: str = ""
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ConnectivityCheck:
    remote_name: str
    branch: str
    attempted: bool
    ok: bool
    remote_head: str = ""
    failure_code: str = ""
    raw_error_summary: str = ""

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PushAttempt:
    attempted: bool
    succeeded: bool
    skipped_reason: str = ""
    failure_code: str = ""
    stdout_summary: str = ""
    stderr_summary: str = ""

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RemoteConfirmation:
    attempted: bool
    confirmed: bool
    local_head: str
    remote_head: str = ""
    failure_code: str = ""
    residual_reason: str = ""

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RepositoryDeliveryAssessment:
    branch: str
    expected_branch: str
    local_head: str
    expected_head: str
    remote_head: str
    repository_delivery_rt1: int
    next_milestone_allowed: bool
    failure_code: str
    preflight: DeliveryPreflight
    connectivity: ConnectivityCheck
    push_attempt: PushAttempt
    remote_confirmation: RemoteConfirmation
    owner_handoff: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


def default_git_runner(repo_root: Path, args: Sequence[str], timeout_seconds: int = 20) -> GitCommandResult:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )
    return GitCommandResult(list(args), completed.returncode, completed.stdout.strip(), completed.stderr.strip())


def _truncate(text: str, max_chars: int = 500) -> str:
    stripped = text.strip()
    if len(stripped) <= max_chars:
        return stripped
    return stripped[: max_chars - 3] + "..."


def classify_git_failure(output: str) -> str:
    lowered = output.lower()
    if "could not resolve host" in lowered and "github.com" in lowered:
        return DeliveryFailureCode.DNS_GITHUB_UNRESOLVED
    if "unable to create temporary object directory" in lowered or "remote unpack failed" in lowered:
        return DeliveryFailureCode.REMOTE_OBJECT_DIRECTORY_FAILURE
    if "authentication failed" in lowered or "could not read username" in lowered or "invalid username" in lowered:
        return DeliveryFailureCode.AUTHENTICATION_FAILURE
    if "permission denied" in lowered or "write access" in lowered or "403" in lowered or "not authorized" in lowered:
        return DeliveryFailureCode.PERMISSION_DENIED
    if "no such host" in lowered or "network is unreachable" in lowered:
        return DeliveryFailureCode.PUSH_SKIPPED_NO_NETWORK
    return DeliveryFailureCode.UNKNOWN_PUSH_FAILURE


def redact_remote_url(remote_url: str) -> str:
    if "@" in remote_url and "://" in remote_url:
        scheme, rest = remote_url.split("://", 1)
        host = rest.split("@", 1)[-1]
        return f"{scheme}://<redacted>@{host}"
    return remote_url


def parse_status_paths(status_output: str) -> List[str]:
    paths: List[str] = []
    for line in status_output.splitlines():
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 and line[2] == " " else line[2:].lstrip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path.strip())
    return paths


def unsafe_dirty_paths(paths: Iterable[str]) -> List[str]:
    unsafe: List[str] = []
    for path in paths:
        lowered = path.lower()
        if any(pattern in lowered for pattern in UNSAFE_COMMIT_PATTERNS):
            unsafe.append(path)
    return unsafe


def get_current_branch(repo_root: Path, runner: GitRunner = default_git_runner) -> str:
    return runner(repo_root, ["branch", "--show-current"]).stdout.strip()


def get_local_head(repo_root: Path, runner: GitRunner = default_git_runner) -> str:
    return runner(repo_root, ["rev-parse", "HEAD"]).stdout.strip()


def get_remote_url(repo_root: Path, remote_name: str = "origin", runner: GitRunner = default_git_runner) -> str:
    result = runner(repo_root, ["remote", "get-url", remote_name])
    return result.stdout.strip() if result.returncode == 0 else ""


def run_delivery_preflight(
    repo_root: Path,
    expected_branch: str,
    expected_head: str = "",
    remote_name: str = "origin",
    runner: GitRunner = default_git_runner,
) -> DeliveryPreflight:
    current_branch = get_current_branch(repo_root, runner)
    local_head = get_local_head(repo_root, runner)
    status = runner(repo_root, ["status", "--porcelain"])
    dirty = parse_status_paths(status.stdout)
    unsafe = unsafe_dirty_paths(dirty)
    remote_url = get_remote_url(repo_root, remote_name, runner)
    errors: List[str] = []
    failure_code = ""
    branch_ok = current_branch == expected_branch
    head_ok = not expected_head or local_head.startswith(expected_head) or expected_head.startswith(local_head)
    if not branch_ok:
        errors.append(f"wrong_branch: expected {expected_branch}, got {current_branch}")
        failure_code = DeliveryFailureCode.WRONG_BRANCH
    if dirty:
        errors.append("worktree_dirty")
        failure_code = failure_code or DeliveryFailureCode.WORKTREE_DIRTY
    if unsafe:
        errors.append("unsafe_generated_drift_present")
    if expected_head and not head_ok:
        errors.append(f"unexpected_head: expected {expected_head}, got {local_head}")
        failure_code = failure_code or DeliveryFailureCode.REMOTE_CONFIRMATION_FAILED
    if not remote_url:
        errors.append(f"missing_remote_url: {remote_name}")
        failure_code = failure_code or DeliveryFailureCode.REMOTE_CONFIRMATION_FAILED
    return DeliveryPreflight(
        repo_root=str(repo_root),
        expected_branch=expected_branch,
        current_branch=current_branch,
        local_head=local_head,
        expected_head=expected_head,
        worktree_clean=not dirty,
        dirty_paths=dirty,
        unsafe_dirty_paths=unsafe,
        remote_name=remote_name,
        remote_url_present=bool(remote_url),
        remote_url_redacted=redact_remote_url(remote_url),
        branch_ok=branch_ok,
        head_ok=head_ok,
        push_allowed=branch_ok and not dirty and bool(remote_url) and head_ok,
        failure_code=failure_code,
        errors=errors,
    )


def check_github_connectivity(
    repo_root: Path,
    branch: str,
    remote_name: str = "origin",
    runner: GitRunner = default_git_runner,
) -> ConnectivityCheck:
    result = runner(repo_root, ["ls-remote", remote_name, branch], 30)
    if result.returncode != 0:
        return ConnectivityCheck(
            remote_name=remote_name,
            branch=branch,
            attempted=True,
            ok=False,
            failure_code=classify_git_failure(result.combined_output),
            raw_error_summary=_truncate(result.combined_output),
        )
    remote_head = parse_ls_remote_head(result.stdout)
    return ConnectivityCheck(remote_name=remote_name, branch=branch, attempted=True, ok=bool(remote_head), remote_head=remote_head)


def parse_ls_remote_head(output: str) -> str:
    for line in output.splitlines():
        parts = line.split()
        if parts and len(parts[0]) >= 7:
            return parts[0]
    return ""


def attempt_push_with_confirmation(
    repo_root: Path,
    preflight: DeliveryPreflight,
    runner: GitRunner = default_git_runner,
) -> PushAttempt:
    if not preflight.push_allowed:
        return PushAttempt(
            attempted=False,
            succeeded=False,
            skipped_reason=preflight.failure_code or DeliveryFailureCode.UNKNOWN_PUSH_FAILURE,
            failure_code=preflight.failure_code,
        )
    result = runner(repo_root, ["push", preflight.remote_name, preflight.current_branch], 120)
    if result.returncode == 0:
        return PushAttempt(
            attempted=True,
            succeeded=True,
            stdout_summary=_truncate(result.stdout),
            stderr_summary=_truncate(result.stderr),
        )
    code = classify_git_failure(result.combined_output)
    return PushAttempt(
        attempted=True,
        succeeded=False,
        failure_code=code,
        stdout_summary=_truncate(result.stdout),
        stderr_summary=_truncate(result.stderr),
    )


def confirm_remote_matches_local(
    repo_root: Path,
    branch: str,
    local_head: str,
    remote_name: str = "origin",
    runner: GitRunner = default_git_runner,
) -> RemoteConfirmation:
    connectivity = check_github_connectivity(repo_root, branch, remote_name, runner)
    if not connectivity.ok:
        return RemoteConfirmation(
            attempted=True,
            confirmed=False,
            local_head=local_head,
            remote_head=connectivity.remote_head,
            failure_code=connectivity.failure_code or DeliveryFailureCode.REMOTE_CONFIRMATION_FAILED,
            residual_reason=connectivity.raw_error_summary or "remote confirmation failed",
        )
    if connectivity.remote_head == local_head:
        return RemoteConfirmation(attempted=True, confirmed=True, local_head=local_head, remote_head=connectivity.remote_head)
    return RemoteConfirmation(
        attempted=True,
        confirmed=False,
        local_head=local_head,
        remote_head=connectivity.remote_head,
        failure_code=DeliveryFailureCode.LOCAL_AHEAD_REMOTE_MISSING,
        residual_reason="remote_head_does_not_match_local_head",
    )


def build_owner_handoff(
    preflight: DeliveryPreflight,
    remote_confirmation: Optional[RemoteConfirmation] = None,
    failure_code: str = "",
) -> str:
    remote_head = remote_confirmation.remote_head if remote_confirmation else ""
    code = failure_code or preflight.failure_code or (remote_confirmation.failure_code if remote_confirmation else "")
    commands = [
        f"cd {preflight.repo_root}",
        "git status --short",
        "git branch --show-current",
        "git log -1 --oneline",
        f"git push {preflight.remote_name} {preflight.expected_branch}",
        f"git ls-remote {preflight.remote_name} {preflight.expected_branch}",
    ]
    unsafe = preflight.unsafe_dirty_paths or [
        "__pycache__/",
        "*.pyc",
        "reports/integration/mission_grade_ecosystem_demo.md drift",
        "*.db / *.sqlite / *.wal / *.shm",
        "*.log",
        "active-agent markers",
    ]
    lines = [
        "# Repository Delivery Owner Handoff",
        "",
        f"- current_branch: {preflight.current_branch}",
        f"- expected_branch: {preflight.expected_branch}",
        f"- local_head: {preflight.local_head}",
        f"- expected_head: {preflight.expected_head or 'not_specified'}",
        f"- remote_head: {remote_head or 'unavailable'}",
        f"- exact_blocker: {code or 'none'}",
        f"- next_milestone_allowed: {str(remote_confirmation.confirmed if remote_confirmation else False).lower()}",
        "",
        "## Safe Owner Commands",
    ]
    lines.extend(f"- `{command}`" for command in commands)
    lines.extend(["", "## Do Not Commit"])
    lines.extend(f"- {path}" for path in unsafe)
    return "\n".join(lines)


def e13_entry_allowed(repository_delivery_rt1: int) -> bool:
    return repository_delivery_rt1 == 0


def assess_repository_delivery(
    repo_root: Path,
    expected_branch: str,
    expected_head: str = "",
    remote_name: str = "origin",
    attempt_push: bool = False,
    runner: GitRunner = default_git_runner,
) -> RepositoryDeliveryAssessment:
    preflight = run_delivery_preflight(repo_root, expected_branch, expected_head, remote_name, runner)
    connectivity = check_github_connectivity(repo_root, expected_branch, remote_name, runner)
    push = PushAttempt(attempted=False, succeeded=False, skipped_reason="push_not_requested")
    if attempt_push:
        push = attempt_push_with_confirmation(repo_root, preflight, runner)
    confirmation = confirm_remote_matches_local(repo_root, expected_branch, preflight.local_head, remote_name, runner)
    rt1 = 0 if confirmation.confirmed and preflight.branch_ok and preflight.worktree_clean and preflight.head_ok else 1
    if rt1 == 0:
        failure_code = DeliveryFailureCode.PUSH_SUCCEEDED_CONFIRMATION_SUCCEEDED
    elif preflight.failure_code:
        failure_code = preflight.failure_code
    elif confirmation.failure_code:
        failure_code = confirmation.failure_code
    elif connectivity.failure_code:
        failure_code = connectivity.failure_code
    else:
        failure_code = DeliveryFailureCode.REMOTE_CONFIRMATION_FAILED
    handoff = build_owner_handoff(preflight, confirmation, failure_code) if rt1 else ""
    return RepositoryDeliveryAssessment(
        branch=preflight.current_branch,
        expected_branch=expected_branch,
        local_head=preflight.local_head,
        expected_head=expected_head,
        remote_head=confirmation.remote_head,
        repository_delivery_rt1=rt1,
        next_milestone_allowed=e13_entry_allowed(rt1),
        failure_code=failure_code,
        preflight=preflight,
        connectivity=connectivity,
        push_attempt=push,
        remote_confirmation=confirmation,
        owner_handoff=handoff,
    )
