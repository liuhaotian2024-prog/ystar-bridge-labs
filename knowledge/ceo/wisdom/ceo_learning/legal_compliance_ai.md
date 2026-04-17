---
name: CEO Legal & Compliance — AI Regulation + IP + Open Source (学习笔记 Round 13)
type: ceo_learning
discovered: 2026-04-17
source: AI regulation 2025-2026 legal landscape
depth: medium
---

## CEO 必知 4 个法律领域

### 1. Y*gov 开源许可 (MIT License)
- MIT = 最宽松开源许可 → 任何人可用/改/商用 → 只需保留版权声明
- 风险: 如果 Y*gov 代码中含第三方 AGPL/GPL 代码 → 许可证冲突 → 法律风险
- **K9Audit 是 AGPL-3.0** — per CLAUDE.md "Respect license boundaries (Y*gov: MIT, K9Audit: AGPL-3.0)"
- CEO check: 确保 Y*gov 没有直接 copy K9Audit 代码 (只 extract patterns)

### 2. EU AI Act (2026-08-02 生效)
- 高风险 AI 需要: 风险评估 + 透明度 + 人类监督 + 技术文档
- Y*gov 定位: **我们不是高风险 AI — 我们是帮别人合规的工具** → 反而是市场机会
- 但: 如果客户用 Y*gov 治理高风险 AI → 我们的工具质量影响他们的合规 → 间接责任?
- **CEO 行动**: 让 eng-compliance (Elena Chen) 研究 EU AI Act 对治理工具的要求

### 3. 数据隐私 (GDPR)
- CIEU 审计日志含 agent 行为数据 → 如果客户用 Y*gov → 客户的 agent 数据存在我们的 CIEU 中?
- **架构决策**: CIEU 数据应只存客户本地 (不上传到我们) → per data isolation (CZL-149 原则延伸)
- GDPR 罚款: 最高 €20M 或年营收 4% → CEO 必须确保产品设计 privacy-by-default

### 4. 训练数据 IP
- California AB 2013: 必须公开披露训练数据来源
- 我们: 不训练模型 (用 Anthropic API) → 不直接适用 → 但需要在 docs 中说明
- 客户 concern: "Y*gov 的治理决策基于什么数据?" → 答: Claude model + CIEU 历史事件 + FG rules (全可审计)

## Y* Labs 法律 Todo

| 优先 | 行动 | 谁做 |
|---|---|---|
| P1 | 审计 Y*gov 依赖许可证 (确认无 GPL 污染) | CTO |
| P2 | eng-compliance 研究 EU AI Act 对治理工具影响 | Elena (trust=30) |
| P3 | Privacy-by-default 架构确认 (CIEU 本地存储) | CTO |
| P4 | Terms of Service + Privacy Policy 草稿 | 需律师 or Board |
