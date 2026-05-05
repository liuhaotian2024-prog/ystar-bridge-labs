from __future__ import annotations

from typing import Any

from .e42_reuse_first_no_rebuild_gate import evaluate_reuse_first_gate
from .e42_task_capability_matcher import match_task_to_capabilities


def task_preflight_packet_schema() -> dict[str, Any]:
    return {
        "artifact_id": "e42_ceo_task_preflight_packet_schema",
        "fields": [
            "task_interpretation",
            "relevant_existing_resources",
            "top_reusable_modules",
            "top_reusable_artifacts",
            "top_tests_to_run",
            "repo_ownership_boundary",
            "no_rebuild_gate_result",
            "smallest_implementation_delta",
            "forbidden_duplicate_work",
            "recommended_execution_path",
        ],
        "compact": True,
    }


def build_ceo_task_preflight_packet(
    task_title: str,
    task_description: str,
    owner_constraints: list[str] | None = None,
    target_repo: str | None = None,
    expected_base_head: str | None = None,
) -> dict[str, Any]:
    matches = match_task_to_capabilities(task_description, top_n=10)
    gate = evaluate_reuse_first_gate(task_description, matches)
    modules = [m for m in matches if m["resource_path"].endswith(".py") and m["repo"] == "ystar-bridge-labs"][:5]
    artifacts = [m for m in matches if m["resource_path"].endswith((".json", ".jsonl", ".md"))][:5]
    tests = []
    for match in matches:
        for test in match.get("tests_to_run", []):
            if test not in tests:
                tests.append(test)
    boundaries = sorted({m["owner_layer"] for m in matches})
    return {
        "task_title": task_title,
        "task_interpretation": task_description[:500],
        "owner_constraints": owner_constraints or [],
        "target_repo": target_repo,
        "expected_base_head": expected_base_head,
        "relevant_existing_resources": matches,
        "top_reusable_modules": modules,
        "top_reusable_artifacts": artifacts,
        "top_tests_to_run": tests[:10],
        "repo_ownership_boundary": boundaries,
        "no_rebuild_gate_result": gate,
        "smallest_implementation_delta": gate["smallest_useful_delta"],
        "forbidden_duplicate_work": gate["forbidden_duplicate_work"],
        "recommended_execution_path": gate["decision"],
        "compact": True,
    }
