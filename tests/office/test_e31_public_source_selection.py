import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_public_source_selection_is_bounded_and_safe():
    data = json.loads((ROOT / "operations/external_validation/e31_public_source_selection.json").read_text())
    assert data["selection_status"] == "selected"
    assert data["source_count"] == 8
    assert data["rules"]["public_only"] is True
    assert data["rules"]["no_login"] is True
    assert data["rules"]["no_forms"] is True
