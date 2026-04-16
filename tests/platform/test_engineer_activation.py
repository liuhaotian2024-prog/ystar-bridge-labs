"""
Test engineer activation steps 3-5 (CZL-102 Ryan atomic).

Verifies:
1. governance_boot.sh CHARTER_MAP contains 5 new engineer entries
2. dispatch_board.py accepts new engineer IDs in claim validation
3. engineer_trust_scores.json contains 5 new entries with trust=0

Platform Engineer: Ryan Park
"""
import json
import subprocess
import sys
from pathlib import Path

YSTAR_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
NEW_ENGINEERS = ["eng-data", "eng-security", "eng-ml", "eng-perf", "eng-compliance"]


def test_charter_map_has_new_engineers():
    """Verify governance_boot.sh CHARTER_MAP contains 5 new engineer entries."""
    boot_script = YSTAR_DIR / "scripts" / "governance_boot.sh"
    content = boot_script.read_text()

    for eng_id in NEW_ENGINEERS:
        # Check for entry like: "eng-data": [".claude/agents/eng-data.md"],
        assert f'"{eng_id}":' in content, f"CHARTER_MAP missing {eng_id}"
        assert f'.claude/agents/{eng_id}.md' in content, f"CHARTER_MAP missing {eng_id} path"

    print(f"✓ CHARTER_MAP contains all 5 new engineers")


def test_dispatch_board_accepts_new_engineers():
    """Verify dispatch_board.py accepts new engineer IDs in claim validation."""
    dispatch_board = YSTAR_DIR / "scripts" / "dispatch_board.py"
    content = dispatch_board.read_text()

    # Check VALID_ENGINEERS list contains new IDs
    for eng_id in NEW_ENGINEERS:
        assert f'"{eng_id}"' in content, f"dispatch_board.py missing {eng_id} in VALID_ENGINEERS"

    print(f"✓ dispatch_board.py VALID_ENGINEERS contains all 5 new engineers")


def test_trust_scores_has_new_engineers():
    """Verify engineer_trust_scores.json contains 5 new entries with trust=0."""
    trust_file = YSTAR_DIR / "knowledge" / "engineer_trust_scores.json"
    with open(trust_file) as f:
        data = json.load(f)

    engineers_dict = {e["engineer_id"]: e for e in data["engineers"]}

    for eng_id in NEW_ENGINEERS:
        assert eng_id in engineers_dict, f"trust_scores missing {eng_id}"
        assert engineers_dict[eng_id]["trust_score"] == 0, f"{eng_id} trust != 0"
        assert engineers_dict[eng_id]["activation_status"] == "inactive", f"{eng_id} not inactive"
        assert engineers_dict[eng_id]["gauntlet_status"] == "pending", f"{eng_id} gauntlet not pending"

    print(f"✓ engineer_trust_scores.json contains all 5 new engineers with trust=0")


if __name__ == "__main__":
    try:
        test_charter_map_has_new_engineers()
        test_dispatch_board_accepts_new_engineers()
        test_trust_scores_has_new_engineers()
        print("\n[PASS] All 3 activation tests passed (CZL-102 W3 criterion)")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[FAIL] {e}", file=sys.stderr)
        sys.exit(1)
