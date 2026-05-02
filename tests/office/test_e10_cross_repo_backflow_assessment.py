from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "integration"


def test_cross_repo_backflow_assessment_mentions_Y_star_gov_and_gov_mcp():
    text = (REPORTS / "e10_cross_repo_backflow_assessment.md").read_text(encoding="utf-8")
    assert "Y-star-gov" in text
    assert "gov-mcp" in text
    assert "proposed vs approved target seed" in text
    assert "no-contact assurance tool" in text


def test_cross_repo_backflow_assessment_keeps_e10_changes_in_bridge_labs():
    text = (REPORTS / "e10_cross_repo_backflow_assessment.md").read_text(encoding="utf-8")
    assert "Do not modify Y-star-gov or gov-mcp in E10" in text
    assert "bridge-labs" in text
