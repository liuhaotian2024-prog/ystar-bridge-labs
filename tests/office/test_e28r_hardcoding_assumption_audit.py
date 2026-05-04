import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
def test_hardcoding_audit_corrects_e28_without_undoing_it():
    d = json.loads((ROOT / "operations/external_validation/e28r_hardcoding_assumption_audit.json").read_text())
    assert d["do_not_undo_e28"] is True
    assert d["history_rewritten"] is False
    assert d["e28_artifacts_deleted"] is False
    assert d["hardcoded_or_overweighted_assumption_count"] == 4
    assert d["production_live_config_global_default_corrected"] is True
