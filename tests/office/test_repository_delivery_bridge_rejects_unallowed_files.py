from __future__ import annotations

import subprocess
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from repository_delivery_bridge_schema import build_job
from repository_delivery_bridge_worker import process_job


def test_unallowlisted_dirty_file_blocks_job(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo, check=True)
    (repo / "README.md").write_text("initial\n")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo, check=True, capture_output=True)
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, text=True, capture_output=True, check=True).stdout.strip()
    branch = subprocess.run(["git", "branch", "--show-current"], cwd=repo, text=True, capture_output=True, check=True).stdout.strip()
    (repo / "unrelated.txt").write_text("nope\n")

    source = tmp_path / "source"
    source.mkdir()
    (source / "safe.txt").write_text("safe\n")
    payload = tmp_path / "payload.tar.gz"
    with tarfile.open(payload, "w:gz") as tar:
        tar.add(source / "safe.txt", arcname="safe.txt")
    job = build_job(
        job_id="dirty_block",
        repo_path=str(repo),
        expected_branch=branch,
        expected_base_head=head,
        payload_path=str(payload),
        allowed_files=["safe.txt"],
        validation_commands=[],
        commit_message="test",
        push_branch=branch,
    )
    job["allow_temp_repo_for_smoke_test"] = True
    report = process_job(job, push=False)
    assert report["failure_code"] == "WORKTREE_DIRTY_UNEXPECTED"
    assert "unrelated.txt" in report["unexpected_dirty_files"]
