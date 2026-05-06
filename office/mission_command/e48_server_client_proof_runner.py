from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

from .e48_gov_mcp_sandbox import build_sandbox_strategy
from .e48_real_code_interface_discovery import GOV_MCP_ROOT, Y_GOV_ROOT, discover_real_code_interfaces


def _run(command: list[str], cwd: Path, timeout: int = 20, env: dict[str, str] | None = None) -> dict[str, Any]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    try:
        completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=False, env=merged)
        return {'command': command, 'cwd': str(cwd), 'returncode': completed.returncode, 'stdout': (completed.stdout or '')[:6000], 'stderr': (completed.stderr or '')[:6000], 'timed_out': False}
    except subprocess.TimeoutExpired as exc:
        return {'command': command, 'cwd': str(cwd), 'returncode': None, 'stdout': (exc.stdout or '')[:6000] if isinstance(exc.stdout, str) else '', 'stderr': (exc.stderr or '')[:6000] if isinstance(exc.stderr, str) else '', 'timed_out': True}
    except Exception as exc:
        return {'command': command, 'cwd': str(cwd), 'returncode': None, 'stdout': '', 'stderr': str(exc), 'timed_out': False}


def _classify_command(result: dict[str, Any], *, success_codes: set[int] | None = None) -> str:
    if result.get('timed_out'):
        return 'timed_out'
    success_codes = success_codes or {0}
    return 'passed' if result.get('returncode') in success_codes else 'failed'


def _kernel_check(command: str, expected: str) -> dict[str, Any]:
    sys.path.insert(0, str(Y_GOV_ROOT))
    from ystar import IntentContract, check  # type: ignore
    contract = IntentContract(deny=['/.env', '/etc', '/production'], deny_commands=['rm -rf', 'cat .env', 'git push --force', 'sudo'])
    params = {'tool_name': 'Bash', 'command': command}
    result = check(params=params, result={}, contract=contract)
    decision = 'ALLOW' if result.passed else 'DENY'
    payload = {
        'strategy': 'in_process_ystar_kernel_check',
        'command': command,
        'expected': expected,
        'decision': decision,
        'passed': decision == expected,
        'violations': [getattr(v, 'message', str(v)) for v in getattr(result, 'violations', [])],
        'contract_digest': hashlib.sha256(json.dumps({'deny': contract.deny, 'deny_commands': contract.deny_commands}, sort_keys=True).encode()).hexdigest()[:16],
    }
    return payload


def run_server_client_proof() -> dict[str, Any]:
    discovery = discover_real_code_interfaces()
    sandbox = build_sandbox_strategy()
    scratch = sandbox['scratch_workspace_manifest']
    env = dict(scratch['env_overrides'])
    env['PYTHONPATH'] = f'{GOV_MCP_ROOT}:{Y_GOV_ROOT}'
    steps: list[dict[str, Any]] = []

    status = _run(['python3', '-m', 'gov_mcp', 'status'], GOV_MCP_ROOT, env=env, timeout=15)
    steps.append({'step_id': 'gov_mcp_status_sandbox_read', 'classification': _classify_command(status), 'result': status, 'decision_effect': 'status is safe read-only and confirmed no server running in sandbox path'})

    server_import = _run(['python3', '-c', 'from gov_mcp.server import create_server; print("server_import_ok")'], GOV_MCP_ROOT, env=env, timeout=10)
    import_classification = _classify_command(server_import)
    if import_classification != 'passed' and 'No module named' in (server_import.get('stderr') or ''):
        import_classification = 'blocked_missing_dependency'
    steps.append({'step_id': 'gov_mcp_server_import', 'classification': import_classification, 'result': server_import, 'decision_effect': 'determines whether actual FastMCP server/client transport can be exercised locally without internet install'})

    demo = _run(['python3', '-m', 'ystar', 'demo'], Y_GOV_ROOT, env={'PYTHONPATH': str(Y_GOV_ROOT)}, timeout=20)
    demo_classification = _classify_command(demo)
    steps.append({'step_id': 'ystar_demo_zero_config_allow_deny', 'classification': demo_classification, 'result': demo, 'decision_effect': 'proves local governance allow/deny semantics independent of MCP transport'})

    allow = _kernel_check('echo e48_safe', 'ALLOW')
    deny = _kernel_check('rm -rf /tmp/e48_nonexistent', 'DENY')
    steps.append({'step_id': 'gov_check_allow_case', 'classification': 'passed' if allow['passed'] else 'failed', 'result': allow, 'decision_effect': 'safe command is allowed by actual Y-star-gov kernel check'})
    steps.append({'step_id': 'gov_check_deny_case', 'classification': 'passed' if deny['passed'] else 'failed', 'result': deny, 'decision_effect': 'destructive command is denied by actual Y-star-gov kernel check'})

    tool_call_blocker = 'none'
    transport_closed = False
    if import_classification == 'passed':
        tool_call_blocker = 'client_path_not_exercised_in_e48_tests'
    elif import_classification == 'blocked_missing_dependency':
        tool_call_blocker = 'missing_mcp_dependency_blocks_server_import_no_internet_install_allowed'
    else:
        tool_call_blocker = 'gov_mcp_server_import_failed_unknown_reason'
    steps.append({'step_id': 'mcp_server_client_tool_call', 'classification': 'blocked_missing_client_path' if import_classification != 'passed' else 'skipped_safety', 'result': {'blocker': tool_call_blocker, 'server_transport_attempted': False, 'install_attempted': False}, 'decision_effect': 'prevents claiming full MCP server/client proof closure'})

    cleanup = {'process_started': False, 'process_left_running': False, 'port_opened': False, 'port_left_occupied': False, 'scratch_root': scratch['scratch_root']}
    steps.append({'step_id': 'cleanup', 'classification': 'passed', 'result': cleanup, 'decision_effect': 'no server was started, so no process or port could be left behind'})

    governed_proof = bool(allow['passed'] and deny['passed'])
    return {
        'artifact_id': 'e48_server_client_proof_result',
        'selected_strategy': discovery['selected_demo_strategy'],
        'selected_strategy_reason': discovery['selected_demo_strategy_reason'],
        'proof_steps': steps,
        'gov_demo_result': demo,
        'allow_result': allow,
        'deny_result': deny,
        'governance_envelope_or_contract_proof': {'available': True, 'contract_digest': allow['contract_digest'], 'source': 'Y-star-gov IntentContract + check(...)'},
        'governed_allow_deny_proof_generated': governed_proof,
        'local_server_client_demo_closed': transport_closed,
        'server_client_transport_blocker': tool_call_blocker,
        'ready_for_owner_approved_external_attempt': False,
        'readiness_class': 'blocked_by_local_env_missing_mcp_dependency_or_client_path',
        'cleanup_result': cleanup,
        'no_real_client_config_mutation': scratch['real_client_config_mutation_proof'],
        'no_external_action': True,
    }


if __name__ == '__main__':
    print(json.dumps(run_server_client_proof(), indent=2, ensure_ascii=False))
