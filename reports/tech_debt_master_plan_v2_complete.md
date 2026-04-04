# Y*gov技术债清理完整计划 v2

**执行时间：** 2026-04-03  
**执行人：** CTO团队（eng-platform/eng-kernel/eng-governance并行）  
**目标：** A-级系统健康度  
**当前状态：** C级 → 目标 A-级

---

## 技术债完整汇总

### v1计划（17项）+ 老大补充（20项）= **37项总计**

| 分类 | 数量 | 预计工作量 |
|------|------|------------|
| P0级（阻塞投产） | 4项 | 4-5小时 |
| P1级（功能不完整） | 5项 | 8-10小时 |
| P2级（代码质量） | 8项 | 6-8小时 |
| **架构断裂** | 4项 | 6-8小时 |
| **宪法修复** | 2项 | 3-4小时 |
| **发布安全** | 2项 | 2-3小时 |
| **CIEU盲区** | 3项 | 4-5小时 |
| **待完成交付** | 3项 | 4-6小时 |
| **测试覆盖** | 6项 | 15-23小时 |
| **总计** | **37项** | **52-74小时** |

---

## P0级 - 阻塞投产（4项，4-5小时）

### P0-1: experience_bridge断裂 🔴
- **问题：** Path B → Path A反馈通道缺失
- **修复：** orchestrator集成ExperienceBridge
- **工作量：** 2-3小时
- **分配：** eng-governance

### P0-2: external_governance_loop.py孤立 🔴
- **问题：** Path B高级编排层未接入
- **修复：** 调查后接入或删除
- **工作量：** 2-3小时
- **分配：** eng-governance

### P0-3: hook.py注释自相矛盾 🟡
- **问题：** "Ingress Controller" vs "纯翻译层"
- **修复：** 统一描述
- **工作量：** 5分钟
- **分配：** eng-platform

### P0-4: README可见性不足 🟡
- **问题：** baseline/delta/trend命令不突出
- **修复：** 增加Quick Start示例
- **工作量：** 30分钟
- **分配：** eng-platform

---

## P1级 - 功能不完整（5项，8-10小时）

### P1-1: Causal Engine零使用 🔴
- **问题：** 15,076条CIEU中0条causal_analysis
- **修复：** 激活调用链或删除
- **工作量：** 2小时
- **分配：** eng-governance

### P1-2: ml/objectives.py代码重复 🟡
- **问题：** 与metalearning.py重复53KB
- **修复：** 完成v0.41拆分或删除
- **工作量：** 1小时
- **分配：** eng-kernel

### P1-3: 7个孤立模块清理 🟡
- **文件：** report_metrics.py, ml/records.py, ml/registry.py, proposals.py, metrics.py, constraints.py
- **工作量：** 2-3小时
- **分配：** eng-governance

### P1-4: _hook_server.py状态确认 🟢
- **问题：** 老大提到但未找到
- **工作量：** 30分钟
- **分配：** eng-platform

### P1-5: 义务积压根因未解决 🔴 **NEW**
- **问题：** autonomous_daily_report/knowledge_gap_bootstrap每次session大量注册无fulfil路径
- **影响：** 今天清库三次根本原因
- **修复：** 实现fulfil路径或修改obligation触发条件
- **工作量：** 2-3小时
- **分配：** eng-governance

---

## P2级 - 代码质量（8项，6-8小时）

### P2-1: runtime_contracts.py placeholder 🟡
- **工作量：** 15分钟
- **分配：** eng-platform

### P2-2: Obligation定义漂移 🟡
- **工作量：** 30分钟
- **分配：** eng-governance

### P2-3: 21个零调用类清理 🟢
- **明细：**
  - Amendment系统（2个）：AmendmentEngine, AmendmentProposal
  - Metrics报告（6个）：CIEUMetrics, CausalMetrics, ChainClosureMetrics, InterventionMetrics, ObligationMetrics, OmissionMetrics
  - Domain配置（2个）：FinancePackConfig, SkillProvenance
  - NL翻译器（2个）：RegexProvider, TranslationProvider
  - 其他（9个）：ContractLifecycle, DimensionDiscovery, ExternalAuthorityScope, GEventType, PolicySourceTrust, TimeWindow, TradingCalendar, WorkloadRunner, BridgeInput
- **处理决策：** 逐个确认（删除/接入主线/标记实验性）
- **工作量：** 2-4小时
- **分配：** eng-kernel + eng-governance

### P2-4至P2-8: 其他优化（明细展开）
- **P2-4:** NullCIEUStore警告suppress（30分钟）
- **P2-5:** 死代码检测工具改进（1小时）
- **P2-6:** P2层49个模块深度审计（2小时）
- **P2-7:** CLI文档完整性验证（30分钟）
- **P2-8:** 测试覆盖gap分析（1小时）

---

## 架构断裂（4项，6-8小时）**NEW**

