from office.mission_command.e39_durable_strategic_research_thread import build_durable_strategic_research_thread


def test_durable_threads_are_artifact_only_and_safe_to_replay():
    threads = build_durable_strategic_research_thread()
    assert threads["thread_count"] >= 4
    clusters = {t["cluster"] for t in threads["threads"]}
    assert "enterprise / professional AI transformation" in clusters
    assert "AI productivity / workflow / toolchain" in clusters
    assert any("agent economy" in c for c in clusters)
    assert threads["external_runtime_integrated"] is False
    for thread in threads["threads"]:
        assert all(thread["replay_safety"].values())
        assert thread["checkpoint_state"] in {"created", "public evidence collected", "contradiction reviewed", "expert preflight ready", "owner approval pending", "parked"}
