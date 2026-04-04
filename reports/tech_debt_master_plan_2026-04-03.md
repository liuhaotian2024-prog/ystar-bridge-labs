# Y*gov技术债清理总计划

**执行时间：** 2026-04-03  
**执行人：** CTO (eng-platform主导，eng-kernel/eng-governance协同)  
**目标：** A-级系统健康度  
**当前状态：** C级 → 目标 A-级

---

## 技术债全景汇总

### 来源
1. full_system_tech_debt_2026-04-03_v2.md（128模块扫描）
2. isolation_investigation_2026-04-03.md（Top 2孤立模块调查）
3. design_debt_analysis_2026-04-03.md（今日交付质量）
4. cto_self_check_2026-04-03.md（自检发现）
5. 老大对话中追加发现

### 技术债总数：17项

| 优先级 | 数量 | 预计工作量 |
|--------|------|------------|
| P0 | 4项 | 4-5小时 |
| P1 | 4项 | 6-8小时 |
| P2 | 9项 | 8-10小时 |
| **总计** | **17项** | **18-23小时** |

---

## P0级 - 阻塞投产（4项）

### P0-1: experience_bridge断裂 🔴
- **文件：** adapters/orchestrator.py（需添加集成）
- **问题：** Path B → Path A反馈通道缺失
- **影响：** 今日Path B激活不完整，只有观察无反馈闭环
- **修复：**
  1. orchestrator.__init__()初始化ExperienceBridge
  2. 传给GovernanceLoop(experience_bridge=bridge)
  3. 定期调用bridge.ingest_path_b_cieu()
- **工作量：** 2-3小时
- **验证：** 9个集成测试通过 + 新增orchestrator集成测试

### P0-2: external_governance_loop.py孤立 🔴
- **文件：** path_b/external_governance_loop.py (17KB, 456行)
- **问题：** 0外部引用，Path B高级编排层未接入
- **调查方向：**
  - Option A：接入orchestrator（激活功能）
  - Option B：已被path_b_agent.py取代（删除代码）
- **工作量：** 1小时调查 + 1-2小时修复
- **验证：** 确认Path B完整链路

### P0-3: hook.py注释自相矛盾 🟡
- **文件：** adapters/hook.py:3,7
- **问题：** 第3行"Ingress Controller"，第7行"纯翻译层"
- **修复：** 统一为"Runtime Ingress Controller"，删除矛盾表述
- **工作量：** 5分钟

### P0-4: README可见性不足 🟡
- **文件：** README.md
- **问题：** baseline/delta/trend命令有文档但不突出
- **修复：**
  1. Quick Start章节增加baseline/delta示例
  2. 增加实际输出示例
  3. 突出CIEU四级分级
- **工作量：** 30分钟

---

## P1级 - 功能不完整（4项）

### P1-1: Causal Engine零使用 🔴
- **文件：** governance/causal_engine.py
- **问题：** 有7个外部引用，但15,076条CIEU中0条causal_analysis
- **根因：** orchestrator._run_causal_advisory()定义但从未调用
- **修复方向：**
  - Option A：激活调用链（修复bug）
  - Option B：删除Causal Engine代码和文档
  - Option C：标记为实验功能
- **工作量：** 2小时

### P1-2: ml/objectives.py代码重复 🟡
- **文件：** governance/ml/objectives.py (53KB)
- **问题：** 与metalearning.py重复定义NormativeObjective/ContractQuality
- **根因：** v0.41拆分未完成
- **修复：** 删除objectives.py或完成拆分
- **工作量：** 1小时

### P1-3: 7个孤立模块清理 🟡
- **文件：**
  - governance/report_metrics.py (12KB)
  - governance/ml/records.py (12KB)
  - governance/ml/registry.py (7KB)
  - governance/proposals.py (2.5KB)
  - governance/metrics.py (1.4KB)
  - governance/constraints.py (1KB)
- **工作量：** 2-3小时（逐个调查确认）

### P1-4: _hook_server.py状态确认 🟢
- **文件：** adapters/_hook_server.py（老大提到但未找到）
- **工作量：** 30分钟

---

## P2级 - 代码质量（9项）

### P2-1: runtime_contracts.py placeholder 🟡
- **文件：** adapters/runtime_contracts.py:217
- **问题：** 未使用kernel完整merge实现
- **修复：** 改为调用kernel.merge.merge_contracts()
- **工作量：** 15分钟

### P2-2: Obligation定义漂移 🟡
- **文件：** AGENTS.md Timing Registry
- **问题：** 2种触发的obligation未注册
- **修复：** 补全Registry或删除未使用章节
- **工作量：** 30分钟

