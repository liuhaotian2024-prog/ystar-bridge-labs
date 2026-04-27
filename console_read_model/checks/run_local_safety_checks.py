#!/usr/bin/env python3
"""Run safe local checks for the curated Y* company read-model stack."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Check:
    label: str
    command: list[str]
    mutates_generated_files: bool = False


REBUILD_CHECKS = [
    Check(
        "Build runtime artifact manifest",
        ["python3", "runtime_artifact_quarantine/tools/build_runtime_artifact_manifest.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build Markdown report safe-mining candidates",
        ["python3", "runtime_artifact_quarantine/safe_mining/tools/build_markdown_report_candidates.py"],
        mutates_generated_files=True,
    ),
    Check(
        "Build team console snapshot",
        ["python3", "console_read_model/loader/build_team_console_snapshot.py"],
        mutates_generated_files=True,
    ),
]

VALIDATION_CHECKS = [
    Check(
        "Validate JSON: team_console_snapshot.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/team_console_snapshot.json"],
    ),
    Check(
        "Validate JSON: quarantine_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/quarantine_summary.json"],
    ),
    Check(
        "Validate JSON: safe_mining_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/safe_mining_summary.json"],
    ),
    Check(
        "Validate JSON: markdown_report_candidates.json",
        ["python3", "-m", "json.tool", "runtime_artifact_quarantine/safe_mining/generated/markdown_report_candidates.json"],
    ),
    Check(
        "Validate JSON: mining_manifest.json",
        ["python3", "-m", "json.tool", "runtime_artifact_quarantine/safe_mining/generated/mining_manifest.json"],
    ),
    Check(
        "Validate JSON: generation_manifest.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/generation_manifest.json"],
    ),
    Check(
        "Validate JSON: readiness_summary.json",
        ["python3", "-m", "json.tool", "console_read_model/generated/readiness_summary.json"],
    ),
    Check(
        "Static team read model validator",
        ["python3", "console_read_model/validation/validate_team_read_model.py"],
    ),
    Check(
        "Team console validate-local",
        ["python3", "console_read_model/cli/team_console.py", "validate-local"],
    ),
    Check(
        "CLI smoke: quarantine",
        ["python3", "console_read_model/cli/team_console.py", "quarantine"],
    ),
    Check(
        "CLI smoke: mining-candidates",
        ["python3", "console_read_model/cli/team_console.py", "mining-candidates"],
    ),
    Check(
        "CLI smoke: sources",
        ["python3", "console_read_model/cli/team_console.py", "sources"],
    ),
]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run safe local checks for curated console/quarantine read-model files."
    )
    parser.add_argument(
        "--no-rebuild",
        action="store_true",
        help="Skip generated-file rebuild steps and validate current generated files only.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print stdout/stderr for every check.",
    )
    parser.add_argument(
        "--continue-on-failure",
        action="store_true",
        help="Run all checks and report failures at the end.",
    )
    return parser.parse_args(argv)


def run_check(check: Check, verbose: bool) -> tuple[bool, str]:
    result = subprocess.run(
        check.command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    output = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
    if verbose and output:
        print(output)
    return result.returncode == 0, output


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    checks = ([] if args.no_rebuild else REBUILD_CHECKS) + VALIDATION_CHECKS
    failures: list[tuple[Check, str]] = []

    print("Y* Company Local Safety Checks")
    print()

    total = len(checks)
    for index, check in enumerate(checks, start=1):
        print(f"[{index}/{total}] {check.label} ... ", end="", flush=True)
        ok, output = run_check(check, args.verbose)
        if ok:
            print("PASS")
            continue

        print("FAIL")
        failures.append((check, output))
        if not args.continue_on_failure:
            break

    print()
    if failures:
        print("Result: FAIL")
        print()
        print("Failures:")
        for check, output in failures:
            print(f"- {check.label}")
            if output and not args.verbose:
                print("  Output:")
                for line in output.splitlines()[:20]:
                    print(f"  {line}")
        return 1

    print("Result: PASS")
    print(
        "Safety note: This wrapper uses only curated read-model inputs and generated "
        "summaries. It does not read DB/log/runtime artifact contents."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
