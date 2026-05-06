from office.mission_command.e59_controlled_public_page_read_adapter import controlled_public_read, is_forbidden_source, run_controlled_public_page_read_adapter


def test_adapter_blocks_forbidden_sources_and_handles_network_unavailable():
    data = run_controlled_public_page_read_adapter()
    assert data["adapter_status"] == "fixture_only_network_unavailable"
    assert data["supports_fixture_reads"] is True
    assert data["forbidden_probe"]["retrieval_status"] == "blocked_by_policy"
    assert all(item["retrieval_status"] == "network_unavailable" for item in data["live_candidate_receipts"])
    assert data["never_collects_contact_info"] is True
    blocked, reason = is_forbidden_source("https://www.linkedin.com/in/person")
    assert blocked is True
    assert "linkedin" in reason
    receipt = controlled_public_read({"source_id": "login", "source_url_or_fixture": "https://example.com/login", "source_type": "login", "domain": "bad"})
    assert receipt["retrieval_status"] == "blocked_by_policy"