### A1: DelegationChain不支持树形validate() 🔴
- **问题：** 今天用主干绕过，根本问题未修
- **修复：** 在dimensions.py实现树形validate()
- **工作量：** 2-3小时
- **分配：** eng-kernel

### A2: ObligationStatus.CANCELLED无调用路径 🔴
- **问题：** cancel_obligation()方法缺失，今天删库三次根因之一
- **修复：** 实现cancel_obligation()方法
- **工作量：** 1-2小时
- **分配：** eng-governance

### A3: session边界管理缺失 🔴
- **问题：** ObligationRecord无session_id字段，新session无法cancel旧session遗留义务
- **修复：** 
  1. ObligationRecord增加session_id字段
  2. 实现cross-session cancel机制
- **工作量：** 2-3小时
- **分配：** eng-governance

### A4: CEO的allowedTools含Agent可bypass CTO 🟡
- **问题：** ceo.md的Agent权限过宽
- **修复：** 改为"Agent(ystar-cto)"限制只能调用CTO
- **工作量：** 10分钟
- **分配：** eng-platform

---

## 宪法修复（2项，3-4小时）**NEW**

### C1: 执行BOARD_PENDING.md的17个宪法修改点 🟡
- **内容：**
  1. 删除HOW描述（只保留WHAT/WHY）
  2. 集中obligation_timing到专门章节
  3. 补全fulfil机制
  4. 新增CTO自检义务
  5-17. 其他14个修改点（见BOARD_PENDING.md）
- **工作量：** 2-3小时
- **分配：** eng-governance

### C2: CTO自检义务写入宪法层 🟡
- **内容：**
  - pre-change health check
  - post-commit doctor
- **工作量：** 1小时
- **分配：** eng-governance

---

## 发布安全（2项，2-3小时）**NEW**

### S1: pyproject.toml加入include/exclude规则 🟡
- **内容：**
  ```toml
  [tool.setuptools.packages.find]
  include = ["ystar*"]
  exclude = ["tests*", "*.egg-info"]
  ```
- **工作量：** 30分钟
- **分配：** eng-platform

### S2: CI加入pre-publish packaging检查脚本 🟡
- **内容：** 发布前验证*.map、test_*等文件不被打包
- **工作量：** 1.5-2小时
- **分配：** eng-platform

---

## CIEU盲区（3项，4-5小时）**NEW**

### I1: 外部CLAUDE.md读取无CIEU记录 🟡
- **问题：** check_hook()对Read外部CLAUDE.md时无external_config_read事件
- **修复：** 写入external_config_read事件
- **工作量：** 1-2小时
- **分配：** eng-platform

### I2: CIEU归档机制缺失 🔴
- **问题：** 今天永久丢失所有历史数据
- **修复：** 实现ystar archive-cieu命令（已实现但未测试）
- **工作量：** 1-2小时
- **分配：** eng-platform

### I3: doctor --layer1缺少External Config Reads检查项 🟡
- **修复：** 增加第9个检查项
- **工作量：** 1小时
- **分配：** eng-platform

---

## 待完成交付（3项，4-6小时）**NEW**

### D1: PyPI v0.48.0发布 🟡
- **状态：** Board已批准，未执行
- **工作量：** 2小时
- **分配：** eng-platform

### D2: 义务积压根因解决（与P1-5重复，已合并）

### D3: Show HN发布 🟢
- **状态：** 需Board最终批准
- **工作量：** 2-3小时
- **分配：** CEO

---

## 测试覆盖（5项，15-23小时）**NEW**

### T1: CLI层18个命令无功能测试 🔴 **P20**
- **问题：** 18个CLI命令中只有domain有完整测试，14个完全无测试（78%）
- **最大风险：** setup和hook-install无测试（用户首次安装必经流程）
- **无测试命令：** setup, hook-install, demo, doctor, baseline, delta, verify, seal, audit, check, check-impact, report, reset-breaker, archive-cieu, simulate, quality, policy-builder, init
- **影响：** 这些命令任何一个坏掉，669/669测试全通过也不会发现
- **修复分阶段：**
  - Week 1 (P0): setup, hook-install（1-1.5小时）← **立即执行**
  - Week 2 (P1): baseline, delta, trend, audit, simulate, quality, init（5-8小时）
  - Week 3 (P2): check, impact, archive, demo, policy-builder（3-4.5小时）
  - Week 4 (P3): reset-breaker + E2E测试（2-3小时）
- **工作量：** 15-23小时总计，Week 1先做1-1.5小时
- **分配：** eng-platform
- **交付物：** 5个报告文件已生成（54.5KB，reports/目录）

### T2: experience_bridge集成测试增强 🟡
- **工作量：** 1小时
- **分配：** eng-governance

### T3: orchestrator Path B完整链路测试 🟡
- **工作量：** 1小时
- **分配：** eng-governance

### T4: session边界管理测试 🟡
- **工作量：** 1小时
- **分配：** eng-governance

