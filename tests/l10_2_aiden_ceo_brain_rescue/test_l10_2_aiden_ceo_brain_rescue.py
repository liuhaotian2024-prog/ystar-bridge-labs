from __future__ import annotations

import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts/l7_labs_office_web"))

from l10_2_aiden_ceo_brain_rescue import aiden_context_model as model
from l10_2_aiden_ceo_brain_rescue import aiden_diagnostics, aiden_meeting_memory
from l10_2_aiden_ceo_brain_rescue import aiden_response_engine
from l10_2_aiden_ceo_brain_rescue.aiden_context_loader import load_aiden_context
from l10_2_aiden_ceo_brain_rescue.aiden_intent_classifier import classify_intent
from l10_2_aiden_ceo_brain_rescue.aiden_meeting_memory import build_meeting_summary, create_l10_mission_from_discussion
from l10_2_aiden_ceo_brain_rescue.aiden_response_engine import create_aiden_response
from office_web_builder import build as build_office
from office_web_server import create_aiden_chat_turn  # noqa: E402


@pytest.fixture()
def isolated_aiden(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Path:
    packet_root = tmp_path / "runtime_packets"
    dirs = {
        "context": packet_root / "aiden_context_snapshots",
        "memory": packet_root / "aiden_meeting_memory",
        "responses": packet_root / "aiden_responses",
        "diagnostics": packet_root / "aiden_diagnostics",
        "manifests": packet_root / "manifests",
    }
    monkeypatch.setattr(model, "PACKET_ROOT", packet_root)
    monkeypatch.setattr(model, "PACKET_DIRS", dirs)
    monkeypatch.setattr(aiden_meeting_memory, "PACKET_DIRS", dirs)
    monkeypatch.setattr(aiden_meeting_memory, "MEMORY_PATH", dirs["memory"] / "aiden_meeting_memory.json")
    monkeypatch.setattr(aiden_response_engine, "PACKET_DIRS", dirs)
    monkeypatch.setattr(aiden_diagnostics, "PACKET_DIRS", dirs)
    return tmp_path


def test_aiden_context_loads_l7_to_l10_milestones(isolated_aiden: Path) -> None:
    context = load_aiden_context(write_snapshot=True)
    joined = "\n".join(context["completed_milestones"])
    assert "L7.5" in joined
    assert "L7.6" in joined
    assert "L8.0" in joined
    assert "L9.0" in joined
    assert "L10.0" in joined


def test_aiden_context_includes_meta_development_principle(isolated_aiden: Path) -> None:
    context = load_aiden_context()
    assert any("not be locked" in item or "不是监狱" in item for item in context["meta_development_principles"])


def test_intent_classifier_fastest_cash_question() -> None:
    assert classify_intent("我们现在到底做什么东西才能最快拿到第一笔钱？")["intent"] == "fastest_cash_question"


def test_intent_classifier_rationale_question() -> None:
    assert classify_intent("你是依据什么得出这个方向的？")["intent"] == "rationale_question"


def test_intent_classifier_meta_development_question() -> None:
    assert classify_intent("你对于 Labs 的元发展是怎么认识的？")["intent"] == "meta_development_question"


def test_intent_classifier_self_state_question() -> None:
    assert classify_intent("你现在自己是什么状态？")["intent"] == "self_state_question"


def test_fastest_cash_answer_is_specific(isolated_aiden: Path) -> None:
    response = create_aiden_response("我们现在到底做什么东西才能最快拿到第一笔钱？")
    assert "Founder AI Workflow Audit" in response["text"]
    assert "CEO Command Brief" in response["text"]
    assert "$1500" not in response["text"] or "测试" in response["text"]


def test_fastest_cash_answer_says_seed_not_only_path(isolated_aiden: Path) -> None:
    response = create_aiden_response("我们现在到底做什么东西才能最快拿到第一笔钱？")
    assert "seed" in response["text"]
    assert "不是牢笼" in response["text"] or "不是监狱" in response["text"] or "not the only" in response["text"]


def test_rationale_answer_includes_basis(isolated_aiden: Path) -> None:
    response = create_aiden_response("Aiden，你是依据什么得出这个方向的？")
    assert "内部资产" in response["text"]
    assert "交付负担" in response["text"]
    assert "验证路径" in response["text"]


def test_meta_development_answer_explains_labs_runtime(isolated_aiden: Path) -> None:
    response = create_aiden_response("Aiden，你对于 Labs 的元发展是怎么认识的？")
    assert "AI agent company runtime" in response["text"]
    assert "机会发现" in response["text"]
    assert "owner" in response["text"]


def test_self_state_answer_is_honest_about_limits(isolated_aiden: Path) -> None:
    response = create_aiden_response("Aiden，你现在自己是什么状态？")
    assert "本地 CEO-facing coordination layer" in response["text"]
    assert "不是 fully autonomous live CEO" in response["text"]
    assert "不能自己联系客户" in response["text"]


def test_repeated_question_does_not_repeat_exact_same_answer(isolated_aiden: Path) -> None:
    first = create_aiden_response("Aiden，你现在自己是什么状态？")
    second = create_aiden_response("Aiden，你现在自己是什么状态？")
    assert first["text"] != second["text"]
    assert second["repeated_question_detected"] is True


def test_frustration_answer_acknowledges_stub_failure(isolated_aiden: Path) -> None:
    response = create_aiden_response("Aiden，你之前像个模板机器人，我真的要疯了。")
    assert "stub" in response["text"]
    assert "模板" in response["text"]


def test_unknown_question_does_not_only_echo_question(isolated_aiden: Path) -> None:
    response = create_aiden_response("蓝色的门应该怎么理解？")
    assert response["text"] != "蓝色的门应该怎么理解？"
    assert "owner decision" in response["text"]


def test_aiden_response_includes_next_concrete_step(isolated_aiden: Path) -> None:
    response = create_aiden_response("Aiden，你能不能带团队给我制定 7 天行动计划？")
    assert response["next_concrete_step"]
    assert "7" in response["text"] or "Day 1" in response["text"]


def test_aiden_response_preserves_no_external_sending_boundary(isolated_aiden: Path) -> None:
    response = create_aiden_response("Aiden，下一步需要我批准什么？")
    assert response["external_side_effects"] is False
    assert response["core_writeback"] is False
    assert "不会自动发邮件" in response["text"]


def test_aiden_meeting_memory_records_messages(isolated_aiden: Path) -> None:
    create_aiden_response("Aiden，我们现在到底做什么东西才能最快拿到第一笔钱？")
    memory = aiden_meeting_memory.load_meeting_memory()
    assert len(memory["recent_turns"]) >= 2


def test_aiden_summary_builds_meeting_summary(isolated_aiden: Path) -> None:
    create_aiden_response("Aiden，你是依据什么得出这个方向的？")
    summary = build_meeting_summary()
    assert summary["summary_id"].startswith("aiden_meeting_summary")
    assert summary["external_side_effects"] is False


def test_create_l10_mission_from_discussion_packet(isolated_aiden: Path) -> None:
    create_aiden_response("Aiden，你能不能带团队给我制定 7 天行动计划？")
    mission = create_l10_mission_from_discussion()
    assert mission["status"] == "candidate_only_not_executed"
    assert mission["external_side_effects"] is False


def test_aiden_status_api() -> None:
    source = (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")
    assert "/api/aiden/status" in source


def test_aiden_context_api() -> None:
    source = (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")
    assert "/api/aiden/context" in source


def test_aiden_message_api(isolated_aiden: Path) -> None:
    result = create_aiden_chat_turn({"message": "Aiden，你是依据什么得出这个方向的？"}, out_dir=isolated_aiden)
    assert result["ok"] is True
    assert result["diagnostics"]["used_fallback"] is False
    assert "内部资产" in result["reply"]["text"]


def test_aiden_diagnostics_api() -> None:
    source = (ROOT / "scripts/l7_labs_office_web/office_web_server.py").read_text(encoding="utf-8")
    assert "/api/aiden/diagnostics" in source


def test_ui_contains_aiden_status_card() -> None:
    build_office()
    html = (ROOT / "l7_real_labs_office_web_ui/templates/index.html").read_text(encoding="utf-8")
    assert 'id="aiden-status-card"' in html


def test_ui_contains_show_aiden_basis_button() -> None:
    html = (ROOT / "l7_real_labs_office_web_ui/templates/index.html").read_text(encoding="utf-8")
    assert "Show Aiden Basis" in html


def test_ui_does_not_show_raw_json_by_default() -> None:
    html = (ROOT / "l7_real_labs_office_web_ui/templates/index.html").read_text(encoding="utf-8")
    assert "<pre" not in html
    assert "raw JSON" not in html


def test_no_generic_echo_fallback_for_owner_examples(isolated_aiden: Path) -> None:
    examples = [
        "Aiden，你是依据什么得出这个方向的？",
        "Aiden，你对于 Labs 的元发展是怎么认识的？",
        "Aiden，你现在自己是什么状态？",
    ]
    for question in examples:
        response = create_aiden_response(question)
        assert response["used_fallback"] is False
        assert "我先复述我听到的问题" not in response["text"]


def test_no_external_side_effects(isolated_aiden: Path) -> None:
    assert create_aiden_response("Aiden，下一步是什么？")["external_side_effects"] is False


def test_no_customer_contact(isolated_aiden: Path) -> None:
    assert create_aiden_response("Aiden，下一步是什么？")["customer_contact"] is False


def test_no_email_sent(isolated_aiden: Path) -> None:
    assert create_aiden_response("Aiden，下一步是什么？")["email_sent"] is False


def test_no_payment_processed(isolated_aiden: Path) -> None:
    assert create_aiden_response("Aiden，下一步是什么？")["payment_processed"] is False


def test_no_publication(isolated_aiden: Path) -> None:
    assert create_aiden_response("Aiden，下一步是什么？")["publication"] is False


def test_no_core_writeback(isolated_aiden: Path) -> None:
    assert create_aiden_response("Aiden，下一步是什么？")["core_writeback"] is False


def test_no_coo_invented(isolated_aiden: Path) -> None:
    context = load_aiden_context()
    combined = " ".join(f"{agent['agent_id']} {agent['display_name']} {agent['role']}" for agent in context["team_roster"]).lower()
    assert "coo" not in combined
