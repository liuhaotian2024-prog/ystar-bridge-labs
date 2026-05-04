from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import repository_delivery_bridge_status as bridge_status
from repository_delivery_bridge_status import collect_status, render_markdown


def test_status_reports_install_required_when_launch_agent_not_loaded(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        bridge_status,
        "launchctl_status",
        lambda: {
            "launchctl_available": True,
            "plist_path": str(tmp_path / "bridge.plist"),
            "plist_exists": False,
            "loaded": False,
            "tokens_printed": False,
            "credential_values_printed": False,
        },
    )
    status = collect_status(tmp_path / "bridge")
    assert status["queues"]["pending"] == []
    assert status["bridge_installed"] is False
    assert status["transport_mode"] == "bridge_install_required_once"
    assert status["next_milestone_delivery_mode"] == "bridge_install_required_once"
    assert status["future_owner_delivery_commands_required"] is True
    assert status["per_milestone_bootstrap_allowed"] is False
    markdown = render_markdown(status)
    assert "Repository Delivery Bridge Status" in markdown


def test_status_reports_host_local_bridge_when_launch_agent_loaded(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        bridge_status,
        "launchctl_status",
        lambda: {
            "launchctl_available": True,
            "plist_path": str(tmp_path / "bridge.plist"),
            "plist_exists": True,
            "loaded": True,
            "tokens_printed": False,
            "credential_values_printed": False,
        },
    )
    status = collect_status(tmp_path / "bridge")
    assert status["bridge_installed"] is True
    assert status["transport_mode"] == "host_local_bridge"
    assert status["next_milestone_delivery_mode"] == "host_local_bridge"
    assert status["future_owner_delivery_commands_required"] is False
    assert status["per_milestone_bootstrap_allowed"] is False
