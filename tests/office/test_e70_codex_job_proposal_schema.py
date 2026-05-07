import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_codex_job_proposal_schema_has_bridge_boundaries():
    data = json.loads((ROOT / "operations/external_validation/e70_codex_job_proposal_schema.json").read_text())
    required = set(data["required_fields"])
    assert "archaeology_requirement" in required
    assert "reuse_first_requirement" in required
    assert "delivery_bridge_fallback" in required
    assert data["CEO_may_generate_internal_Codex_job_proposals"] is True
    assert data["CEO_may_execute_arbitrary_code_directly"] is False
