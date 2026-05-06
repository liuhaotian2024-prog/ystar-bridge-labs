from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from .e51_labs_runtime_linkage_manifest import build_labs_runtime_linkage_manifest

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
GOV_MCP_ROOT = Path(os.environ.get('GOV_MCP_ROOT', '/Users/haotianliu/.openclaw/workspace/gov-mcp'))
Y_GOV_ROOT = Path(os.environ.get('YSTAR_GOV_ROOT', '/Users/haotianliu/.openclaw/workspace/Y-star-gov'))


class FakeMCP:
    def __init__(self) -> None:
        self.tools: dict[str, Any] = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn
        return decorator


def _ensure_paths() -> None:
    for root in [GOV_MCP_ROOT, Y_GOV_ROOT]:
        if root.exists() and str(root) not in sys.path:
            sys.path.insert(0, str(root))


def _parse(value: Any) -> dict[str, Any]:
    if isinstance(value, str):
        return json.loads(value)
    return value


def _broken_manifest(valid: dict[str, Any]) -> dict[str, Any]:
    broken = json.loads(json.dumps(valid))
    for artifact in broken['artifacts']:
        if artifact.get('artifact_type') == 'selected_route':
            artifact['readers'] = []
            artifact['next_runtime_readers'] = []
            artifact['tests'] = []
            break
    broken['readback_proof']['passed'] = False
    broken['readback_proof']['missing_reads'] = ['e50b_selected_route']
    return broken


def run_gov_mcp_runtime_linkage_tool_harness() -> dict[str, Any]:
    _ensure_paths()
    from gov_mcp.runtime_linkage_tools import register_runtime_linkage_tools

    fake = FakeMCP()
    register_runtime_linkage_tools(fake, state=None)
    manifest = build_labs_runtime_linkage_manifest()
    required = ['gov_validate_runtime_linkage', 'gov_validate_centerline_contract', 'gov_validate_readback_proof', 'gov_enforce_anti_drift_gate']
    valid_results = {name: _parse(fake.tools[name](json.dumps(manifest))) for name in required}
    broken = _broken_manifest(manifest)
    broken_gate = _parse(fake.tools['gov_enforce_anti_drift_gate'](broken))
    allow = valid_results['gov_enforce_anti_drift_gate']
    passed = all(valid_results[name]['allowed'] is True for name in required) and allow['status'] == 'ALLOW' and broken_gate['status'] == 'DENY' and broken_gate['allowed'] is False
    return {
        'artifact_id': 'e51_gov_mcp_runtime_linkage_tool_harness_result',
        'gov_mcp_root': str(GOV_MCP_ROOT),
        'registered_tools': sorted(fake.tools),
        'required_tools_present': all(name in fake.tools for name in required),
        'allow_proof': allow,
        'individual_tool_results': valid_results,
        'deny_proof': broken_gate,
        'passed': passed,
        'no_server_started': True,
        'no_port_opened': True,
        'no_real_client_config_mutation': True,
        'no_external_action': True,
    }


def render_tool_harness_markdown(data: dict[str, Any]) -> str:
    return '\n'.join(['# E51 gov-mcp Runtime Linkage Tool Harness', '', f"Passed: `{data['passed']}`", f"Required tools present: `{data['required_tools_present']}`", f"ALLOW status: `{data['allow_proof'].get('status')}`", f"DENY status: `{data['deny_proof'].get('status')}`", '', 'FakeMCP capture was used. No server, port, or real client config mutation occurred.', ''])


def write_gov_mcp_tool_harness_result(output_root: Path | None = None) -> dict[str, Any]:
    data = run_gov_mcp_runtime_linkage_tool_harness()
    root = output_root or BRIDGE_ROOT
    (root / 'operations/external_validation').mkdir(parents=True, exist_ok=True)
    (root / 'reports/integration').mkdir(parents=True, exist_ok=True)
    (root / 'operations/external_validation/e51_gov_mcp_runtime_linkage_tool_harness_result.json').write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    (root / 'reports/integration/e51_gov_mcp_runtime_linkage_tool_harness_result.md').write_text(render_tool_harness_markdown(data), encoding='utf-8')
    return data


if __name__ == '__main__':
    print(json.dumps(run_gov_mcp_runtime_linkage_tool_harness(), indent=2, ensure_ascii=False))
