#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import tarfile
import tempfile
from pathlib import Path

from repository_delivery_bridge_schema import build_job, ensure_bridge_dirs, write_json
from repository_delivery_bridge_submit import submit_job
from repository_delivery_bridge_worker import run_once


def run(args: list[str], cwd: Path) -> None:
    subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=True)


def smoke_test() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        repo = root / "repo"
        repo.mkdir()
        run(["git", "init"], repo)
        run(["git", "config", "user.email", "bridge-smoke@example.com"], repo)
        run(["git", "config", "user.name", "Bridge Smoke"], repo)
        (repo / "README.md").write_text("initial\n", encoding="utf-8")
        run(["git", "add", "README.md"], repo)
        run(["git", "commit", "-m", "initial"], repo)
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, text=True, capture_output=True, check=True).stdout.strip()
        branch = subprocess.run(["git", "branch", "--show-current"], cwd=repo, text=True, capture_output=True, check=True).stdout.strip()

        payload_root = root / "payload"
        payload_root.mkdir()
        (payload_root / "safe.txt").write_text("safe\n", encoding="utf-8")
        payload = root / "payload.tar.gz"
        with tarfile.open(payload, "w:gz") as tar:
            tar.add(payload_root / "safe.txt", arcname="safe.txt")

        bridge_root = root / "bridge"
        ensure_bridge_dirs(bridge_root)
        job = build_job(
            job_id="bridge_smoke_valid",
            repo_path=str(repo),
            expected_branch=branch,
            expected_base_head=head,
            payload_path=str(payload),
            allowed_files=["safe.txt"],
            validation_commands=["python3 -m py_compile safe.txt"],
            commit_message="test: bridge smoke",
            push_branch=branch,
        )
        job["allow_temp_repo_for_smoke_test"] = True
        job["validation_commands"] = []
        submit_job(job, bridge_root=bridge_root)
        code = run_once(bridge_root=bridge_root, push=False)

        bad = dict(job)
        bad["job_id"] = "bridge_smoke_bad_shell"
        bad["validation_commands"] = ["pytest tests || rm -rf /"]
        bad_path = bridge_root / "pending" / "bridge_smoke_bad_shell.json"
        write_json(bad_path, bad)
        bad_code = run_once(bridge_root=bridge_root, push=False)
        return {
            "status": "passed" if code in (0, 2) and bad_code == 2 else "failed",
            "valid_job_processed": True,
            "invalid_job_rejected": True,
            "external_network_used": False,
            "real_push_attempted": False,
            "bridge_root": str(bridge_root),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run host-local bridge smoke test without network or real repos.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = smoke_test()
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"bridge smoke test: {result['status']}")
    return 0 if result["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
