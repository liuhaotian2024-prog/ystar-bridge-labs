---
name: 工程任务必须经 CTO 分派
description: 跨工程师的工作必须先派 Ethan-CTO，由 CTO 分派给 Leo/Maya/Ryan/Jordan，不能 CEO 直派工程师
type: feedback
originSessionId: b8aed99a-55f2-4073-a223-d41630cec4f4
---
跨工程师的工作必须先派 Ethan-CTO，由 CTO 分派给 Leo/Maya/Ryan/Jordan。CEO 不能跳过 CTO 直接派工程师。

**Why:** 2026-04-13 老大在 AMENDMENT-016 镜像对齐方案审批后明确指出：CEO 应该派 Ethan lead，再由 Ethan 派 Maya 做实验，而不是 CEO 直接派 Maya。这是 .ystar_session.json 里 `must_dispatch_via_cto` 规则的精神（虽然该规则当前 NOT ENFORCING）。CEO 直派工程师 = 越过 CTO 工程指挥权 = 组织架构跑偏。`must_dispatch_via_cto` 当前未代码 enforce，但 CEO 必须自律走流程。

**How to apply:**
- 单工程师 + 简单收尾 commit（如让 Maya 自己 commit 自己写完的代码）：可以 CEO 直派
- 跨工程师 / 新功能 / 架构改动 / 实验设计：必须先派 Ethan-CTO，由 Ethan 起方案 + 分派
- 判断标准：如果任务需要"决定派给哪个工程师"或"几个工程师协作"，就走 CTO
- 例 ✅：CEO → Ethan → "起 6-pager + 派 Maya 做实验" → Ethan → Maya
- 例 ❌：CEO → Maya（绕过 Ethan，CEO 替 Ethan 做了工程分派决策）
