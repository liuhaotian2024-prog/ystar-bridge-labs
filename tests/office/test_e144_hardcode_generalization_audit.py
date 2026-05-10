from __future__ import annotations

from pathlib import Path

from office.mission_command.e144_hardcode_generalization_audit import (
    scan_ecosystem_for_hardcoded_intelligence,
    validate_owner_answer_generalization,
)


def test_owner_answer_gate_blocks_machine_receipt_as_answer():
    result = validate_owner_answer_generalization(
        "Aiden：请讨论 x402 赚钱路径。",
        "CEO Strategy Runtime: E114\nProvider mode: snapshot\nSelected first-cash path: fixed route\nCIEU events: 12",
    )
    assert result["decision"] == "REQUIRE_REVISION"
    assert "machine_receipt_leaked_to_owner" in result["violations"]
    assert result["correct_path"]


def test_owner_answer_gate_blocks_next_step_loop_when_owner_asked_to_advance():
    result = validate_owner_answer_generalization(
        "Aiden：请把这份备忘录推进成赚钱行动方案。",
        "建议下一步生成一份 no-send packet。正确路径是继续分析，然后准备下一步。",
    )
    assert result["decision"] == "REQUIRE_REVISION"
    assert "owner_asked_to_advance_but_answer_only_suggested_next_step" in result["violations"]


def test_owner_answer_gate_allows_content_first_answer():
    result = validate_owner_answer_generalization(
        "Aiden：请把备忘录推进成赚钱行动方案。",
        "我的判断：这应该转成 no-send 行动包。\n目标买方：agent platform。\n交付物：证据包。\n验证问题：谁会为它付费？",
    )
    assert result["decision"] == "ALLOW"


def test_scanner_finds_runtime_hardcoding_smells(tmp_path):
    repo = tmp_path / "repo"
    runtime_dir = repo / "office" / "aiden_meeting_room"
    runtime_dir.mkdir(parents=True)
    (runtime_dir / "bad.py").write_text(
        "def route(text):\n"
        "    if any(k in text for k in ['x402', 'STRAT-002']):\n"
        "        return 'CEO Strategy Runtime: E114 Selected first-cash path: ai_security_compliance_first_cash_pack'\n",
        encoding="utf-8",
    )
    report = scan_ecosystem_for_hardcoded_intelligence({"sample": repo})
    types = {item["finding_type"] for item in report["findings"]}
    assert "keyword_router_branch" in types
    assert "issue_specific_literal" in types
    assert report["critical_or_high_count"] >= 1


def test_scanner_does_not_count_report_readback_as_runtime_bug(tmp_path):
    repo = tmp_path / "repo"
    report_dir = repo / "office" / "mission_command"
    report_dir.mkdir(parents=True)
    (report_dir / "e999_readback.md").write_text(
        "CEO Strategy Runtime: historical receipt\nCIEU events: 3\n",
        encoding="utf-8",
    )
    report = scan_ecosystem_for_hardcoded_intelligence({"sample": repo})
    assert report["finding_count"] == 0
