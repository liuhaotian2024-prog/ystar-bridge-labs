from office.mission_command.e39_e38_evidence_ingestion_adapter import build_e38_evidence_ingestion_manifest


def test_e38_evidence_ingestion_consumes_required_artifacts():
    manifest = build_e38_evidence_ingestion_manifest()
    assert manifest["normalized_source_count"] == 27
    assert manifest["normalized_claim_count"] == 54
    assert manifest["normalized_cluster_count"] >= 7
    assert manifest["frontier_backlog_items_consumed"] >= 11
    assert manifest["graph_construction_can_proceed"] is True
    assert manifest["missing_fields"] == []
    assert manifest["data_quality_issues"] == []
    assert manifest["customer_validation_claimed"] is False
    assert manifest["paid_signal_claimed"] is False
