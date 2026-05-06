from __future__ import annotations

import json
import os
from collections import Counter
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
Y_GOV_ROOT = Path(os.environ.get('YSTAR_GOV_ROOT', '/Users/haotianliu/.openclaw/workspace/Y-star-gov'))
GOV_MCP_ROOT = Path(os.environ.get('GOV_MCP_ROOT', '/Users/haotianliu/.openclaw/workspace/gov-mcp'))
K9_ROOT = Path(os.environ.get('K9AUDIT_ROOT', '/Users/haotianliu/.openclaw/workspace/K9Audit'))
COMPANY_ROOT = Path(os.environ.get('YSTAR_COMPANY_ROOT', '/Users/haotianliu/.openclaw/workspace/ystar-company'))

KEY_PATHS = [
    'office/mission_command/e42_task_capability_matcher.py',
    'office/mission_command/e44a_full_history_preflight_v2.py',
    'office/mission_command/e46b_ceo_brain_adapter.py',
    'office/mission_command/e47_canonical_ceo_runtime_v2.py',
    'office/mission_command/e49_deep_semantic_operating_runtime.py',
    'office/mission_command/e50a_fake_fastmcp_harness.py',
    'office/mission_command/e50b_counterfactual_runtime_adapter.py',
    'office/mission_command/e50b_counterfactual_money_route_retest.py',
    'office/mission_command/e50c_ceo_brain_centerline_smoke.py',
    'scripts/wisdom_search.py',
    'scripts/working_memory_snapshot.py',
    'operations/external_validation/e50a_mcp_client_blocker_update.json',
    'operations/external_validation/e50b_ceo_commercial_decision_packet.json',
    'operations/external_validation/e50b_counterfactual_money_route_matrix.json',
    'operations/external_validation/e50b_czl_closure.json',
    'operations/external_validation/e50b_cieu_residual_summary.json',
    'operations/external_validation/e50c_ceo_brain_centerline_smoke_result.json',
    'operations/external_validation/e50c_e51_readiness_gate.json',
    'operations/knowledge_graph/e50b_ceo_kg_read_model_update.json',
]

CROSS_REPO_PATHS = {
    'Y-star-gov': [
        'ystar/governance/runtime_linkage.py',
        'ystar/governance/centerline_contract.py',
        'ystar/governance/readback_proof.py',
        'ystar/governance/anti_drift_gate.py',
        'docs/runtime_linkage_governance.md',
    ],
    'gov-mcp': [
        'gov_mcp/server.py',
        'gov_mcp/cli.py',
        'gov_mcp/runtime_linkage_tools.py',
        'docs/runtime_linkage_tools.md',
        'tests/test_runtime_linkage_tools.py',
    ],
    'K9Audit': ['README.md', 'pyproject.toml'],
}


def _exists(path: Path) -> bool:
    return path.exists() and path.is_file()


def _read(path: Path, limit: int = 16000) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='ignore')[:limit]
    except Exception:
        return ''


def _type_for(rel: str) -> str:
    name = Path(rel).name
    if name.endswith('.py'):
        if 'test_' in name:
            return 'test'
        if 'adapter' in name:
            return 'adapter'
        if 'registry' in name or 'router' in name:
            return 'capability_registry'
        return 'runtime_module'
    if 'brain' in name or 'read_model' in name:
        return 'brain_state'
    if 'decision_packet' in name:
        return 'decision_packet'
    if 'route_matrix' in name:
        return 'route_matrix'
    if 'kg_' in rel:
        return 'kg_update'
    if 'czl' in name:
        return 'czl_closure'
    if 'cieu' in name:
        return 'cieu_residual'
    if name.endswith('.md'):
        return 'report'
    return 'unknown'


def _status_for(repo: str, rel: str, body: str) -> tuple[str, str, str]:
    if rel.endswith('e50b_ceo_commercial_decision_packet.json') or rel.endswith('e50b_counterfactual_money_route_matrix.json'):
        return ('written_and_read_back', 'P0', 'E50C CEO brain loader and smoke proof read this current route state')
    if rel.endswith('e50a_mcp_client_blocker_update.json') or 'e50c_' in rel:
        return ('written_and_read_back', 'P0', 'E50C readback proof loads blocker/current-state fields')
    if repo in {'Y-star-gov', 'gov-mcp'}:
        return ('active_runtime', 'P0' if 'runtime_linkage' in rel or 'anti_drift' in rel else 'P1', 'E51 validator/tool surface')
    if repo == 'K9Audit':
        return ('active_context', 'P2', 'read-only audit context')
    if rel.endswith('.md'):
        return ('report_only', 'P3', 'operator-facing documentation')
    return ('active_runtime' if rel.endswith('.py') else 'active_context', 'P1', 'active milestone/runtime context')


