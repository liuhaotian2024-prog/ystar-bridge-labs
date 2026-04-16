#!/usr/bin/env python3
"""
Tests for CTO Dispatch Broker Daemon
Per governance/cto_dispatch_broker_v1.md Part 5 test spec
"""
import sys
from pathlib import Path

# Add scripts to path for import
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
from cto_dispatch_broker import classify_tier, select_engineer_for_t1, validate_receipt


def test_cto_broker_tier_classify():
    """Test tier classifier logic."""
    # T3 examples (Board approval required)
    assert classify_tier("git push origin main", "src/", 5) == "T3"
    assert classify_tier("PyPI release 0.43.0", "pyproject.toml", 3) == "T3"
    assert classify_tier("Send cold email to prospect", "sales/", 2) == "T3"
    assert classify_tier("Propose AMENDMENT-030 rollback", "governance/", 4) == "T3"

    # T2 examples (CTO design required)
    assert classify_tier("Refactor CIEU event taxonomy", "src/cieu/", 20) == "T2"  # >15 tool_uses
    assert classify_tier("Add new MCP server", "src/mcp/server.py,src/mcp/client.py,tests/mcp/test.py,docs/mcp.md", 10) == "T2"  # 4 files >3
    assert classify_tier("Architecture change for API", "ystar/kernel/api.py", 8) == "T2"  # "architecture" keyword
    assert classify_tier("New module for governance pipeline", "ystar/governance/pipeline.py", 12) == "T2"  # "new module" keyword

    # T1 examples (direct engineer dispatch)
    assert classify_tier("Add ForgetGuard warn rule", "governance/forget_guard_rules.yaml", 8) == "T1"
    assert classify_tier("Extend hook try/except", "scripts/governance_boot.sh", 5) == "T1"
    assert classify_tier("Fix typo in error message", "ystar/kernel/parser.py", 2) == "T1"
    assert classify_tier("Add test assertions", "tests/platform/test_hook.py", 6) == "T1"


def test_cto_broker_engineer_select():
    """Test engineer selection based on scope."""
    assert select_engineer_for_t1("governance/forget_guard_rules.yaml") == "maya-governance"
    assert select_engineer_for_t1("governance/amendments/a001.md") == "maya-governance"

    assert select_engineer_for_t1("scripts/dispatch_board.py") == "ryan-platform"
    assert select_engineer_for_t1("scripts/governance_boot.sh,tests/platform/test_hook.py") == "ryan-platform"

    assert select_engineer_for_t1("ystar/kernel/parser.py") == "leo-kernel"
    assert select_engineer_for_t1("kernel/runtime.py") == "leo-kernel"

    assert select_engineer_for_t1("ystar/domains/claw_template.py") == "jordan-domains"
    assert select_engineer_for_t1("domains/registry.py") == "jordan-domains"


def test_cto_broker_receipt_validate():
    """Test receipt validation (Rt+1=0 check + scope compliance)."""
    task = {
        "atomic_id": "CZL-99",
        "scope": "governance/forget_guard_rules.yaml",
    }

    # Valid receipt: Rt+1=0, files in scope
    receipt_valid = """
Y*: ForgetGuard rule added mode=warn
Xt: 0 rules for ceo_dispatch_velocity
U: add rule to forget_guard_rules.yaml
Yt+1: 1 rule active
Rt+1: 0

Modified files:
- governance/forget_guard_rules.yaml
"""
    assert validate_receipt(task, receipt_valid) == True

    # Invalid: Rt+1 > 0
    receipt_rt_fail = """
Y*: rule added
Xt: partial work
U: attempted add
Yt+1: incomplete
Rt+1: 0.5
"""
    assert validate_receipt(task, receipt_rt_fail) == False

    # Invalid: Rt+1 missing
    receipt_no_rt = """
Y*: rule added
Xt: 0 rules
U: add rule
Yt+1: 1 rule
"""
    assert validate_receipt(task, receipt_no_rt) == False

    # Valid: Rt+1=0.0 (float format)
    receipt_float_rt = "Y*: done\nXt: init\nU: work\nYt+1: complete\nRt+1: 0.0"
    assert validate_receipt(task, receipt_float_rt) == True
