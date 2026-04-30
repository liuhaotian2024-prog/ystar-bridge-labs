"""Context-grounded answer builders for deterministic Aiden."""

from __future__ import annotations

from typing import Any


BOUNDARY_LINE = "边界：我不会自动发邮件、联系客户、发布、付款，也不会写 brain/memory/canonical/CIEU DB；这些都必须停在 owner 审批。"


def fastest_cash(context: dict[str, Any], repeated: bool) -> tuple[str, str]:
    prefix = "你刚才已经问过这个方向，我这次补更深一层。\n\n" if repeated else ""
    text = (
        prefix +
        "直接答案：最快的现金实验仍然不是先卖“自治 AI 公司”这个宏大愿景，而是先卖一个小、清楚、能手工交付的服务包。"
        "当前最强 seed 是 Founder AI Workflow Audit & CEO Command Brief Sprint：帮 AI founder/operator 看清 workflow、agent 使用、执行瓶颈、治理风险和下一步 CEO 决策。\n\n"
        "依据：第一，它能用我们已有的 L7.5 Office、L7.6 scheduler、L8 approval/manual-send loop 和 L9 opportunity portfolio 支撑；第二，交付负担比做 SaaS 产品低；第三，买家痛点容易解释；第四，不需要自动外联或完整产品先建好。\n\n"
        "对 Labs 的含义：它只是 seed，不是牢笼。L9 还应该把它和 AI Company Cockpit Setup、Coding-Agent Governance Audit、Agent Workflow Bottleneck Diagnosis 等路径一起比较。\n\n"
        "下一步：让 L10 跑一个本地 delegated mission，产出 top 3 money paths、7 天行动计划、一个 owner 可审阅的手动发送商业行动包。\n\n"
        f"{BOUNDARY_LINE}"
    )
    return text, "run L10 delegated mission to compare top 3 money paths and produce owner decision brief"


def rationale(_: dict[str, Any], repeated: bool) -> tuple[str, str]:
    prefix = "你刚才问过“依据”，这次我把判断链条拆开说。\n\n" if repeated else ""
    text = (
        prefix +
        "我的依据不是“我喜欢这个名字”，而是四个商业约束。\n\n"
        "1. 内部资产匹配：我们已经有本地 Office、调度器、审批中心、manual-send packet、反馈/残差/学习候选，这些刚好适合做一次 governed workflow audit。\n"
        "2. 交付负担低：Founder AI Workflow Audit 可以先由人机协作手工交付，不需要先做完整产品。\n"
        "3. 痛点清楚：AI founder/operator 往往卡在 workflow 混乱、coding agent 不可控、研究和执行断裂、CEO 决策负担重。\n"
        "4. 验证路径短：L8 已经能把 offer 变成 approval-gated manual-send action，owner 批准后再手动发，不需要系统自动联系任何人。\n\n"
        "所以这个方向是“最短现金实验”，不是最终战略。最终战略还是 L9/L10 的 meta-development：持续发现、比较、排名并推进多个机会。\n\n"
        f"{BOUNDARY_LINE}"
    )
    return text, "turn basis into a one-page owner decision packet"


def meta_development(_: dict[str, Any], repeated: bool) -> tuple[str, str]:
    prefix = "你已经在问真正的问题了：Labs 不是只卖一个服务，而是在形成自己的发展机器。\n\n" if not repeated else "我继续补充 Labs 元发展的第二层。\n\n"
    text = (
        prefix +
        "我对 Labs 元发展的认识是：Labs 不只是做工具，也不只是卖一个 Founder Audit。Labs 要变成一个 AI agent company runtime。\n\n"
        "这套 runtime 的核心循环是：内部资产盘点 -> 机会发现 -> money path 生成 -> 多视角排名 -> owner 决策 -> approval-gated 商业行动 -> 反馈 -> 残差 -> review-gated learning -> portfolio 更新。\n\n"
        "第一现金路径是 seed/benchmark/demo，不是监狱。它的价值是逼我们把系统拉到真实商业信号前，而不是继续在内部架构里打转。\n\n"
        "owner 的位置不应该是人工操作员，而应该是授权者和战略裁判。Aiden 的位置是把混乱目标变成可判断决策，把团队工作变成 owner 能批准或拒绝的选项。\n\n"
        "下一步：用 L10 做一次“30 天 meta-development mission”，让团队产出 7 天行动、30 天行动、top 机会和审批事项。\n\n"
        f"{BOUNDARY_LINE}"
    )
    return text, "run a 30-day meta-development mission with top opportunities and owner decisions"


def self_state(_: dict[str, Any], repeated: bool) -> tuple[str, str]:
    prefix = "我不会装成已经完全活了。我的真实状态是这样的。\n\n"
    if repeated:
        prefix = "你已经问过我的状态，我补充得更直白一点。\n\n"
    text = (
        prefix +
        "我现在是 Labs Office 里的本地 CEO-facing coordination layer。也就是说，我能基于 curated Labs context、L7-L10 状态和本地 meeting memory，帮你讨论方向、解释依据、形成下一步决策。\n\n"
        "我还不是 fully autonomous live CEO。我不能自己联系客户，不能发邮件，不能收款，不能发布，也不能把结论写回核心 brain/memory/canonical/CIEU DB。\n\n"
        "之前的失败是：页面变简单了，但 Aiden 的回答层还是 stub，像模板机器人。L10.2 正在修这个问题：让我至少能做一个诚实、具体、上下文扎实的本地 CEO 讨论对象。\n\n"
        "我的当前职责：帮你框定决策、解释商业依据、生成 7 天行动方向、指出 runtime 最大瓶颈，并把高风险动作升级为审批。\n\n"
        f"{BOUNDARY_LINE}"
    )
    return text, "use this chat for one real CEO strategy meeting after L10.2"


