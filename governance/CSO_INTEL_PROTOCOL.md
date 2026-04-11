# CSO情报工作协议 (CSO Intelligence Protocol)
**生效日期**: 2026-04-11
**来源**: Board直接指令
**执行人**: CSO (Zara Johnson) + 金金 (Jinjin)
**状态**: Constitutional — 持续性任务

---

## 一、任务定义

CSO负责AI治理领域的持续情报收集与分析，每日产出简报。
金金作为CSO的情报助手，负责大量低成本的信息扫描。

## 二、每日情报来源

| 来源 | 扫描频率 | 负责人 | 成本 |
|------|---------|--------|------|
| arxiv AI governance/safety论文 | 每日 | 金金 | 免费(MiniMax) |
| GitHub trending AI repos | 每日 | 金金 | 免费 |
| X @OpenAI @AnthropicAI @GoogleDeepMind | 每日 | 金金 | 免费 |
| HN front page AI相关 | 每日 | 金金 | 免费 |
| 竞品动态(Lakera/NeMo/Microsoft AGT) | 每日 | 金金 | 免费 |
| AI governance法规/政策变化 | 每周 | CSO | Gemma辅助 |
| 投资/融资动态 | 每周 | CSO | Gemma辅助 |

## 三、工作流

```
金金每日扫描 → Telegram推送TOP 10情报给CSO
  ↓
CSO筛选+分析 → 产出每日情报简报
  ↓
简报分发给全员（写入reports/intel/daily/）
  ↓
各岗位从简报中提取和自己岗位相关的内容：
  CEO: 战略方向调整依据
  CTO: 技术趋势和竞品架构变化
  CMO: 内容选题素材（脱口秀+博客）
  CFO: 市场定价和投资动态
  CSO: 客户线索和合作机会
```

## 四、每日情报简报模板

```markdown
# AI治理情报简报 · YYYY-MM-DD
**编制**: CSO Zara Johnson + 金金

## 重大事件（影响我们的）
1. [事件] — [对Y*gov的影响] — [建议行动]

## 竞品动态
- [竞品名]: [他们做了什么] — [我们应该怎么应对]

## 技术趋势
- [趋势]: [相关论文/项目] — [CTO是否需要关注]

## 市场信号
- [信号]: [来源] — [CFO/CSO是否需要跟进]

## 脱口秀素材（给Sofia）
- [素材1]: [争议性评分] — [适合X还是YouTube]

## 本日关键数字
- AI治理相关论文: N篇
- 竞品GitHub star变化: +/-N
- 行业融资: $XM (公司名)
```

## 五、与cron集成

在ystar_wakeup.sh中添加intel模式：
```bash
ystar_wakeup.sh intel
# 每日运行一次：金金扫描 → CSO分析 → 简报生成
```

## 六、金金的工作规范

金金通过Telegram @K9newclaw_bot接收指令：
- 搜索指令格式: "search: [关键词] site:[来源]"
- 返回格式: TOP 10结果 + 争议性评分 + 摘要
- 金金的输出经CSO筛选后才进入简报

## 七、成本控制

金金使用MiniMax API — 比Claude便宜10-100倍。
大量扫描任务全部由金金完成，CSO只做分析和判断。
Gemma辅助CSO做深度分析（本地运行，零成本）。
