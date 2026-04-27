#!/usr/bin/env python3
"""Run the dry-run cross-repo governance alignment acceptance check."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "cross_repo_alignment" / "generated" / "cross_repo_status_manifest.json"
SUMMARY = ROOT / "cross_repo_alignment" / "generated" / "cross_repo_alignment_summary.json"
REQUIRED_ROLES = {"Aiden-CEO", "Ethan-CTO", "Samantha-Secretary"}


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected object JSON: {path}")
    return data


def check(label: str, condition: bool, failures: list[str]) -> None:
    print(f"{label} ... ", end="", flush=True)
    if condition:
        print("PASS")
    else:
        print("FAIL")
        failures.append(label)


def main() -> int:
    failures: list[str] = []
    print("Y* Cross-Repo Governance Alignment Acceptance")
    print()

    print("[1/5] Build cross-repo status manifest ... ", end="", flush=True)
    result = run_command(["python3", "cross_repo_alignment/tools/build_cross_repo_status_manifest.py"])
    if result.returncode == 0:
        print("PASS")
    else:
        print("FAIL")
        print(result.stdout)
        print(result.stderr)
        return 1

    manifest = load_json(MANIFEST)
    summary = load_json(SUMMARY)

    check(
        "[2/5] Verify Y-star-gov endpoint acceptance",
        manifest["ystar_gov_endpoint_acceptance"]["accepted"] is True,
        failures,
    )
    check(
        "[3/5] Verify labs runtime acceptance",
        manifest["labs_runtime_acceptance"]["accepted"] is True,
        failures,
    )
    bridge_ok = (
        manifest["labs_governance_bridge"]["dry_run_only"] is True
        and set(manifest["multi_role_pre_u_governance"]["roles_covered"]) == REQUIRED_ROLES
        and bool(manifest["multi_role_pre_u_governance"]["decision_counts"])
    )
    check("[4/5] Verify labs governance bridge decisions", bridge_ok, failures)
    check("[5/5] Verify safety assertions", all(manifest["safety_assertions"].values()), failures)

    print()
    if failures or summary.get("alignment_accepted") is not True:
        print("Result: FAIL")
        print("Cross-repo alignment: NOT ACCEPTED")
        return 1

    print("Result: PASS")
    print("Cross-repo alignment: ACCEPTED")
    return 0


if __name__ == "__main__":
    sys.exit(main())

