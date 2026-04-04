# Y*gov Three-Layer Closed-Loop Governance Architecture

**Source:** RFC-2026-005 (Board批准, 2026-04-03)  
**Status:** 架构级指导文档，指导所有未来开发方向  
**CTO责任:** 按阶段执行，每个新阶段前提交RFC

---

## Architecture Vision

Y*gov从线性架构升级为三层闭环系统：

```
Layer 3: MetaLearning Hub (元知识层)
    ↕ 双向数据流
Layer 2: Governance Layer (内部治理 + 外部治理)
    ↕ 双向数据流
Layer 1: Execution Layer (hook + Orchestrator + CIEU)
```

**核心理念:** "谁来治理治理者" — 治理系统监控自己，学习自己的效果，改进自己的规则。

---

## Current Problems (现状诊断)

### Problem 1: Architecture is Linear, Not Closed-Loop
数据流是单向的：用户行为 → hook → check() → CIEU → OmissionEngine → GovernanceLoop → Path A → 结果写CIEU（断裂，没有回流学习层）

### Problem 2: MetaLearning Hub Does Not Exist
- YStarLoop: STATUS: LEGACY, 只处理内部CallRecord
- ExperienceBridge: 单向 Path B → GovernanceLoop, 外部治理经验无法回流到Path B本身
- Path A执行效果: 只写入CIEU，没有任何模块消费这个数据

三个学习数据源从未融合，互相孤立。

### Problem 3: Path A Execution Scope is Narrowed
- 设计意图: 改善治理能力（包括治理规则本身）
- 实际实现: 只能wire模块图的is_wired标志位
- AmendmentEngine存在但未被Orchestrator实例化，Path A无法自主提出contract参数调整

---

## Three-Layer Architecture (目标状态)

### Layer 3: MetaLearning Hub (元知识层)

**统一输入接口 (三个数据源):**
1. 内部CallRecord (来自hook路径)
2. 外部ExternalObservation (来自Path B)
3. 治理行动效果记录 (来自Path A执行结果)

**统一学习引擎:**
- 融合三种输入 → 统一知识表示
- "此类行为 × 此上下文 → 此治理效果"
- "此类wiring → 历史成功率 → 推荐优先级"

**统一输出接口 (三个方向):**
1. 更新IntentContract参数 (→ GovernanceLoop)
2. 更新Path B约束建议 (→ ExperienceBridge双向化)
3. Path A经验库 (→ Path A优先wiring方向)

**心跳检测:** 区分"数据源沉默=无新数据" vs "数据源断裂"

### Layer 2: Governance Layer (治理层)

**内部治理 (GovernanceLoop + Path A):**
- GovernanceLoop: 观测系统健康 → 产出GovernanceSuggestion → 委托Path A执行 → 验证执行效果
- Path A扩展后:
  - 现有: wire模块图
  - 新增: 提出contract参数调整建议
  - 不变: GovernanceLoop是委托者和裁判，Path A永远受约束
- 心跳: GovernanceLoop每次cycle写governance_loop_alive记录

**外部治理 (Path B):**
- 观测外部agent行为
- ExperienceBridge升级: 现在单向 Path B→GL，目标双向 GL也→Path B
- 心跳: 外部agent存活信号

### Layer 1: Execution Layer (执行层)

**Hook path:**
- hook → check() (10维度) → CIEU记录
- OmissionEngine (义务追踪)
- InterventionEngine (干预升级)
- CircuitBreaker (熔断保护)

**Orchestrator (5个子系统):**
1. InterventionEngine scan (每10次调用或60s)
2. GovernanceLoop + Path A (每50次调用或5min)
3. CausalEngine advisory (高风险工具触发)
4. Coverage scan (每200次调用或30min) [已实现]
5. **Governance heartbeat (每N次调用) [待实现]** ← 当前阶段首要任务

**心跳:** Orchestrator定期写governance_heartbeat到CIEU

---

## Heartbeat Mechanism (心跳机制 — 贯穿三层的基础设施)

### Y*gov Product Side (系统内部心跳)

| Layer | Heartbeat Implementation | Detection Method |
|-------|-------------------------|------------------|
| Layer 1 | Orchestrator第5个子系统，写event_type: governance_heartbeat | doctor检测最后heartbeat时间 |
| Layer 2 | GovernanceLoop每次tighten()写governance_loop_alive | doctor检测最后alive时间 |
| Layer 3 | Hub检测每个数据源最后活跃时间 | 区分"无新数据" vs "数据源断裂" |

**Configuration (session.json, 不硬编码):**
```json
{
  "heartbeat": {
    "interval_calls": 100,
    "governance_loop_timeout_secs": 600,
    "heartbeat_timeout_secs": 300
  }
}
```

**Doctor检查项 (新增):**
```
[✓] governance_heartbeat: 最后5分钟内有记录
[✓] governance_loop_alive: 最后10分钟内有记录
[✗] 超过阈值 → "治理层可能失联，请检查hook安装状态"
```

