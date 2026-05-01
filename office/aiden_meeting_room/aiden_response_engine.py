from __future__ import annotations

from pathlib import Path

from .aiden_intent_classifier import classify_intent
from .company_context_loader import CompanyContext, load_company_context
from .meeting_memory import MeetingMemory, default_memory_path


def _boundary() -> str:
    return "边界：我不会自动发邮件、联系客户、发布、付款、提交表单、创建账号或写回核心 DB/brain/memory/CIEU。"


def _repeat_prefix(memory: MeetingMemory, message: str) -> str:
    if memory.repeated(message):
        return "你刚才已经问过这个方向，我这次补更深一层。\n\n"
    return ""


def _fastest_cash(ctx: CompanyContext) -> str:
    return (
        "直接答案：现在最快的第一笔钱，不应该先卖宏大的“AI agent 公司 runtime”，"
        "而应该先卖一个小、具体、可手工交付的服务实验：Founder AI Workflow Audit & CEO Command Brief Sprint。\n\n"
        "它解决的是 AI founder/operator 当前最疼的事：workflow 混乱、coding/agent 工具不可控、"
        "研究和执行断裂、CEO 决策负担过重。交付物应该是一份 CEO 能读懂的 command brief，"
        "包含瓶颈诊断、治理风险、下一步行动、以及是否值得继续用我们搭更完整 runtime。\n\n"
        "但这只是 seed，不是 prison。M Triangle 要求我们最终证明 M-3 Value Production：真产品、真客户、真收入、真外部影响。"
        "所以它要和 AI Company Cockpit Setup、Coding-Agent Governance Audit、Agent Workflow Bottleneck Diagnosis 等路径继续比较。"
    )


def _rationale_meta(ctx: CompanyContext) -> str:
    return (
        "依据不是一句口号，而是 repo 里已经存在的资产和 M Triangle。\n\n"
        "第一，内部资产匹配：这个 repo 已经有 Aiden/team 身份、DIRECTIVE_TRACKER、OPERATIONS、M Triangle、"
        "WORK_METHODOLOGY、sales 资料和 gov_order pipeline。第二，交付负担低：Audit/Brief 可以先由人机协作手工交付，"
        "不需要先做 SaaS。第三，痛点清楚：AI 小团队确实会卡在 agent workflow、治理、执行节奏和 CEO 决策负担。"
        "第四，能对齐 M-3：它比继续写内部报告更接近真客户和真收入。\n\n"
        "我对 Labs 元发展的理解是：Labs 不是单纯写工具，也不是只做治理文档；Labs 要变成一个能发现机会、比较 money path、"
        "组织团队执行、把外部动作升级给 owner 审批、从反馈里形成 residual 和学习候选的 AI agent 公司运行系统。"
        "第一现金路径是样本，不是终局。"
    )


def _self_state(ctx: CompanyContext) -> str:
    return (
        "我的真实状态：我是 ystar-bridge-labs 里的 repo-grounded CEO meeting layer，不是完全自治 CEO。\n\n"
        "我能读取这个 repo 的公开上下文：README、AGENTS、OPERATIONS、DIRECTIVE_TRACKER、M Triangle、WORK_METHODOLOGY 和 gov_order 设计，"
        "然后帮你做 CEO 级判断、解释依据、指出 M-3 价值生产缺口、生成下一步团队方向。\n\n"
        "我现在不能自己联系客户、不能发邮件、不能发布、不能收款、不能写核心记忆/DB。"
        "我的价值是把原来散在文档里的公司脑，变成一个能和 owner 开会的入口。"
    )


def _repo_repair(ctx: CompanyContext) -> str:
    return (
        "之前仓库的问题不是“没东西”，而是好东西没有变成可用运行入口。\n\n"
        "ystar-bridge-labs 的问题：Aiden 身份、M Triangle、directive tracker、sales/meta-development 都在，但 owner 不能直接和 Aiden 开会。"
        "大量 autonomous work 容易变成 report-only，M-3 Value Production 没有被压成日常 runtime。\n\n"
        "Y-star-gov 的问题：底层 governance 很强，但缺 company_runtime 领域包，不能直接表达 mission、permission tier、escalation/action preflight。"
        "gov-mcp 的问题：gov_check/gov_enforce 很底层，缺公司任务级工具。\n\n"
        "这几天 ystar-company 的有用部分不是那些 L-number 目录，而是三个模式：Aiden 会议入口、permission-tier/approval escalation、"
        "manual-send/feedback/residual 的商业闭环。现在应该只回流这三件事，其他 demo scaffolding 留在 incubator。"
    )


