from __future__ import annotations

import subprocess
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from repository_delivery_bridge_schema import build_job
from repository_delivery_bridge_worker import process_job


def build_repo(tmp_path: Path) -> tuple[Path, str, str]:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    (repo / "README.md").write_text("initial\n")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, capture_output=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, text=True, capture_output=True, check=True).stdout.strip()
    branch = subprocess.run(["git", "branch", "--show-current"], cwd=repo, text=True, capture_output=True, check=True).stdout.strip()
    return repo, head, branch


def payload_with(tmp_path: Path, name: str = "safe.txt") -> Path:
    source = tmp_path / "source"
    source.mkdir(parents=True, exist_ok=True)
    (source / name).write_text("safe\n")
    payload = tmp_path / f"{name}.tar.gz"
    with tarfile.open(payload, "w:gz") as tar:
        tar.add(source / name, arcname=name)
    return payload


def test_persistent_unsafe_env_file_is_not_auto_cleaned_and_blocks(tmp_path: Path) -> None:
    repo, head, branch = build_repo(tmp_path)
    (repo / ".env").write_text("TOKEN=secret\n")
    job = build_job(
        job_id="env_blocks",
        repo_path=str(repo),
        expected_branch=branch,
        expected_base_head=head,
        payload_path=str(payload_with(tmp_path)),
        allowed_files=["safe.txt"],
        validation_commands=[],
        commit_message="test",
        push_branch=branch,
    )
    job["allow_temp_repo_for_smoke_test"] = True
    report = process_job(job, push=False)
    assert report["failure_code"] == "WORKTREE_DIRTY_UNEXPECTED"
    assert any(".env" in path for path in report["unexpected_dirty_files"])
    assert (repo / ".env").exists()


def test_persistent_unsafe_key_db_and_credential_json_block(tmp_path: Path) -> None:
    for name in ["credentials.json", "private.pem", "local.key", "state.db", "state.wal", "state.shm"]:
        repo, head, branch = build_repo(tmp_path / name.replace(".", "_"))
        (repo / name).write_text("unsafe\n")
        job = build_job(
            job_id=f"block_{name.replace('.', '_')}",
            repo_path=str(repo),
            expected_branch=branch,
            expected_base_head=head,
            payload_path=str(payload_with(tmp_path / ("payload_" + name.replace(".", "_")))),
            allowed_files=["safe.txt"],
            validation_commands=[],
            commit_message="test",
            push_branch=branch,
        )
        job["allow_temp_repo_for_smoke_test"] = True
        report = process_job(job, push=False)
        assert report["failure_code"] == "WORKTREE_DIRTY_UNEXPECTED", name
