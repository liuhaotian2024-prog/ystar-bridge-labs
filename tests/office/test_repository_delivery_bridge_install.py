from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from repository_delivery_bridge_install import plist_text


def test_install_plist_points_to_worker_and_bridge_root(tmp_path: Path) -> None:
    text = plist_text(tmp_path / "repo", tmp_path / "bridge")
    assert "com.ystar.repository-delivery-bridge" in text
    assert "repository_delivery_bridge_worker.py" in text
    assert "--daemon" in text
    assert str(tmp_path / "bridge") in text


def test_installer_uses_modern_launchctl_fallback_when_load_fails(monkeypatch, tmp_path: Path) -> None:
    import repository_delivery_bridge_install as installer

    calls: list[list[str]] = []

    def fake_run(args: list[str]) -> dict:
        calls.append(args)
        return {"command": args, "returncode": 1 if args[:2] == ["launchctl", "load"] else 0, "stdout": "", "stderr": ""}

    def fake_status(bridge_root: Path) -> dict:
        return {"launch_agent": {"loaded": True}, "bridge_root": str(bridge_root)}

    monkeypatch.setattr(installer, "run", fake_run)
    monkeypatch.setattr(installer, "collect_status", fake_status)
    monkeypatch.setattr(installer, "PLIST_PATH", tmp_path / "LaunchAgents" / "com.ystar.repository-delivery-bridge.plist")
    result = installer.install(tmp_path / "repo", tmp_path / "bridge", start=True)
    assert result["started"] is True
    assert any(call[:2] == ["launchctl", "bootstrap"] for call in calls)
    assert any(call[:2] == ["launchctl", "kickstart"] for call in calls)
