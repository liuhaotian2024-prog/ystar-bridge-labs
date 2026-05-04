import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def test_e26_persistent_idempotency_is_hardened_but_not_live_ready():
    d=json.loads((ROOT/"operations/external_validation/e26_persistent_idempotency_readiness.json").read_text())
    assert d["extension_delivered"] is True
    assert d["persistent_ready"] is False
    assert d["store_type"]=="file_backed_json_contract"
    assert d["duplicate_protection_result"]=="validated_by_gov_mcp_tests_duplicate_noop"
    assert d["corruption_handling"]=="corrupted_store_blocked"
