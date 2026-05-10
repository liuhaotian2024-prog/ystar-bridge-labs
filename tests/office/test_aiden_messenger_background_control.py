from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import aiden_messenger_background_control as control


def test_background_control_health_reports_unavailable_port() -> None:
    result = control.health_check(port=9)
    assert result["ok"] is False
    assert result["url"] == "http://127.0.0.1:9/api/health"


def test_background_control_status_shape(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(control, "DEFAULT_LOG_ROOT", tmp_path / "messenger")
    result = control.status_background(port=9)
    assert result["pid"] is None
    assert result["pid_file"].endswith("aiden_messenger.pid")
    assert result["health"]["ok"] is False
