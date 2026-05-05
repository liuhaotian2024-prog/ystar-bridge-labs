from __future__ import annotations

import re
from typing import Any

from .e42_internal_resource_inventory import build_internal_resource_inventory


SYNONYM_MAP = {
    "external action": ["gov_mcp", "owner approval", "croba", "pre_action", "mcp_execution_boundary"],
    "tool use": ["gov_mcp", "mcp_execution_boundary", "gov_check", "gov_enforce"],
    "provider api": ["gov_mcp", "mcp_execution_boundary", "provider", "no_send"],
    "evidence": ["evidence", "receipt", "claim_graph", "source", "public_readonly"],
    "route drift": ["route", "drift", "e41", "frontier_capability_import"],
    "ceo memory": ["ceo_memory", "brain", "kg", "daily", "directive"],
    "delivery": ["delivery", "repository_delivery", "bridge_status", "check_repository_delivery"],
    "governance": ["governance", "Y-star-gov", "IntentContract", "check", "enforce"],
    "mcp": ["gov-mcp", "mcp_execution_boundary", "gov_check", "gov_enforce"],
    "frontier capability": ["frontier_capability_import", "e41", "import_loop", "capability"],
    "public read-only": ["public_research", "evidence", "readonly", "receipt"],
    "customer validation": ["no_fake_evidence", "customer_validation", "paid_signal", "evidence"],
    "owner decision": ["owner_decision", "route_selection", "decision", "packet"],
}


def _tokens(value: str) -> set[str]:
    return {token for token in re.split(r"[^a-z0-9]+", value.lower()) if len(token) >= 2}


def expand_task_terms(task: str) -> set[str]:
    terms = _tokens(task)
    lower = task.lower()
    for phrase, mapped in SYNONYM_MAP.items():
        if phrase in lower:
            terms.update(_tokens(" ".join(mapped)))
    return terms


def build_task_capability_matcher_model() -> dict[str, Any]:
    return {
        "artifact_id": "e42_task_capability_matcher_model",
        "generated_at": "2026-05-05T00:00:01Z",
        "matching_modes": [
            "keyword matching",
            "capability tag matching",
            "path/name matching",
            "artifact dependency matching",
            "test coverage matching",
            "repo ownership matching",
            "milestone lineage matching",
            "known synonym mapping",
        ],
        "synonym_map": SYNONYM_MAP,
        "requires_llm": False,
    }


def _recommended_action(resource: dict[str, Any], terms: set[str]) -> str:
    layer = resource.get("owning_layer")
    rtype = resource.get("resource_type")
    tags = set(resource.get("capability_tags", []))
    if layer == "gov_mcp_execution_boundary":
        return "blocked_by_boundary" if {"send", "provider", "execution", "tool", "mcp"} & terms else "read_existing"
    if layer == "ystar_gov_governance_kernel":
        return "propose_cross_repo_change" if "governance" in terms else "read_existing"
    if resource.get("reuse_mode") == "direct_call":
        return "call_existing"
    if resource.get("reuse_mode") == "use_as_test_fixture":
        return "use_existing"
    if rtype in {"runtime_module", "script"}:
        return "extend_existing"
    if "delivery" in tags:
        return "call_existing"
    if resource.get("reuse_mode") in {"read_as_input", "use_as_report_context"}:
        return "read_existing"
    return "create_thin_adapter"


def match_task_to_capabilities(task_description: str, inventory: dict[str, Any] | None = None, top_n: int = 12) -> list[dict[str, Any]]:
    inventory = inventory or build_internal_resource_inventory()
    terms = expand_task_terms(task_description)
    matches: list[dict[str, Any]] = []
    for resource in inventory.get("resources", []):
        resource_terms = set(resource.get("task_keywords", [])) | set(resource.get("capability_tags", [])) | _tokens(resource.get("path", ""))
        overlap = terms & resource_terms
        path = resource.get("path", "").lower()
        score = len(overlap) * 8
        if any(term in path for term in terms):
            score += 6
        if resource.get("validation_tests"):
            score += 2
        if resource.get("repo") != "ystar-bridge-labs" and ({"governance", "mcp", "execution", "tool", "audit", "commercial"} & terms):
            score += 6
        if not score:
            continue
        action = _recommended_action(resource, terms)
        warning = resource.get("boundary_notes", "")
        if action == "blocked_by_boundary":
            warning = "Future execution/tool/send action belongs behind gov-mcp and owner approval; do not build a Labs execution layer."
        matches.append(
            {
                "resource_id": resource["resource_id"],
                "resource_path": resource["path"],
                "repo": resource["repo"],
                "relevance_score": score,
                "relevance_reason": f"matched {sorted(overlap)[:8]} via deterministic tags/path/keywords",
                "reuse_mode": resource["reuse_mode"],
                "owner_layer": resource["owning_layer"],
                "boundary_warning": warning,
                "recommended_action": action,
                "tests_to_run": resource.get("validation_tests", [])[:8],
            }
        )
    return sorted(matches, key=lambda item: (-item["relevance_score"], item["repo"], item["resource_path"]))[:top_n]
