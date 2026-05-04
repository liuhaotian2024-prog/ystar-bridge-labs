import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_e25_provider_sandbox_capability_sync_reads_gov_mcp_foundation():
    data = json.loads((ROOT / "operations/external_validation/e25_provider_sandbox_capability_sync.json").read_text())
    assert data["source_repo"] == "gov-mcp"
    assert data["source_delivery_remote_confirmed"] is True
    assert data["sandbox_mode_available"] is True
    assert data["sandbox_scaffold_ready"] is True
    assert data["live_enabled"] is False
    assert data["persistent_idempotency"]["foundation_available"] is True
