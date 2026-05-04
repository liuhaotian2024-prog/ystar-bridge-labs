import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def test_e25_sandbox_guard_stack_passes_sandbox_and_blocks_live_promotion():
    data = json.loads((ROOT / "operations/external_validation/e25_sandbox_guard_results.json").read_text())
    assert data["guard_block_count"] == 0
    checks = data["guard_results"][0]["checks"]
    assert any(c["check"] == "live_disabled_check" and c["status"] == "passed" for c in checks)
    assert any(c["check"] == "persistent_idempotency_live_check" and "not_applicable" in c["status"] for c in checks)
