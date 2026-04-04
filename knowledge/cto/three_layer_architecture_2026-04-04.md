# RFC-2026-005
# 标题：Y*gov 三层闭环治理架构
# 提出者：Board（刘浩天）
# 日期：2026-04-03
# 状态：Board直接批准，CTO负责执行规划
# 优先级：架构级，指导未来所有开发方向

---

## 一、现状诊断

经过2026-04-03全面审计，现有架构存在三个根本性缺陷：

### 缺陷1：架构是线性的，不是闭环的

现有数据流：
```
用户行为 → hook → check() → CIEU
         → OmissionEngine → 义务追踪
         → GovernanceLoop → 产出建议
         → Path A → wire模块图
                    ↓
               结果写CIEU（断裂，没有回流学习层）
```

### 缺陷2：MetaLearning Hub不存在

- YStarLoop（metalearning.py）：STATUS: LEGACY，只处理内部CallRecord
- ExperienceBridge：Direction: Path B → GovernanceLoop（单向），外部治理经验无法回流到Path B本身
- Path A执行效果：只写入CIEU，没有任何模块消费这个数据

三个学习数据源从未融合，互相孤立。

### 缺陷3：Path A执行范围被窄化

- 设计意图：改善治理能力（包括治理规则本身）
- 实际实现：只能wire模块图的is_wired标志位
- AmendmentEngine存在但：在Orchestrator中未被实例化，需要人工审批才能激活，Path A无法自主提出contract参数调整

---

## 二、目标架构：三层闭环系统

```
╔══════════════════════════════════════════════════════════════════╗
║               Layer 3：元知识层（MetaLearning Hub）               ║
║                                                                  ║
║  ┌───────────────────────────────────────────────────────────┐  ║
║  │           统一输入接口（三个数据源）                         │  ║
║  │  · 内部CallRecord（来自hook路径）                           │  ║
║  │  · 外部ExternalObservation（来自Path B）                   │  ║
║  │  · 治理行动效果记录（来自Path A执行结果）                    │  ║
║  └──────────────────────────┬────────────────────────────────┘  ║
║                             ↓                                    ║
║  ┌───────────────────────────────────────────────────────────┐  ║
║  │           统一学习引擎                                      │  ║
║  │  融合三种输入 → 统一知识表示                                 │  ║
║  │  "此类行为 × 此上下文 → 此治理效果"                          │  ║
║  │  "此类wiring → 历史成功率 → 推荐优先级"                     │  ║
║  └──────────────────────────┬────────────────────────────────┘  ║
║                             ↓                                    ║
║  ┌───────────────────────────────────────────────────────────┐  ║
║  │           统一输出接口（三个方向）                           │  ║
║  │  → 更新IntentContract参数（→ GovernanceLoop）               │  ║
║  │  → 更新Path B约束建议（→ ExperienceBridge双向化）            │  ║
║  │  → Path A经验库（→ Path A优先wiring方向）                   │  ║
║  └───────────────────────────────────────────────────────────┘  ║
║                                                                  ║
║  心跳检测：区分"数据源沉默=无新数据"vs"数据源断裂"                ║
╚═══════════════════╦════════════════════════╦════════════════════╝
                    ↕ 双向                   ↕ 双向
╔═══════════════════╩══════════════╗  ╔══════╩══════════════════════╗
║   Layer 2：内部治理层              ║  ║  Layer 2：外部治理层          ║
║                                  ║  ║                              ║
║  GovernanceLoop                  ║←─║  Path B                      ║
║  · 观测系统健康                   ║─→║  · 观测外部agent行为           ║
║  · 产出GovernanceSuggestion      ║  ║                              ║
║  · 委托Path A执行                 ║  ║  ExperienceBridge（升级）     ║
║  · 验证执行效果                   ║  ║  · 现在：单向Path B→GL        ║
║                                  ║  ║  · 目标：双向，GL也→Path B    ║
║  Path A（扩展后）                 ║  ║                              ║
║  · 现有：wire模块图               ║  ║  心跳：外部agent存活信号       ║
║  · 新增：提出contract参数调整建议  ║  ║                              ║
║  · 不变：GovernanceLoop是委托者   ║  ║                              ║
║    和裁判，Path A永远受约束        ║  ║                              ║
║                                  ║  ║                              ║
║  心跳：GovernanceLoop每次cycle    ║  ║                              ║
║  写governance_loop_alive记录      ║  ║                              ║
╚═══════════════════╦══════════════╝  ╚═════════════════════════════╝
                    ↕ 双向
╔═══════════════════╩══════════════════════════════════════════════╗
║   Layer 1：执行层                                                  ║
║                                                                   ║
║  hook → check()（10维度） → CIEU记录                               ║
║       → OmissionEngine（义务追踪）                                 ║
║       → InterventionEngine（干预升级）                             ║
║       → CircuitBreaker（熔断保护）                                 ║
║                                                                   ║
║  Orchestrator（5个子系统）：                                        ║
║    1. InterventionEngine scan（每10次调用或60s）                    ║
║    2. GovernanceLoop + Path A（每50次调用或5min）                   ║
║    3. CausalEngine advisory（高风险工具触发）                       ║
║    4. Coverage scan（每200次调用或30min）[已实现]                   ║
║    5. Governance heartbeat（每N次调用）[待实现]                     ║
║                                                                   ║
║  心跳：Orchestrator定期写governance_heartbeat到CIEU               ║
║  doctor检测：沉默不等于健康，超过阈值即需要调查                      ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## 三、Y*Bridge Labs对应架构（轻量手工版）

Y*Bridge Labs作为第一个用户，用文件系统和daemon实现同样的三层逻辑：

```
╔══════════════════════════════════════╗
║  Layer 3：知识积累层                   ║
║  knowledge/目录 + bootstrap机制       ║
║  improvement_queue（经验驱动任务队列） ║
║  输入：CIEU记录 + 任务完成效果记录     ║
║  输出：下次session @knowledge加载      ║
╚══════════════════╦═══════════════════╝
                   ↕
