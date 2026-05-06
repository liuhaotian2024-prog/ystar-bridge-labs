from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
GOV_MCP_ROOT = Path(os.environ.get('GOV_MCP_ROOT', '/Users/haotianliu/.openclaw/workspace/gov-mcp'))
Y_GOV_ROOT = Path(os.environ.get('YSTAR_GOV_ROOT', '/Users/haotianliu/.openclaw/workspace/Y-star-gov'))


def _read(path: Path, limit: int = 400_000) -> str:
    try:
        if not path.exists() or path.is_dir() or path.stat().st_size > limit:
            return ''
        return path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return ''


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


def _git_head(repo: Path) -> str:
    result = _run(['git', 'rev-parse', 'HEAD'], repo, timeout=10)
    return result.get('stdout', '').strip()


def _mcp_tool_names(server_text: str) -> list[str]:
    names: list[str] = []
    lines = server_text.splitlines()
    for idx, line in enumerate(lines):
        if '@mcp.tool' not in line:
            continue
        for follow in lines[idx + 1: idx + 8]:
            match = re.search(r'def\s+(gov_[a-zA-Z0-9_]+)\s*\(', follow)
            if match:
                names.append(match.group(1))
                break
    return sorted(dict.fromkeys(names))


def discover_real_code_interfaces() -> dict[str, Any]:
    cli_text = _read(GOV_MCP_ROOT / 'gov_mcp' / 'cli.py')
    main_text = _read(GOV_MCP_ROOT / 'gov_mcp' / '__main__.py')
    server_text = _read(GOV_MCP_ROOT / 'gov_mcp' / 'server.py')
    pyproject_text = _read(GOV_MCP_ROOT / 'pyproject.toml')
    doctor_text = _read(Y_GOV_ROOT / 'ystar' / 'cli' / 'doctor_cmd.py')
    demo_text = _read(Y_GOV_ROOT / 'ystar' / 'cli' / 'demo_cmd.py')
    tools = _mcp_tool_names(server_text)
    cli_subcommands = [name for name in ['install', 'uninstall', 'status', 'restart'] if name in main_text or name in cli_text]
    install_side_effects = {
        'detects_local_mcp_ecosystems': 'detect_ecosystems' in cli_text,
        'starts_background_server': 'start_server' in cli_text and 'subprocess.Popen' in cli_text,
        'writes_pid_log_port_agents_state': all(token in cli_text for token in ['PID_FILE_NAME', 'LOG_FILE_NAME', 'PORT_FILE_NAME', 'AGENTS_FILE_NAME']),
        'may_call_claude_mcp_add': 'claude mcp add' in cli_text or 'mcp", "add"' in cli_text,
        'may_bind_localhost_port': '_find_available_port' in cli_text or '127.0.0.1' in cli_text,
    }
    server_import = _run(
        ['python3', '-c', 'from gov_mcp.server import create_server; print("ok")'],
        GOV_MCP_ROOT,
        env={'PYTHONPATH': f'{GOV_MCP_ROOT}:{Y_GOV_ROOT}'},
        timeout=10,
    )
    ystar_demo = _run(['python3', '-m', 'ystar', 'demo'], Y_GOV_ROOT, env={'PYTHONPATH': str(Y_GOV_ROOT)}, timeout=20)
    mcp_dependency_available = importlib.util.find_spec('mcp') is not None
    if server_import['returncode'] == 0 and mcp_dependency_available:
        selected = 'in_process_tool_call'
        selected_reason = 'gov-mcp server imports successfully and FastMCP dependency is available.'
    elif ystar_demo['returncode'] == 0 and {'gov_check', 'gov_demo'}.issubset(set(tools)):
        selected = 'in_process_ystar_kernel_proof_with_server_transport_blocker'
        selected_reason = 'Y-star-gov kernel demo works and gov-mcp exposes gov_check/gov_demo, but the local gov-mcp server import is blocked by missing mcp dependency or client path; no internet install is allowed.'
    else:
        selected = 'blocked_with_exact_missing_code_path'
        selected_reason = 'Neither direct server import nor local Y-star-gov demo proof is available.'
    doctor_supports_explicit_override = any(token in doctor_text for token in ['--session-config', '--cieu-db', '--db', '--project-root'])
    return {
        'artifact_id': 'e48_real_code_interface_discovery',
        'bridge_head': _git_head(BRIDGE_ROOT),
        'gov_mcp_head': _git_head(GOV_MCP_ROOT),
        'y_star_gov_head': _git_head(Y_GOV_ROOT),
        'gov_mcp': {
            'cli_subcommands': cli_subcommands,
            'entrypoint_script': 'gov-mcp = gov_mcp.cli:cli_main' if 'gov-mcp = "gov_mcp.cli:cli_main"' in pyproject_text else 'unknown',
            'server_entrypoint': 'python -m gov_mcp --agents-md <path> --transport sse --host 127.0.0.1 --port <port>',
            'transport_support': [transport for transport in ['stdio', 'sse'] if transport in main_text],
            'install_side_effects': install_side_effects,
            'uninstall_cleanup_behavior': {'stop_server': 'stop_server' in cli_text, 'remove_claude_config': '_remove_claude_code' in cli_text, 'state_dir_cleanup': 'STATE_DIR' in cli_text or '_state_dir' in cli_text},
            'status_is_safe_read': 'def cmd_status' in cli_text and 'Run \'gov-mcp install\'' in cli_text,
            'available_mcp_tools': tools,
            'proof_tools_present': {name: name in tools for name in ['gov_check', 'gov_demo', 'gov_doctor', 'gov_enforce']},
            'server_import_check': server_import,
            'mcp_dependency_available': mcp_dependency_available,
            'fastmcp_test_client_discovered': 'ClientSession' in _read(GOV_MCP_ROOT / 'tests' / 'test_server.py') or 'call_tool' in _read(GOV_MCP_ROOT / 'tests' / 'test_server.py'),
        },
        'y_star_gov': {
            'doctor_module': 'ystar/cli/doctor_cmd.py',
            'demo_module': 'ystar/cli/demo_cmd.py',
            'doctor_supports_explicit_path_or_db_override': doctor_supports_explicit_override,
            'doctor_searches_cwd_and_home_session_config': '.ystar_session.json' in doctor_text and 'Path.cwd' in doctor_text,
            'demo_zero_config_local': 'Y*gov Demo' in demo_text or 'demo' in demo_text,
            'demo_smoke': ystar_demo,
        },
        'selected_demo_strategy': selected,
        'selected_demo_strategy_reason': selected_reason,
        'blocked_external_requirement': mcp_dependency_available is False,
        'no_external_action': True,
    }


if __name__ == '__main__':
    print(json.dumps(discover_real_code_interfaces(), indent=2, ensure_ascii=False))
