from office.mission_command.e38_cluster_evidence_update import build_cluster_evidence_update


def test_cluster_evidence_update_tracks_levels_without_validation_claim():
    data = build_cluster_evidence_update()
    assert data["cluster_updates"]
    assert data["strongest_supported_cluster"]
    for row in data["cluster_updates"]:
        assert row["evidence_level_after_E38"] >= row["evidence_level_before_E38"]
        assert row["customer_validation_claimed"] is False
        assert row["paid_signal_claimed"] is False