### P2-3: 21个零调用类清理 🟢
- **文件：** 多个文件（Amendment系统、Metrics、Domain配置等）
- **工作量：** 2-4小时

### P2-4至P2-9: 其他小问题
- Interrupt Gate精准清理（已完成）✅
- 67个NullCIEUStore警告（suppress）
- 死代码检测工具改进
- P2层49个模块深度审计
- CLI文档完整性验证
- 测试覆盖gap分析

---

## 分阶段执行计划

### Phase 1: P0修复（4-5小时）
**目标：** C级 → B级

1. **P0-3: hook.py注释**（5分钟）✅ 快速胜利
2. **P0-4: README可见性**（30分钟）✅ 快速胜利
3. **P0-2: external_governance_loop调查**（1小时）
4. **P0-1: experience_bridge集成**（2-3小时）🔴 最关键

**验收标准：**
- experience_bridge反馈闭环工作
- Path B完整链路验证
- 669+N测试全部通过

### Phase 2: P1修复（6-8小时）
**目标：** B级 → B+级

1. **P1-1: Causal Engine激活或删除**（2小时）
2. **P1-2: ml/objectives.py清理**（1小时）
3. **P1-3: 7个孤立模块调查**（2-3小时）
4. **P1-4: _hook_server状态确认**（30分钟）

**验收标准：**
- 无功能断裂
- 无代码重复
- 孤立模块清理完成

### Phase 3: P2修复（8-10小时）
**目标：** B+级 → A-级

1. **P2-1: runtime_contracts placeholder**（15分钟）
2. **P2-2: Obligation定义漂移**（30分钟）
3. **P2-3: 21个零调用类清理**（2-4小时）
4. **P2-4至P2-9: 其他优化**（5-6小时）

**验收标准：**
- 无placeholder实现
- 配置文档一致
- 代码清洁度高

### Phase 4: 验证与测试（2-3小时）
**目标：** 确保A-级质量

1. **完整测试套件**（669+新增测试）
2. **ystar doctor --layer1 --layer2**
3. **全模块import测试**
4. **CIEU功能验证**
5. **性能基准测试**

### Phase 5: 文档与交付（1-2小时）
1. 更新CHANGELOG
2. 更新README
3. 生成技术债清理报告
4. Board最终验收

---

## A-级标准定义

**A-级：** 生产就绪，零阻塞性技术债

**必须满足：**
- ✅ 所有测试通过（669+新增）
- ✅ ystar doctor全通过
- ✅ 无功能断裂
- ✅ 无代码重复
- ✅ 无孤立模块（>5KB）
- ✅ 无placeholder实现
- ✅ 配置文档一致
- ✅ CIEU功能完整（包括反馈闭环）
- ✅ 核心功能覆盖率>90%

**允许存在（不影响A-级）：**
- 🟢 实验性功能（明确标记）
- 🟢 规划中功能（roadmap文档）
- 🟢 小于5KB的工具脚本孤立

---

## 预计时间线

| 阶段 | 工作量 | 完成时间 |
|------|--------|----------|
| Phase 1 (P0) | 4-5小时 | 今晚 |
| Phase 2 (P1) | 6-8小时 | 明天上午 |
| Phase 3 (P2) | 8-10小时 | 明天下午+晚上 |
| Phase 4 (验证) | 2-3小时 | 后天上午 |
| Phase 5 (交付) | 1-2小时 | 后天中午 |
| **总计** | **21-28小时** | **2.5天** |

---

## 执行策略

### 并行执行
- eng-platform: P0-1 experience_bridge集成（最关键）
- eng-kernel: P1-1 Causal Engine调查
- eng-governance: P0-2 external_governance_loop调查

### 快速胜利
- P0-3 hook.py注释（5分钟）
- P0-4 README可见性（30分钟）
- P2-1 runtime_contracts placeholder（15分钟）

### 风险管理
- P0-1 experience_bridge是最大风险（2-3小时，复杂集成）
- P1-1 Causal Engine需要决策（激活 vs 删除）
- P2-3 21个零调用类需要逐个判断

---

## 立即开始

**Phase 1.1: 快速胜利（35分钟）**

按照优先级立即执行：
1. P0-3: hook.py注释（5分钟）
2. P0-4: README可见性（30分钟）

然后进入：
3. P0-2: external_governance_loop调查（1小时）
4. P0-1: experience_bridge集成（2-3小时）

---

**CTO签字：** eng-platform (执行)  
**Board批准：** 待批准  
**执行开始：** 2026-04-03 23:00  
**预计完成：** 2026-04-06 12:00
