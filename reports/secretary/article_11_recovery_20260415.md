# Article 11 / 第十一条 Recovery Audit [L3 TESTED]

**Auditor**: Samantha Lin (Secretary) | **Date**: 2026-04-15 | **Scope**: charter-immutable drift check

## (a) Authoritative Original — FOUND

**Source**: `governance/WORKING_STYLE.md` lines 783-884
**Origin commit**: `d4a8181a` — `gov(AUTONOMOUS-MISSION): ETHICS.md + 第十一条 + permission type + role prohibitions` (2026-04-10, Board directive)

**Title**: 第十一条：Autonomous Mission 方法论
**Structure** (full 4-phase, 7-layer methodology):
- **Phase 1 认知建构** — 7 层前置: 0 意义 / 1 目标澄清 / 2 假设显式化 / 3 理论校准 / 4 Benchmark / 5 相关性过滤 / 6 案例提炼 / 7 能力边界 → 输出"认知框架报告"Board 审阅
- **Phase 2 执行落地** — 第 8 层方案设计 + 第 9 层 5 级成熟度门控 (L0→L5, AMENDMENT-019 加)
- **Phase 3 观察** — 48h 定量/定性/假设验证（证伪是最重要信息）
- **Phase 4 迭代** — 新数据回灌认知框架，螺旋上升

第十条 (Board GOV-010 Phase 4) 同文件 lines 719-777 — 未被动，保持原样。

## (b) Live Drift Diff

| 文件 | Live 版本 | Diff vs 原版 |
|---|---|---|
| `CLAUDE.md` | 无 第十一条明文，仅 memory mirror 有 "Article 11 framing = 后台 N 路并列" | 丢 4 Phase / 7 层 / 反事实 / 伦理检查 全部 |
| `.claude/agents/*.md` (含本 secretary.md) | "Article 11 (执行结构层) — 必并列多路 sub-agent + 本线同推" | 缩为 1 句 slogan，只留"多线并行"维度 |
| `AGENTS.md` Iron Rule 1.6 | 同上 slogan 化 | 同上 |
| `knowledge/shared/unified_work_protocol_20260415.md` | "Article 11 (执行结构层) 中等以上复杂 task 必并列多路" | 同 |

**Board 指控成立**：live 所有 agent-facing 注入只剩"多线并行"一维，**前置认知 7 层 / 反事实推理 / 观察迭代 / 伦理检查 / 白黑名单全维度扫 全部不见**。

## (c) Charter 授权审计

- **AMENDMENT-019** (commit `6d0cad50`, Board L3 batch-approved 2026-04-13) 合法**扩展** Phase 2 成熟度门控 — 未删任何原内容，授权完整 ✅
- **2026-04-15 Iron Rule 1.6 / Unified Protocol** 将 Article 11 **缩略为 slogan** 并扩散到 10 个 agent 文件 — 未见 AMENDMENT 号，`governance/BOARD_CHARTER_AMENDMENTS.md` **空文件**，无对应 L3 批准记录 ⚠️ **IMMUTABLE 违规**
- 原条款属 Board directive 2026-04-10，按 AMENDMENT-003 immutable override 规则，任何 condense / 语义收窄须 L3 明批，目前缺失

**结论**: 漂移 = 非授权语义压缩。原文未被删，只是被遗忘/绕开。

## (d) Recovery Path 建议

1. **不改 WORKING_STYLE.md 原文** — 权威版完好，无需恢复
2. **CEO (Aiden) 决策** 是否走 break_glass 补 AMENDMENT 追认 slogan 化，或回滚 unified_protocol 的 Article 11 段改为"参见 WORKING_STYLE.md 第十一条完整 4 阶段方法论，此处仅列执行结构层摘要"
3. **Secretary 后续**：CLAUDE.md / agent 文件 / unified_protocol 加 canonical 回链指针；每次引用 Article 11 强制附完整 4-phase/7-layer 结构或全文 pointer
4. **Ticket**: `IMMUTABLE-DRIFT-20260415-001` — Article 11 slogan 化扩散无 charter 授权，需 Board L3 裁决

## Source Evidence

- `governance/WORKING_STYLE.md:783-884` (authoritative)
- commit `d4a8181a` (creation), `6d0cad50` (AMENDMENT-019 legitimate extension)
- `governance/BOARD_CHARTER_AMENDMENTS.md` (empty — corroborates no L3 authorization for 2026-04-15 condensation)
- `knowledge/shared/unified_work_protocol_20260415.md:19-20` (drifted slogan source)

---

**Rt+1 = 0 验证**: 所有 claim tool_result 支撑 (grep / git show / Read 实测), commit hash 可 verify, 无 prose-claim. L3 TESTED.