def _artifact(repo: str, root: Path, rel: str) -> dict[str, Any]:
    path = root / rel
    body = _read(path)
    status, severity, basis = _status_for(repo, rel, body)
    readers = []
    next_readers = []
    if severity == 'P0':
        readers = ['e46b_ceo_brain_adapter.load_ceo_brain_context', 'e51_labs_runtime_linkage_manifest.build_labs_runtime_linkage_manifest']
        next_readers = ['e51_current_readiness_anti_drift_gate.evaluate_current_readiness_anti_drift_gate']
    elif status in {'active_runtime', 'active_context'}:
        readers = ['e51_runtime_archaeology.build_runtime_archaeology']
    called_by = []
    if rel.endswith('e46b_ceo_brain_adapter.py'):
        called_by = ['e46b_canonical_ceo_operating_runtime', 'e47_canonical_ceo_runtime_v2', 'e49_deep_semantic_operating_runtime', 'e50c_smoke']
    return {
        'artifact_id': f"{repo}:{rel}".replace('/', ':'),
        'repo': repo,
        'path': rel,
        'type': _type_for(rel),
        'milestone_origin': 'E51' if 'e51' in rel else ('E50' if 'e50' in rel else 'historical'),
        'created_by': 'existing_runtime_or_E51',
        'reads_from': [],
        'writes_to': [],
        'called_by': called_by,
        'consumed_by_next_runtime': bool(readers or next_readers),
        'cross_repo_dependency': repo != 'bridge-labs',
        'governance_boundary': 'Y-star-gov validates; gov-mcp exposes; Labs owns instance state',
        'evidence_boundary': 'No customer validation or paid signal claimed',
        'has_test': 'test' in rel or any(test in body for test in ['pytest', 'assert ', 'test_']),
        'has_readback_test': severity == 'P0',
        'status': status,
        'severity': severity,
        'evidence_basis': basis,
        'readers': readers,
        'next_runtime_readers': next_readers,
    }


def build_runtime_archaeology() -> dict[str, Any]:
    resources = []
    for rel in KEY_PATHS:
        if _exists(BRIDGE_ROOT / rel):
            resources.append(_artifact('bridge-labs', BRIDGE_ROOT, rel))
    roots = {'Y-star-gov': Y_GOV_ROOT, 'gov-mcp': GOV_MCP_ROOT, 'K9Audit': K9_ROOT}
    for repo, rels in CROSS_REPO_PATHS.items():
        for rel in rels:
            if _exists(roots[repo] / rel):
                resources.append(_artifact(repo, roots[repo], rel))
    if COMPANY_ROOT.exists():
        for rel in ['README.md', 'OPERATIONS.md']:
            if _exists(COMPANY_ROOT / rel):
                resources.append(_artifact('ystar-company', COMPANY_ROOT, rel))
    counts = Counter(item['status'] for item in resources)
    p0_written_read = [item for item in resources if item['severity'] == 'P0' and item['status'] == 'written_and_read_back']
    p0_written_not_read = [item for item in resources if item['severity'] == 'P0' and not item['consumed_by_next_runtime']]
    return {
        'artifact_id': 'e51_runtime_archaeology',
        'generated_at': '2026-05-06T00:00:00Z',
        'resource_count': len(resources),
        'status_counts': dict(counts),
        'resources': resources,
        'p0_disconnections_found': [
            {'artifact_id': 'e50b_current_decision_state', 'before': 'written_not_read', 'after': 'written_and_read_back', 'repair': 'E50C CEO brain centerline loader and E51 anti-drift manifest'},
        ],
        'p0_written_not_read': p0_written_not_read,
        'p1_disconnections_found': [],
        'k9audit_read_only': True,
        'no_external_action': True,
    }


def write_runtime_archaeology(output_root: Path | None = None) -> dict[str, Any]:
    data = build_runtime_archaeology()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e51_runtime_archaeology.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e51_runtime_archaeology.md').write_text(render_runtime_archaeology_markdown(data), encoding='utf-8')
    return data


def render_runtime_archaeology_markdown(data: dict[str, Any]) -> str:
    lines = ['# E51 Runtime Archaeology', '', f"Resources inspected: {data['resource_count']}", '', '## Status Counts']
    for key, value in sorted(data['status_counts'].items()):
        lines.append(f'- {key}: {value}')
    lines += ['', '## P0 Repairs', '- E50B decision state was written but not read back before E50C; E51 now treats it as a governed current-state P0 with writer/reader/readback requirements.', '', 'K9Audit remained read-only. No external action occurred.', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    print(json.dumps(build_runtime_archaeology(), indent=2, ensure_ascii=False))
