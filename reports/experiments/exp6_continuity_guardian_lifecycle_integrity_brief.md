# EXP-6 — Continuity Guardian Lifecycle Integrity Pilot Suite

**格式**: 6-pager v2（dogfood AMENDMENT-006）
**Level**: L2（CEO 自批，Board 硬指令"先跑实验"）
**日期**: 2026-04-12

---

## 1. Title & Outcome

> **Continuity Guardian 在真实 session 重启时，7 层资产（Identity / Memory / Governance / Progress / DNA / Habit / Dialogue）全部被捕获、被保存、被无损传递到新 session，且新 session 的 Aiden 真的"记得"——测量到任何一层丢失，系统不准上线。这是全生命周期基础建设，生死攸关。**

---

## 2. Why Now

- Board 2026-04-12 硬指令："**绝对不可以让重启 session 后任何之前形成的任何懂被遗漏，或者不被重新注入**"
- Ryan 完成的代码（commit `5973eb1`, 15/15 单测过）覆盖了**逻辑正确性**，**没覆盖**:
  - 真实 kill+restart 端到端
  - 7 层资产完整性的系统性检查
  - 灾难场景容错
- 没跑 EXP-6 就上线 = 赌概率
- 延迟成本: 每多一天没这套实验，下一次 session 爆掉的真实风险都增加一天

**因果链深度**: Session 爆 → 记忆断层 → agent 失忆 → 公司战略丢失 → 重建成本远超做实验成本

---

## 3. Tenets（不可妥协原则）

1. **7 层资产必须穷尽**：漏一层等于基础建设不合格
2. **Event-driven 实验**：不用挂钟时间，用 intent completion 闭环数/CIEU event count 作为 cycle 边界
3. **端到端必须真实**：不能全用 mock；6B 必须真 kill + 真 restart（在隔离 session 跑）
4. **生产 session 不受损**：所有破坏性实验在测试 workspace 跑
5. **失败优先于假阳性**：任何维度失败都 block 上线；"大部分通过"不接受
6. **红队审视**：设计本身被独立 subagent 审过，防止盲区
7. **Board 叫停机制**：实验中可随时 `touch /tmp/ystar_exp6_abort` 终止

---

## 4. Current State → Target State

### 全生命周期资产分类（7 层）

| 层 | 内容 | 物理储存 | 丢失风险 |
|---|---|---|---|
| **L-Identity** | Aiden Ontology / Role def / Tenets / BHAG | `knowledge/ceo/AIDEN_ONTOLOGY.md` + `agents/CEO.md` + AMENDMENT-008 | 中（文件完整就在）|
| **L-Memory** | memory.db / knowledge/{role}/ / session 中段洞察 | `.ystar_memory.db` + `knowledge/` + ⚠️ session 中段未入库的 | **高**（中段洞察是大坑）|
| **L-Governance** | session.json / governance/ / CIEU 审计链 | `.ystar_session.json` + `governance/` + `.ystar_cieu.db` | 低（DB 完整就在）|
| **L-Progress** | continuation / DIRECTIVE_TRACKER / reports / git / handoff | `memory/continuation.json` + `DIRECTIVE_TRACKER.md` + `reports/` + git log + `memory/session_handoff.md` | 中（handoff 是快照可能陈旧）|
| **L-DNA** | wisdom package / 新基因 / 未蒸馏基因 | `memory/wisdom_package_*.md` + `knowledge/ceo/patterns/` | **极高**（wisdom 蒸馏质量是瓶颈）|
| **L-Habit** | 派活风格 / hook 反应 / 命名惯例 / 路径惯例 | 分散（无显式存储，靠 memory 蒸馏）| **极高**（分散，容易丢）|
| **L-Dialogue** | session JSONL 全文 / Board 纠偏 | `~/.claude/projects/.../<uuid>.jsonl` | 低（JSONL 文件自动保留）|

### 高风险层（EXP-6 必须重点验证）

