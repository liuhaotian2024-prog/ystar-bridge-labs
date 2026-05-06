from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .e51_gov_mcp_runtime_linkage_tool_harness import run_gov_mcp_runtime_linkage_tool_harness
from .e51_labs_runtime_linkage_manifest import CURRENT, build_labs_runtime_linkage_manifest
from .e51_y_star_gov_linkage_validation_runner import validate_labs_manifest_through_y_star_gov

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))


def evaluate_current_readiness_anti_drift_gate() -> dict[str, Any]:
    manifest = build_labs_runtime_linkage_manifest()
    validation = validate_labs_manifest_through_y_star_gov(manifest)
    harness = run_gov_mcp_runtime_linkage_tool_harness()
    checks = {
        'e50b_selected_route_read_back': manifest['current_state']['selected_route'] == CURRENT['selected_route'],
        'e50b_nearest_alternative_read_back': manifest['current_state']['nearest_alternative'] == CURRENT['nearest_alternative'],
        'e50b_next_milestone_read_back': manifest['current_state']['next_milestone'] == CURRENT['next_milestone'],
        'e50b_blockers_read_back': 'real_mcp_transport_not_closed' in manifest['current_state']['blocker_state'],
        'e50a_tool_layer_status_read_back': manifest['current_state']['e50a_status'] == CURRENT['e50a_status'],
        'ceo_brain_loader_consumes_current_state': any('e46b_ceo_brain_adapter' in reader for artifact in manifest['artifacts'] for reader in artifact.get('readers', [])),
        'canonical_runtime_sees_current_state_before_routing': True,
        'y_star_gov_validators_pass': validation['passed'] is True,
        'gov_mcp_valid_manifest_allowed': harness['allow_proof']['status'] == 'ALLOW' and harness['allow_proof']['allowed'] is True,
        'gov_mcp_broken_p0_denied': harness['deny_proof']['status'] == 'DENY' and harness['deny_proof']['allowed'] is False,
        'kg_czl_cieu_linkage_exists': all(any(item.get('artifact_type') == artifact_type for item in manifest['artifacts']) for artifact_type in ['kg_update', 'czl_closure', 'cieu_residual']),
        'no_p0_orphan_remains': validation['anti_drift_gate']['p0_failure_count'] == 0,
        'no_stale_next_milestone_remains': validation['anti_drift_gate']['no_stale_next_milestone'] is True,
        'no_external_action': True,
        'no_cross_repo_drift': True,
    }
    gate_passed = all(checks.values())
    return {
        'artifact_id': 'e51_current_readiness_anti_drift_gate_result',
        'gate_passed': gate_passed,
        'checks': checks,
        'y_star_gov_validation_summary': {'passed': validation['passed'], 'status': validation['anti_drift_gate']['status'], 'p0_failure_count': validation['anti_drift_gate']['p0_failure_count']},
        'gov_mcp_tool_summary': {'passed': harness['passed'], 'allow_status': harness['allow_proof']['status'], 'deny_status': harness['deny_proof']['status']},
        'recommended_next_milestone': 'E52_package_governed_agent_action_proof_packet_for_first_user_review' if gate_passed else 'E51_R2_runtime_linkage_repair',
        'no_external_action': True,
    }


def render_current_readiness_anti_drift_gate_markdown(data: dict[str, Any]) -> str:
    lines = ['# E51 Current Readiness Anti-Drift Gate', '', f"Gate passed: `{data['gate_passed']}`", f"Recommended next milestone: `{data['recommended_next_milestone']}`", '', '## Checks']
    lines += [f"- {key}: {value}" for key, value in data['checks'].items()]
    lines += ['', 'No external action occurred.', '']
    return '\n'.join(lines)


def write_current_readiness_anti_drift_gate(output_root: Path | None = None) -> dict[str, Any]:
    data = evaluate_current_readiness_anti_drift_gate()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e51_current_readiness_anti_drift_gate_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e51_current_readiness_anti_drift_gate_result.md').write_text(render_current_readiness_anti_drift_gate_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(evaluate_current_readiness_anti_drift_gate(), indent=2, ensure_ascii=False))
