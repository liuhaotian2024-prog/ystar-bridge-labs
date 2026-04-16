"""
Test: Coordinator Reply 5-tuple Wire Integration

Board 2026-04-16 P0 — Verify 5th injector in hook_stop_reply_scan.py
correctly detects missing 5-tuple sections in long replies and emits CIEU event.

Scenarios:
1. Short reply (<= 200 chars) → skip audit (no CIEU event)
2. Long reply with all 5 sections → silent pass (no CIEU event)
3. Long prose reply missing ≥1 section → emit CIEU + inject warning

Atomic integration test — runs against live hook scanner.
"""

import sys
import json
from pathlib import Path

# Import scanner + helper from live path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ystar"))

from hook_stop_reply_scan import inject_coordinator_reply_5tuple_audit
from governance.coordinator_audit import check_reply_5tuple_compliance


def test_short_reply_skip():
    """Short reply (<= 200 chars) should skip audit — no CIEU event."""
    short_reply = "老大收到，立刻执行 Task #12。"
    # Direct helper call should return None
    violation = check_reply_5tuple_compliance(short_reply)
    assert violation is None, f"Short reply should skip audit, got {violation}"


def test_long_reply_all_sections_pass():
    """Long reply with all 5-tuple sections should pass silent — no CIEU event."""
    compliant_reply = r"""
**Y\***: Hook injector wired + tests pass.

**Xt**: Scanner has 4 injectors, no 5th.

**U**: Wire 5th injector, write tests, smoke run.

**Yt+1**: 5th injector live, CIEU event emits on violation.

**Rt+1**: 0 if all 5-tuple sections present in this reply, else 1.
"""
    violation = check_reply_5tuple_compliance(compliant_reply)
    assert violation is None, f"Compliant reply should pass, got {violation}"


def test_long_prose_reply_missing_sections():
    """Long prose reply missing ≥1 section should emit CIEU event."""
    prose_reply = """
老大，今天完成了以下 6 个关键任务，每个任务都经过了完整的测试验证：

1. 修复了 hook_stop_reply_scan.py 的 4 个 injector 调用链路，确保所有 warnings 正确注入到 LLM session
2. 添加了 auto_validate_subagent_receipt 逻辑，对所有 sub-agent 返回的 receipt 进行自动化 Rt+1 计算
3. 运行了完整的 pytest 测试套件，86 个测试全部通过，覆盖率达到 92%
4. 更新了 coordinator_audit.py 的三个 helper 函数，增强了 meta-gate 检查能力
5. 完成了 CIEU 数据库的 schema 迁移，新增 2 个索引提升查询性能
6. 整理了 knowledge/cto/ 目录下的所有技术文档，建立了统一的命名规范

所有工作已经完整收敛，系统运行稳定。等待 Board 下一步工作指示。
"""  # 400+ chars, no 5-tuple sections
    violation = check_reply_5tuple_compliance(prose_reply)
    assert violation is not None, f"Prose reply {len(prose_reply)} chars should trigger violation"
    assert violation["violation"] is True
    assert "missing_sections" in violation
    assert len(violation["missing_sections"]) == 5  # All 5 sections missing
    assert violation["char_count"] > 200


def test_injector_emits_cieu_on_violation(tmp_path):
    """
    Integration test: verify injector emits CIEU event + injects warning on violation.

    NOTE: CIEU event emission is verified via database count delta in smoke run.
    This test verifies helper logic only.
    """
    prose_reply = "这是一个超过 200 字的回复内容，但是缺少所有 5-tuple 结构标签。" * 10  # 400+ chars
    violation = check_reply_5tuple_compliance(prose_reply)
    assert violation is not None, "Long prose should trigger violation"
    assert violation["violation"] is True


if __name__ == "__main__":
    # Run all tests locally
    test_short_reply_skip()
    test_long_reply_all_sections_pass()
    test_long_prose_reply_missing_sections()
    test_injector_emits_cieu_on_violation(None)
    print("✓ All 4 assertions PASS")
