Audience: Ethan-CTO (技术审), Maya-Governance (治理兼容性审), Board (approve final triage + Phase 0 track 7+8), 全 agent team (了解外部工具边界).
Research basis: Board 2026-04-21 顾问建议分 3 类 (借鉴 / 已更强 / 直接装); Hermes ecosystem (MIT, hermes-agent + hermes-workspace + mission-control 3.7k star + HermesHub); mem0-mcp-selfhosted (Qdrant + Ollama 全本地); claude-mem (37777 端口无认证高风险, 2026-02 社区审计); Y* 现有 aiden_brain.db (6D 语义图 146 nodes/1902 edges) + idle_learning.py + SKILL.md 自定义; v0.3 Section 18 Engram 方向; Ethan v0.4 ruling 15 INV + M Triangle.
Synthesis: 11 项顾问建议 triage 为 3 层 × 3 紧急度矩阵. 采纳 6 项 (FTS5 记忆检索 / 5-条件学习触发 / Qdrant 向量 / mem0-mcp-selfhosted MCP wrapper / mission-control fork dashboard / agentskills.io 标准化), 拒绝 3 项 (Hermes Profiles / claude-mem / hermes-workspace), 谨慎 2 项 (hermes-agent 全栈 / HermesHub). 采纳集成位置 Phase 0 Track 7+8 (记忆栈 + 学习触发) + Phase 2 Track 9 (mission-control UI) + Phase 3 Track 10 (Skill 标准化). 所有采纳**不侵犯** Y*gov 治理核心 (CIEU Merkle / check() / DelegationChain), 只填记忆检索 gap.
Purpose: Enable Board approval of 外部工具 triage 结果; Ethan 技术 ruling 兼容性审; Maya 治理 invariant 审; 集成 Phase 0 新 Track 7+8 + Phase 2 Track 9 + Phase 3 Track 10 进 Phase 0 实施单 v2 + v0.3 迁移方案 Section 19 更新.

---

# External Tool Adoption Triage (Y* vs Hermes / claude-mem / mem0-mcp-selfhosted)

**日期**: 2026-04-21
**CEO**: Aiden, 初判 per Board 顾问建议
**状态**: Draft pending Ethan + Maya independent dual review

---

## 1. Y* 现有优势 (不可让步的 invariant)

审每条采纳前必先守住:

| Y* 核心 | Hermes/claude-mem 等 | 让步? |
|---|---|---|
| CIEU SHA-256 Merkle 链 (不可篡改 audit) | Hermes 普通日志 (agent 可改) | **❌ 不让步** — 让 = M-2a 根崩 |
| Y*gov check() 0.042ms pre-execution | Hermes 无预执行治理 | **❌ 不让步** — 让 = 治理绕过 |
| DelegationChain 单调性 (sub-agent 不超父权限) | Hermes sub-agent 可超父 | **❌ 不让步** — 让 = 权限漂 |
| OmissionEngine SOFT/HARD 强制 | Hermes 建议性自评 | **❌ 不让步** — 让 = M-2b 弱化 |
| forget_guard 17 规则 hook 拦 | 外部工具 bypass 风险 | **❌ 不让步** — 让 = precision + recall 双崩 |
| immutable_paths (charter 级) | 外部工具直写配置 | **❌ 不让步** — 让 = charter drift |
| 9-11 agent 7-layer identity | Hermes Profiles (config+memory 层) | **❌ 不退化** — 采 Profile 命名不采结构 |

**铁律**: 任何外部工具采纳, 必**不侵犯**上述 7 条. 必经 gov-mcp 为 single governance gate.

---

## 2. 11 项建议 Triage Matrix

### ✅ Matrix A: 采纳 (6 项)

| ID | 建议 | M-tag | Track | 解决的 Y* Gap | 不侵犯 invariant 的理由 |
|---|---|---|---|---|---|
| A.1 | **FTS5 全文搜索** (sidecar 到 .ystar_memory.db) | M-1 身份 + M-2b 防遗忘 | **Phase 0 新 Track 7** | 我们有 6D 语义图 (brain.db) 但无文本 fuzzy. 补上**双索引** | FTS5 只读, 不写 CIEU. 不绕 check() |
| A.2 | **5 条精确学习触发** (>5 工具/self-correct/user-correct/非显性有效) | M-2b + M-1 | **Phase 0 新 Track 8** | idle_learning.py 时间粗驱动. 精准减 noise | 触发条件 only 决定"何时学习", 不改 Merkle / check(). 融入 `CZL-BRAIN-ERROR-CORRECTION-EXERCISE` (existing 白板卡, P-12 不重造) |
| A.3 | **Qdrant 向量数据库** (Docker 本地) | M-1 | **Phase 0 Track 7 (合 A.1)** | 6D brain 是图结构, 无稠密向量搜索. Qdrant 填 | Qdrant 只读 embeddings, 独立进程, 不碰 CIEU |
| A.4 | **mem0-mcp-selfhosted** (Qdrant + Ollama, 无 Neo4j) | M-1 + M-3 采 MCP 标准 | **Phase 0 Track 7 (合 A.1)** | MCP 协议 wrapper, 天然集成 gov-mcp (同 MCP 栈). Neo4j **不要** — brain.db 已有图, P-12 避重造 | 纯本地无开放端口 (claude-mem 安全问题已解). 走 gov-mcp MCP 协议 |
| A.5 | **mission-control fork dashboard** (3.7k star) | M-3 可视化 + M-2b 监控 | **Phase 2 新 Track 9** (gov-mcp ship 后) | dispatch_board 只 CLI+JSONL 无 UI | UI 层 only, 调度逻辑仍 Y* 的. 只消费 CIEU 只读. 不改 check() |
| A.6 | **agentskills.io Skill 标准化** | M-3 生态互通 | **Phase 3 新 Track 10** 远期 | 自定义 SKILL.md → 开放标准, 可被 Hermes/OpenClaw 复用 | 只改格式不改 semantics. gov-mcp 仍前置检每 Skill 调用 |

