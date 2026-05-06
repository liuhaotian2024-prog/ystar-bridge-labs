from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))


def _read_text(path: Path, limit: int = 800000) -> str:
    try:
        data = path.read_text(encoding='utf-8', errors='ignore')
        return data[:limit]
    except Exception:
        return ''


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _contains(text: str, needles: list[str]) -> bool:
    low = text.lower()
    return any(needle.lower() in low for needle in needles)

from .e50b_counterfactual_asset_inventory import build_counterfactual_asset_inventory
from .e50b_counterfactual_disconnection_diagnosis import diagnose_counterfactual_disconnection
from .e50b_counterfactual_money_route_retest import run_counterfactual_money_route_retest
from .e50b_external_commercial_semantic_graph import build_external_commercial_semantic_graph
from .e50b_external_observation_preflight import build_external_observation_preflight
from .e50b_public_observation import build_observation_run


def build_ceo_commercial_decision_packet() -> dict[str, Any]:
    inventory = build_counterfactual_asset_inventory()
    diagnosis = diagnose_counterfactual_disconnection()
    retest = run_counterfactual_money_route_retest()
    preflight = build_external_observation_preflight()
    observation = build_observation_run()
    graph = build_external_commercial_semantic_graph()
    selected = retest['selected_route']
    nearest = retest['nearest_rejected_or_deferred_route']
    final_status = 'counterfactual_runtime_reconnected_external_observation_closed_money_route_selected'
    return {
        'artifact_id': 'e50b_ceo_commercial_decision_packet',
        'final_status': final_status,
        'e50a_status_consumed': retest['e50a_status_consumed'],
        'counterfactual_asset_count': inventory['asset_count'],
        'counterfactual_disconnection_status_before_e50b': diagnosis['final_status'],
        'counterfactual_runtime_adapter_status': 'counterfactual_runtime_reconnected',
        'external_observation_status': observation['status'] if preflight['safe_to_observe'] else preflight['blocked_status'],
        'external_source_receipt_count': observation['source_receipt_count'],
        'commercial_semantic_graph_node_count': graph['node_count'],
        'commercial_semantic_graph_edge_count': graph['edge_count'],
        'selected_route': selected,
        'nearest_rejected_or_deferred_alternative': nearest,
        'why_selected_beats_alternative': retest['why_selected_beats_nearest'],
        'what_remains_blocked': [
            'real MCP transport/client package remains unclaimed and should not be represented as closed',
            'owner approval required before any first-user contact, publication, or outreach',
            'no customer validation, expert feedback, or paid signal exists yet',
        ],
        'next_executable_milestone': 'E51_package_governed_agent_action_proof_packet_for_first_user_review',
        'not_recommended_now': [
            'direct customer/expert outreach before owner approval',
            'grant/RFP route as default',
            'full enterprise compliance pilot before proof packet language hardening',
            'real MCP transport as prerequisite to public-read-only commercial observation',
        ],
        'no_external_action': True,
        'customer_validation_claimed': False,
        'paid_signal_claimed': False,
    }


if __name__ == '__main__':
    print(json.dumps(build_ceo_commercial_decision_packet(), indent=2, ensure_ascii=False))