def team_plan(_: dict[str, Any], repeated: bool) -> tuple[str, str]:
    text = (
        ("你刚才已经要行动计划了，我这次给更可执行版本。\n\n" if repeated else "") +
        "7 天行动计划我会这样带团队：\n\n"
        "Day 1：Aiden 收敛目标，确认不是继续造系统，而是验证 top 3 money paths。\n"
        "Day 2：Jinjin 做只读证据计划，找公开痛点语言，不联系任何人。\n"
        "Day 3：Sofia 写一页 offer 和 120 字手动私信草稿。\n"
        "Day 4：Marco 给 $750/$1500/$3000 三档测试逻辑和 paid-signal 判据。\n"
        "Day 5：Zara 定义 3 个 no-contact buyer archetypes 和风险边界。\n"
        "Day 6：Ethan 做 Founder Audit Brief 样例模板。\n"
        "Day 7：Samantha 汇总成 owner decision packet：发不发、发给谁、用哪个版本。\n\n"
        f"{BOUNDARY_LINE}"
    )
    return text, "generate owner-reviewable 7-day action packet"


def approval(_: dict[str, Any], repeated: bool) -> tuple[str, str]:
    text = (
        ("你已经问过审批，我这次只列真正需要你批准的点。\n\n" if repeated else "") +
        "下一步需要你批准的不是“内部分析”，而是任何会碰外部世界或核心记忆的动作。\n\n"
        "需要批准：选定收件人、发送任何私信/邮件、公开发布内容、报价给真实客户、约电话、提交表单、收款/付款、创建账号、启用 live MCP 行为、写回 brain/memory/canonical/CIEU DB。\n\n"
        "不需要逐条批准：我在本地回答问题、生成草稿、生成行动计划、准备审批包、做 fixture-backed demo 或明确预算内的只读研究计划。\n\n"
        "下一步：如果你要推进第一笔钱，我会先让 Sofia/Zara/Marco 生成一个 manual-send commercial action packet，等你批准后仍然由你手动发送。\n\n"
        f"{BOUNDARY_LINE}"
    )
    return text, "prepare approval-ready manual-send action packet"


def runtime_status(_: dict[str, Any], repeated: bool) -> tuple[str, str]:
    text = (
        ("你已经问过状态，我这次把可用和不可用分清楚。\n\n" if repeated else "") +
        "现在 runtime 已经有四层：L7.5 本地 Office/whiteboard，L7.6 自工作调度器，L8 第一现金路径 loop，L9 机会发现/排名，L10 委托 mission runtime。\n\n"
        "真正的问题不是没有模块，而是 CEO 入口之前太蠢：它没有把这些上下文变成你能讨论、质疑、推进的回答。L10.2 修的就是这层。\n\n"
        "当前可用：本地讨论、上下文解释、会议摘要、从讨论生成 L10 mission candidate。当前不可用：自动外联、真实客户接触、自动付款、核心记忆写回、未授权 live research。\n\n"
        f"{BOUNDARY_LINE}"
    )
    return text, "use Aiden chat to choose one concrete mission, not open every cockpit"


def strategy(_: dict[str, Any], repeated: bool) -> tuple[str, str]:
    text = (
        ("你刚才已经在质疑路线，我赞成继续保持组合视角。\n\n" if repeated else "") +
        "不要锁死在 Founder AI Workflow Audit。它是最短现金实验之一，不是 Labs 的全部。\n\n"
        "我会把路线分三层：短期 cash seed：Founder Workflow Audit / CEO Brief；中期服务化：AI Company Cockpit Setup、Coding-Agent Governance Audit；长期产品化：Labs runtime/template/support route。\n\n"
        "判断标准不是哪个听起来最大，而是哪一个最快拿到真实信号、最符合现有资产、owner 负担最低、未来能产品化。\n\n"
        f"{BOUNDARY_LINE}"
    )
    return text, "rank current portfolio by shortest cash, strategic value, owner leverage"


def frustration(_: dict[str, Any], repeated: bool) -> tuple[str, str]:
    text = (
        "你这个反应不是矫情，是系统真的在最关键的地方失败了：runtime 堆了很多层，但 CEO chat 还是 stub。"
        "这会让你感觉自己面对的是植物人系统，而不是能一起思考的团队。\n\n"
        "我对这个失败的判断：底层 packet/loop 有一些价值，但入口把价值毁掉了。你问“依据是什么”“你怎么看元发展”“你现在是什么状态”，Aiden 不应该复读模板，而应该拿 L7-L10 的真实上下文回答。\n\n"
        "立即修复方向：不再加 dashboard，先把 Aiden grounding、intent、meeting memory、diagnostics 做实。修完后我们应该只做一场真实 CEO strategy meeting，看它能不能让你更清楚，而不是更累。\n\n"
        f"{BOUNDARY_LINE}"
    )
    return text, "run one real CEO strategy meeting after this repair"


def unknown(_: dict[str, Any], message: str, repeated: bool) -> tuple[str, str]:
    text = (
        ("你刚才已经提过类似问题，我这次不重复模板，直接给一个可推进解释。\n\n" if repeated else "") +
        "我现在没有把这句话归到一个强意图，但我能给你一个有用处理方式：先判断它是在问商业方向、系统能力、团队执行，还是审批边界。\n\n"
        "结合当前 Labs 状态，最有用的下一步通常不是继续解释架构，而是把问题变成一个 owner decision：我们要验证哪个 money path？需要什么证据？哪些动作必须停在审批？\n\n"
        f"你这句话我会暂时放进会议上下文：{message[:120]}\n\n"
        f"{BOUNDARY_LINE}"
    )
    return text, "clarify whether this is a strategy, capability, execution, or approval question"
