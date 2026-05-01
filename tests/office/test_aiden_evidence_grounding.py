from pathlib import Path

from office.aiden_meeting_room.aiden_response_engine import answer_owner
from office.aiden_meeting_room.company_context_loader import load_company_context
from office.aiden_meeting_room.repo_evidence_index import build_repo_evidence_index


REPO_ROOT = Path(__file__).resolve().parents[2]


def _ask(message: str, tmp_path: Path) -> str:
    return answer_owner(message, repo_root=REPO_ROOT, memory_path=tmp_path / "memory.json")


def test_evidence_index_loads_required_files():
    index = build_repo_evidence_index(REPO_ROOT)
    sources = {item.source for item in index.items}
    assert "AGENTS.md" in sources
    assert "OPERATIONS.md" in sources
    assert "DIRECTIVE_TRACKER.md" in sources
    assert "knowledge/ceo/wisdom/M_TRIANGLE.md" in sources
    assert "knowledge/ceo/wisdom/WORK_METHODOLOGY.md" in sources
    assert "scripts/gov_order.py" in sources


def test_extracts_m_triangle_value_production():
    index = build_repo_evidence_index(REPO_ROOT)
    labels = {item.label for item in index.items}
    assert "M-3 Value Production" in labels
    assert "Without M-3 toy warning" in labels


def test_extracts_gov_order_pipeline():
    index = build_repo_evidence_index(REPO_ROOT)
    labels = {item.label for item in index.items}
    assert "Board NL pipeline" in labels
    assert "Deterministic validator" in labels
    assert "Obligation registered" in labels


def test_aiden_answers_unseen_agents_burden_question_with_specific_rules(tmp_path):
    text = _ask("AGENTS.md 里哪些治理规则现在会拖慢 M-3 Value Production？", tmp_path)
    assert "12-layer" in text or "5-tuple" in text
    assert "Nightly" in text or "daily" in text or "报告" in text
    assert "Idle" in text or "学习" in text
    assert "M-2 不能被削弱" in text
    assert "Evidence:" in text


def test_aiden_answers_directive_retriage_question_with_specific_categories(tmp_path):
    text = _ask("DIRECTIVE_TRACKER 里哪些任务应该归档，哪些应该继续推进？", tmp_path)
    assert "ARCHIVE_LEGACY" in text
    assert "REVENUE_RELEVANT_NOW" in text
    assert "OWNER_DECISION_REQUIRED" in text
    assert "directive_retriage.json" in text


def test_aiden_answers_operations_calendar_question_not_active_by_default(tmp_path):
    text = _ask("OPERATIONS.md 里的旧 HN/LinkedIn 日程现在还应该约束我们吗？", tmp_path)
    assert "不应该默认" in text
    assert "历史" in text
    assert "M-3" in text
    assert "Evidence:" in text


def test_aiden_answers_current_money_blocker_with_evidence(tmp_path):
    text = _ask("当前最阻碍 Labs 赚钱的是治理问题、产品问题、还是分发问题？依据是什么？", tmp_path)
    assert "不是“治理不够”" in text
    assert "产品化交付" in text
    assert "分发" in text
    assert "Evidence:" in text


def test_aiden_identifies_permission_tier_replacements(tmp_path):
    text = _ask("哪些旧规则应该被 permission tier 替代？", tmp_path)
    assert "permission tier" in text
    assert "外部动作" in text
    assert "Tier 0" in text
    assert "Tier 4" in text


def test_aiden_does_not_use_generic_fallback_for_unseen_questions(tmp_path):
    text = _ask("AGENTS.md 里哪些治理规则现在会拖慢 M-3 Value Production？", tmp_path)
    assert "我理解你问的是" not in text
    assert "Evidence:" in text


def test_context_exposes_analyzer_outputs():
    ctx = load_company_context(REPO_ROOT)
    assert ctx.evidence_index is not None
    assert ctx.governance_findings
    assert ctx.directive_findings
    assert ctx.operations_findings

