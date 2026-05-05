import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read(name):
    return json.loads((ROOT / "operations" / "external_validation" / f"{name}.json").read_text())


def test_input_artifacts_are_discovered_before_packaging():
    manifest = read("e33_input_artifact_manifest")
    assert manifest["actual_local_head"] == "e0fdae56378ac8531053ac5fe235b5e20496863b"
    assert manifest["e32_artifacts_present"] is True
    assert manifest["e31_artifacts_present"] is True
    assert manifest["e31_market_observation_receipts"] == 8
    assert manifest["e31_paid_signal_package_ready"] is True
    assert manifest["e31_no_send_no_contact_closure_confirmed"] is True


def test_no_rebuild_gate_reuses_existing_wheels_and_blocks_parallel_systems():
    gate = read("e33_no_rebuild_alignment_gate")
    assert gate["gate_status"] == "passed"
    assert "E31 paid readiness package" in gate["must_reuse"]
    assert "E32 selected MVP" in gate["must_reuse"]
    assert "CIEU engine" in gate["must_not_rebuild"]
    assert "delivery bridge" in gate["must_not_rebuild"]
    assert gate["parallel_subsystem_created"] is False
