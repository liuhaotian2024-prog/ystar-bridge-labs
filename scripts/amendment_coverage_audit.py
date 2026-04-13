#!/usr/bin/env python3
"""
scripts/amendment_coverage_audit.py — Amendment Coverage Matrix Audit
======================================================================

Scans Y*gov governance rules and produces coverage matrix:
  rule × remediation_filled × has_fulfiller × has_test × last_tested

Rule Classes Audited:
  1. Behavior Rules (agent_behavior_rules in .ystar_session.json)
  2. Obligation Types (contract.obligation_timing in .ystar_session.json)
  3. Write Boundaries (agent_write_paths, restricted_write_paths, immutable_paths)
  4. Delegation Chain (delegation_chain.links)
  5. Intent Guards (intent_guard_protected_paths)

Output: reports/amendment_coverage_matrix.md

Missing items flagged with ❌ (red in markdown renderers).

Usage:
    python3 scripts/amendment_coverage_audit.py
    cat reports/amendment_coverage_matrix.md
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Set

# Add Y-star-gov to path for imports
YSTAR_GOV_PATH = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
if YSTAR_GOV_PATH.exists():
    sys.path.insert(0, str(YSTAR_GOV_PATH))

try:
    from ystar.governance.obligation_remediation import OBLIGATION_REMEDIATION_MAP
except ImportError:
    OBLIGATION_REMEDIATION_MAP = {}


# ── Config ──────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
SESSION_CONFIG = REPO_ROOT / ".ystar_session.json"
OUTPUT_FILE = REPO_ROOT / "reports" / "amendment_coverage_matrix.md"
YSTAR_GOV_TESTS = YSTAR_GOV_PATH / "tests"


# ── Helpers ─────────────────────────────────────────────────────────────────────

def load_session_config() -> dict:
    """Load .ystar_session.json."""
    if not SESSION_CONFIG.exists():
        return {}
    with open(SESSION_CONFIG) as f:
        return json.load(f)


def scan_tests_for_coverage(rule_name: str, rule_class: str) -> tuple[bool, str]:
    """
    Scan Y-star-gov/tests/ for test coverage of this rule.

    Returns: (has_test: bool, last_tested: str)
    """
    if not YSTAR_GOV_TESTS.exists():
        return False, "N/A"

    # Patterns to search for
    patterns = [
        rule_name.lower(),
        rule_name.replace("_", "-").lower(),
        rule_class.lower(),
    ]

    # Scan test files
    test_files = list(YSTAR_GOV_TESTS.glob("test_*.py"))
    for test_file in test_files:
        content = test_file.read_text()
        for pattern in patterns:
            if pattern in content.lower():
                # Get file mtime
                mtime = test_file.stat().st_mtime
                from datetime import datetime
                last_tested = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                return True, last_tested

    return False, "never"


def check_behavior_rule_remediation(rule_name: str) -> bool:
    """
    Check if behavior rule has remediation in boundary_enforcer.py.

    Heuristic: search for rule_name in boundary_enforcer.py Remediation() calls.
    """
    boundary_enforcer = YSTAR_GOV_PATH / "ystar" / "adapters" / "boundary_enforcer.py"
    if not boundary_enforcer.exists():
        return False

    content = boundary_enforcer.read_text()
    # Look for Remediation(...rule_name="<rule_name>"...)
    return f'rule_name="{rule_name}"' in content


def check_obligation_remediation(obligation_type: str) -> bool:
    """Check if obligation type has remediation in OBLIGATION_REMEDIATION_MAP."""
    return obligation_type in OBLIGATION_REMEDIATION_MAP


def check_fulfiller(rule_name: str, rule_class: str) -> bool:
    """
    Check if rule has fulfiller logic (auto-fulfillment code).

    For obligations: check if there's trigger/fulfillment code in obligation_triggers.py
    For behaviors: check if there's auto-fix code in boundary_enforcer.py
    """
    # Obligation fulfiller: check obligation_triggers.py
    if rule_class == "obligation":
        triggers_file = YSTAR_GOV_PATH / "ystar" / "governance" / "obligation_triggers.py"
        if not triggers_file.exists():
            return False
        content = triggers_file.read_text()
        return rule_name in content

    # Behavior fulfiller: check if boundary_enforcer has auto-fix
    boundary_enforcer = YSTAR_GOV_PATH / "ystar" / "adapters" / "boundary_enforcer.py"
    if not boundary_enforcer.exists():
        return False
    content = boundary_enforcer.read_text()
    # Look for auto-fix patterns (e.g., "auto_fix_<rule_name>")
    return f"auto_fix_{rule_name}" in content or f"_fulfill_{rule_name}" in content


# ── Main Audit ──────────────────────────────────────────────────────────────────

def audit_behavior_rules(cfg: dict) -> List[dict]:
    """Audit agent_behavior_rules."""
    rows = []
    behavior_rules = cfg.get("agent_behavior_rules", {})

    all_rules: Set[str] = set()
    for agent, rules in behavior_rules.items():
        if isinstance(rules, dict):
            all_rules.update(rules.keys())

    for rule_name in sorted(all_rules):
        has_remediation = check_behavior_rule_remediation(rule_name)
        has_fulfiller = check_fulfiller(rule_name, "behavior")
        has_test, last_tested = scan_tests_for_coverage(rule_name, "behavior_rule")

        rows.append({
            "rule_class": "behavior_rule",
            "rule_name": rule_name,
            "remediation_filled": has_remediation,
            "has_fulfiller": has_fulfiller,
            "has_test": has_test,
            "last_tested": last_tested,
        })

    return rows


def audit_obligation_types(cfg: dict) -> List[dict]:
    """Audit obligation_timing types."""
    rows = []
    obligation_timing = cfg.get("contract", {}).get("obligation_timing", {})

    for obligation_type in sorted(obligation_timing.keys()):
        has_remediation = check_obligation_remediation(obligation_type)
        has_fulfiller = check_fulfiller(obligation_type, "obligation")
        has_test, last_tested = scan_tests_for_coverage(obligation_type, "obligation")

        rows.append({
            "rule_class": "obligation",
            "rule_name": obligation_type,
            "remediation_filled": has_remediation,
            "has_fulfiller": has_fulfiller,
            "has_test": has_test,
            "last_tested": last_tested,
        })

    return rows


def audit_write_boundaries(cfg: dict) -> List[dict]:
    """Audit write boundary rules."""
    rows = []

    # Immutable paths
    immutable = cfg.get("immutable_paths", {}).get("patterns", [])
    for pattern in immutable:
        has_remediation = check_behavior_rule_remediation("immutable_paths")
        has_test, last_tested = scan_tests_for_coverage("immutable_paths", "boundary")
        rows.append({
            "rule_class": "write_boundary",
            "rule_name": f"immutable:{pattern}",
            "remediation_filled": has_remediation,
            "has_fulfiller": False,  # No auto-fulfiller for write boundaries
            "has_test": has_test,
            "last_tested": last_tested,
        })

    # Restricted write paths
    restricted = cfg.get("restricted_write_paths", {})
    for pattern in restricted.keys():
        has_remediation = check_behavior_rule_remediation("restricted_write_paths")
        has_test, last_tested = scan_tests_for_coverage("restricted_write_paths", "boundary")
        rows.append({
            "rule_class": "write_boundary",
            "rule_name": f"restricted:{pattern}",
            "remediation_filled": has_remediation,
            "has_fulfiller": False,
            "has_test": has_test,
            "last_tested": last_tested,
        })

    # CEO deny paths
    ceo_deny = cfg.get("ceo_deny_paths", [])
    for pattern in ceo_deny:
        has_remediation = check_behavior_rule_remediation("ceo_code_block")
        has_test, last_tested = scan_tests_for_coverage("ceo_code_block", "boundary")
        rows.append({
            "rule_class": "write_boundary",
            "rule_name": f"ceo_deny:{pattern}",
            "remediation_filled": has_remediation,
            "has_fulfiller": False,
            "has_test": has_test,
            "last_tested": last_tested,
        })

    return rows


def audit_delegation_chain(cfg: dict) -> List[dict]:
    """Audit delegation_chain rules."""
    rows = []
    links = cfg.get("delegation_chain", {}).get("links", [])

    for i, link in enumerate(links):
        principal = link.get("principal", "unknown")
        actor = link.get("actor", "unknown")
        rule_name = f"delegate:{principal}→{actor}"
        has_remediation = check_behavior_rule_remediation("delegation_chain")
        has_test, last_tested = scan_tests_for_coverage("delegation_chain", "delegation")

        rows.append({
            "rule_class": "delegation",
            "rule_name": rule_name,
            "remediation_filled": has_remediation,
            "has_fulfiller": False,
            "has_test": has_test,
            "last_tested": last_tested,
        })

    return rows


def audit_intent_guards(cfg: dict) -> List[dict]:
    """Audit intent_guard_protected_paths."""
    rows = []
    protected = cfg.get("intent_guard_protected_paths", [])

    for pattern in protected:
        has_remediation = check_obligation_remediation("intent_declaration")
        has_test, last_tested = scan_tests_for_coverage("intent_guard", "intent")
        rows.append({
            "rule_class": "intent_guard",
            "rule_name": f"intent_guard:{pattern}",
            "remediation_filled": has_remediation,
            "has_fulfiller": False,
            "has_test": has_test,
            "last_tested": last_tested,
        })

    return rows


# ── Report Generation ───────────────────────────────────────────────────────────

def generate_report(rows: List[dict]) -> str:
    """Generate markdown report."""
    # Count stats
    total = len(rows)
    remediation_filled = sum(1 for r in rows if r["remediation_filled"])
    has_fulfiller = sum(1 for r in rows if r["has_fulfiller"])
    has_test = sum(1 for r in rows if r["has_test"])

    missing_remediation = [r for r in rows if not r["remediation_filled"]]
    missing_fulfiller = [r for r in rows if not r["has_fulfiller"]]
    missing_test = [r for r in rows if not r["has_test"]]

    md = f"""# Amendment Coverage Matrix Audit