╔══════════════════╩═══════════════════╗
║  Layer 2：协调层                       ║
║  CEO(Aiden) + daemon                  ║
║  · 读取CIEU发现问题                    ║
║  · 调度agent执行改进任务               ║
║  · 验证执行结果                        ║
║  · 产出新的improvement_queue条目       ║
╚══════════════════╦═══════════════════╝
                   ↕
╔══════════════════╩═══════════════════╗
║  Layer 1：执行层                       ║
║  各agent工具调用                       ║
║  Y*gov hook治理所有操作                ║
║  CIEU记录完整行为链                    ║
║  心跳：.agent_daemon_state.json       ║
╚══════════════════════════════════════╝
```

两个系统（Y*gov产品 vs Y*Bridge Labs运营）的心跳机制分开设计，不混用。

---

## 四、心跳机制：贯穿三层的基础设施

### Y*gov产品侧——系统内部心跳，用户不感知

| 层次 | 心跳实现 | 检测方式 |
|------|---------|---------|
| Layer 1 | Orchestrator第5个子系统，写event_type: governance_heartbeat | doctor检测最后heartbeat时间 |
| Layer 2 | GovernanceLoop每次tighten()写governance_loop_alive | doctor检测最后alive时间 |
| Layer 3 | Hub检测每个数据源最后活跃时间 | 区分"无新数据"vs"数据源断裂" |

配置参数（session.json，不硬编码）：
```json
{
  "heartbeat": {
    "interval_calls": 100,
    "governance_loop_timeout_secs": 600,
    "heartbeat_timeout_secs": 300
  }
}
```

doctor新增检查项：
```
[✓] governance_heartbeat: 最后5分钟内有记录
[✓] governance_loop_alive: 最后10分钟内有记录
[✗] 超过阈值 → "治理层可能失联，请检查hook安装状态"
```

### Y*Bridge Labs运营侧——agent存活监控，Board可见

agent每5分钟写入.agent_daemon_state.json：
```json
{
  "agent_id": "eng-kernel",
  "status": "running",
  "current_task": "修复nl_to_contract正则",
  "progress": "3/5测试通过",
  "last_heartbeat": 1743734400
}
```

daemon检测：超过10分钟无更新 → status: presumed_dead → Board可见。

---

## 五、实现路径（三个阶段）

### 当前阶段：夯实Layer 1（正在执行）

- DelegationChain每次调用验证 ✅ RFC-2026-001批准，线6完成
- governance-coverage命令 ✅ 完成
- GoalDrift/SkillProvenance/NonceLedger接入 RFC-2026-002/003/004批准中
- **Orchestrator心跳（第5个子系统）← 纳入当前阶段，本周启动**

### 下一阶段：建立Layer 3 MVP

优先级P1，目标：三个数据源有统一接口，数据流打通。

**任务1：YStarLoop去LEGACY化**
- 移除STATUS: LEGACY标记
- 正式纳入GovernanceLoop主线
- 与GovernanceLoop的连接从Optional改为Required
- 需要RFC

**任务2：ExperienceBridge双向化**
- 现在：Path B → GovernanceLoop（单向）
- 新增：GovernanceLoop学习结果 → Path B约束更新
- 新接口：bridge.push_governance_learning(result)
- 需要RFC

**任务3：Path A执行效果收集**
- 每次cycle完成后写标准格式效果记录
- 格式：{suggestion_type, wiring_executed, health_before, health_after, delta, timestamp}
- 这些记录成为MetaLearning Hub的第三个输入源
- 风险LOW，新增输出不改现有逻辑

**任务4：MetaLearning Hub骨架**
- 统一输入接口（接受三种记录）
- 简单融合逻辑（MVP先跑通数据流，不追求算法最优）
- 统一输出接口（三个方向）
- 需要RFC

### 未来阶段：完成Layer 2升级

**Path A能力扩展：**
- 在现有wiring能力基础上新增：提出contract参数调整建议
- 通过AmendmentEngine提交，GovernanceLoop验证效果
- 低风险调整（放松）：可自动执行
- 高风险调整（收紧）：需Board确认
- 需要RFC

**Path A获得经验库：**
- 从MetaLearning Hub读取历史wiring成功率
- 优先尝试历史上有效的wiring方向
- "谁来治理治理者"完整闭环实现

---

## 六、不做的事（风险隔离）

- ❌ 不在当前阶段改GovernanceLoop.tighten()核心逻辑（HIGH风险，三处依赖）
- ❌ 不把Y*Bridge Labs心跳和Y*gov心跳混用（场景不同，混用造成架构混乱）
- ❌ Path A不能自己修改PATH_A_AGENTS.md（宪法文件，Board专属权限）
- ❌ MetaLearning Hub不替代现有机制（Hub是聚合层，不重写底层逻辑）
- ❌ 所有新参数不硬编码（全部通过session.json可配置，代码只有默认值）

---

## 七、验收标准

### 当前阶段完成标志
- Orchestrator有第5个子系统写governance_heartbeat
- ystar doctor能检测heartbeat状态并报告
- RFC-2026-001~004全部执行完毕，测试通过
- 测试套件全部通过（当前基准）

### 下一阶段完成标志
- ExperienceBridge有push_governance_learning()接口并被调用
- Path A每次cycle写标准格式效果记录到CIEU
- MetaLearning Hub能接收三种输入并产出三种输出
- YStarLoop不再标记为LEGACY
- ystar trend能显示学习质量相关指标

### 未来阶段完成标志
- Path A能提出contract参数调整建议并走AmendmentEngine流程
- 调整效果被MetaLearning Hub记录并影响下次建议方向
- CIEU可追溯完整链条：观测→建议→执行→效果→经验记录

---

## 八、CTO执行要求

1. 读完此文档，把三个阶段的任务分解写入.claude/tasks/
2. 当前阶段第一个任务：Orchestrator心跳，本周内启动
3. 此架构文档同步写入knowledge/cto/，确保每次session加载
4. 下一阶段开始前，每个任务都需要RFC，Board审批后执行
5. 任何实现细节与此文档有冲突，以此文档为准，冲突需上报Board

---

Board签字：刘浩天
日期：2026-04-03
文件编号：RFC-2026-005
