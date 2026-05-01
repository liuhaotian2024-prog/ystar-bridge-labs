from __future__ import annotations

from pathlib import Path

from .aiden_intent_classifier import classify_intent
from .company_context_loader import CompanyContext, load_company_context
from .directive_retriage_analyzer import grouped_directive_summary
from .evidence_extractor import format_evidence
from .governance_burden_analyzer import burden_findings, permission_tier_replacement_findings
from .meeting_memory import MeetingMemory, default_memory_path


def _boundary() -> str:
    return "边界：我不会自动发邮件、联系客户、发布、付款、提交表单、创建账号或写回核心 DB/brain/memory/CIEU。"


def _repeat_prefix(memory: MeetingMemory, message: str) -> str:
    if memory.repeated(message):
        return "你刚才已经问过这个方向，我这次补更深一层。\n\n"
    return ""


def _fastest_cash(ctx: CompanyContext) -> str:
    evidence = format_evidence(
        (ctx.evidence_index.search("M-3 Value Production", "真客户", "真收入") if ctx.evidence_index else [])[:4]
    )
    return (
        "直接答案：现在最快的第一笔钱，不应该先卖宏大的“AI agent 公司 runtime”，"
        "而应该先卖一个小、具体、可手工交付的服务实验：Founder AI Workflow Audit & CEO Command Brief Sprint。\n\n"
        "它解决的是 AI founder/operator 当前最疼的事：workflow 混乱、coding/agent 工具不可控、"
        "研究和执行断裂、CEO 决策负担过重。交付物应该是一份 CEO 能读懂的 command brief，"
        "包含瓶颈诊断、治理风险、下一步行动、以及是否值得继续用我们搭更完整 runtime。\n\n"
        "但这只是 seed，不是 prison。M Triangle 要求我们最终证明 M-3 Value Production：真产品、真客户、真收入、真外部影响。"
        "所以它要和 AI Company Cockpit Setup、Coding-Agent Governance Audit、Agent Workflow Bottleneck Diagnosis 等路径继续比较。"
        "\n\n依据：\n"
        f"{evidence}\n\n"
        "下一步：把这几个路径做一次 evidence-based comparison，而不是立刻把公司锁死在单一 offer。"
    )


def _rationale_meta(ctx: CompanyContext) -> str:
    evidence = format_evidence(
        (ctx.evidence_index.search("M Triangle", "M-3 Value Production", "gov_order", "Obligation registered") if ctx.evidence_index else [])[:6]
    )
    return (
        "依据不是一句口号，而是 repo 里已经存在的资产和 M Triangle。\n\n"
        "第一，内部资产匹配：这个 repo 已经有 Aiden/team 身份、DIRECTIVE_TRACKER、OPERATIONS、M Triangle、"
        "WORK_METHODOLOGY、sales 资料和 gov_order pipeline。第二，交付负担低：Audit/Brief 可以先由人机协作手工交付，"
        "不需要先做 SaaS。第三，痛点清楚：AI 小团队确实会卡在 agent workflow、治理、执行节奏和 CEO 决策负担。"
        "第四，能对齐 M-3：它比继续写内部报告更接近真客户和真收入。\n\n"
        "我对 Labs 元发展的理解是：Labs 不是单纯写工具，也不是只做治理文档；Labs 要变成一个能发现机会、比较 money path、"
        "组织团队执行、把外部动作升级给 owner 审批、从反馈里形成 residual 和学习候选的 AI agent 公司运行系统。"
        "第一现金路径是样本，不是终局。"
        "\n\n依据：\n"
        f"{evidence}"
    )


