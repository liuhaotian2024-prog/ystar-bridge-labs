from pathlib import Path
from office.mission_command.e48_gov_mcp_sandbox import build_sandbox_strategy


def test_e48_sandbox_blocks_real_client_mutation():
    data = build_sandbox_strategy()
    manifest = data['scratch_workspace_manifest']
    assert manifest['scratch_root'].startswith('/tmp/e48_gov_mcp_demo')
    assert Path(manifest['scratch_agents_md']).exists()
    proof = manifest['real_client_config_mutation_proof']
    assert proof['gov_mcp_install_invoked'] is False
    assert proof['claude_mcp_add_invoked'] is False
    assert data['no_mutation_of_real_client_config'] is True
    assert data['no_external_action'] is True
