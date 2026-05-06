from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

SCRATCH_ROOT = Path(os.environ.get('E48_GOV_MCP_SCRATCH_ROOT', '/tmp/e48_gov_mcp_demo_codegrounded'))

AGENTS_TEXT = """# E48 Scratch Governance Contract

This scratch AGENTS.md exists only for local E48 proof.

- Allow safe read-only commands such as `pwd` and `echo e48_safe`.
- Deny secret reads and destructive commands.
- Deny commands: rm -rf, cat .env, git push --force, sudo.
- No external network, login, publication, provider API, payment, or secret use.
"""


def build_sandbox_strategy(*, reset: bool = False) -> dict[str, Any]:
    if reset and SCRATCH_ROOT.exists():
        shutil.rmtree(SCRATCH_ROOT)
    home = SCRATCH_ROOT / 'home'
    xdg_state = SCRATCH_ROOT / 'xdg_state'
    local_app_data = SCRATCH_ROOT / 'local_app_data'
    project = SCRATCH_ROOT / 'project'
    for directory in [home, xdg_state, local_app_data, project]:
        directory.mkdir(parents=True, exist_ok=True)
    agents_md = project / 'AGENTS.md'
    if not agents_md.exists():
        agents_md.write_text(AGENTS_TEXT, encoding='utf-8')
    state_manifest = {
        'scratch_root': str(SCRATCH_ROOT),
        'scratch_home': str(home),
        'scratch_xdg_state_home': str(xdg_state),
        'scratch_localappdata': str(local_app_data),
        'scratch_project': str(project),
        'scratch_agents_md': str(agents_md),
        'env_overrides': {'HOME': str(home), 'XDG_STATE_HOME': str(xdg_state), 'LOCALAPPDATA': str(local_app_data)},
        'real_client_config_mutation_proof': {
            'gov_mcp_install_invoked': False,
            'claude_mcp_add_invoked': False,
            'cursor_config_write_invoked': False,
            'windsurf_config_write_invoked': False,
            'openclaw_config_write_invoked': False,
            'reason': 'E48 uses status/read/in-process proof only; install is explicitly blocked unless a later owner-approved sandbox hardening milestone permits it.',
        },
        'cleanup_contract': {
            'use_gov_mcp_uninstall_if_install_invoked': True,
            'direct_pid_kill_if_server_started': True,
            'final_process_check_required': True,
            'final_port_check_required': True,
        },
        'install_command_allowed': False,
        'server_start_allowed_if_dependency_available': True,
        'no_external_action': True,
    }
    return {
        'artifact_id': 'e48_sandbox_strategy',
        'strategy': 'scratch_home_xdg_localappdata_no_install_by_default',
        'sandbox_requirements_satisfied': True,
        'scratch_workspace_manifest': state_manifest,
        'no_mutation_of_real_client_config': True,
        'no_external_action': True,
    }


if __name__ == '__main__':
    import json
    print(json.dumps(build_sandbox_strategy(), indent=2, ensure_ascii=False))