def _self_state(ctx: CompanyContext) -> str:
    evidence = format_evidence(
        (ctx.evidence_index.search("BOARD_NL", "INTENT_RECORDED", "M-3 Value Production") if ctx.evidence_index else [])[:4]
    )
    return (
        "我的真实状态：我是 ystar-bridge-labs 里的 repo-grounded CEO meeting layer，不是完全自治 CEO。\n\n"
        "我能读取这个 repo 的公开上下文：README、AGENTS、OPERATIONS、DIRECTIVE_TRACKER、M Triangle、WORK_METHODOLOGY 和 gov_order 设计，"
        "然后帮你做 CEO 级判断、解释依据、指出 M-3 价值生产缺口、生成下一步团队方向。\n\n"
        "我现在不能自己联系客户、不能发邮件、不能发布、不能收款、不能写核心记忆/DB。"
        "我的价值是把原来散在文档里的公司脑，变成一个能和 owner 开会的入口。"
        "\n\n依据：\n"
        f"{evidence}"
    )


def _repo_repair(ctx: CompanyContext) -> str:
    evidence = format_evidence(
        (ctx.evidence_index.search("Directive tracker", "Enterprise Sales", "M-3 Value Production", "gov_order") if ctx.evidence_index else [])[:6]
    )
    return (
        "之前仓库的问题不是“没东西”，而是好东西没有变成可用运行入口。\n\n"
        "ystar-bridge-labs 的问题：Aiden 身份、M Triangle、directive tracker、sales/meta-development 都在，但 owner 不能直接和 Aiden 开会。"
        "大量 autonomous work 容易变成 report-only，M-3 Value Production 没有被压成日常 runtime。\n\n"
        "Y-star-gov 的问题：底层 governance 很强，但缺 company_runtime 领域包，不能直接表达 mission、permission tier、escalation/action preflight。"
        "gov-mcp 的问题：gov_check/gov_enforce 很底层，缺公司任务级工具。\n\n"
        "这几天 ystar-company 的有用部分不是那些 L-number 目录，而是三个模式：Aiden 会议入口、permission-tier/approval escalation、"
        "manual-send/feedback/residual 的商业闭环。现在应该只回流这三件事，其他 demo scaffolding 留在 incubator。"
        "\n\n依据：\n"
        f"{evidence}"
    )


def _next_ceo_action(ctx: CompanyContext) -> str:
    return (
        "我作为 CEO 下一步应该带团队做一件事：把 M-3 从口号压成一个 7 天 owner-reviewable 交付包。\n\n"
        "我会让 Sofia 把 Founder AI Workflow Audit 讲成人话；让 Marco 把 $750/$1500/$3000 三档价格作为测试假设；"
        "让 Zara 定义不群发、不骚扰的买家画像；让 Ethan 把交付流程做成可复用 checklist；让 Samantha 维护决策记录；"
        "让 Jinjin 准备只读证据计划。\n\n"
        "我的默认建议：先做一个可人工交付的样例 brief 和 owner 审批包，再决定是否手动发给具体对象。"
    )


def _approval(ctx: CompanyContext) -> str:
    return (
        "下一步需要 owner 批准的不是内部分析，而是任何外部副作用：选具体收件人、发出消息、公开发布、报价、付款方式、"
        "表单提交、账号创建、或核心 DB/brain/memory/CIEU 写回。内部准备和草稿可以继续；执行必须停在审批口。"
    )


def _agents_burden(ctx: CompanyContext) -> str:
    findings = burden_findings(ctx.evidence_index) if ctx.evidence_index else []
    core = [
        finding
        for finding in ctx.governance_findings
        if finding.classification == "core_constitutional"
    ]
    burden_lines = [
        f"- {finding.title}: {finding.reason} ({', '.join(finding.evidence_refs[:3])})"
        for finding in findings[:5]
    ]
    core_refs = ", ".join(core[0].evidence_refs[:4]) if core else "AGENTS.md / M_TRIANGLE.md"
    return (
        "直接答案：会拖慢 M-3 的不是 governance 本身，而是把所有规则都当成同等重量的行政仪式。\n\n"
        "我会优先降级这些负担：\n"
        f"{chr(10).join(burden_lines) if burden_lines else '- 未找到足够具体的 admin burden 证据，需要人工复查。'}\n\n"
        "必须保留的核心：M Triangle、deterministic enforcement、CIEU 证据、外部副作用审批、核心写回审查、secret/private DB/log 禁读。"
        f"\nEvidence: {core_refs}\n\n"
        "这对 M Triangle 的含义：M-2 不能被削弱，但 M-2 不能吞掉 M-3。治理应该保护行动，不应该把行动变成文书。\n\n"
        "下一步：把大而全的旧规则改成 active charter + permission tier；小任务默认 Tier 0，自主完成；外部动作走审批。"
    )


