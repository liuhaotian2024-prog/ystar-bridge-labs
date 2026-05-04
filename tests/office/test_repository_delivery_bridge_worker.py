from __future__ import annotations

import subprocess
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from repository_delivery_bridge_schema import build_job
from repository_delivery_bridge_worker import clean_and_validate_dirty_set, process_job


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=repo, text=True, capture_output=True, check=True).stdout.strip()


def make_repo(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init")
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    (repo / "README.md").write_text("initial\n")
    git(repo, "add", "README.md")
    git(repo, "commit", "-m", "initial")
    return repo, git(repo, "rev-parse", "HEAD"), git(repo, "branch", "--show-current")


def make_payload(tmp_path: Path, name: str = "safe.txt") -> Path:
    payload_root = tmp_path / "payload"
    payload_root.mkdir(exist_ok=True)
    (payload_root / name).write_text("safe\n")
    payload = tmp_path / f"{name}.tar.gz"
    with tarfile.open(payload, "w:gz") as tar:
        tar.add(payload_root / name, arcname=name)
    return payload


def test_worker_processes_valid_job_without_real_push(tmp_path: Path) -> None:
    repo, head, branch = make_repo(tmp_path)
    payload = make_payload(tmp_path)
    job = build_job(
        job_id="worker_ok",
        repo_path=str(repo),
        expected_branch=branch,
        expected_base_head=head,
        payload_path=str(payload),
        allowed_files=["safe.txt"],
        validation_commands=[],
        commit_message="test: safe",
        push_branch=branch,
    )
    job["allow_temp_repo_for_smoke_test"] = True
    report = process_job(job, push=False)
    assert report["status"] == "DRY_RUN_COMPLETED"
    assert report["committed"] is True
    assert report["external_business_side_effects"] is False


def test_worker_cleans_transient_dirty_paths_from_dirty_set(monkeypatch, tmp_path: Path) -> None:
    repo, head, branch = make_repo(tmp_path)
    dirty_file = repo / "tests" / "kernel" / "__pycache__" / "test_brain_writeback_semantic.cpython-311-pytest-9.0.2.pyc"
    dirty_file.parent.mkdir(parents=True)
    dirty_file.write_bytes(b"pyc")
    payload = make_payload(tmp_path)
    job = build_job(
        job_id="dirty_cleanup",
        repo_path=str(repo),
        expected_branch=branch,
        expected_base_head=head,
        payload_path=str(payload),
        allowed_files=["safe.txt"],
        validation_commands=[],
        commit_message="test: safe",
        push_branch=branch,
    )
    calls = iter(
        [
            ["tests/kernel/__pycache__/test_brain_writeback_semantic.cpython-311-pytest-9.0.2.pyc"],
            [],
            [],
        ]
    )

    import repository_delivery_bridge_worker as worker

    monkeypatch.setattr(worker, "dirty_paths", lambda _repo: next(calls))
    report: dict = {}
    ok, failure_code, unexpected = clean_and_validate_dirty_set(repo, job, report, "initial_dirty_validation")
    assert ok is True
    assert failure_code == ""
    assert unexpected == []
    assert report["initial_dirty_validation_transient_cleanup"]
    assert not dirty_file.parent.exists()