**Generated:** {Path(__file__).name} at {os.popen('date').read().strip()}

## Summary

| Metric | Count | % Coverage |
|--------|-------|------------|
| Total Rules | {total} | 100% |
| Remediation Filled | {remediation_filled} | {remediation_filled*100//total if total else 0}% |
| Has Fulfiller | {has_fulfiller} | {has_fulfiller*100//total if total else 0}% |
| Has Test | {has_test} | {has_test*100//total if total else 0}% |

## Coverage Matrix

| Rule Class | Rule Name | Remediation | Fulfiller | Test | Last Tested |
|------------|-----------|-------------|-----------|------|-------------|
"""

    for row in rows:
        rem = "✅" if row["remediation_filled"] else "❌"
        ful = "✅" if row["has_fulfiller"] else "❌"
        tst = "✅" if row["has_test"] else "❌"
        md += f"| {row['rule_class']} | `{row['rule_name']}` | {rem} | {ful} | {tst} | {row['last_tested']} |\n"

    # Gap sections
    md += "\n## Gaps: Missing Remediation\n\n"
    if missing_remediation:
        for r in missing_remediation:
            md += f"- ❌ `{r['rule_name']}` ({r['rule_class']})\n"
    else:
        md += "✅ All rules have remediation\n"

    md += "\n## Gaps: Missing Fulfiller\n\n"
    if missing_fulfiller:
        for r in missing_fulfiller:
            md += f"- ❌ `{r['rule_name']}` ({r['rule_class']})\n"
    else:
        md += "✅ All rules have fulfiller logic\n"

    md += "\n## Gaps: Missing Tests\n\n"
    if missing_test:
        for r in missing_test:
            md += f"- ❌ `{r['rule_name']}` ({r['rule_class']})\n"
    else:
        md += "✅ All rules have test coverage\n"

    md += f"""
## Next Steps

1. **Remediation Gaps ({len(missing_remediation)})**: Add Remediation() to boundary_enforcer.py or obligation_remediation.py
2. **Fulfiller Gaps ({len(missing_fulfiller)})**: Add auto-fulfillment logic to obligation_triggers.py or boundary_enforcer.py
3. **Test Gaps ({len(missing_test)})**: Add test cases to Y-star-gov/tests/test_*.py

## Notes

- **Remediation**: Structured guidance when rule is violated (AMENDMENT-012)
- **Fulfiller**: Auto-fulfillment code that proactively satisfies obligations (AMENDMENT-012)
- **Test**: Automated test coverage in Y-star-gov test suite
- **Last Tested**: File mtime of test file containing rule name (heuristic)

Write boundaries and delegation chains typically don't have fulfillers (enforcement only).
Obligations should have both remediation AND fulfiller (teach how + auto-fix when possible).
"""

    return md


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    print(f"Loading session config from {SESSION_CONFIG}...")
    cfg = load_session_config()

    if not cfg:
        print("ERROR: Could not load .ystar_session.json", file=sys.stderr)
        return 1

    print("Auditing rule classes...")
    rows = []
    rows.extend(audit_behavior_rules(cfg))
    rows.extend(audit_obligation_types(cfg))
    rows.extend(audit_write_boundaries(cfg))
    rows.extend(audit_delegation_chain(cfg))
    rows.extend(audit_intent_guards(cfg))

    print(f"Scanned {len(rows)} rules")

    print(f"Generating report to {OUTPUT_FILE}...")
    report = generate_report(rows)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(report)

    print(f"✅ Report written to {OUTPUT_FILE}")
    print(f"\nSummary: {len(rows)} rules audited")
    print(f"  Remediation: {sum(1 for r in rows if r['remediation_filled'])}/{len(rows)}")
    print(f"  Fulfiller:   {sum(1 for r in rows if r['has_fulfiller'])}/{len(rows)}")
    print(f"  Test:        {sum(1 for r in rows if r['has_test'])}/{len(rows)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