### Y*Bridge Labs Operations Side (agent存活监控)

Agent每5分钟写入.agent_daemon_state.json (与Y*gov heartbeat分开，不混用)

---

## Implementation Roadmap (三个阶段)

### Phase 1: Solidify Layer 1 (当前阶段, P0)

**Tasks (本周启动):**
- [x] DelegationChain每次调用验证 (RFC-2026-001批准，完成)
- [x] governance-coverage命令 (完成)
- [ ] GoalDrift/SkillProvenance/NonceLedger接入 (RFC-2026-002/003/004批准中)
- [ ] **Orchestrator heartbeat (第5个子系统) ← 首要任务**
  - Task file: .claude/tasks/eng-governance-heartbeat.md
  - Engineer: eng-governance
  - Due: 本周内
- [ ] **Doctor heartbeat detection**
  - Task file: .claude/tasks/eng-platform-doctor-heartbeat.md
  - Engineer: eng-platform
  - Due: 本周内

**Acceptance Criteria:**
- Orchestrator有第5个子系统写governance_heartbeat
- ystar doctor能检测heartbeat状态并报告
- RFC-2026-001~004全部执行完毕
- 测试套件全部通过

### Phase 2: Build Layer 3 MVP (下一阶段, P1)

**Tasks (需RFC, Phase 1完成后启动):**
1. YStarLoop去LEGACY化 (需RFC)
   - 移除STATUS: LEGACY标记
   - 与GovernanceLoop连接从Optional改为Required
2. ExperienceBridge双向化 (需RFC)
   - 新增: GovernanceLoop学习结果 → Path B约束更新
   - 新接口: bridge.push_governance_learning(result)
3. Path A执行效果收集 (低风险)
   - 格式: {suggestion_type, wiring_executed, health_before, health_after, delta, timestamp}
4. MetaLearning Hub骨架 (需RFC)
   - 统一输入接口
   - 简单融合逻辑 (MVP先跑通数据流)
   - 统一输出接口

**Acceptance Criteria:**
- ExperienceBridge有push_governance_learning()接口并被调用
- Path A每次cycle写标准格式效果记录到CIEU
- MetaLearning Hub能接收三种输入并产出三种输出
- YStarLoop不再标记为LEGACY
- ystar trend能显示学习质量相关指标

### Phase 3: Upgrade Layer 2 (未来阶段, P2)

**Tasks (需RFC, Phase 2完成后启动):**
1. Path A能力扩展: 提出contract参数调整建议
   - 通过AmendmentEngine提交
   - GovernanceLoop验证效果
   - 低风险调整(放松): 可自动执行
   - 高风险调整(收紧): 需Board确认
2. Path A获得经验库
   - 从MetaLearning Hub读取历史wiring成功率
   - 优先尝试历史上有效的wiring方向
   - "谁来治理治理者"完整闭环实现

**Acceptance Criteria:**
- Path A能提出contract参数调整建议并走AmendmentEngine流程
- 调整效果被MetaLearning Hub记录并影响下次建议方向
- CIEU可追溯完整链条: 观测→建议→执行→效果→经验记录

---

## What NOT to Do (风险隔离)

- ❌ 不在当前阶段改GovernanceLoop.tighten()核心逻辑 (HIGH风险，三处依赖)
- ❌ 不把Y*Bridge Labs心跳和Y*gov心跳混用 (场景不同，混用造成架构混乱)
- ❌ Path A不能自己修改PATH_A_AGENTS.md (宪法文件，Board专属权限)
- ❌ MetaLearning Hub不替代现有机制 (Hub是聚合层，不重写底层逻辑)
- ❌ 所有新参数不硬编码 (全部通过session.json可配置，代码只有默认值)

---

## CTO Execution Protocol

1. ✅ 读完此文档，把三个阶段的任务分解写入.claude/tasks/
2. ⏳ 当前阶段第一个任务: Orchestrator心跳，本周内启动
3. ✅ 此架构文档同步写入knowledge/cto/ (本文件)
4. ⏳ 下一阶段开始前，每个任务都需要RFC，Board审批后执行
5. ⚠️ 任何实现细节与此文档有冲突，以此文档为准，冲突需上报Board

---

## Quick Reference

**当前阶段 (Phase 1) 焦点:**
- Orchestrator第5个子系统: governance_heartbeat
- Doctor新增检查: heartbeat timeout detection
- 所有参数从session.json读取，不硬编码

**下一步 (Phase 2启动前):**
- 等待Phase 1完成
- CTO提交RFC for YStarLoop/ExperienceBridge/MetaLearning Hub
- Board审批后执行

**长期目标 (Phase 3):**
- Path A能提出contract参数调整
- 完整闭环: 观测→建议→执行→效果→学习→改进建议

---

**Board签字:** 刘浩天  
**日期:** 2026-04-03  
**文件编号:** RFC-2026-005
