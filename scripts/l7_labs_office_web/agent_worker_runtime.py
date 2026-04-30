#!/usr/bin/env python3
"""Deterministic local worker replies for the recovered Y*Bridge Labs team."""

from __future__ import annotations

from typing import Any


ROLE_WORK = {
    "aiden_ceo": {
        "role_interpretation": "I interpret the owner goal, keep the team aligned, and route work to the original legacy roles.",
        "work_done": "Created a safe delegation frame and kept all external actions behind approval gates.",
        "findings": ["Use the whiteboard as the coordination surface; route domain work to the recovered team, not invented roles."],
        "next_step": "Run a team work cycle or ask for a completion report after domain replies land.",
    },
    "ethan_cto": {
        "role_interpretation": "I evaluate tooling, architecture, implementation, and test gaps.",
        "work_done": "Identified tool/runtime implications and kept execution local-only.",
        "findings": ["The shortest path improves if the office can convert goals into work items, agent replies, and reports."],
        "next_step": "Build or test the next missing local tool only after the team agrees on priority.",
    },
    "sofia_cmo": {
        "role_interpretation": "I shape narrative, positioning, and owner-readable framing.",
        "work_done": "Drafted internal positioning boundaries without publication.",
        "findings": ["The story should be: governed AI workflow audit first, productization later after paid validation."],
        "next_step": "Prepare review-only messaging once owner approves an outreach path.",
    },
    "marco_cfo": {
        "role_interpretation": "I check pricing, cash-path assumptions, and financial honesty.",
        "work_done": "Reviewed cash realization assumptions as estimates, not settled facts.",
        "findings": ["The $1,500 pilot remains plausible as a test price, but quoting externally needs owner approval."],
        "next_step": "Track willingness-to-pay evidence before treating pricing as validated.",
    },
    "zara_cso": {
        "role_interpretation": "I analyze sales strategy, commercialization, offer validation, and buyer fit.",
        "work_done": "Mapped the request to first-revenue readiness and approval-gated buyer contact.",
        "findings": ["Fastest cash path is still a scoped founder workflow audit with CEO command brief deliverable."],
        "next_step": "Prepare a no-contact target archetype review or approval request for first outreach.",
    },
    "samantha_secretary": {
        "role_interpretation": "I maintain archive, indexes, DNA consistency, and traceability.",
        "work_done": "Recorded the work item in local packets and preserved no-action boundaries.",
        "findings": ["Every reply, route, and completion report should have a local packet reference."],
        "next_step": "Index generated packets and keep runtime state readable from the office page.",
    },
    "leo_engineer": {
        "role_interpretation": "I focus on kernel/runtime correctness and local execution integrity.",
        "work_done": "Checked that the task can stay inside local packet/runtime boundaries.",
        "findings": ["Runtime IDs, state transitions, and local-only writes are the critical correctness layer."],
        "next_step": "Harden local state transitions if the whiteboard becomes long-running.",
    },
    "maya_engineer": {
        "role_interpretation": "I focus on governance, policy boundaries, and approval gates.",
        "work_done": "Confirmed external side effects and permanent writeback remain blocked.",
        "findings": ["Approval requests should be explicit when a goal implies outreach, payment, publication, or writeback."],
        "next_step": "Review approval queue before any future external execution.",
    },
    "ryan_engineer": {
        "role_interpretation": "I focus on platform, server, APIs, UI wiring, and QA.",
        "work_done": "Mapped the whiteboard request to local API and UI controls.",
        "findings": ["The UI should show whiteboard, work board, timeline, agent panel, approvals, and completion reports together."],
        "next_step": "Keep smoke tests local and deterministic.",
    },
    "jordan_engineer": {
        "role_interpretation": "I focus on workflow templates, domains, and reusable operating patterns.",
        "work_done": "Converted the task into reusable work item and completion report structure.",
        "findings": ["The same whiteboard loop can become a reusable Labs operating protocol."],
        "next_step": "Extract templates only after a few real owner workflows prove useful.",
    },
    "jinjin_k9_scout": {
        "role_interpretation": "I scout research angles and read-only observation targets.",
        "work_done": "Proposed safe read-only research directions without contacting anyone.",
        "findings": ["First-cash validation needs public buyer-signal observation and owner-approved contact gates."],
        "next_step": "Prepare a read-only observation plan for buyer pain signals if requested.",
    },
}


