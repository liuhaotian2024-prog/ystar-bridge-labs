from __future__ import annotations

from typing import Any

from .e42_task_capability_matcher import match_task_to_capabilities


def build_reuse_first_no_rebuild_gate() -> dict[str, Any]:
    return {
        "artifact_id": "e42_reuse_first_no_rebuild_gate",
        "generated_at": "2026-05-05T00:00:01Z",
        "required_questions": [
            "Did we search the internal resource inventory?",
            "Which existing resources are relevant?",
            "Why are they insufficient?",
            "Can we directly reuse them?",
            "Can we extend them with a thin adapter?",
            "Are we duplicating Y-star-gov or gov-mcp responsibility?",
            "Are we creating another CEO brain/KG?",
            "Are we producing another report instead of using a runtime?",
            "What is the smallest useful delta?",
        ],
        "decisions": [
            "reuse_existing",
            "extend_existing",
            "thin_adapter_allowed",
            "new_build_allowed",
            "cross_repo_proposal_required",
            "blocked_duplicate",
            "blocked_wrong_layer",
            "blocked_report_pile",
        ],
        "default_policy": "reuse or thin adapter before new build",
    }


def evaluate_reuse_first_gate(task_description: str, matches: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    matches = matches if matches is not None else match_task_to_capabilities(task_description, top_n=10)
    actions = [match["recommended_action"] for match in matches]
    top = matches[0] if matches else None
    lower = task_description.lower()
    execution_terms = ["external execution", "external action", "tool use", "mcp", "provider", "send"]
    if any(term in lower for term in execution_terms) or any(action == "blocked_by_boundary" for action in actions):
        decision = "blocked_wrong_layer"
        smallest_delta = "create Labs-only planning artifact or propose gov-mcp-aligned route; do not implement execution layer"
    elif "another report" in lower or "broad audit" in lower:
        decision = "blocked_report_pile"
        smallest_delta = "call reuse router and produce compact preflight only"
    elif "second ceo brain" in lower or "new ceo brain" in lower or "new kg" in lower:
        decision = "blocked_duplicate"
        smallest_delta = "reuse CEO brain/KG delta conventions"
    elif any(action in {"call_existing", "read_existing", "use_existing"} for action in actions):
        decision = "reuse_existing"
        smallest_delta = "use existing resource(s) and run mapped tests"
    elif any(action == "extend_existing" for action in actions):
        decision = "extend_existing"
        smallest_delta = "extend the best matching module with a thin adapter"
    elif any(action == "propose_cross_repo_change" for action in actions):
        decision = "cross_repo_proposal_required"
        smallest_delta = "prepare proposal; do not modify other repo in Labs milestone"
    elif matches:
        decision = "thin_adapter_allowed"
        smallest_delta = "create a thin adapter around relevant artifact"
    else:
        decision = "new_build_allowed"
        smallest_delta = "new build allowed only after documented inventory miss"
    return {
        "inventory_searched": True,
        "relevant_resource_count": len(matches),
        "top_resource": top,
        "why_existing_insufficient": "not insufficient yet; reuse-first path selected" if decision == "reuse_existing" else "gap or boundary requires narrower delta",
        "can_directly_reuse": any(action in {"call_existing", "read_existing", "use_existing"} for action in actions),
        "can_extend_thin_adapter": any(action in {"extend_existing", "create_thin_adapter"} for action in actions),
        "duplicating_Y_star_gov_or_gov_mcp": decision == "blocked_wrong_layer",
        "creating_second_CEO_brain_or_KG": False,
        "producing_report_instead_of_runtime": decision == "blocked_report_pile",
        "smallest_useful_delta": smallest_delta,
        "decision": decision,
        "forbidden_duplicate_work": [
            "duplicate governance kernel",
            "duplicate MCP execution layer",
            "second CEO brain",
            "second CEO KG",
            "duplicate CIEU/CZL/route registry",
            "new report pile when existing runtime can be called",
        ],
    }
