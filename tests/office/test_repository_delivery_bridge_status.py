from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from repository_delivery_bridge_status import collect_status, render_markdown


def test_status_reports_bridge_queues(tmp_path: Path) -> None:
    status = collect_status(tmp_path / "bridge")
    assert status["queues"]["pending"] == []
    assert status["future_owner_delivery_commands_required"] is True
    assert status["per_milestone_bootstrap_allowed"] is False
    markdown = render_markdown(status)
    assert "Repository Delivery Bridge Status" in markdown