### T5: CIEU归档功能测试 🟡
- **工作量：** 1小时
- **分配：** eng-platform

---

## 分阶段执行计划（更新）

### Phase 1: P0修复 + 架构断裂（8-10小时）
**目标：** C级 → B级

**P0层（4-5小时）：**
1. P0-3: hook.py注释（5分钟）
2. P0-4: README可见性（30分钟）
3. P0-2: external_governance_loop调查（2-3小时）
4. P0-1: experience_bridge集成（2-3小时）

**架构断裂（4-6小时）：**
1. A4: CEO allowedTools限制（10分钟）
2. A2: cancel_obligation()实现（1-2小时）
3. A3: session边界管理（2-3小时）
4. A1: 树形validate()（2-3小时）

### Phase 2: P1修复 + 宪法修复（11-14小时）
**目标：** B级 → B+级

**P1层（8-10小时）：**
1. P1-1: Causal Engine（2小时）
2. P1-2: ml/objectives.py（1小时）
3. P1-3: 7个孤立模块（2-3小时）
4. P1-4: _hook_server（30分钟）
5. P1-5: 义务积压根因（2-3小时）

**宪法修复（3-4小时）：**
1. C1: BOARD_PENDING.md执行（2-3小时）
2. C2: CTO自检义务（1小时）

### Phase 3: P2修复 + 发布安全 + CIEU盲区（12-16小时）
**目标：** B+级 → A-级

**P2层（6-8小时）：**
1. P2-1: runtime_contracts（15分钟）
2. P2-2: Obligation定义（30分钟）
3. P2-3: 21个零调用类（2-4小时）
4. P2-4至P2-8: 其他优化（3-4小时）

**发布安全（2-3小时）：**
1. S1: pyproject.toml规则（30分钟）
2. S2: CI检查脚本（1.5-2小时）

**CIEU盲区（4-5小时）：**
1. I1: 外部CLAUDE.md记录（1-2小时）
2. I2: CIEU归档机制（1-2小时）
3. I3: doctor检查项（1小时）

### Phase 4: 测试覆盖增强（8-12小时）
**目标：** 确保A-级质量

1. T1: CLI功能测试（6-8小时）
2. T2-T5: 其他测试增强（4小时）

### Phase 5: 待完成交付 + 验证（4-8小时）
1. D1: PyPI v0.48.0发布（2小时）
2. D3: Show HN发布（2-3小时）
3. 完整测试套件运行（1小时）
4. 最终验收（1-2小时）

---

## 并行执行策略（MAC机三条线）

### 线程1: CLI功能测试检测（eng-platform）
**任务：** T1: CLI层18个命令无功能测试
**工作量：** 6-8小时
**交付物：**
- 18个命令的功能测试覆盖报告
- 每个命令的测试用例清单
- 测试实现（如果时间允许）

### 线程2: 原计划技术债修复（eng-kernel + eng-governance）
**任务：** P0-1至P2-8（v1的17项）
**工作量：** 18-23小时
**交付物：**
- experience_bridge集成完成
- Causal Engine激活或删除
- 孤立模块清理
- 代码质量提升

### 线程3: 新补充技术债修复（eng-platform + eng-governance）
**任务：** A1-A4, C1-C2, S1-S2, I1-I3, D1
**工作量：** 19-26小时
**交付物：**
- 架构断裂修复
- 宪法修复
- 发布安全加固
- CIEU盲区填补
- v0.48.0发布

---

## 更新后时间线

| 阶段 | 工作量 | 并行执行 | 完成时间 |
|------|--------|----------|----------|
| Phase 1 | 8-10h | 3线并行 | 明天上午 |
| Phase 2 | 11-14h | 3线并行 | 明天晚上 |
| Phase 3 | 12-16h | 3线并行 | 后天晚上 |
| Phase 4 | 8-12h | 2线并行 | 大后天下午 |
| Phase 5 | 4-8h | 串行 | 大后天晚上 |
| **总计** | **43-60h** | **并行** | **4天** |

考虑并行执行，实际时钟时间：**2.5-3天**

---

## A-级标准（更新）

**必须满足：**
- ✅ 所有测试通过（669+新增）
- ✅ ystar doctor全通过
- ✅ 无功能断裂
- ✅ 无架构断裂
- ✅ 无代码重复
- ✅ 无孤立模块（>5KB）
- ✅ 无placeholder实现
- ✅ 配置文档一致
- ✅ CIEU功能完整（包括反馈闭环）
- ✅ CLI命令100%测试覆盖
- ✅ 核心功能覆盖率>90%
- ✅ session边界管理完整
- ✅ 宪法层完整更新
- ✅ 发布流程安全

---

**CTO签字：** eng-platform (主导)  
**Board批准：** 待批准  
**更新时间：** 2026-04-03 23:30  
**版本：** v2.0 (完整版，36项)
