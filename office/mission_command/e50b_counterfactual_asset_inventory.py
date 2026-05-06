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

COUNTERFACTUAL_TERMS = [
    'counterfactual', '反事实', 'what if', 'parallel universe', 'sandbox replay',
    'Rt+1', 'Yt+1', 'Xt', 'Y*', 'alternative route', '方案A', '最优解', '次优解',
    'GOV-005', 'Awareness of Possibility', 'nearest alternative', 'what-if',
]
MANDATORY_PATHS = [
    'governance/WORKING_STYLE.md', 'governance/INTERNAL_GOVERNANCE.md',
    'agents/CEO.md', '.claude/agents/ceo.md',
    'knowledge/ceo/wisdom/meta/autonomous_loop_algorithm.md',
    'knowledge/ceo/wisdom/meta/retrospective_sandbox_workflow.md',
    'knowledge/ceo/wisdom/meta/sandbox_16h_counterfactual_replay.md',
    'knowledge/ceo/wisdom/meta/capability_iteration_engine.md',
    'knowledge/ceo/wisdom/meta/17_meta_rules_from_practice.md',
    'scripts/local_learn.py', 'office/mission_command/counterfactual_router.py',
    'office/mission_command/e49_semantic_route_scorer.py',
    'office/mission_command/e49_deep_semantic_operating_runtime.py',
    'office/mission_command/e46b_ceo_brain_adapter.py',
    'office/mission_command/e47_canonical_ceo_runtime_v2.py',
    'operations/external_validation/e49_semantic_route_score_matrix.json',
    'operations/external_validation/e50a_mcp_client_blocker_update.json',
]
SCAN_DIRS = [
    'governance', 'agents', '.claude/agents', 'knowledge/ceo/wisdom/meta', 'scripts',
    'office/mission_command', 'operations/external_validation', 'reports/integration', 'tests/office',
]


def _asset_type(path: Path) -> str:
    rel = str(path.relative_to(BRIDGE_ROOT)) if path.is_absolute() and path.exists() else str(path)
    if rel.startswith('governance/'):
        return 'governance_protocol'
    if rel in {'agents/CEO.md', '.claude/agents/ceo.md'}:
        return 'ceo_agent_charter'
    if rel.startswith('knowledge/ceo/wisdom/'):
        return 'wisdom_memory'
    if 'sandbox' in rel.lower() or 'retrospective' in rel.lower():
        return 'retrospective_sandbox'
    if rel.startswith('office/mission_command/'):
        return 'runtime_module' if rel.endswith('.py') else 'report_artifact'
    if rel.startswith('tests/'):
        return 'test'
    if rel.startswith('operations/') or rel.startswith('reports/'):
        return 'report_artifact'
    return 'unknown'


def _callable_names(text: str) -> list[str]:
    return sorted(set(re.findall(r'^def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', text, flags=re.M)))


def _connection_status(rel: str, text: str) -> str:
    if rel == 'office/mission_command/counterfactual_router.py':
        return 'disconnected'
    if rel in {'office/mission_command/e49_semantic_route_scorer.py', 'office/mission_command/e49_deep_semantic_operating_runtime.py'}:
        return 'active_runtime_input' if 'counterfactual' in text.lower() else 'disconnected'
    if rel == 'office/mission_command/e46b_ceo_brain_adapter.py':
        return 'loaded_by_ceo_brain_adapter' if 'counterfactual' in text.lower() else 'loaded_by_ceo_brain_adapter_unstructured'
    if rel.endswith('.md') and rel.startswith('knowledge/ceo/wisdom/'):
        return 'static_wisdom_only'
    if rel.endswith('.md'):
        return 'doc_only'
    if rel.endswith('.json'):
        return 'report_artifact'
    if rel.endswith('.py') and _callable_names(text):
        return 'disconnected' if _contains(text, COUNTERFACTUAL_TERMS) else 'unknown'
    return 'unknown'


def _asset_id(rel: str) -> str:
    return 'cf_' + re.sub(r'[^a-zA-Z0-9]+', '_', rel).strip('_').lower()


def _excerpt(text: str) -> str:
    low = text.lower()
    for term in COUNTERFACTUAL_TERMS:
        idx = low.find(term.lower())
        if idx >= 0:
            start = max(0, idx - 100)
            end = min(len(text), idx + 220)
            return ' '.join(text[start:end].split())[:500]
    return ' '.join(text[:300].split())


def _candidate_paths() -> list[Path]:
    paths = {BRIDGE_ROOT / rel for rel in MANDATORY_PATHS}
    for rel_dir in SCAN_DIRS:
        root = BRIDGE_ROOT / rel_dir
        if not root.exists():
            continue
        for pattern in ('*.md', '*.py', '*.json'):
            paths.update(root.rglob(pattern))
    return sorted(path for path in paths if path.exists() and path.is_file())


def build_counterfactual_asset_inventory() -> dict[str, Any]:
    assets: list[dict[str, Any]] = []
    for path in _candidate_paths():
        rel = str(path.relative_to(BRIDGE_ROOT))
        text = _read_text(path)
        mandatory = rel in MANDATORY_PATHS
        if not mandatory and not _contains(text, COUNTERFACTUAL_TERMS):
            continue
        callables = _callable_names(text)
        asset = {
            'asset_id': _asset_id(rel),
            'path': rel,
            'asset_type': _asset_type(path),
            'contains_xt_y_star_u_rt': any(symbol in text for symbol in ['Xt', 'Y*', ' U ', 'Rt+1', 'Yt+1', 'Y_star', 'predicted_Rt_plus_1']),
            'contains_route_alternatives': _contains(text, ['alternative route', 'nearest alternative', '方案A', '最优解', '次优解', 'route']),
            'contains_counterfactual_delta': _contains(text, ['counterfactual', '反事实', 'what if', 'sandbox replay', 'delta']),
            'contains_runtime_callable': bool(callables),
            'callable_entrypoints': callables[:20],
            'current_connection_status': _connection_status(rel, text),
            'evidence_excerpt_or_symbol': _excerpt(text),
            'recommended_reuse_path': 'consume_as_runtime_adapter_source' if rel in {'governance/WORKING_STYLE.md', '.claude/agents/ceo.md', 'knowledge/ceo/wisdom/meta/autonomous_loop_algorithm.md', 'knowledge/ceo/wisdom/meta/retrospective_sandbox_workflow.md', 'office/mission_command/counterfactual_router.py'} else 'consume_as_context_or_evidence',
        }
        assets.append(asset)
    statuses = {}
    types = {}
    for asset in assets:
        statuses[asset['current_connection_status']] = statuses.get(asset['current_connection_status'], 0) + 1
        types[asset['asset_type']] = types.get(asset['asset_type'], 0) + 1
    return {
        'artifact_id': 'e50b_counterfactual_asset_inventory',
        'root': str(BRIDGE_ROOT),
        'terms': COUNTERFACTUAL_TERMS,
        'asset_count': len(assets),
        'mandatory_assets_found': sorted(rel for rel in MANDATORY_PATHS if (BRIDGE_ROOT / rel).exists()),
        'mandatory_assets_missing': sorted(rel for rel in MANDATORY_PATHS if not (BRIDGE_ROOT / rel).exists()),
        'counts_by_status': statuses,
        'counts_by_type': types,
        'assets': assets,
        'no_external_action': True,
    }


if __name__ == '__main__':
    print(json.dumps(build_counterfactual_asset_inventory(), indent=2, ensure_ascii=False))
