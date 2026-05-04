#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from repository_delivery_bridge_schema import BRIDGE_ROOT, PENDING_DIR, build_job, ensure_bridge_dirs, validate_job, write_json


def submit_job(job: dict, *, bridge_root: Path = BRIDGE_ROOT) -> Path:
    ensure_bridge_dirs(bridge_root)
    pending = bridge_root / "pending" / f"{job['job_id']}.json"
    validation = validate_job(job)
    if not validation.ok:
        raise ValueError("invalid_bridge_job: " + ",".join(validation.errors))
    write_json(pending, job)
    return pending


def main() -> int:
    parser = argparse.ArgumentParser(description="Submit a structured repository delivery job to the host-local bridge.")
    parser.add_argument("--job-json", help="Existing job JSON to validate and submit.")
    parser.add_argument("--job-id")
    parser.add_argument("--repo-path")
    parser.add_argument("--expected-branch")
    parser.add_argument("--expected-base-head")
    parser.add_argument("--payload-path")
    parser.add_argument("--allowed-file", action="append", default=[])
    parser.add_argument("--force-add-allowlisted-file", action="append", default=[])
    parser.add_argument("--validation-command", action="append", default=[])
    parser.add_argument("--commit-message")
    parser.add_argument("--push-branch")
    parser.add_argument("--bridge-root", default=str(BRIDGE_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    bridge_root = Path(args.bridge_root)
    if args.job_json:
        job = json.loads(Path(args.job_json).read_text(encoding="utf-8"))
    else:
        missing = [
            name
            for name in [
                "job_id",
                "repo_path",
                "expected_branch",
                "expected_base_head",
                "payload_path",
                "commit_message",
                "push_branch",
            ]
            if not getattr(args, name)
        ]
        if missing:
            print("missing required arguments: " + ", ".join(missing), file=sys.stderr)
            return 2
        job = build_job(
            job_id=args.job_id,
            repo_path=args.repo_path,
            expected_branch=args.expected_branch,
            expected_base_head=args.expected_base_head,
            payload_path=args.payload_path,
            allowed_files=args.allowed_file,
            force_add_allowlisted_files=args.force_add_allowlisted_file,
            validation_commands=args.validation_command,
            commit_message=args.commit_message,
            push_branch=args.push_branch,
        )
    path = submit_job(job, bridge_root=bridge_root)
    payload = {
        "status": "submitted",
        "job_id": job["job_id"],
        "pending_job_path": str(path),
        "bridge_root": str(bridge_root),
        "future_owner_delivery_commands_required": False,
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(f"submitted {job['job_id']} -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