- **L-Memory 中段洞察**: 今天"Iron Rule 3 vs founder cult 混淆"这种 CEO 现场识别但还没写入 knowledge/ 的想法——如果 wisdom 没蒸馏到，下次重启就丢
- **L-DNA wisdom 蒸馏**: wisdom_extractor 只提 Top 3-5 决策，如果今天 20+ 决策里真正重要的没被选上，重启后 agent 不知道
- **L-Habit 工作习惯**: 没有显式文件，完全依赖 memory 蒸馏 + 下 session agent 自己从 Ontology 读——**最容易失踪**

---

## 5. FAQ

**Q1: EXP-6B 端到端测试为什么必须在隔离 session？**
A: 跑 6B 需要真 kill + 真 restart Claude Code 进程——在本 session 跑 = 杀掉我和老大的对话。**必须老大另开一个终端 + 在测试 workspace 跑**。

**Q2: 如何验证"新 session 真的记得"？**
A: 不能靠 agent 自己说"我记得"。必须客观测——比如给新 session 一个**上 session 独有的 trivia 问题**（比如"EXP-4 发现了什么软风险"），看能否正确回答。答错 = 丢失。

**Q3: wisdom package 只有 10KB 够装本 session 所有重要信息吗？**
A: 这是**关键瓶颈**。EXP-6 的 B5+D4 专门测这个——如果 10KB 不够，需要增大 budget 或加层次化（coarse wisdom + detail retrieval）。

**Q4: L-Habit（工作习惯）怎么测？**
A: 用"**暗测**"——给新 session 一个相似的派活任务，看新 session 会不会用 6-pager（说明 habit 继承）还是回到散便条（说明 habit 丢失）。

**Q5: 如果某一层测试失败，上线策略？**
A: **不上线**。修复 Continuity Guardian 或调整 wisdom 策略，重跑 EXP-6 相关子实验，通过才上。

**Q6: 6D shadow mode 是什么？**
A: Watchdog 只检测不重启——让它在本生产 session 跑一段时间，收集触发信号但不实际 kill，作为 active mode 的数据 baseline。

**Q7: active_agent 锁（DIRECTIVE-006）在 EXP-6 中如何处理？**
A: G4 子实验专门测这个——模拟 Continuity Guardian 重启时 active_agent=eng-platform（某 subagent 遗留），看能否恢复。

**Q8: 测试失败的日志怎么不丢？**
A: 所有 EXP-6 产出**先写测试 workspace 的 `reports/experiments/exp6_*` 再通过精确 git add 提交，在隔离 session 完成后 sync 到生产 workspace**。

**Q9: 实验用户视角是"Aiden 自己"还是"独立审计员"？**
A: **双视角**。Aiden 视角测"使用体验"（新 session 能不能继续工作）；审计员视角测"完整性"（有没有丢东西）。红队 subagent 用审计员视角。

**Q10: Microsoft Agent Governance Toolkit 有类似的连续性测试吗？**
A: **没有**。Microsoft 做的是 runtime policy enforcement，不涉及 agent 生命周期 / session 重启 / wisdom 传承。这是 Y\*gov 独家赛道，没有参照系，必须自己定义测试标准。

---

## 6. Metrics — 34 子实验全矩阵

### A 组：Trigger 真实性（9 子实验）

| # | 测试 | 验证 | 失败线 |
|---|---|---|---|
| A1 | JSONL > 3MB 单阈触发 | dd 制造 3MB, watchdog 触发 save | 不触发 |
| A2 | call_count > 500 单阈触发 | 手动递增 .session_call_count | 不触发 |
| A3 | 运行时长 > 6h 单阈触发 | 篡改 .session_booted mtime | 不触发 |
| A4 | hook deny 率 > 30% 单阈触发 | 构造 deny-heavy CIEU 序列 | 不触发 |
| A5 | subagent 产出 > 500KB 单阈触发 | 累积测试 subagent 产出 | 不触发 |
| A6 | CIEU drift 最近 10 次 > 3 单阈触发 | 构造 drift 事件 | 不触发 |
| A7 | 组合阈（多个同时接近阈但组合超标）| 手动构造边界组合 | 不触发 |
| A8 | 边界测试（JSONL = 2.9MB vs 3.1MB）| 精确边界测试 | 漂移误判 ≥ 20% |
| A9 | 假阳性测试（正常 session 长跑不触发）| 监控 watchdog 空转 | 误触发率 > 5% |