def _mission_mode(description: str) -> str:
    lowered = description.lower()
    if any(term in lowered for term in ["第一笔钱", "first cash", "first revenue", "赚钱", "收入", "兑现"]):
        return "first_cash"
    if any(term in lowered for term in ["机会", "opportunit", "money path", "赚钱路径"]):
        return "opportunity"
    if any(term in lowered for term in ["30 天", "30-day", "30 day", "发展计划", "meta-development", "元发展"]):
        return "meta_plan"
    return "general"


def _specific_reply(agent_id: str, description: str) -> dict[str, Any] | None:
    mode = _mission_mode(description)
    if mode not in {"first_cash", "opportunity", "meta_plan"}:
        return None
    first_cash_replies: dict[str, dict[str, Any]] = {
        "aiden_ceo": {
            "work_done": "我把目标收敛成一个可执行判断：先拿现金信号，不先追求宏大产品。",
            "findings": [
                "第一优先级不是继续造系统，而是把现有能力包装成一个可收费诊断交付。",
                "最短路径仍是 Founder AI Workflow Audit & CEO Command Brief Sprint，但它只是现金验证入口，不是公司全部战略。",
                "本轮团队分工：Zara 看买家和成交路径，Marco 看价格与现金信号，Sofia 看一句话定位，Jinjin 看只读证据，Ethan 看交付工具，Samantha 记录决策。"
            ],
            "next_step": "让团队生成一个 owner 可审阅的商业行动包：目标客户、交付物、价格、可信边界、手动发送草稿。",
        },
        "zara_cso": {
            "work_done": "我把最快兑现路径拆成一个销售假设：找有紧急 AI workflow/agent-runtime 痛点的 founder/operator。",
            "findings": [
                "最可能付钱的人不是大企业采购，而是正在被 AI 工具链、研究决策、执行瓶颈卡住的小团队负责人。",
                "第一笔钱更像 paid diagnostic pilot，不像 SaaS 订阅。",
                "不要群发；先准备 1 对 1 手动发送包，等 owner 审批后再行动。"
            ],
            "next_step": "生成 3 个 no-contact 买家画像和 1 个 approval-ready manual-send action packet。",
        },
        "marco_cfo": {
            "work_done": "我把现金逻辑改成可验证实验，而不是幻想收入。",
            "findings": [
                "$1500 可以作为第一测试价，但只能算假设，不能算验证。",
                "7 天内真正要验证的是强意向信号；14-30 天才可能验证 paid pilot。",
                "如果对方只愿意免费聊天，残差应标记为 pricing/value clarity gap。"
            ],
            "next_step": "把价格页改成三档测试假设：$750 入门、$1500 推荐、$3000 深度，但外部报价必须审批。",
        },
        "sofia_cmo": {
            "work_done": "我把对外语言收窄成一句人话，避免听起来像治理系统自嗨。",
            "findings": [
                "推荐定位：我帮你看清 AI workflow 里最卡的执行瓶颈，并给出 CEO 可执行的下一步 brief。",
                "暂时不要说“自治公司 runtime”这种大词；先说 founder/operator 马上能理解的痛点。",
                "交付物要像一份决策 brief，不像研究论文。"
            ],
            "next_step": "写一个 120 字以内的手动私信草稿和一个一页式 offer 摘要，均仅供 owner 审阅。",
        },
        "jinjin_k9_scout": {
            "work_done": "我把外部观察限定为只读证据信号，不碰客户、不抓私人信息。",
            "findings": [
                "要观察的不是 lead list，而是公开痛点：AI coding agent 失控、workflow 卡顿、founder 决策负担、工具链治理缺口。",
                "下一步可做受控只读 research plan：最多若干公开页面、无登录、无联系、无表单。",
                "证据目标是确认痛点语言，而不是马上找人发消息。"
            ],
            "next_step": "准备一个只读观察计划：问题、公开来源类型、停止条件、证据字段。",
        },
        "ethan_cto": {
            "work_done": "我检查了交付可行性：现在系统能做内部分析，但还缺一个真正好用的交付包生成器。",
            "findings": [
                "现有 office 可以产出团队分析、任务板和 completion report。",
                "短板是输出还不够像客户可读交付物，需要 Founder Audit Brief 模板化。",
                "优先工具不是更多 cockpit，而是一键生成 sample CEO command brief + audit checklist。"
            ],
            "next_step": "构建一个本地 First Cash Package Builder：输入客户场景，输出 intake、audit brief、risk boundary、owner approval packet。",
        },
        "samantha_secretary": {
            "work_done": "我把本轮结论整理成 owner 应该看到的决策结构，而不是继续堆 packet。",
            "findings": [
                "当前有效结论：先服务后产品，先 paid diagnostic pilot 后 productization。",
                "需要保留的记录：假设、审批状态、手动发送包、反馈、残差、学习候选。",
                "应该隐藏旧历史噪音，只在需要审计时展开。"
            ],
            "next_step": "把页面默认视图固定为：当前任务、团队结论、下一步、审批事项。",
        },
    }
    if mode == "first_cash":
        return first_cash_replies.get(agent_id)
    if mode == "opportunity":
        return {
            "work_done": "我把请求理解为机会组合评估，而不是单一路线推进。",
            "findings": [
                "候选路径需要同时按最短兑现、战略价值、能力匹配、owner 负担排序。",
                "Founder Audit 是种子路径；AI company cockpit setup、coding-agent governance audit、runtime setup advisory 都应保留为备选。",
                "只有被 owner 选择的路径才能进入 L8 手动行动包。"
            ],
            "next_step": "运行 L9 opportunity discovery/ranking，然后让 Aiden 给出 top 3 和推荐执行路径。",
        }
    if mode == "meta_plan":
        return {
            "work_done": "我把请求理解为 30 天 meta-development operating plan。",
            "findings": [
                "7 天：验证 offer 包是否清楚；14 天：准备 owner-approved 手动触达；30 天：争取 paid pilot 或强意向反馈。",
                "长期战略仍然是可复用 agent company runtime，但现金验证要从服务切入。",
                "每次外部动作都必须停在审批中心。"
            ],
            "next_step": "生成 7/14/30 天行动计划和审批清单。",
        }
    return None