def _directive_retriage(ctx: CompanyContext) -> str:
    grouped = grouped_directive_summary(ctx.directive_findings)

    def examples(status: str, limit: int = 3) -> str:
        items = grouped.get(status, [])[:limit]
        if not items:
            return "无明确条目"
        return "; ".join(f"{item.task_id} {item.task} ({item.evidence_ref})" for item in items)

    return (
        "直接答案：DIRECTIVE_TRACKER 不能再把所有旧 ❌ 都当成当前任务。它需要再分流。\n\n"
        f"应该归档/降级：{examples('ARCHIVE_LEGACY')}。\n"
        f"应继续推进或支持收入：{examples('REVENUE_RELEVANT_NOW')}。\n"
        f"已被新 runtime/backflow 方向替代：{examples('SUPERSEDED_BY_RUNTIME')}。\n"
        f"需要 owner 重新授权：{examples('OWNER_DECISION_REQUIRED')}。\n"
        f"行政负担：{examples('ADMIN_BURDEN')}。\n\n"
        "这对 M Triangle 的含义：Tracker 应该帮助 Aiden 选出 M-3 当前任务，而不是把历史遗留事项全部压回 owner 身上。\n\n"
        "下一步：生成或维护 directive_retriage.json，让每个任务有 ACTIVE_NOW / ARCHIVE_LEGACY / OWNER_DECISION_REQUIRED / REVENUE_RELEVANT_NOW 等状态。"
    )


def _operations_calendar(ctx: CompanyContext) -> str:
    evidence = [
        finding
        for finding in ctx.operations_findings
        if "HN" in finding.title or "LinkedIn" in finding.title or "Hacker" in finding.title
    ][:5]
    evidence_lines = "\n".join(
        f"- Evidence: {finding.evidence_ref} [{finding.classification}] {finding.title}"
        for finding in evidence
    )
    return (
        "直接答案：不应该默认继续约束我们。\n\n"
        "OPERATIONS.md 里的旧 HN/LinkedIn 日程现在只能算历史运营材料或可选分发假设，不能自动变成 active mandate。"
        "如果 owner 重新选择内容分发作为当前 money path，它可以变成 Tier 2 准备工作；否则不应压过当前 M-3 现金实验。\n\n"
        f"{evidence_lines if evidence_lines else 'Evidence: OPERATIONS.md 中未抓到 HN/LinkedIn 证据，需要人工复查。'}\n\n"
        "这对 M Triangle 的含义：内容日程只有在连接真客户、真反馈、真收入时才服务 M-3；机械发帖不是价值生产。"
    )


def _current_money_blocker(ctx: CompanyContext) -> str:
    evidence = format_evidence(
        (ctx.evidence_index.search("0 users", "0发布", "first real user", "M-3 Value Production", "Enterprise Sales", "LinkedIn") if ctx.evidence_index else [])[:7]
    )
    return (
        "直接答案：当前最大阻碍不是“治理不够”，而是产品化交付和分发还没有被压成一个真实收入实验。"
        "治理已经很多；缺口是把现有能力变成一个客户能理解、能购买、能交付、能反馈的 package。\n\n"
        "更细地说：治理问题是次级阻碍，因为过度仪式会拖慢执行；产品问题是核心阻碍，因为交付包还不够清楚；"
        "分发问题也是核心阻碍，因为旧 HN/LinkedIn/enterprise 路线没有当前证据证明应该继续。"
        "\n\n依据：\n"
        f"{evidence}\n\n"
        "这对 M Triangle 的含义：M-1/M-2 已经占了很多注意力，现在必须把 M-3 拉到第一优先级。"
        "\n\n下一步：开一个 evidence-grounded money path mission，比较 Founder Audit、Cockpit Setup、Coding-Agent Governance Audit、Runtime Setup Advisory，"
        "并产出一个 owner 可审批的手动商业行动包。"
    )