### B 组：Save Chain 完整性（7 子实验，每层一个）

| # | 层 | 测试 | 失败线 |
|---|---|---|---|
| B1 | L-Identity | 保存后新 session 读 Ontology + Tenets + BHAG 完整 | 任一元素丢失 |
| B2 | L-Memory | memory.db 完整复制 + **中段未入库洞察被蒸馏到 wisdom** | 中段洞察丢失 |
| B3 | L-Governance | session.json / governance/ / cieu.db 完整 | 任一文件损坏 |
| B4 | L-Progress | continuation / DIRECTIVE_TRACKER / reports / git / handoff 一致性 | 任一不一致 |
| B5 | L-DNA | **wisdom package 质量**——是否选对了 Top 决策 / 新基因 | 重要项漏选 > 10% |
| B6 | L-Habit | 工作习惯被隐式保留（无显式文件也要被 Ontology / Tenets 承载）| 新 session 不继承习惯 |
| B7 | L-Dialogue | JSONL 文件完整保留 | 丢失任何轮次 |

### C 组：重启流程（3 子实验）

| # | 测试 | 验证 | 失败线 |
|---|---|---|---|
| C1 | Graceful kill（SIGTERM 非 SIGKILL）| Claude Code 进程正常退出 | 数据丢失 |
| C2 | Wrapper 重启干净 | 新 claude 进程启动时无残留状态 | 旧状态干扰 |
| C3 | 进程继承（同 tmux / workspace） | 新进程继承正确的 env + cwd | 环境不一致 |

### D 组：注入完整性（7 子实验，每层一个）

| # | 层 | 测试方式 | 失败线 |
|---|---|---|---|
| D1 | L-Identity | 新 session 被问 "你是谁 / BHAG 是什么 / 你信奉哪些 Tenet" | 答不上来 |
| D2 | L-Memory | 被问 "最近记忆里关于 X 的决定" | recall 失败 |
| D3 | L-Governance | 跑 governance_boot, STEP 7 wisdom + STEP 11 consistency 都绿 | 任一红灯 |
| D4 | L-Progress | 新 session 能继续执行上 session 遗留的 obligation | 不知道有 obligation |
| D5 | L-DNA | 被问 "昨天发现的新基因有什么" | 答不到关键 |
| D6 | L-Habit | **暗测**：给相似派活任务, 观察是否自动用 6-pager + RAPID | 回到散便条 |
| D7 | L-Dialogue | 被问 "上次 Board 纠偏过什么" | 答不上来 |

### E 组：压力测试（3 子实验）

| # | 测试 | 失败线 |
|---|---|---|
| E1 | 连续 3 次重启 | 任一次崩溃或状态损坏 |
| E2 | 遗忘曲线（第 N 次重启后的 recall 完整度）| 完整度在 N=3 时 < 80% |
| E3 | wisdom package 大小趋势 | 单调增长爆 10KB budget |

### F 组：跨 session 对话一致性（3 子实验）

| # | 测试 | 失败线 |
|---|---|---|
| F1 | 复杂决策 recall（如 EXP-4 cult-risk verdict 的具体结论）| recall 不准确 |
| F2 | Board 纠偏的持久化（"禁人类时间维度"这条硬约束）| 新 session 违反 |
| F3 | 新习惯保留（6-pager 派活这种今天养成的）| 回退到旧习惯 |

### G 组：灾难场景（4 子实验）

