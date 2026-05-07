from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / "office/mission_command/e86_cieu_log_insertion_point_report.json"
READBACK_PATH = ROOT / "office/mission_command/e86_cieu_log_insertion_point_readback.md"


def _report() -> dict:
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def test_e86_report_records_formal_cieu_insertion_path():
    report = _report()

    assert report["job_id"] == "E86_YStarGov_CEO_Cognitive_OS_CIEU_Log_Write_Insertion_Point_R1"
    assert report["path_chosen"] == "formal insertion implemented"
    assert report["formal_CIEU_log_written"] is True
    assert report["formal_CIEU_log_status"] == "formal_CIEU_record_write_path_verified"
    assert report["validator_output_status"] == "formal_CIEU_record_written_when_E86_writer_invoked"
    assert report["runtime_default_formal_CIEU_log_written"] is False
    assert (
        report["exact_insertion_path"]["underlying_formal_store"]
        == "ystar.governance.cieu_store.CIEUStore.write_dict"
    )


def test_e86_report_preserves_required_decision_mapping():
    mapping = _report()["decision_mapping"]

    assert "allow" in mapping["ALLOW"]
    assert "rewrite" in mapping["REQUIRE_REVISION"]
    assert "deny" in mapping["DENY"]
    assert "escalate" in mapping["ESCALATE"]
    assert "info" in mapping["STATUS_ONLY"]


def test_e86_report_does_not_claim_k9_or_external_execution():
    report = _report()

    assert report["K9Audit_boundary"]["K9Audit_mutated"] is False
    assert report["K9Audit_boundary"]["K9Audit_ledger_written"] is False
    assert report["safety_statement"]["no_external_action"] is True
    assert report["safety_statement"]["no_gov_mcp_live_provider_execution"] is True
    assert report["safety_statement"]["no_parallel_ledger_created"] is True


def test_e86_readback_exists_and_states_default_runtime_write_boundary():
    text = READBACK_PATH.read_text(encoding="utf-8")

    assert "formal insertion implemented" in text
    assert "CIEUStore.write_dict" in text
    assert "side-effect-free by default" in text
    assert "K9Audit ledger write" in text
