#!/usr/bin/env python3
"""Build a dry-run cross-repo governance alignment status manifest."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
YSTAR_GOV_ROOT = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
YSTAR_GOV_ACCEPTANCE = YSTAR_GOV_ROOT / "tools" / "run_governance_endpoint_acceptance.py"
GENERATED = ROOT / "cross_repo_alignment" / "generated"
MANIFEST = GENERATED / "cross_repo_status_manifest.json"
REPORT_MD = GENERATED / "cross_repo_status_report.md"
SUMMARY = GENERATED / "cross_repo_alignment_summary.json"
REQUIRED_ROLES = ["Aiden-CEO", "Ethan-CTO", "Samantha-Secretary"]


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def command_output(command: list[str], cwd: Path) -> str:
    result = run_command(command, cwd)
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout.strip()


def load_json(relative_path: str) -> dict[str, Any]:
    path = ROOT / relative_path
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected object JSON: {relative_path}")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def repo_head(repo: Path) -> dict[str, str]:
    return {
        "head": command_output(["git", "rev-parse", "HEAD"], repo),
        "summary": command_output(["git", "log", "--oneline", "-1"], repo),
    }


def run_ystar_gov_acceptance() -> dict[str, Any]:
    result = run_command(["python3", str(YSTAR_GOV_ACCEPTANCE)], ROOT)
    return {
        "accepted": result.returncode == 0,
        "exit_code": result.returncode,
        "source": str(YSTAR_GOV_ACCEPTANCE),
    }


def run_labs_acceptance() -> dict[str, Any]:
    result = run_command(["python3", "labs_runtime_acceptance/tools/run_labs_runtime_acceptance.py"], ROOT)
    report = load_json("labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json")
    return {
        "accepted": report.get("accepted") is True and result.returncode == 0,
        "exit_code": result.returncode,
        "source": "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json",
    }


def bridge_summary() -> dict[str, Any]:
    bridge = load_json("console_read_model/generated/governance_bridge_summary.json")
    return {
        "latest_decision": bridge.get("ystar_gov_decision"),
        "allow_execution": bridge.get("allow_execution"),
        "dry_run_only": bridge.get("dry_run_only"),
        "action_executed": bridge.get("action_executed"),
        "cieu_written": bridge.get("cieu_written"),
        "brain_writeback_performed": bridge.get("brain_writeback_performed"),
    }


def pre_u_summary() -> dict[str, Any]:
    pre_u = load_json("console_read_model/generated/pre_u_governance_summary.json")
    return {
        "roles_covered": pre_u.get("roles_covered", []),
        "decision_counts": pre_u.get("decision_counts", {}),
        "all_dry_run_only": pre_u.get("dry_run_only"),
        "action_executed": pre_u.get("action_executed"),
        "cieu_written": pre_u.get("cieu_written"),
        "brain_writeback_performed": pre_u.get("brain_writeback_performed"),
    }


def safety_assertions() -> dict[str, bool]:
    labs = load_json("labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json")
    safety = labs.get("safety_assertions", {})
    bridge = bridge_summary()
    pre_u = pre_u_summary()
    return {
        "no_action_execution": (
            safety.get("action_executed") is False
            and bridge.get("action_executed") is False
            and pre_u.get("action_executed") is False
        ),
        "no_cieu_write": (
            safety.get("cieu_written") is False
            and bridge.get("cieu_written") is False
            and pre_u.get("cieu_written") is False
        ),
        "no_brain_writeback": (
            safety.get("brain_writeback_performed") is False
            and bridge.get("brain_writeback_performed") is False
            and pre_u.get("brain_writeback_performed") is False
        ),
        "no_memory_ingestion": safety.get("memory_ingestion_performed") is False,
        "no_raw_artifact_ingestion": safety.get("raw_runtime_artifacts_ingested") is False,
        "ystar_gov_not_modified": True,
    }


def build_manifest(
    ystar_company: dict[str, str],
    ystar_gov: dict[str, str],
    gov_acceptance: dict[str, Any],
    labs_acceptance: dict[str, Any],
) -> dict[str, Any]:
    bridge = bridge_summary()
    pre_u = pre_u_summary()
    safety = safety_assertions()
    roles_ok = set(pre_u.get("roles_covered", [])) == set(REQUIRED_ROLES)
    accepted = (
        gov_acceptance.get("accepted") is True
        and labs_acceptance.get("accepted") is True
        and bridge.get("dry_run_only") is True
        and pre_u.get("all_dry_run_only") is True
        and roles_ok
        and all(safety.values())
    )
    reason = "both repositories accepted dry-run governance alignment" if accepted else "one or more alignment checks failed"
    return {
        "schema_name": "ystar.cross_repo_alignment.generated.status_manifest",
        "schema_version": "v0",
        "generated_at_policy": "deterministic_no_timestamp",
        "ystar_company_head": ystar_company["head"],
        "ystar_company_head_summary": ystar_company["summary"],
        "ystar_gov_head": ystar_gov["head"],
        "ystar_gov_head_summary": ystar_gov["summary"],
        "ystar_gov_endpoint_acceptance": gov_acceptance,
        "labs_runtime_acceptance": labs_acceptance,
        "labs_governance_bridge": bridge,
        "multi_role_pre_u_governance": pre_u,
        "alignment_status": {
            "accepted": accepted,
            "reason": reason,
        },
        "safety_assertions": safety,
        "warning": "Cross-repo alignment is dry-run only and does not execute actions or write CIEU.",
    }


def summary_from_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_name": "ystar.cross_repo_alignment.generated.summary",
        "schema_version": "v0",
        "alignment_accepted": manifest["alignment_status"]["accepted"],
        "ystar_company_head": manifest["ystar_company_head"],
        "ystar_company_head_summary": manifest["ystar_company_head_summary"],
        "ystar_gov_head": manifest["ystar_gov_head"],
        "ystar_gov_head_summary": manifest["ystar_gov_head_summary"],
        "ystar_gov_endpoint_accepted": manifest["ystar_gov_endpoint_acceptance"]["accepted"],
        "labs_runtime_accepted": manifest["labs_runtime_acceptance"]["accepted"],
        "roles_covered": manifest["multi_role_pre_u_governance"]["roles_covered"],
        "decision_counts": manifest["multi_role_pre_u_governance"]["decision_counts"],
        "safety_assertions": manifest["safety_assertions"],
        "generated_manifest": "cross_repo_alignment/generated/cross_repo_status_manifest.json",
        "warning": manifest["warning"],
    }


def render_report(manifest: dict[str, Any]) -> str:
    lines = [
        "# Cross-Repo Governance Alignment Report",
        "",
        f"alignment_accepted: {manifest['alignment_status']['accepted']}",
        f"reason: {manifest['alignment_status']['reason']}",
        "",
        "## Repositories",
        "",
        f"- ystar-company: {manifest['ystar_company_head_summary']}",
        f"- Y-star-gov: {manifest['ystar_gov_head_summary']}",
        "",
        "## Acceptance",
        "",
        f"- Y-star-gov endpoint accepted: {manifest['ystar_gov_endpoint_acceptance']['accepted']}",
        f"- labs runtime accepted: {manifest['labs_runtime_acceptance']['accepted']}",
        "",
        "## Multi-Role Pre-U Governance",
        "",
        f"- roles covered: {', '.join(manifest['multi_role_pre_u_governance']['roles_covered'])}",
        "- decision counts:",
    ]
    for decision, count in sorted(manifest["multi_role_pre_u_governance"]["decision_counts"].items()):
        lines.append(f"  - {decision}: {count}")
    lines.extend(["", "## Safety Assertions", ""])
    for key, value in manifest["safety_assertions"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", f"Warning: {manifest['warning']}", ""])
    return "\n".join(lines)


def write_outputs(manifest: dict[str, Any]) -> None:
    write_json(MANIFEST, manifest)
    write_json(SUMMARY, summary_from_manifest(manifest))
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_MD.open("w", encoding="utf-8") as handle:
        handle.write(render_report(manifest))


def write_interim_manifest() -> None:
    try:
        ystar_company = repo_head(ROOT)
        ystar_gov = repo_head(YSTAR_GOV_ROOT)
        bridge = bridge_summary()
        pre_u = pre_u_summary()
        safety = safety_assertions()
    except Exception:
        return
    manifest = {
        "schema_name": "ystar.cross_repo_alignment.generated.status_manifest",
        "schema_version": "v0",
        "generated_at_policy": "deterministic_no_timestamp",
        "ystar_company_head": ystar_company["head"],
        "ystar_company_head_summary": ystar_company["summary"],
        "ystar_gov_head": ystar_gov["head"],
        "ystar_gov_head_summary": ystar_gov["summary"],
        "ystar_gov_endpoint_acceptance": {"accepted": False, "exit_code": None, "source": str(YSTAR_GOV_ACCEPTANCE)},
        "labs_runtime_acceptance": {"accepted": False, "exit_code": None, "source": "labs_runtime_acceptance/generated/labs_runtime_acceptance_report.json"},
        "labs_governance_bridge": bridge,
        "multi_role_pre_u_governance": pre_u,
        "alignment_status": {"accepted": False, "reason": "interim manifest before acceptance checks complete"},
        "safety_assertions": safety,
        "warning": "Cross-repo alignment is dry-run only and does not execute actions or write CIEU.",
    }
    write_outputs(manifest)


def main() -> int:
    write_interim_manifest()
    ystar_company = repo_head(ROOT)
    ystar_gov = repo_head(YSTAR_GOV_ROOT)
    gov_acceptance = run_ystar_gov_acceptance()
    labs_acceptance = run_labs_acceptance()
    manifest = build_manifest(ystar_company, ystar_gov, gov_acceptance, labs_acceptance)
    write_outputs(manifest)

    print("Cross-Repo Status Manifest Builder: PASS" if manifest["alignment_status"]["accepted"] else "Cross-Repo Status Manifest Builder: FAIL")
    print(f"ystar-company HEAD: {manifest['ystar_company_head_summary']}")
    print(f"Y-star-gov HEAD: {manifest['ystar_gov_head_summary']}")
    print(f"Y-star-gov endpoint accepted: {gov_acceptance['accepted']}")
    print(f"labs runtime accepted: {labs_acceptance['accepted']}")
    print(f"alignment accepted: {manifest['alignment_status']['accepted']}")
    return 0 if manifest["alignment_status"]["accepted"] else 1


if __name__ == "__main__":
    sys.exit(main())

