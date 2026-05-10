from pathlib import Path

from office.aiden_meeting_room.aiden_intent_classifier import classify_intent
from office.aiden_meeting_room.aiden_response_engine import answer_owner
from office.aiden_meeting_room.company_context_loader import load_company_context


REPO_ROOT = Path(__file__).resolve().parents[2]


def _ask(message: str, tmp_path: Path) -> str:
    return answer_owner(message, repo_root=REPO_ROOT, memory_path=tmp_path / "memory.json")


def test_context_loads_required_company_files():
    ctx = load_company_context(REPO_ROOT)
    assert "README.md" in ctx.source_texts
    assert "AGENTS.md" in ctx.source_texts
    assert "knowledge/ceo/wisdom/M_TRIANGLE.md" in ctx.source_texts
    assert "Aiden Liu — CEO" in ctx.team_roster


def test_intent_classifier_owner_examples():
    assert classify_intent("Aiden，我们现在到底做什么东西才能最快拿到第一笔钱？") == "fastest_cash"
    assert classify_intent("Aiden，你是依据什么得出这个方向的？你对于我们 Labs 的元发展是怎么认识的？") == "rationale_meta"
    assert classify_intent("Aiden，你现在自己是一个什么状态？你现在怎么形容自己的？") == "self_state"
    assert classify_intent("我们之前仓库的问题是什么？这几天的新架构能怎么修？") == "repo_repair"


def test_fastest_cash_answer_is_repo_grounded(tmp_path):
    text = _ask("Aiden，我们现在到底做什么东西才能最快拿到第一笔钱？", tmp_path)
    assert "我的判断" in text
    assert "strategy/memo runtime" in text
    assert "repo 证据" in text
    assert "M-3" in text
    assert "真客户" in text


def test_rationale_mentions_meta_development_and_assets(tmp_path):
    text = _ask("Aiden，你是依据什么得出这个方向的？你对于我们 Labs 的元发展是怎么认识的？", tmp_path)
    assert "owner 真正要决定的问题" in text
    assert "M Triangle" in text
    assert "依据" in text


def test_self_state_is_honest_about_limits(tmp_path):
    text = _ask("Aiden，你现在自己是一个什么状态？你现在怎么形容自己的？", tmp_path)
    assert "repo-grounded" in text
    assert "不是完全自治 CEO" in text
    assert "不会自动发邮件" in text


def test_repo_repair_answer_identifies_original_repo_problems(tmp_path):
    text = _ask("我们之前仓库的问题是什么？这几天的新架构能怎么修？", tmp_path)
    assert "repo 证据" in text
    assert "Search before build" in text or "Evidence:" in text
    assert "重复造轮子" in text or "现有能力" in text or "evidence" in text


def test_next_ceo_action_routes_existing_team_without_coo(tmp_path):
    text = _ask("下一步你作为 CEO 应该带团队做什么？", tmp_path)
    assert "行动包" in text
    assert "目标" in text
    assert "交付物" in text
    assert "风险边界" in text
    assert "COO" not in text


def test_no_external_action_claims(tmp_path):
    text = _ask("下一步你需要我批准什么？", tmp_path)
    assert "外部副作用" in text
    assert "不会自动发邮件" in text
