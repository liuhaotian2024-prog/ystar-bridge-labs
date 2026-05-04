#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from repository_delivery_transport import inspect_repo_transport, render_transport_report


DEFAULT_REPOS = [
    "/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs",
    "/Users/haotianliu/.openclaw/workspace/gov-mcp",
    "/Users/haotianliu/.openclaw/workspace/Y-star-gov",
    "/Users/haotianliu/.openclaw/workspace/ystar-company",
]


def write_outputs(repo_root: Path, results: list[dict]) -> None:
    reports = repo_root / "operations" / "repository_delivery" / "delivery_reports"
    reports.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact_id": "repository_delivery_transport_doctor",
        "transport_mode": (
            "direct_push_first"
            if all(item.get("transport_classification") == "direct_push_available" for item in results if item.get("is_git_repo"))
            else "host_bootstrap_fallback"
        ),
        "repos": results,
        "credential_safety": {
            "tokens_printed": False,
            "credential_values_printed": False,
            "credential_helper_secret_read": False,
        },
    }
    (reports / "repository_delivery_transport_doctor.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (reports / "repository_delivery_transport_doctor.md").write_text(
        render_transport_report(results),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose repository delivery transport and direct push readiness.")
    parser.add_argument("--repo-root", default="/Users/haotianliu/.openclaw/workspace/ystar-bridge-labs")
    parser.add_argument("--repo", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repos = args.repo or DEFAULT_REPOS
    results = [inspect_repo_transport(path) for path in repos]
    write_outputs(Path(args.repo_root), results)
    if args.json:
        print(json.dumps({"status": "complete", "repos": len(results)}, indent=2))
    else:
        print(render_transport_report(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
