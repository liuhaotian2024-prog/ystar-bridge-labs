import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "integration"


def _inventory():
    return json.loads((REPORTS / "e11_semantic_capability_inventory.json").read_text(encoding="utf-8"))


def test_global_inventory_covers_bridge_labs():
    inventory = _inventory()
    assert inventory["repos"]["ystar_bridge_labs"]["available"] is True
    assert any(item["repo"] == "ystar_bridge_labs" and item["file_path"].startswith("office/mission_command") for item in inventory["files"])


def test_global_inventory_covers_y_star_gov_or_records_blocker():
    repo = _inventory()["repos"]["y_star_gov"]
    assert repo["available"] is True or repo["blocker"]


def test_global_inventory_covers_gov_mcp_or_records_blocker():
    repo = _inventory()["repos"]["gov_mcp"]
    assert repo["available"] is True or repo["blocker"]


def test_global_inventory_covers_ystar_company_or_records_blocker():
    repo = _inventory()["repos"]["ystar_company"]
    assert repo["available"] is True or repo["blocker"]


def test_inventory_includes_aiden_brain_dream_cieu_method_czl_governance_and_revenue():
    files = _inventory()["files"]
    text = "\n".join(
        " ".join(
            [
                item["file_path"],
                " ".join(item.get("capability_terms", [])),
                " ".join(item.get("classes", [])),
                " ".join(item.get("functions", [])),
                item.get("snippet", ""),
            ]
        )
        for item in files
    ).lower()
    assert "aiden_brain.py" in text or "aiden brain" in text
    assert "aiden_dream.py" in text or "dream" in text
    assert "cieu" in text and "prediction" in text
    assert "aiden_meta_development_method_kernel.md" in text
    assert "czl" in text
    assert "preflight" in text or "permission tier" in text
    assert "revenue path" in text or "buyer signal" in text