### ❌ Matrix B: 拒绝 (3 项)

| ID | 建议 | 为什么拒 |
|---|---|---|
| B.1 | **Hermes Profiles (多 agent 隔离)** | 我们 7-layer identity + WHO_I_AM × 10 + {agent}_brain.db + AGENTS.md role boundary 已更强. Hermes Profiles 只 config+memory 层. 借命名 pattern 可, 代码不抄. **P-12 不重造也不降级** |
| B.2 | **claude-mem** (37777 无认证) | 2026-02 社区审计高风险. CIEU 链 / 治理数据**绝对不能暴露**. **M-2a 红线** |
| B.3 | **hermes-workspace Web UI** | 已选 openclaw-office fork (§24). 天生连 OpenClaw gateway + launchd/WSL2 双平台. 替换成本高, 收益 0 |

### ⚠️ Matrix C: 谨慎 (需 empirical 测试先行) (2 项)

| ID | 建议 | 放哪 + 测试 gate |
|---|---|---|
| C.1 | **Hermes 全栈 `pip install hermes-agent`** | **Phase 3 candidate**. 需 staging 实测 4 条全 PASS: (1) 不碰 CIEU Merkle 链完整性 (2) 不绕 forget_guard (3) 不污染 .ystar_active_agent (4) CPU+mem 占用可接受. 4 PASS 才集成记忆层, 执行层关 |
| C.2 | **HermesHub Skill Market** | **Phase 4+**. 前置: A.6 agentskills.io 标准化完 |

---

## 3. 新 Track 集成到 Phase 0 实施单

原 Ethan 5 next action + Aiden Track 6 (Ops-Gov Info Sync) + 本 triage 2 new track:

| Track | Scope | Owner | Budget | 新/原 |
|---|---|---|---|---|
| Track A (§24.4) | WHO_I_AM COMPANY+agent split | Samantha | 20 | 原 |
| Track B (§24.5 + CZL-GOV-MCP-ACTIVATE) | gov-mcp Day 4-N + PyPI ship + API decouple | Ethan+Ryan+Leo | 25+15 | 原 critical path |
| Track C (§24.1 prototype) | master daemon + 2 test workers | Ryan+Leo | 25 | 原 |
| Track D (experiment harness) | run_phase0_experiments.py + 15 test impl | CTO+Ryan/Leo | 20 | 原 (Ethan next action #1) |
| Track E (INV-9 identity) | worker-ID resolution for master daemon | Ethan design + Leo impl | 15 | 原 (Ethan next action #2) |
| Track F (subscriber spawn bridge) | 修 claim→spawn gap | Maya + CTO review | 20 | 原 (Ethan next action #3) |
| **Track 6 (Ops-Gov Info Sync)** | 4 channel: IntentRegister + ProgressReport + RedirectCommand + CIEU subscribe | Ethan ruling + Ryan impl + Maya invariant 审 | **35** | **新 (today)** |
| **Track 7 (记忆栈)** | FTS5 sidecar + Qdrant Docker + mem0-mcp-selfhosted | Leo kernel + Ryan deploy + Ethan schema ruling | **20** | **新 (本 triage)** |
| **Track 8 (学习精准触发)** | 5 条 trigger 改 idle_learning.py + 融 CZL-BRAIN-ERROR-CORRECTION-EXERCISE | Leo + Maya | **10** | **新 (本 triage)** |

Phase 2 Track 9 (mission-control fork) 和 Phase 3 Track 10 (Skill 标准化) 不算 Phase 0 scope.

**Phase 0 完成度重估**: 加 Track 6+7+8 scope ~65 tool_uses, 但全部**填现有 M-1/M-2a/M-2b 硬 gap**, 不是 scope creep. Phase 1 Gate 升级加 4 个 smoke test: FTS5 retrieval + Qdrant embedding match + 5-trigger 触发实测 + mem0-mcp MCP 协议握手.

---

## 4. Hermes 学习循环 5 触发条件 (A.2 细节)

顾问原话整理:
1. 工具被调用 **> 5 次** (同一 session 同类 tool)
2. Agent **自己犯错后 self-correct** (CIEU 先 WARN 后 RESOLVED)
3. 被**用户 / Board 纠正** (Board catch event)
4. 走了一条**不明显但有效的路径** (新 edge 在 brain.db 加 + 后续被 activate)
5. 本 triage 新加: **stream timeout 后 retry 成功的 pattern** (本 session 实证: scope-split + progressive checkpoint 有效, 是典型的 "不明显但有效路径")

满足任意 1 条 → 自动把本次执行 **提炼为 Skill 文档** (标准格式 per A.6 agentskills.io, 或暂时我们自定义 SKILL.md 格式) 写到 `knowledge/{agent}/skills/`.

---

## 5. Ethan + Maya 独立审请求

### Ethan (技术审) 要回答:

1. Qdrant Docker 占用 M4 Pro 24GB 多少 RAM 典型? (Gemma 12B 已 9.6GB, 余 14.4GB 够吗?)
2. mem0-mcp-selfhosted 的 MCP tool 和 gov-mcp 的 8 tools 会不会 namespace 冲突?
3. FTS5 加到 .ystar_memory.db 还是独立 DB? 索引大小估?
4. 5 条学习触发写进 `CZL-BRAIN-ERROR-CORRECTION-EXERCISE` 合理还是另开?
5. mission-control fork 后 Track 9 具体 scope (只抄 dashboard UI 还是抄 adapter?)

### Maya (治理 invariant 审) 要回答:

1. FTS5 读/写进 CIEU 审计吗? 外部工具读 .ystar_memory.db **也必产 CIEU read event**?
2. Qdrant embedding 是否可能成 covert channel (绕 CIEU)? 需要 add forget_guard rule 限制 embedding 写?
3. 5 触发条件实现时, 每触发必 CIEU emit `LEARNING_TRIGGER_FIRED` + 包含 trigger id?
4. agentskills.io 格式 Skill 调用前, 是否经 forget_guard 同现有 Skill 一样路径?
5. Hermes 候选 (C.1) staging 测试时, 有没有 "行为等价" 测试框架 (同一 task Y* vs Hermes 比较行为差)?

两路**独立**写审, 不看对方. CEO 收齐后 cross-compare 合并成 triage v0.2.

---

## 6. Open Questions for Board

1. **Track 7 里 Neo4j 明确不采** (P-12 避重造). 但如果 Ethan 审时认为 aiden_brain.db 图功能**不够用**某场景, Neo4j 能否升级为"Phase 3 candidate"?
2. **mission-control fork (Track 9)** 名字撞 Y* CEO "Mission Control" 概念. 实施时是 fork 改名 "Y* Command Center" 还是 keep "mission-control" 承认撞名?
3. **Hermes 全栈集成 (C.1)** 4 条 gate 谁定? Ethan 是 technical arch, Maya 是 governance, Board 是战略. 建议: Ethan+Maya 联审定 gate 阈值, Board 批准
4. **agentskills.io 标准化 (A.6)** 生态参与度: 只出自己 skill 到开源社区, 还是主动贡献 governance-aware 扩展?

---

## 7. 与 M Triangle + WORK_METHODOLOGY 对齐 check

**M Triangle 三问**:
1. 推进哪几面? A.1-A.6 全推进 M-1 (记忆/身份持续) 或 M-3 (生态/产品). B/C 被拒绝或延后.
2. 削弱哪面? **7 核心 invariant 无一被削弱** (见 Section 1).
3. 三角平衡? ✅ 6 采纳项填 M-1/M-3 gap, M-2a/M-2b 靠 gov-mcp 单一 gate 保持.

**WORK_METHODOLOGY 14 原则 check**:
- P-1 对齐 M Triangle ✅ 每条建议都有 M-tag
- P-3 反事实推导 ✅ 拒绝项都有"为什么不" 理由
- P-4 真实测试 ⚠️ **尚未实测**, 这是 initial triage, 实测 gate 在 Ethan/Maya 审后
- P-6 独立验证 ✅ 要求 Ethan+Maya 双盲审, 不信 CEO 单源
- P-12 先查后造 ✅ A.3 拒 Neo4j 就是因为我们已有图
- P-13 8-cascade ⚠️ 每 Track 加入前走 8-cascade (charter / registry / boot / dispatch / hook / CIEU / FG scope / pre-auth)
- P-14 诚实 ✅ 标"initial assessment 等实测"

---

## 8. 一句话

**外网顾问分类准, 我们借记忆 + 学习触发 + 向量检索 (6 项采纳), 不借身份 Profiles + UI 工具 + 可疑 claude-mem (3 项拒绝), 谨慎 Hermes 全栈 + 市场 (2 项延测). 采纳的 6 项全不侵 Y\*gov 治理优势, 只填 M-1 记忆 gap.**

— Aiden, 2026-04-21, 老大外网建议回复后 CEO 本线 triage. 等 Ethan 技术 + Maya 治理双盲独立审合成 v0.2.