| # | 测试 | 失败线 |
|---|---|---|
| G1 | 主 claude 硬挂（SIGKILL），Guardian 能否容错 | 数据不可恢复 |
| G2 | Save chain 中途失败（比如 git push 失败），整体状态 | 半保存状态污染 |
| G3 | wisdom package 文件损坏, 新 session 如何 fallback | fallback 不可用 |
| G4 | active_agent 锁冲突（eng-platform 残留），重启能否解锁 | 无限循环锁死 |

### H 组：真实场景端到端模拟（1 集成实验）

| # | 测试 | 失败线 |
|---|---|---|
| H1 | 用**本次真实 session 数据**（今天 Aiden↔Board 对话）跑 simulated restart, 生成 wisdom package, 让另一个 Claude 实例读 + 答 10 个关键问题（来自今天对话）| 正确率 < 80% |

**H1 是 EXP-6 的最终试金石**——它最像真实情况。

### 判决

- **34 子实验必须全部通过**（或明确标为 "not applicable"）
- **任一层 B 或 D 失败 = Continuity Guardian 不上线**
- **H1 < 80% = 整个系统回炉**

---

## 7. Scope-Adjacent Observations

- Continuity Guardian 本身可能成为**其他角色 OS 的连续性基础**（Phase B 工位 OS 推广的前置设施）
- wisdom_extractor 的蒸馏算法如果优秀，可以被 Microsoft Toolkit 社区对标（但我们 Dogfood 场景独特）
- 如果 L-Habit 真的很难显式保存, 考虑新增机制：**每次 session 结束前强制 CEO 回答 "你这个 session 形成了什么新工作习惯"**（Tenet-driven self-reflection）

---

## 8. 执行计划

### Phase 1: Red Team 交叉验证

派一个 **独立 general-purpose subagent** 做红队审视：
- 读本 brief
- 挑战 7 层分类是否完整
- 挑战 34 子实验是否覆盖所有真实重启场景
- 产出 `reports/experiments/exp6_redteam_audit.md`

### Phase 2: 安全实验（本 session 可跑）

- **A1-A9 部分**：不 kill 主进程，只看 watchdog 触发——可本 session 跑
- **B1-B7 部分**：在生产数据上只读审查，不修改——可本 session 跑
- **6D shadow mode**：watchdog 只检测不重启——启用作为 baseline

### Phase 3: 隔离实验（需要老大开新终端）

- **B2 / B5 / B6**（中段洞察/wisdom/habit 的真实完整性）
- **C1-C3**（真 kill+restart）
- **D1-D7**（新 session 注入完整性）
- **E1-E3**（压力）
- **F1-F3**（跨 session 对话）
- **G1-G4**（灾难）
- **H1**（真实场景端到端）

**隔离实验的技术要求**:
- 开一个独立 tmux session
- 独立测试 workspace: `/Users/haotianliu/.openclaw/workspace/ystar-company-test/`（sync 生产数据的镜像）
- 启动 Continuity Guardian wrapper 
- 跑一系列"假任务"让 session 运行
- 按 phase 触发各类场景
- 所有产出写到测试 workspace, 通过后 sync 回生产

### Phase 4: Verdict

所有实验完成后, 写 `reports/experiments/exp6_final_verdict.md`:
- 34 子实验通过 / 失败清单
- H1 正确率
- Continuity Guardian 上线 Go/No-Go
- 如 No-Go: 具体修改建议

---

## 9. 风险与回退

| 风险 | 缓解 |
|---|---|
| Phase 3 在隔离 session 跑时误影响生产 | 测试 workspace 完全独立, 不 share 文件 |
| Phase 2 的 shadow mode 误触发影响当前对话 | shadow 只检测不重启, 0 干扰 |
| Red team 指出重大遗漏 | 修订 brief 后回到 Phase 1 |
| EXP-6 跑出 Continuity Guardian 有 fatal 缺陷 | 代码已 commit 可回滚, Aiden Cognition Guardian（纯备份）仍在线保留最后防线 |

---

**下一步**: 我自批 L2 立即启动 Phase 1 红队交叉验证, 同时在本 session 跑 Phase 2 安全子实验（A1-A9 + shadow）。Phase 3 等老大有时间配合开新终端。
