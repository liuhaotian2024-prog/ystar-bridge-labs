# gov_dispatch 设计规范
**版本**: 0.1.0-draft  
**状态**: 待CTO审核  
**涉及仓库**: gov-mcp · Y-star-gov  
**创建**: 2026-04-10 Board直接撰写
**前置调研**: 基于对 gov-mcp/server.py、Y-star-gov/ystar/governance/omission_models.py、
ystar/adapters/hook.py、ystar/kernel/dimensions.py 及 .ystar_session.json 的完整阅读

---

## 一、问题陈述

当前 gov-mcp 的治理能力覆盖两个层面：
- **Commission层**（做了不该做的）：`gov_check` 拦截每个 tool call
- **Omission层**（没做该做的）：`OmissionEngine` 检测义务超时

**缺失的层面**：任务从一个 agent 流向另一个 agent 这个行为本身，既不被 check，也不被记录，也不触发任何 obligation。dispatch 决策对 CIEU 完全透明——不可审计，不可追溯，不可被 OmissionEngine 约束。

这不是 Labs 的配置问题，是 gov-mcp 的架构缺口。

---

## 二、设计原则

1. **渠道无关**：gov_dispatch 不关心任务通过什么渠道送达（Telegram、Agent tool、ssh、未来的其他方式）。渠道是 Labs 自己的实现，治理层只管 dispatch 决策本身。

2. **delegation chain 约束**：dispatcher 必须在 delegation chain 中对 target_agent 拥有合法的委托权限。无权委托 = DENY。

3. **CIEU 全程记录**：dispatch 事件写入 CIEU，与 `gov_check` 产生的事件在同一条 Merkle 链上，可被 `gov_verify` 验证。

4. **OmissionEngine 可检测**：dispatch 触发一个 `TASK_DISPATCHED` 义务，target_agent 必须在规定时间内产生 `ACKNOWLEDGEMENT_EVENT` 来履行它。超时 = violation。

5. **确定性**：所有判断不经过 LLM，纯 deterministic 逻辑，与 Iron Rule 1 一致。

---

## 三、需要修改的文件

### 3.1 Y-star-gov：新增事件类型

**文件**: `ystar/governance/omission_models.py`  
**位置**: `GEventType` 类末尾（现有 `GAP_FILLED = "gap_filled"` 之后）

```python
# gov_dispatch layer（v0.50）
TASK_DISPATCHED        = "task_dispatched"      # dispatcher 发出任务
TASK_ACKNOWLEDGED      = "task_acknowledged"    # target_agent 确认接收
TASK_REJECTED          = "task_rejected"        # target_agent 拒绝（须附 reason）
TASK_COMPLETED         = "task_completed"       # target_agent 完成并上报
DISPATCH_EXPIRED       = "dispatch_expired"     # 超时未被 acknowledge
```

### 3.2 gov-mcp：新增 gov_dispatch 工具
### 3.3 gov-mcp：新增 gov_acknowledge 工具
### 3.4 .ystar_session.json：激活 obligation scope

（完整实现代码见Board原始spec）

---

## 七、未解决的问题（需 CTO 判断）

1. ObligationRecord 构造器字段名对齐
2. GovernanceEvent 构造器签名确认
3. obligation_id 匹配逻辑确认
4. Labs agent ID 与 delegation_chain actor 字段一致性

---

**CTO Action Required**: 审核本spec，确认第七节的4个技术问题，提交实现PR。
