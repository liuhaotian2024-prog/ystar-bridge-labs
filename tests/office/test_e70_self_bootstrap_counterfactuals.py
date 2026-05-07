import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_e70_counterfactuals_cover_skill_codex_measurement_and_sequence():
    data = json.loads((ROOT / "operations/external_validation/e70_self_bootstrap_counterfactuals.json").read_text())
    text = " ".join(item["question"] + " " + item["answer"] for item in data["counterfactuals"])
    assert len(data["counterfactuals"]) >= 12
    assert "skill" in text
    assert "Codex" in text
    assert "CIEU residuals" in text
    assert data["best_sequence"][0] == "E70 self-bootstrap runtime"
