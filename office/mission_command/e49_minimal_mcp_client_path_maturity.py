from __future__ import annotations

import importlib.util
import os
import re
import subprocess
from pathlib import Path
from typing import Any

BRIDGE_ROOT = Path(os.environ.get('YSTAR_BRIDGE_LABS_ROOT', Path(__file__).resolve().parents[2]))
GOV_MCP_ROOT = Path(os.environ.get('GOV_MCP_ROOT', '/Users/haotianliu/.openclaw/workspace/gov-mcp'))
Y_GOV_ROOT = Path(os.environ.get('YSTAR_GOV_ROOT', '/Users/haotianliu/.openclaw/workspace/Y-star-gov'))


def _read(path: Path, limit: int = 500_000) -> str:
    try:
        if not path.exists() or path.is_dir() or path.stat().st_size > limit:
            return ''
        return path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return ''


def _run(command: list[str], cwd: Path, timeout: int = 15) -> dict[str, Any]:
    env = os.environ.copy()
    env['PYTHONPATH'] = f'{GOV_MCP_ROOT}:{Y_GOV_ROOT}'
    try:
        cp = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout, check=False)
        return {'command': command, 'cwd': str(cwd), 'returncode': cp.returncode, 'stdout': (cp.stdout or '')[:4000], 'stderr': (cp.stderr or '')[:4000], 'timed_out': False}
    except subprocess.TimeoutExpired as exc:
        return {'command': command, 'cwd': str(cwd), 'returncode': None, 'stdout': (exc.stdout or '')[:4000] if isinstance(exc.stdout, str) else '', 'stderr': (exc.stderr or '')[:4000] if isinstance(exc.stderr, str) else '', 'timed_out': True}
    except Exception as exc:
        return {'command': command, 'cwd': str(cwd), 'returncode': None, 'stdout': '', 'stderr': str(exc), 'timed_out': False}


def inspect_minimal_mcp_client_path() -> dict[str, Any]:
    server = _read(GOV_MCP_ROOT / 'gov_mcp' / 'server.py')
    tests = '\n'.join(_read(path, 120_000) for path in sorted((GOV_MCP_ROOT / 'tests').glob('*.py')))
    pyproject = _read(GOV_MCP_ROOT / 'pyproject.toml')
    direct_functions = sorted(set(re.findall(r'def\s+(gov_[a-zA-Z0-9_]+)\s*\(', server)))
    tool_names = []
    lines = server.splitlines()
    for idx, line in enumerate(lines):
        if '@mcp.tool' in line:
            for follow in lines[idx + 1:idx + 8]:
                m = re.search(r'def\s+(gov_[a-zA-Z0-9_]+)\s*\(', follow)
                if m:
                    tool_names.append(m.group(1))
                    break
    tool_names = sorted(set(tool_names))
    mcp_available = importlib.util.find_spec('mcp') is not None
    server_import = _run(['python3', '-c', 'from gov_mcp.server import create_server; print("ok")'], GOV_MCP_ROOT)
    has_test_helper = any(term in tests for term in ['ClientSession', 'call_tool', 'FastMCP', 'TestClient'])
    exposes_direct_gov_check = 'gov_check' in direct_functions and '@mcp.tool' not in server[server.find('def gov_check')-80:server.find('def gov_check')]
    # gov_check/gov_demo are nested FastMCP tools in current code, not direct module-level callables.
    direct_callable_status = 'nested_fastmcp_tool_only' if {'gov_check', 'gov_demo'}.issubset(set(tool_names)) else 'not_found'
    can_build_without_internet = bool(mcp_available and has_test_helper)
    if can_build_without_internet:
        classification = 'client_path_available_with_existing_dependency'
        next_module = 'use_existing_fastmcp_test_client_helper'
    elif not mcp_available:
        classification = 'blocked_missing_local_mcp_dependency'
        next_module = 'E50_build_minimal_gov_mcp_local_test_client_dependency_gate'
    elif not has_test_helper:
        classification = 'blocked_missing_test_client_helper'
        next_module = 'E50_build_minimal_gov_mcp_local_test_client'
    else:
        classification = 'blocked_unknown_client_path_gap'
        next_module = 'E50_build_minimal_gov_mcp_local_test_client'
    return {
        'artifact_id': 'e49_minimal_mcp_client_path_maturity',
        'gov_mcp_head': _run(['git', 'rev-parse', 'HEAD'], GOV_MCP_ROOT).get('stdout', '').strip(),
        'questions': {
            'has_in_process_fastmcp_test_helper': has_test_helper,
            'exposes_direct_python_callable_for_gov_check_gov_demo': direct_callable_status,
            'local_mcp_dependency_available': mcp_available,
            'can_minimal_client_be_built_without_internet_install': can_build_without_internet,
            'safe_stdio_or_sse_call_currently_available': can_build_without_internet,
        },
        'tool_names_sample': tool_names[:24],
        'server_import_check': server_import,
        'pyproject_declares_mcp_dependency': 'mcp>=' in pyproject,
        'classification': classification,
        'exact_minimal_test_client_module_needed_next': next_module,
        'blocked_external_requirement': not mcp_available,
        'no_internet_install': True,
        'no_external_action': True,
    }
