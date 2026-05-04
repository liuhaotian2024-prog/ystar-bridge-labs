from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from repository_delivery_bridge_install import installer_success_payload


def test_payload_regenerated_is_not_success_without_remote_confirmation() -> None:
    payload = installer_success_payload({"committed": False, "pushed": False, "remote_confirmed": False}, False)
    assert payload["status"] == "BLOCKED"
    assert payload["repository_delivery_rt1"] == 1
    assert payload["future_owner_delivery_commands_required"] is True


def test_success_requires_self_delivery_remote_confirmed_and_launchagent_loaded() -> None:
    payload = installer_success_payload({"committed": True, "pushed": True, "remote_confirmed": True}, True)
    assert payload["status"] == "DELIVERY_SUCCEEDED"
    assert payload["repository_delivery_rt1"] == 0
    assert payload["future_owner_delivery_commands_required"] is False


def test_remote_confirmed_without_daemon_loaded_is_not_full_success() -> None:
    payload = installer_success_payload({"committed": True, "pushed": True, "remote_confirmed": True}, False)
    assert payload["status"] == "BLOCKED"
    assert payload["self_delivery"]["repository_delivery_rt1"] == 0
    assert payload["future_owner_delivery_commands_required"] is True


def test_per_milestone_bootstrap_is_disabled_only_after_success() -> None:
    success = installer_success_payload({"committed": True, "pushed": True, "remote_confirmed": True}, True)
    failed = installer_success_payload({"committed": True, "pushed": False, "remote_confirmed": False}, True)
    assert success["per_milestone_bootstrap_allowed"] is False
    assert failed["per_milestone_bootstrap_allowed"] is None

