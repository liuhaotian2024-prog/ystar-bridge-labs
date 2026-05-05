from office.mission_command.e38_public_evidence_research_agenda import build_public_evidence_research_agenda


def test_research_agenda_covers_primary_watchlist_and_sentinels():
    data = build_public_evidence_research_agenda()
    assert "AI productivity / workflow / toolchain" in data["primary_clusters"]
    assert "enterprise / professional AI transformation" in data["primary_clusters"]
    assert data["secondary_watchlist_clusters"]
    assert data["high_imagination_sentinel_clusters"]
    assert data["claim_extraction_schema"]
