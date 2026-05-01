from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List

from .evidence_extractor import EvidenceItem, find_keyword_evidence


@dataclass
class RepoEvidenceIndex:
    repo_root: Path
    items: List[EvidenceItem] = field(default_factory=list)

    def add(self, items: Iterable[EvidenceItem]) -> None:
        self.items.extend(items)

    def by_source(self, source: str) -> List[EvidenceItem]:
        return [item for item in self.items if item.source == source]

    def by_label(self, *labels: str) -> List[EvidenceItem]:
        wanted = set(labels)
        return [item for item in self.items if item.label in wanted]

    def by_classification(self, *classifications: str) -> List[EvidenceItem]:
        wanted = set(classifications)
        return [item for item in self.items if item.classification in wanted]

    def search(self, *keywords: str) -> List[EvidenceItem]:
        lowered = [keyword.lower() for keyword in keywords]
        return [
            item
            for item in self.items
            if any(keyword in item.text.lower() or keyword in item.label.lower() for keyword in lowered)
        ]


def build_repo_evidence_index(repo_root: Path) -> RepoEvidenceIndex:
    index = RepoEvidenceIndex(repo_root=repo_root)

    charter_specs = [
        ("Active charter mission", ["prove that an AI agent team", "produce real value"], "core_constitutional"),
        ("Active charter default priority", ["Default priority is M-3", "M-3 Value Production unless"], "active_runtime_rule"),
        ("Active runtime Mission Command", ["Mission Command", "company_runtime policy", "gov-mcp company preflight"], "active_runtime_rule"),
        ("Administrative rationalization", ["Old daily", "HN and LinkedIn calendars", "Old directive tracker items"], "active_runtime_rule"),
        ("Approval model", ["approve", "reject", "request_revision", "hold"], "replace_with_permission_tier"),
    ]
    for label, keywords, classification in charter_specs:
        index.add(find_keyword_evidence(repo_root, "governance/ACTIVE_OPERATING_CHARTER.md", keywords, label, classification, limit=3))

    # AGENTS.md: extract both core rules and possible administrative burden.
    agents_specs = [
        ("M Triangle", ["M TRIANGLE", "M(t)", "M-3 Value Production"], "core_constitutional"),
        ("Iron Rule 0 choice rule", ["IRON RULE 0", "NO CHOICE QUESTIONS"], "replace_with_permission_tier"),
        ("Deterministic enforcement", ["Deterministic Enforcement", "NO LLM"], "core_constitutional"),
        ("Maturity transparency", ["Maturity State Transparency", "L0 IDEA"], "active_runtime_rule"),
        ("Unified work protocol", ["Unified Three-Framework", "CIEU 5-Tuple", "12-layer"], "administrative_burden"),
        ("Idle learning loop", ["Idle Learning Loop", "空闲学习循环"], "administrative_burden"),
        ("Continuous autonomous work", ["Continuous Autonomous Work Mandate", "Nightly Report"], "administrative_burden"),
        ("Social media approval", ["Social Media Engagement", "Content Approval Request"], "replace_with_permission_tier"),
        ("Article source verification", ["Article Writing Constitutional Rule", "cite the exact source"], "active_runtime_rule"),
        ("Reporting obligation", ["autonomous_daily_report", "weekly_board_summary", "session_report_before_close"], "administrative_burden"),
        ("Company mission", ["AI agent 团队能自主运营一家真公司", "真价值"], "core_constitutional"),
    ]
    for label, keywords, classification in agents_specs:
        index.add(find_keyword_evidence(repo_root, "AGENTS.md", keywords, label, classification, limit=3))

    # OPERATIONS.md: extract old schedules and commercial history.
    operations_specs = [
        ("Daily schedule", ["Daily Schedule", "周报+周计划", "今日简报"], "stale_admin"),
        ("Weekly cycle", ["Weekly Cycle", "reports/weekly"], "stale_admin"),
        ("HN cadence", ["HN发帖窗口", "HN文章发布节奏", "Show HN"], "historical"),
        ("LinkedIn cadence", ["LinkedIn内容发布", "LinkedIn内容策略", "LinkedIn"], "historical"),
        ("Enterprise sales phase", ["Enterprise Sales Phase", "warm intro", "enterprise"], "owner_decision_required"),
        ("Legacy dispatch", ["Legacy Internal Governance", "DEPRECATED", "Active Dispatch"], "historical"),
        ("Old reporting obligation", ["CEO周报", "CFO周报", "CEO日报", "Daily operations"], "stale_admin"),
        ("Revenue blocker", ["0 users", "0 forks", "3用户", "0发布", "first real user"], "revenue_relevant_now"),
    ]
    for label, keywords, classification in operations_specs:
        index.add(find_keyword_evidence(repo_root, "OPERATIONS.md", keywords, label, classification, limit=4))

    # DIRECTIVE_TRACKER.md: extract active directives and known stale/revenue items.
    directive_specs = [
        ("Directive tracker decomposition rule", ["10分钟内", "活跃指令"], "active_runtime_rule"),
        ("HN article task", ["HN文章系列", "Series", "content/articles"], "archive_legacy"),
        ("LinkedIn task", ["LinkedIn策略", "LinkedIn"], "archive_legacy"),
        ("Three repo task", ["三仓库综合运用", "三仓库"], "superseded_by_runtime"),
        ("Enterprise sales task", ["Enterprise Sales Phase", "warm intro"], "owner_decision_required"),
        ("NotebookLM task", ["NotebookLM", "$890"], "owner_decision_required"),
        ("Patent task", ["专利", "USPTO"], "owner_decision_required"),
        ("Testing baseline task", ["测试覆盖率基线", "test"], "revenue_relevant_now"),
        ("K9 long-term task", ["长期数据收集", ".ystar_cieu.db"], "owner_decision_required"),
    ]
    for label, keywords, classification in directive_specs:
        index.add(find_keyword_evidence(repo_root, "DIRECTIVE_TRACKER.md", keywords, label, classification, limit=4))

    # M Triangle.
    m_specs = [
        ("M-1 Survivability", ["M-1 Survivability", "生存性"], "core_constitutional"),
        ("M-2 Governability", ["M-2 Governability", "可治性"], "core_constitutional"),
        ("M-3 Value Production", ["M-3 Value Production", "价值产出"], "core_constitutional"),
        ("Without M-3 toy warning", ["没一个客户", "没一分收入", "内部玩具", "no customers"], "revenue_relevant_now"),
        ("Value production criteria", ["真产品", "真客户", "真收入", "真业界影响"], "revenue_relevant_now"),
    ]
    for label, keywords, classification in m_specs:
        index.add(find_keyword_evidence(repo_root, "knowledge/ceo/wisdom/M_TRIANGLE.md", keywords, label, classification, limit=3))

    # Work methodology.
    methodology_specs = [
        ("Plan is not done", ["plan ≠ done", "plan + document", "不是 done"], "active_runtime_rule"),
        ("Real tests over hand-wave", ["真实测试", "empirical data", "hand-wave"], "active_runtime_rule"),
        ("OODA", ["OODA", "观察", "搜索", "分析", "验证"], "active_runtime_rule"),
        ("Search before build", ["先查后造", "EXTEND existing"], "active_runtime_rule"),
        ("M to action chain", ["M → 中间目标", "目标传导链", "U → action"], "active_runtime_rule"),
        ("Quantitative honesty", ["定量诚实", "% completion"], "active_runtime_rule"),
    ]
    for label, keywords, classification in methodology_specs:
        index.add(find_keyword_evidence(repo_root, "knowledge/ceo/wisdom/WORK_METHODOLOGY.md", keywords, label, classification, limit=3))

    # gov_order pipeline.
    gov_order_specs = [
        ("Board NL pipeline", ["Detect LLM provider", "Translate via LLM", "BOARD_NL"], "active_runtime_rule"),
        ("Deterministic validator", ["validate_obligation_dict", "Hard schema gate", "No LLM"], "core_constitutional"),
        ("Intent recorded", ["INTENT_RECORDED", "source='gov_order'"], "active_runtime_rule"),
        ("Obligation registered", ["OBLIGATION_REGISTERED", "register_obligation_programmatic"], "active_runtime_rule"),
        ("Pending fallback", ["reports/board_proposed_changes/pending", "manual fallback"], "active_runtime_rule"),
    ]
    for label, keywords, classification in gov_order_specs:
        index.add(find_keyword_evidence(repo_root, "scripts/gov_order.py", keywords, label, classification, limit=3))

    return index