def _obsolete_rules(ctx: CompanyContext) -> str:
    return (
        "现在不应该再自动约束我们的旧规则，主要是那些只制造行政动作、但不推进 M Triangle 的规则。\n\n"
        "具体包括：固定每日/每周/夜间报告、旧 HN/LinkedIn 发布日历、旧 enterprise sales warm-intro 节奏、"
        "未重新验证的内容 pipeline、以及旧 directive 里因为没完成就一直挂着的任务。它们可以作为历史证据和素材库保留，"
        "但不能默认占用团队当前精力。\n\n"
        "真正保留的是 M Triangle、确定性 enforcement、CIEU 证据、外部副作用审批、核心写回 review gate、"
        "不读 secrets/private DB/log，以及团队身份边界。"
    )


def _active_rules(ctx: CompanyContext) -> str:
    return (
        "当前真正 active 的治理规则可以压成一句话：用 M Triangle 判断方向，用 permission tiers 判断行动风险，"
        "用 owner approval/escalation 卡住外部副作用和核心写回。\n\n"
        "Tier 0 内部分析和草稿可以自主做；Tier 1 只读研究必须有预算；Tier 2 可以准备但不能执行外部动作；"
        "Tier 3 未来只允许预批准且受限的外部动作；Tier 4 高风险动作必须 blocked 或 review-gated。\n\n"
        "行政报告不是默认 active。报告只有在帮助决策、证据、合规、mission summary 时才有价值。"
    )


def _legacy_burden(ctx: CompanyContext) -> str:
    return (
        "当前最明显的历史包袱有四类。\n\n"
        "第一，旧内容节奏：HN、LinkedIn、article series、podcast 等，不应作为自动 cadence。"
        "第二，旧销售路径：enterprise Phase 1 和 warm intro list 需要重新证据化，不能直接执行。"
        "第三，旧报告义务：daily/weekly/nightly report 如果不服务 mission，就是消耗。"
        "第四，旧 directive 未完成项：NotebookLM、专利、K9 长期数据、测试基线等需要 re-triage，而不是默认 active。\n\n"
        "我的建议：把它们保留为 archive/evidence inventory，只把能推进 M-3 的部分转成当前 mission。"
    )


def _reduce_owner_burden(ctx: CompanyContext) -> str:
    return (
        "我应该减少你的手工负担，不是让你少看信息，而是让你只处理真正需要 owner 授权的东西。\n\n"
        "我的工作方式应该变成：先理解目标，再把历史包袱过滤掉；我给出默认建议和理由；团队做 Tier 0/Tier 1 的安全工作；"
        "只有涉及客户联系、发布、付款、账号、表单、核心写回、战略授权时，才把一个清晰 escalation packet 放到你面前。\n\n"
        "你不应该帮团队维护日报、选旧任务、整理历史 backlog。你应该只批准方向、边界、外部动作和关键战略判断。"
    )


def _m_triangle_priority(ctx: CompanyContext) -> str:
    return (
        "现在最该优先推进的是 M-3 Value Production，同时不能削弱 M-1 和 M-2。\n\n"
        "原因很直接：M-1 生存性和 M-2 可治理性已经积累了很多资产；当前最大风险是系统继续在内部治理里自转，"
        "没有把能力转成真实客户、真实收入、真实外部信号。\n\n"
        "所以我会把旧行政规则降噪，把安全边界保留，然后推动 mission-based money-path work："
        "先生成可审阅商业行动包，再由你批准是否手动执行外部动作。"
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


def _general(ctx: CompanyContext, message: str) -> str:
    return (
        f"我理解你问的是：{message}\n\n"
        "我会先把它放回 M Triangle：它是否推进 M-1 生存、M-2 可治、M-3 价值生产？"
        "如果这件事不能靠近 M-3，我会倾向于砍掉或降级。当前最有用的下一步，是把问题转成一个可验证的 owner decision brief，"
        "而不是继续扩写文档。"
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
        "obsolete_rules": _obsolete_rules,
        "active_rules": _active_rules,
        "legacy_burden": _legacy_burden,
        "reduce_owner_burden": _reduce_owner_burden,
        "m_triangle_priority": _m_triangle_priority,
        "fastest_cash": _fastest_cash,
        "rationale_meta": _rationale_meta,
        "self_state": _self_state,
        "repo_repair": _repo_repair,
        "next_ceo_action": _next_ceo_action,
        "approval": _approval,
    }
    body = handlers.get(intent, lambda c: _general(c, owner_message))(ctx)
    response = _repeat_prefix(memory, owner_message) + body + "\n\n" + _boundary()
    if record_memory:
        memory.record(owner_message, response, intent)
    return response
