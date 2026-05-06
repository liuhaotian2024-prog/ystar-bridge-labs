from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .e57_commercial_route_candidates import BRIDGE_ROOT, NEXT_MILESTONE, OLD_E50B_ROUTE, SELECTED_ROUTE, write_json, write_md
from .e57_counterfactual_route_scorer import build_counterfactual_route_matrix


def run_commercial_route_decision() -> dict[str, Any]:
    matrix = build_counterfactual_route_matrix()
    selected = next(route for route in matrix["routes"] if route["route_id"] == matrix["selected_route"])
    nearest = next(route for route in matrix["routes"] if route["route_id"] == matrix["nearest_alternative"])
    route_changed = OLD_E50B_ROUTE != selected["route_id"] and selected["route_id"] != "governed_agent_action_proof_packet_owner_review_path"
    return {
        "artifact_id": "e57_post_l5_commercial_route_decision_packet",
        "old_E50B_selected_route": OLD_E50B_ROUTE,
        "best_route_changed_from_E50B": route_changed,
        "what_changed": "Post-L5 CEO brain, behavior center, and internal company loop make the company-runtime harness itself a stronger commercial object than the earlier proof-packet-only route.",
        "selected_route": selected["route_id"],
        "nearest_alternative": nearest["route_id"],
        "why_selected": "The L5 internal company runtime harness packages the strongest new proof created after E50B while reusing the E52 proof packet as evidence.",
        "why_not_nearest": "The full governed execution + causal audit stack is strong but more transport/K9 dependent and harder to explain before owner-reviewed external feedback.",
        "selected_route_allowed_now": True,
        "allowed_next_action": NEXT_MILESTONE,
        "blocked_by_owner_approval": ["controlled_single_first_user_review_after_owner_approval", "direct external contact", "publication", "paid setup offer"],
        "blocked_by_real_mcp_transport": ["real_mcp_transport_gate_first", "gov_mcp_integration_service", "full transport claim"],
        "blocked_by_lack_customer_validation_or_paid_signal": ["customer validation claim", "paid signal claim", "paid advisory route as proof"],
        "can_be_done_next_without_external_action": ["package AI agent company runtime harness case study", "prepare owner-review-only materials", "tighten no-overclaim language"],
        "requires_owner_approval": ["external first-user review", "outreach", "publication", "paid offer"],
        "owner_approval_required_before_external_action": True,
        "no_customer_validation_claimed": True,
        "no_paid_signal_claimed": True,
        "no_real_mcp_transport_claimed": True,
        "customer_validation_claimed": False,
        "paid_signal_claimed": False,
        "real_mcp_transport_claimed": False,
        "owner_decision_status": "pending_owner_decision",
        "external_action_allowed": False,
        "no_external_action": True,
    }


def write_commercial_route_decision(output_root: Path | None = None) -> dict[str, Any]:
    root = output_root or BRIDGE_ROOT
    data = run_commercial_route_decision()
    write_json(root, "operations/external_validation/e57_post_l5_commercial_route_decision_packet.json", data)
    write_md(root, "reports/integration/e57_post_l5_commercial_route_decision_packet.md", "E57 Post-L5 Commercial Route Decision Packet", [
        f"Best route changed from E50B: `{data['best_route_changed_from_E50B']}`",
        f"Selected route: `{data['selected_route']}`",
        f"Nearest alternative: `{data['nearest_alternative']}`",
        f"Allowed next action: `{data['allowed_next_action']}`",
    ])
    return data