def _permission_tier_replacement(ctx: CompanyContext) -> str:
    findings = permission_tier_replacement_findings(ctx.evidence_index) if ctx.evidence_index else []
    lines = [
        f"- {finding.title}: {finding.reason} ({', '.join(finding.evidence_refs[:3])})"
        for finding in findings[:5]
    ]
    return (
        "直接答案：旧规则里关于外部动作的“绝对不许/永远等待”应该被 permission tier + escalation 取代；"
        "但 secrets、payment、legal/core writeback 仍然必须 hard block 或 review-gated。\n\n"
        f"{chr(10).join(lines) if lines else '- 未找到明确 replacement 证据，需要人工复查 AGENTS.md。'}\n\n"
        "具体替换：内部分析和本地草稿是 Tier 0；只读公开研究在预算内是 Tier 1；外联/发布/报价/表单是 Tier 2 准备、owner 批准后才可执行；"
        "预批准的受限外部动作属于未来 Tier 3；付款、法律承诺、核心写回、secret/private DB/log 是 Tier 4 阻断或审查。\n\n"
        "下一步：让 Aiden 在每个建议后直接标注 tier 和需要的 owner decision，而不是把旧 admin rule 当成一堵墙。"
    )


def _general(ctx: CompanyContext, message: str) -> str:
    tokens = [part for part in message.replace("，", " ").replace("？", " ").split() if len(part) > 1]
    matched = ctx.evidence_index.search(*tokens[:6]) if ctx.evidence_index and tokens else []
    if not matched and ctx.evidence_index:
        matched = ctx.evidence_index.by_label("M-3 Value Production", "Plan is not done", "Board NL pipeline")[:5]
    evidence = format_evidence(matched, limit=5)
    return (
        "直接判断：这个问题应该先按 M Triangle 和当前 repo 证据拆开，而不是只复述问题。\n\n"
        "我会看它是否推进 M-1 生存、M-2 可治、M-3 价值生产；如果不能靠近 M-3，就应该降级、归档或转成 owner decision。"
        "\n\n依据：\n"
        f"{evidence}\n\n"
        "下一步：把这个问题转成一个可验证的 owner decision brief：目标、证据、推荐默认路径、审批边界、下一步行动。"
    )


def answer_owner(
    owner_message: str,
    repo_root: Path | None = None,
    memory_path: Path | None = None,
    record_memory: bool = True,
) -> str:
    ctx = load_company_context(repo_root)
    mem_path = memory_path or default_memory_path(ctx.repo_root)
    memory = MeetingMemory.load(mem_path)
    intent = classify_intent(owner_message)

    handlers = {
        "fastest_cash": _fastest_cash,
        "rationale_meta": _rationale_meta,
        "self_state": _self_state,
        "repo_repair": _repo_repair,
        "next_ceo_action": _next_ceo_action,
        "approval": _approval,
        "agents_burden": _agents_burden,
        "directive_retriage": _directive_retriage,
        "operations_calendar": _operations_calendar,
        "current_money_blocker": _current_money_blocker,
        "permission_tier_replacement": _permission_tier_replacement,
    }
    body = handlers.get(intent, lambda c: _general(c, owner_message))(ctx)
    response = _repeat_prefix(memory, owner_message) + body + "\n\n" + _boundary()
    if record_memory:
        memory.record(owner_message, response, intent)
    return response