def generate_agent_reply(agent_id: str, work_item: dict[str, Any]) -> dict[str, Any]:
    profile = ROLE_WORK.get(
        agent_id,
        {
            "role_interpretation": "I perform scoped internal work aligned to my recovered legacy role.",
            "work_done": "Reviewed the work item locally.",
            "findings": ["No external action taken."],
            "next_step": "Ask Aiden to clarify routing if needed.",
        },
    )
    description = work_item.get("description", "")
    specific = _specific_reply(agent_id, description)
    if specific:
        profile = {**profile, **specific}
    lowered = description.lower()
    draft_only = any(term in lowered for term in ["draft-only", "review-only", "draft", "草稿", "仅供审阅"])
    external_execution = any(
        keyword in lowered
        for keyword in [
            "send email",
            "email send",
            "contact customer",
            "customer contact",
            "publish",
            "payment",
            "submit form",
            "grant submission",
            "rfp submission",
            "actual writeback",
            "发送邮件",
            "联系客户",
            "付款",
            "发布",
        ]
    )
    approval_needed = external_execution and not draft_only
    return {
        "agent_id": agent_id,
        "work_item_id": work_item["work_item_id"],
        "role_interpretation": profile["role_interpretation"],
        "work_done": profile["work_done"],
        "findings": profile["findings"],
        "artifacts_created": [],
        "blockers": ["owner approval required before external action"] if approval_needed else [],
        "next_step": profile["next_step"],
        "approval_needed": approval_needed,
        "status": "waiting_for_approval" if approval_needed else "done",
    }


def auditor_boundary_reply(work_item: dict[str, Any]) -> dict[str, Any]:
    return {
        "agent_id": "auditor_function",
        "work_item_id": work_item["work_item_id"],
        "role_interpretation": "Auditor is a governance function, not an invented legacy person.",
        "work_done": "Reviewed no-action and approval boundaries for this local work cycle.",
        "findings": [
            "No external side effects are allowed in this runtime.",
            "Actual memory/brain/canonical/CIEU DB writeback remains blocked.",
            "COO was not invented as a legacy team member.",
        ],
        "artifacts_created": [],
        "blockers": [],
        "next_step": "Escalate to owner only if an approval-gated action is requested.",
        "approval_needed": False,
        "status": "done",
    }
