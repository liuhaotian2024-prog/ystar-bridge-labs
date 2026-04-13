# L2 派活 → Secretary Samantha + CEO Aiden：团队 + 治理关系整理

**派发**: CEO Aiden（自分配）+ Secretary Samantha Lin
**Level**: L2（影响内部规范，CEO自批）
**日期**: 2026-04-12
**Board原话**: "我们暂时第一步是先把我们的团队和我们团队跟治理层的关系全部整理清楚，要不然很容易越干越乱"

## 战略意义

这是**对外发布前的一切前置条件**。在团队 + 治理关系整理清楚之前：
- 不发 Show HN
- 不发白皮书
- 不公开定价
- 不接外部用户

## 必交付物

### 1. `governance/TEAM_TOPOLOGY.md`
- 完整 11 角色清单（CEO/CTO/CMO/CSO/CFO/Secretary + 4工程师 + 金金）
- 每个角色：姓名、岗位、职责边界、写权限路径、CIEU 责任域、汇报路径
- 横向协作矩阵（谁可以 delegate 给谁）
- 子agent ↔ MCP delegate ↔ hook write_paths 三套权限的统一视图

### 2. `governance/GOVERNANCE_OVERLAY_MAP.md`
- 每个角色 × 治理子系统的映射：
  - 谁触发哪些 CIEU 事件
  - 谁受哪些 hook 拦截
  - 谁可调用哪些 gov-mcp 工具（59个）
  - 谁的 obligation_agent_scope 是什么
- 决策三层（L0/L1/L2/L3）× 角色 × 触发场景的具体例子表
- Iron Rules（1/2/3）对每个角色的具体含义

### 3. `governance/AUDIT_PERSONA_VIEW.md`
- 用 Sofia 白皮书的 Persona 视角（Compliance Officer / Platform Engineer / Solo Developer）
- 把 Y* Bridge Labs 自己的治理结构作为"产品最佳示范"展示出来
- 每个 persona 看到的入口和价值不同

### 4. 修复发现的所有不一致（与 AMENDMENT-004 对齐）
- 9 份 agent 定义文件交叉引用一致性检查
- DISPATCH.md / BOARD_PENDING.md / OKR.md 状态拉齐
- 删除/标记过期文件

## 责任分配

| 交付物 | 主负责 | 副负责 |
|---|---|---|
| TEAM_TOPOLOGY.md | Secretary | CEO review |
| GOVERNANCE_OVERLAY_MAP.md | Secretary | Maya (gov 子系统) |
| AUDIT_PERSONA_VIEW.md | CMO Sofia | Secretary |
| 一致性修复 | Secretary | 全员配合 |

## 时序

1. AMENDMENT-004 先批先执行（路径正名）
2. 然后启动本任务（拓扑+overlay+persona）
3. 完成后才解锁 Sofia 的对外发布

## 完成定义
- [ ] 4 份文档全部入库
- [ ] CEO 评审通过
- [ ] Board L3 review（如果改动 governance/ 下任何宪法层文件）
- [ ] 才解锁后续 Phase 1 对外动作
