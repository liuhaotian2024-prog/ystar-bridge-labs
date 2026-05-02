#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from office.mission_command.repository_delivery_czl import build_repository_delivery_czl
from office.mission_command.repository_delivery_health import render_repository_delivery_health
from office.mission_command.repository_delivery_status import assess_repository_delivery


def main() -> int:
    parser = argparse.ArgumentParser(description="Push the current branch and require remote SHA confirmation.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--branch", required=True, help="Expected branch name. Push is blocked on any other branch.")
    parser.add_argument("--expect-head", default="", help="Expected local HEAD SHA or prefix.")
    parser.add_argument("--remote", default="origin", help="Remote name.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON instead of Markdown.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    assessment = assess_repository_delivery(
        repo_root=repo_root,
        expected_branch=args.branch,
        expected_head=args.expect_head,
        remote_name=args.remote,
        attempt_push=True,
    )
    czl = build_repository_delivery_czl(assessment)
    if args.json:
        print(json.dumps({"assessment": assessment.to_dict(), "czl": czl.to_dict()}, indent=2))
    else:
        print(render_repository_delivery_health(assessment))
    return 0 if assessment.repository_delivery_rt1 == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
