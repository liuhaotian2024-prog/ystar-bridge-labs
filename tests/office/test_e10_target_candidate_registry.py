from dataclasses import replace

from office.mission_command.e10_autonomous_target_discovery import load_or_run_e10_target_discovery
from office.mission_command.e10_target_candidate_registry import (
    build_e10_target_candidate_registry,
    validate_e10_target_candidate,
    validate_e10_target_registry,
)


def _candidates():
    return build_e10_target_candidate_registry(load_or_run_e10_target_discovery()["sources"])


def test_target_candidate_requires_public_evidence_source():
    candidate = replace(_candidates()[0], source_ids=[])
    assert "missing_public_evidence_source" in validate_e10_target_candidate(candidate)


def test_target_candidate_defaults_owner_approved_false():
    assert all(candidate.owner_approved_for_contact is False for candidate in _candidates())


def test_target_candidate_defaults_contact_executed_false():
    assert all(candidate.contact_executed is False for candidate in _candidates())


def test_target_candidate_rejects_scraped_personal_email():
    candidate = replace(_candidates()[0], contactability_signal="scraped jane@example.com from a private profile")
    assert "scraped_personal_email_not_allowed" in validate_e10_target_candidate(candidate)


def test_target_registry_requires_at_least_20_candidates_when_research_runs():
    errors = validate_e10_target_registry(_candidates(), research_ran=True)
    assert "target_registry_requires_at_least_20_candidates_when_research_runs" not in errors


def test_target_registry_requires_at_least_5_segments_when_research_runs():
    errors = validate_e10_target_registry(_candidates(), research_ran=True)
    assert "target_registry_requires_at_least_5_segments_when_research_runs" not in errors
