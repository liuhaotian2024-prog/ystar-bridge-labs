# CEO Theory: DIRECTIVE_TRACKER维护
# Priority 2 理论库 · 2026-04-11 · CEO自主学习

---

## 核心原则

### 1. 10分钟规则
Board指令下达后，CEO必须在10分钟内分解到DIRECTIVE_TRACKER.md。
这不是建议，是CASE-004的教训——CEO说"完成了"但12个子任务丢失。

### 2. TRACKER是单一事实来源
- 所有Board指令在这里汇总
- 所有子任务状态在这里追踪
- CEO每次向Board汇报前先刷新TRACKER

### 3. 与gov_dispatch的关系
TRACKER记录"要做什么"，gov_dispatch记录"派给了谁"。
两者必须一致——TRACKER有的任务必须有对应的dispatch记录。

### 4. 状态管理
| 状态 | 含义 |
|------|------|
| Active | 有未完成子任务 |
| Completed | 全部子任务完成，Board已确认 |
| Blocked | 等待外部依赖或Board决策 |
| Cancelled | Board明确取消 |

### 5. 今天的教训
今天session的TRACKER更新严重滞后——大量Board指令直接执行没有先记录到TRACKER。这导致：
- 无法追踪哪些指令完成了哪些没完成
- session结束时无法生成完整的完成报告
- 下个session的CEO不知道还有什么没做

---

*TRACKER是CEO的记忆，不更新TRACKER = CEO失忆。*
