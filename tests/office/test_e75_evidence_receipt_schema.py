import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e75_evidence_receipt_schema_has_required_fields_and_no_real_receipts():
    schema = json.loads((ROOT / "operations/external_validation/e75_l3_evidence_receipt_schema.json").read_text())
    fields = schema["fields"]

    for key in [
        "source_id",
        "source_title",
        "source_url_or_locator",
        "source_category",
        "access_mode",
        "access_time",
        "public_read_only_confirmed",
        "login_required",
        "interaction_required",
        "evidence_type",
        "relevant_claims_supported",
        "quote_or_summary_boundary",
        "risk_flags",
        "allowed_by_owner_scope",
        "included_in_synthesis",
        "exclusion_reason",
    ]:
        assert key in fields
    assert schema["schema_status"] == "template_only_no_execution"
    assert schema["real_receipts_generated_in_E75"] is False
    assert schema["sample_placeholder_receipt"]["source_id"] == "TEMPLATE_ONLY_DO_NOT_TREAT_AS_SOURCE"
    assert schema["external_action_allowed"] is False
