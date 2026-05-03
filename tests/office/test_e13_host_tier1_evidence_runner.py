import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("host_tier1_evidence_runner", ROOT / "scripts" / "host_tier1_evidence_runner.py")
host_runner = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules["host_tier1_evidence_runner"] = host_runner
SPEC.loader.exec_module(host_runner)


def test_e13_runner_blocks_no_evidence_without_faking_records(tmp_path: Path):
    request_path = tmp_path / "operations/external_validation/e13_tier1_evidence_request.json"
    request_path.parent.mkdir(parents=True)
    result = host_runner.run_evidence_mission(tmp_path, request_path)
    assert result["classification"] == "blocked_no_evidence"
    records = json.loads((tmp_path / "operations/external_validation/e13_evidence_records.json").read_text(encoding="utf-8"))
    assert records["records"] == []


def test_e13_runner_rejects_login_or_disallowed_source_scheme(tmp_path: Path):
    request_path = tmp_path / "operations/external_validation/e13_tier1_evidence_request.json"
    request_path.parent.mkdir(parents=True)
    request = {
        "request_id": "e13",
        "mission_id": "E13",
        "entry_repository_delivery_rt1": 0,
        "top_offer": "48h AI Ops Operating Room Blueprint",
        "default_path": "Agent Workflow Bottleneck Diagnosis",
        "opportunity_paths": [
            "Agent Workflow Bottleneck Diagnosis",
            "Founder AI Workflow Audit / CEO Command Brief",
            "AI Agent Incident Postmortem Service",
            "Coding-Agent Governance Audit",
            "AI Ops Operating Room Implementation Support",
            "Partner Enablement Package for AI Consultants",
            "Runtime Setup Advisory",
        ],
        "allowed_source_classes": ["public_web_page"],
        "source_urls": [{"url": "file:///private", "source_type": "public_web_page"}],
        "budget": {"max_sources": 1, "max_bytes_per_source": 1000, "max_runtime_seconds": 10},
        "forbidden_actions": [
            "customer_contact",
            "email_or_message",
            "publication",
            "payment",
            "account_creation",
            "form_submission",
            "login",
            "private_data_collection",
            "personal_contact_scraping",
            "high_volume_crawling",
            "secret_reading",
            "core_brain_cieu_memory_writeback",
            "obligation_auto_registration",
        ],
        "counterfactual_questions": [],
        "run_public_collection_if_sources_available": True,
    }
    request_path.write_text(json.dumps(request), encoding="utf-8")
    result = host_runner.run_evidence_mission(tmp_path, request_path)
    assert result["records"] == 0
    assert "blocked_no_evidence" in result["blocked_reason"]


def test_e13_generates_owner_packet_and_czl(tmp_path: Path):
    request_path = tmp_path / "operations/external_validation/e13_tier1_evidence_request.json"
    request_path.parent.mkdir(parents=True)
    host_runner.run_evidence_mission(tmp_path, request_path)
    assert (tmp_path / "operations/external_validation/e13_owner_decision_packet.json").exists()
    assert (tmp_path / "reports/integration/e13_czl_closure.md").exists()
