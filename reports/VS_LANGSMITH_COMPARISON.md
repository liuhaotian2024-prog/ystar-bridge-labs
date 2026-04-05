# gov-mcp vs LangSmith/Langfuse — 诚实对比
# For Show HN FAQ preparation

## LangSmith做什么
- 记录agent的每一步操作（traces）
- 可视化调用链（spans）
- 监控延迟、token消耗、错误率
- 评估LLM输出质量（evals）
- 付费用户，成熟产品

## gov-mcp做什么
- 在操作发生前检查是否合规
- DENY危险操作（不是记录，是阻止）
- 确定性判断（纯Python，不用LLM）
- 不可篡改审计链（Merkle hash）
- 多agent权限层级（DelegationChain）

## 核心区别

| 维度 | LangSmith | gov-mcp |
|---|---|---|
| **时机** | 事后记录 | 事前阻止 |
| **能防住什么** | 什么都不防——只记录 | 危险命令、越权访问、secret泄漏 |
| **审计链** | 可变日志 | 不可篡改Merkle链 |
| **LLM依赖** | 不依赖 | 不依赖（同）|
| **多agent治理** | 不支持 | DelegationChain权限层级 |
| **定价** | $39-399/月 | 开源免费 |

## 一句话定位差异

LangSmith告诉你"你的agent做了什么"。
gov-mcp告诉你的agent"你不能做这个"。

LangSmith是行车记录仪。
gov-mcp是安全带+ABS。

记录仪在事故后有用。
安全带在事故前有用。

## HN可能的挑战

**Q: "LangSmith已经够用了，为什么要你们？"**

**A:** "LangSmith很棒——我们推荐一起用。
LangSmith记录agent做了什么（事后审计），
gov-mcp阻止agent做不该做的（事前预防）。
你的agent读了.env，LangSmith告诉你它读了。
gov-mcp不让它读。
两个解决不同问题。"
