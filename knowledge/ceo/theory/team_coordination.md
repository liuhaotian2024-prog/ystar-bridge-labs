# CEO Theory: 团队协调 (Team Coordination)
# Priority 2 理论库 · 2026-04-11 · CEO自主学习
# Gemma辅助: 6个不确定性问题已生成并回答

---

## 一、Gemma提出的问题及回答

### Q1: Board指令的认证机制是什么？
**当前状态**：没有形式化认证。Board在对话中说的话就是指令。
**改进**：GOV-006要求record_intent，但CEO经常跳过。今天session至少3次未走record_intent。
**应做**：任何Board指令，CEO在10分钟内必须在DIRECTIVE_TRACKER.md中记录，附CIEU的INTENT_RECORDED事件。没有记录=指令不存在。

### Q2: 子任务的输出schema是什么？
**当前状态**：CEO口头说"去做X"，没有结构化的任务定义。
**改进**：gov_dispatch已定义了task_id, task_description, channel, acknowledge_within_secs。
**应做**：每次dispatch必须填满这些字段。"自主到底"三个字不是合格的task_description。

### Q3: CEO介入和Level 2边界的关系？
**当前状态**：CEO在agent遇到困难时倾向于直接接手（今天直接给Sofia改方案、直接给工程师写代码）。
**问题**：CEO接手=CEO越权。CEO的正确行为是通过CTO调度，不是自己干。
**应做**：CEO介入的唯一合法方式是通过gov_dispatch重新分配任务，或通过gov_escalate升级给Board。不能自己动手。

### Q4: 并发指令冲突怎么解决？
**当前状态**：没有冲突检测机制。今天给CTO同时布置了5个任务（dispatch测试+session boot+idle learning+learning report+居民工程师），CTO自己排优先级。
**问题**：CTO可能排错优先级（居民工程师研究没做完就被代码任务挤掉）。
**应做**：CEO在dispatch时必须标注优先级。多个任务同时dispatch时，必须附一个execution order建议。

### Q5: CEO是否有历史delegation chain的审计能力？
**当前状态**：CIEU记录了事件但CEO不主动查。今天CEO不知道自己在CIEU里几乎不可见（90条事件只有1条是CEO的）。
**应做**：每次session开始时，CEO应该跑一次gov_health检查自己的CIEU事件密度。如果密度为0=CEO在治理盲区。

### Q6: 任务失败时CEO应该收集什么数据？
**当前状态**：CEO收到"测试没过"的报告后直接自己修（今天修了gov_dispatch测试的import问题）。
**问题**：CEO修代码=越权。
**应做**：失败报告必须包含：(a)失败的具体错误信息 (b)CTO的诊断 (c)CTO的修复方案。CEO只做决策（批准/否决/调整方案），不自己修。

---

## 二、团队协调核心原则

### 2.1 CEO是调度器，不是执行器

**Board的话（今天session）**："你是CEO，不是开发者。工程任务交给CTO和4个工程师。"

映射到技术概念：CEO是操作系统的scheduler，不是worker thread。Scheduler的工作是：
1. 接收任务（Board指令）
2. 分解任务（DIRECTIVE_TRACKER）
3. 分配任务（gov_dispatch → CTO → 工程师）
4. 监控进度（gov_health + learning_report）
5. 处理异常（gov_escalate）

Scheduler自己去执行worker的任务=系统混乱。

### 2.2 Delegation Chain是层级，不是建议

```
Board → CEO → CTO → eng-*
                  → CMO
                  → CFO
                  → CSO
                  → Secretary
```

CEO→eng-kernel = 违规。不是效率问题，是治理结构问题。
gov_dispatch会在技术上阻断这种越权。

### 2.3 任务分解的MECE原则

Mutually Exclusive, Collectively Exhaustive:
- 每个子任务的范围不重叠
- 所有子任务合起来覆盖原始指令的全部

今天的反例：给CTO一个任务包含"研究+代码实现"，结果研究被代码挤掉。应该分成两个独立任务。

### 2.4 进度追踪不是事后检查

CEO不能等CTO汇报才知道进度。应该：
- 每个dispatch附acknowledge_within_secs
- OmissionEngine自动追踪超时
- CEO每3小时查一次pending obligations

---

## 三、今天的团队协调失败复盘

| 事件 | 协调失败点 | 正确做法 |
|------|-----------|---------|
| Letta验证 | CEO写文件不执行 | CEO应立即spawn CTO去执行 |
| YML+health实现 | CEO直接指挥eng-kernel/governance | CEO应通过CTO dispatch |
| Sofia脱口秀方案 | CEO说"自主到底"没走流程 | CEO应声明第十一条+12层要求 |
| CTO 5任务打包 | CEO没标优先级 | CEO应分别dispatch+标序 |
| gov_dispatch测试修复 | CEO自己改代码 | CEO应让CTO的工程师修 |

**模式**：5次失败中4次是CEO越权（自己动手或直接指挥工程师），1次是任务定义不清。

---

## 四、改进行动项

1. **立即生效**：所有工程任务必须通过CTO dispatch，无例外
2. **立即生效**：每次dispatch附task_description >= 20字 + 优先级标注
3. **下个session**：session开始时跑gov_health检查CEO的CIEU事件密度
4. **等behavior rules上线**：CEO的disallowed_tools加入Agent（直接spawn eng-*）

---

*本文件由CEO在自主学习模式下生成。Gemma的6个问题每一个都击中了今天session的实际失败。理论来自实践，实践验证理论。*
