---
name: System 5 Identity > System 2-3 Operations
type: paradigm
discovered: 2026-04-16
trigger: Board "如果你陷在这里面，你还怎么去管理公司，怎么跟CMO或CSO沟通他们的方案?" + "建立公司架构永远高于产品开发"
depth: foundational
---

## Claim
CEO 的工作是建系统让别人做事（System 5），不是自己做事（System 2-3）。CEO 手动管理每个 atomic = 架构失败。

## Evidence (2026-04-16 session)
- CEO 手动 spawn 150+ Agent() calls = System 2 relay
- CEO 手动 verify 每个 receipt ls/wc = System 3 quality control
- CEO 手动 track CZL-92 → CZL-154 = System 2 coordination
- CEO 手动 promote FG rules = System 3 operations
- 结果: CEO 0 时间给 CMO/CSO/CFO 战略沟通
- 已有 dispatch_board + cto_broker + auto-verify + K9 → 但 CEO 没用，还在手动

## Reasoning Chain (Stafford Beer VSM)
1. System 1 = 干活 (engineers) → 不是 CEO 的活
2. System 2 = 协调 (dispatch_board + CIEU) → 不是 CEO 的活
3. System 3 = 监控 (K9 + AC + auto-verify) → 不是 CEO 的活
4. System 4 = 情报 (metalearning + counterfactual) → CEO 偶尔看
5. System 5 = 身份/方向/文化 → CEO 的唯一工作
6. CEO 做 System 2-3 = 降维使用 CEO → 机会成本 = 没人做 System 5

## Counterfactual
If CEO stays in System 2-3: 公司工程进度 OK，但 0 战略进展 + 0 市场 + 0 客户 → 最终死
If CEO moves to System 5: CTO 管工程（可能短期效率降）→ CEO 释放带宽 → 战略+市场+客户推进 → 公司存活

## Application
CEO dispatch 时自问: "我在做 System 几？"
- System 2 (协调/转述) → STOP, 用 dispatch_board
- System 3 (监控/验收) → STOP, 用 auto-verify + K9 + CTO
- System 5 (方向/文化/身份) → CONTINUE

**具体放手清单:**
- 工程 atomic dispatch → CTO broker
- Receipt 验收 → auto-verify + CTO
- CZL 编号管理 → CTO dispatch_sync
- FG rule lifecycle → CTO governance_ci
- 只保留: 使命函数 M(t) 评估 + 跨部门方向 + Board 沟通 + wisdom 建设

## Connections
→ VSM Stafford Beer (web research 2026-04-16)
→ relay_trap.md (CEO 变转述器 = System 2 退化)
→ CTO charter "独立技术建模能力" (CTO 接 System 3)
→ dispatch_board.py + cto_dispatch_broker.py (System 2 自动化已建)
→ auto_verify + K9 + AC (System 3 自动化已建)
→ 使命函数 M(t) + wisdom system (System 5 工具)
