from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from aiden_messenger_service_install import LABEL, LEGACY_LABELS, build_plist, install_launch_agent, wait_for_health


def test_aiden_messenger_launchagent_plist_points_to_local_server(tmp_path: Path) -> None:
    plist = build_plist(repo_root=tmp_path / "repo", ystar_gov_root=tmp_path / "Y-star-gov")
    assert plist["Label"] == LABEL
    assert LABEL == "com.ystar.aiden-messenger-runtime"
    assert "com.ystar.aiden-agent-native-messenger" in LEGACY_LABELS
    assert plist["ProgramArguments"][1].endswith("office/agent_native_messenger/server.py")
    assert plist["WorkingDirectory"] == str(tmp_path / "repo")
    assert plist["KeepAlive"] is True
    env = plist["EnvironmentVariables"]
    assert env["PYTHONPATH"] == str(tmp_path / "repo")
    assert env["YSTAR_BRIDGE_LABS_ROOT"] == str(tmp_path / "repo")
    assert env["YSTAR_GOV_ROOT"] == str(tmp_path / "Y-star-gov")
    assert env["AIDEN_MESSENGER_PORT"] == "8784"
    assert env["AIDEN_MESSENGER_ALLOW_LIVE_NETWORK"] == "0"


def test_aiden_messenger_launchagent_can_opt_into_default_public_read(tmp_path: Path) -> None:
    plist = build_plist(
        repo_root=tmp_path / "repo",
        ystar_gov_root=tmp_path / "Y-star-gov",
        allow_live_network_by_default=True,
        runtime_timeout_seconds=240,
    )
    env = plist["EnvironmentVariables"]
    assert env["AIDEN_MESSENGER_ALLOW_LIVE_NETWORK"] == "1"
    assert env["AIDEN_MESSENGER_RUNTIME_TIMEOUT_SECONDS"] == "240"


def test_dry_run_does_not_install_launchagent(tmp_path: Path) -> None:
    result = install_launch_agent(repo_root=tmp_path / "repo", ystar_gov_root=tmp_path / "Y-star-gov", dry_run=True)
    assert result["dry_run"] is True
    assert result["installed"] is False
    assert result["target"].endswith(f"{LABEL}.plist")


def test_install_report_uses_dict_results_for_bootout(monkeypatch, tmp_path: Path) -> None:
    import aiden_messenger_service_install as installer

    calls = []

    def fake_run(args):
        calls.append(args)
        if args[:2] == ["/usr/bin/curl", "-sS"]:
            return {"command": args, "returncode": 0, "stdout": '{"ok": true}', "stderr": ""}
        return {"command": args, "returncode": 0, "stdout": "", "stderr": ""}

    class FakeCompleted:
        returncode = 0
        stdout = ""
        stderr = ""

    monkeypatch.setattr(installer, "_run", fake_run)
    monkeypatch.setattr(installer, "_uid", lambda: "501")
    monkeypatch.setattr(installer.subprocess, "run", lambda *args, **kwargs: FakeCompleted())
    monkeypatch.setattr(installer.Path, "home", lambda: tmp_path / "home")

    result = install_launch_agent(repo_root=tmp_path / "repo", ystar_gov_root=tmp_path / "Y-star-gov")

    assert result["installed"] is True
    assert result["bootout_returncode"] == 0
    assert result["bootout_stderr"] == ""
    assert result["health_returncode"] == 0
    assert result["health_attempts"] == 1
    assert calls


def test_health_check_waits_for_server_to_bind(monkeypatch) -> None:
    import aiden_messenger_service_install as installer

    attempts = []

    def fake_run(args):
        attempts.append(args)
        if len(attempts) < 3:
            return {"command": args, "returncode": 7, "stdout": "", "stderr": "connection refused"}
        return {"command": args, "returncode": 0, "stdout": '{"ok": true}', "stderr": ""}

    monkeypatch.setattr(installer, "_run", fake_run)
    monkeypatch.setattr(installer.time, "sleep", lambda seconds: None)

    result = wait_for_health(port=8784, attempts=5, sleep_seconds=0)

    assert result["returncode"] == 0
    assert result["attempts"] == 3
