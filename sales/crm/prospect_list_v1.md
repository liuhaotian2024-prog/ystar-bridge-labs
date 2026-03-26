# Y*gov 潜在客户名单 v1
# CSO Agent | 创建日期：2026-03-26
# 状态：待董事会审核

---

## 评估标准

- **High**：已公开部署 AI agent 或有明确合规需求，预算充足
- **Medium**：有 AI 战略但尚未大规模部署，需要教育市场

---

## 1. JPMorgan Chase — 金融

**为什么需要 Y*gov：**
JPMorgan 已大规模部署 LLM 用于研究、代码生成和客户服务。SEC 和 OCC 对 AI 模型风险管理的监管日趋严格（SR 11-7, OCC 2024-10）。他们需要证明每个 AI agent 的操作都有完整审计链。

**决策者：** Chief Compliance Officer / Head of AI Governance
**接触方式：** LinkedIn 直接联系其 AI Center of Excellence 负责人；参加 JPMorgan 年度 AI 峰会
**优先级：** High

---

## 2. Goldman Sachs — 金融

**为什么需要 Y*gov：**
Goldman 的 GS AI 平台已在内部推广，交易和风控部门依赖 AI agent 做数据分析。FINRA 要求所有影响交易决策的自动化系统必须可审计。CIEU 审计链可以直接满足 FINRA Rule 3110 的监督要求。

**决策者：** CISO / Head of Technology Risk
**接触方式：** 通过 FinTech 合规会议（如 RegTech Summit）建立联系
**优先级：** High

---

## 3. Citadel Securities — 金融

**为什么需要 Y*gov：**
量化交易公司对 AI agent 的使用密度极高，且每笔交易操作都需要监管记录。多 agent 协作场景（研究 agent -> 信号 agent -> 执行 agent）天然需要委托链治理。

**决策者：** CTO / Head of Compliance Technology
**接触方式：** 技术社区（Citadel 工程团队活跃在开源社区）；直接 cold email
**优先级：** High

---

## 4. Pfizer — 制药

**为什么需要 Y*gov：**
FDA 21 CFR Part 11 要求所有电子记录必须有完整审计追踪。Pfizer 在药物发现和临床试验数据分析中使用 AI agent，每个 agent 的决策必须可追溯到具体的输入和推理过程。Y*gov 的 domain pack 可以直接映射 FDA 合规规则。

**决策者：** VP of IT / Computer System Validation Lead
**接触方式：** DIA（Drug Information Association）年会；通过 Pfizer Digital 团队的公开招聘信息定位具体负责人
**优先级：** High

---

## 5. Roche — 制药

**为什么需要 Y*gov：**
Roche 旗下 Genentech 在 AI 药物发现领域投资巨大。ICH E6(R3) 要求临床试验中使用的任何自动化工具都必须有验证和审计记录。多 agent 工作流（分子筛选 agent -> 毒性预测 agent -> 临床方案 agent）需要端到端治理。

**决策者：** Head of Digital Health / IT Validation Director
**接触方式：** Basel 地区 HealthTech 活动；LinkedIn 直接联系其 AI/ML Platform 团队
**优先级：** Medium

---

## 6. Stripe — FinTech

**为什么需要 Y*gov：**
Stripe 使用 AI agent 做欺诈检测、客户支持和代码审查。作为支付公司，PCI DSS 合规要求所有自动化操作留有审计记录。Stripe 的工程文化意味着他们更可能早期采纳开发者友好的治理工具。

**决策者：** CTO / VP of Engineering / Head of Security
**接触方式：** 开源社区直接推广（Stripe 工程团队高度活跃）；通过 Claude Code 集成作为切入点
**优先级：** High

---

## 7. Anthropic 内部 / Claude Code 生态 — AI 基础设施

**为什么需要 Y*gov：**
Claude Code 的重度用户（企业级）需要在多 agent 工作流中管理权限继承。当一个 Claude Code agent spawn 子 agent 时，谁来验证子 agent 的权限不超过父 agent？Y*gov 的 DelegationChain 正好解决这个问题。

**决策者：** 企业版 Claude Code 用户的 CTO / VP of AI
**接触方式：** Claude Code 社区（Discord、GitHub Discussions）；申请成为 Anthropic Partner Program 合作伙伴
**优先级：** High

---

## 8. Deloitte — 咨询/审计

**为什么需要 Y*gov：**
四大审计公司自身在大量使用 AI agent 做审计自动化，同时他们的客户也需要 AI 治理方案。Deloitte 可以同时是用户和渠道合作伙伴：自用 Y*gov 做内部 AI 治理，同时向客户推荐。

**决策者：** AI & Data Practice Lead / Chief Innovation Officer
**接触方式：** 通过 Deloitte 的 AI Institute 公开活动建立联系；以"审计 AI agent 的审计工具"为切入角度
**优先级：** Medium

---

## 9. Epic Systems — 医疗 IT

**为什么需要 Y*gov：**
Epic 是美国最大的电子病历（EHR）供应商，正在集成 AI 助手。HIPAA 和 FDA 对医疗 AI 的审计要求极其严格。当 AI agent 访问患者数据或辅助临床决策时，每一步都必须有不可篡改的记录。

**决策者：** VP of Engineering / Chief Medical Informatics Officer (客户端)
**接触方式：** HIMSS 全球健康大会；通过 Epic 的 App Orchard 生态系统申请合作
**优先级：** Medium

---

## 10. Replit / Cursor — 开发者工具

**为什么需要 Y*gov：**
AI 代码编辑器公司正在从单 agent 走向多 agent 架构（后台 agent 做代码审查、测试生成、部署）。他们的企业客户（银行、政府）会要求这些 agent 有治理和审计能力。Y*gov 可以作为基础设施层嵌入。

**决策者：** CTO / Head of Enterprise
**接触方式：** 开发者社区直接接触（Twitter/X, Hacker News）；通过技术博客展示 Y*gov 与 AI coding tool 的集成
**优先级：** Medium

---

## 下一步行动

1. 本列表提交董事会审核
2. 审核通过后，按 High 优先级客户开始准备定制化接触材料
3. 每个 High 优先级客户准备一份 1 页的价值主张文档
4. 跟踪所有接触记录在 sales/crm/ 目录下
