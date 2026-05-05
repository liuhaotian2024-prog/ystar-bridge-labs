from __future__ import annotations

from typing import Any

from .e42_task_capability_matcher import match_task_to_capabilities
from .e44a_ceo_capability_activation_registry import build_ceo_capability_activation_registry

COGNITION_TAGS = ['imagination', 'innovation', 'strategic_imagination', 'six_dimensional_cognition', 'opportunity_generation', 'cross_domain_opportunity', 'abstraction_recombination', 'adversarial_review', 'contrarian_review', 'skeptical_cfo', 'product_customer_empathy', 'demand_budget_screen', 'evidence_ladder', 'high_imagination_preservation', 'commercial_wedge', 'first_user_value_path', 'execution_feasibility']
COGNITION_SYNONYM_MAP = {'imagination': ['imagination', 'strategic_imagination', 'high_imagination_preservation'], 'innovation': ['innovation', 'abstraction_recombination', 'opportunity_generation'], 'creative': ['imagination', 'innovation', 'abstraction_recombination'], 'strategy': ['strategic_imagination', 'six_dimensional_cognition', 'route_selection'], 'strategic': ['strategic_imagination', 'six_dimensional_cognition'], 'opportunity': ['opportunity_generation', 'cross_domain_opportunity', 'evidence_ladder'], 'new product': ['opportunity_generation', 'commercial_wedge', 'product_customer_empathy'], 'business path': ['commercial_wedge', 'demand_budget_screen', 'evidence_ladder'], 'commercial route': ['commercial_wedge', 'demand_budget_screen', 'route_selection'], 'customer': ['product_customer_empathy', 'demand_budget_screen'], 'buyer': ['product_customer_empathy', 'demand_budget_screen', 'commercial_wedge'], 'budget': ['demand_budget_screen', 'skeptical_cfo'], 'demand': ['demand_budget_screen', 'evidence_ladder'], 'market': ['market_language', 'demand_budget_screen', 'opportunity_generation'], 'wedge': ['commercial_wedge', 'first_user_value_path'], 'first user': ['first_user_value_path', 'product_customer_empathy', 'demand_budget_screen', 'opportunity_generation', 'execution_feasibility'], 'first customer': ['first_user_value_path', 'product_customer_empathy', 'demand_budget_screen', 'commercial_wedge'], 'run company': ['six_dimensional_cognition', 'execution_feasibility', 'commercial_wedge'], 'CEO decision': ['six_dimensional_cognition', 'adversarial_review', 'route_selection'], 'agent company': ['first_user_value_path', 'opportunity_generation', 'execution_feasibility'], 'agent economy': ['high_imagination_preservation', 'opportunity_generation', 'frontier_capability_import'], 'autonomous company': ['high_imagination_preservation', 'frontier_capability_import'], 'high imagination': ['high_imagination_preservation', 'strategic_imagination'], 'cross-domain': ['cross_domain_opportunity', 'abstraction_recombination'], 'contrarian': ['contrarian_review', 'adversarial_review'], 'skeptical': ['skeptical_cfo', 'adversarial_review'], 'product empathy': ['product_customer_empathy', 'customer']}

def route_task_with_cognition_overlay(task_description: str, top_n: int = 12) -> dict[str, Any]:
    registry = build_ceo_capability_activation_registry()
    lower = task_description.lower()
    matched_tags: list[str] = []
    for phrase, tags in COGNITION_SYNONYM_MAP.items():
        if phrase.lower() in lower:
            matched_tags.extend(tags)
    for tag in COGNITION_TAGS:
        if tag in lower or tag.replace("_", " ") in lower:
            matched_tags.append(tag)
    if "first" in lower and "user" in lower and "value" in lower:
        matched_tags.extend(["first_user_value_path", "product_customer_empathy", "demand_budget_screen", "opportunity_generation", "execution_feasibility"])
    if "business" in lower or "route" in lower:
        matched_tags.extend(["commercial_wedge", "evidence_ladder"])
    matched_tags = sorted(dict.fromkeys(matched_tags))
    matched_capabilities = []
    for capability in registry["capabilities"]:
        if set(capability["capability_tags"]) & set(matched_tags):
            matched_capabilities.append(capability["capability_id"])
    return {
        "artifact_id": "e44a_router_cognition_overlay_result",
        "task_description": task_description,
        "e42_matches": match_task_to_capabilities(task_description, top_n=top_n),
        "matched_cognition_tags": matched_tags,
        "matched_capability_ids": sorted(dict.fromkeys(matched_capabilities)),
        "external_action_occurred": False,
    }
