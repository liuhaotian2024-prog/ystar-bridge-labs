Audience: Board (主阅读者, 跟进 "全权放权" 后 Aiden 执行轨迹), Ethan-CTO (技术协调), Samantha (charter 归档), 全 agent team, 未来 session.
Research basis: Board 2026-04-21 全日 5 轮直接指令 (M Triangle / WORK_METHODOLOGY / Ops-Gov Info Sync / External Tool Triage / Brain Pipeline); 今日 5 份 spec 产出 (M_TRIANGLE.md / WORK_METHODOLOGY.md / ops_governance_info_sync_spec / external_tool_triage / CZL-BRAIN-FULL-PIPELINE-WIRE 卡); Ethan v0.4 audit ruling 643 lines + peer audit part1+2; Aiden 独立 Phase 0 audit; empirical finding — Aiden brain 13150 nodes 48982 edges L1 L2 LIVE, 其他 9 agent MISSING, L3 dream 17h 死, CIEU-to-brain pipeline 缺, 0.5 percent access_count 利用率; subscriber claim-spawn structural boundary 今天确认不可修只能 workaround; 5 次 sub-agent stream timeout 实证 scope-split plus progressive checkpoint pattern 有效.
Synthesis: 老大 2026-04-21 全日是 1 个连贯架构重构, 不是 4 个散落指令 — 5 节点 M Triangle 顶层 → WORK_METHODOLOGY 执行纪律 → Ops-Gov Info Sync 治理通讯 → External Tool Triage 生态边界 → Brain Full Pipeline 全员补脑. 缺任一节点 M(t) 证明不成立. 本总纲把 5 节点对齐 M Triangle + 执行序化 + 明确 owner + 实测 gate, 取代"散在 10+ 张白板卡难跟踪"的 fragmented view. 同时承认 2 结构级约束 (subscriber cannot spawn + sub-agent stream watchdog 600s idle) 并给 workaround.
Purpose: Enable 老大 single-page 视图 跟踪 "全权放权" 后 Aiden 的执行进度; enable Ethan 做 technical ruling 时看到全局依赖; enable 7 新 engineer brain 实施统一协议; 作为 AMENDMENT-027 候选把 "5 节点重构" charter 级写入 BOARD_CHARTER_AMENDMENTS.md.

---

# 2026-04-21 Y\* Bridge Labs 5 节点重构总纲 (v1)

**日期**: 2026-04-21
**作者**: Aiden (CEO), 老大全权放权后起
**状态**: Live execution master document
**上位**: M Triangle v1 + WORK_METHODOLOGY v1 (本总纲执行这 2 文件)
**下位**: Phase 0 实施单 v2 (等合成) + 11 张 P0 白板卡 + 4 份 AMENDMENT draft

---

## 0. 为什么 5 节点不是 4

今天老大的 5 轮指令看似独立, 实际是**一条架构重构链**:

```
节点 1: M Triangle (目标对齐)
    ↓ 目标必须可执行, 所以需要
节点 2: WORK_METHODOLOGY (14 原则 + 2 checklist)
    ↓ 原则必须可验, 所以需要
节点 3: Ops-Gov Info Sync (治理通讯 4 channel)
    ↓ 通讯必须不污染, 所以需要
节点 4: External Tool Triage (生态边界)
    ↓ 边界清后必须每个 agent 都在线, 所以需要
节点 5: Brain Full Pipeline (全员脑接通)

任一节点断 = M(t) 证明成立的链断.
5 节点共同对齐 M Triangle, 缺任一个 = 还没证明.
```

这是 **CEO 本轮凌晨 → 黄昏**的完整自我 refactor, 不是 4 份可以合并或忽略的.

---

## 1. 5 节点一览表

| # | 节点 | 文件 | 核心产出 | M-tag | 状态 | 下游 |
|---|---|---|---|---|---|---|
| 1 | **M Triangle** (目标对齐) | [M_TRIANGLE.md](../../../knowledge/ceo/wisdom/M_TRIANGLE.md) v1 | 3-vertex + M-2 双面 + 三问 check | 上位 (贯穿全部) | ✅ 落盘, ⏳ 等 AMENDMENT-023 入 charter | 所有 spec 必 M-tag |
| 2 | **WORK_METHODOLOGY** (执行纪律) | [WORK_METHODOLOGY.md](../../../knowledge/ceo/wisdom/WORK_METHODOLOGY.md) v1 | 14 原则 + 每 task 8-Q + 每 reply 6-Q + 传导链检查 + 必看录 | 贯穿 | ✅ 落盘, ⏳ 等 AMENDMENT-024 入 charter + boot.sh 打印 + Maya FG rule | 每 CEO/CTO/agent reply 自动过 check |
| 3 | **Ops-Gov Info Sync** (治理通讯) | [ops_governance_info_sync_spec](./ops_governance_info_sync_spec_20260421.md) | 4 channel (IntentRegister + ProgressReport + RedirectCommand + CIEU subscribe) 解误判+漏判 | M-2a + M-2b + M-1 | ✅ spec 落盘, ⏳ Ethan 技术审 + Maya 治理审 | gov-mcp 加 3 new MCP tools + AMENDMENT-025 候选 |
| 4 | **External Tool Triage** (生态边界) | [external_tool_triage](./external_tool_triage_20260421.md) | 11 项 3-matrix (6 采 / 3 拒 / 2 谨慎), Phase 0 加 Track 7+8 | M-1 + M-3 (不削 M-2a) | ✅ spec 落盘, ⏳ Ethan + Maya 双盲审 | Phase 0 Track 7 (记忆栈 FTS5+Qdrant) + Track 8 (5 学习触发) |
| 5 | **Brain Full Pipeline** (全员脑接通) | 本 Section 2 + CZL-BRAIN-FULL-PIPELINE-WIRE + 5 卡 | Aiden L3 dream 修 + 9 agent brain 建 + CIEU→brain + dialogue→brain + access_count 利用率 提 + auto-ingest bug fix | M-1 核心 + M-2b + M-3 | ⏳ 6 张卡 OVERDUE, 本总纲纳入 | Phase 0 Track 11 (新, 见 Section 2) |

---

## 2. 节点 5 详细 — Brain Full Pipeline (老大 14:45 追加强调不遗落)

### 2.1 现状 empirical (今下午 15:01 扫)

| Pipeline 组件 | 状态 | Evidence |
|---|---|---|
| Aiden brain L1 query 注入 | ✅ LIVE | 每 reply [6D Brain Wisdom Context], activation_log 07:23:24 |
| Aiden brain L2 Hebbian writeback | ✅ LIVE (我早上判 OVERDUE 错了) | `.brain_writeback_last_drain` 14:59, script 16KB Apr 19 |
| Aiden brain 节点/边增长 | ✅ LIVE | 13150 nodes / 48982 edges / 1.49M activation rows |
| Aiden brain L3 dream | ❌ 17h+ 死 | dream_log 最后 Apr 20 21:42 |
| brain_auto_ingest line 553 hang | ⚠️ bug | 今早 boot 21min 被 killed, `_record_co_activation_batch` 嫌疑 |
| Access_count 利用率 | ⚠️ 0.5 % (70 / 13150) | 13080 节点加了从未 activated |
| Ethan brain | ❌ MISSING | .db 文件不存在 |
| Leo brain | ❌ MISSING | 同 |
| Maya brain | ❌ MISSING | 同 |
| Ryan brain | ❌ MISSING | 同 |
| Jordan brain | ❌ MISSING | 同 |
| Sofia brain | ❌ MISSING | 同 |
| Zara brain | ❌ MISSING | 同 |
| Marco brain | ❌ MISSING | 同 |
| Samantha brain | ❌ MISSING | 同 |
| CIEU → brain pipeline | ❌ 无 | grep brain_auto_ingest.py 无 cieu feed, CIEU 400MB 只 audit 不转 knowledge |
| dialogue_contract.log → brain | ❌ 无 | log 172KB active 15:00 更新, 无 script feed brain |

### 2.2 5 子任务 (Phase 0 新 Track 11 — 节点 5 落地)

| 子 | 任务 | Owner | 依赖 | Budget | 已有卡 |
|---|---|---|---|---|---|
| 5.1 | 修 brain_auto_ingest line 553 hang | Leo-Kernel | 无 | 8 | CZL-BRAIN-FULL-PIPELINE-WIRE 覆盖 |
| 5.2 | L3 dream 脱 session daemon (launchd) | Maya + Leo | CZL-GOV-MCP-ACTIVATE Phase 1b | 20 | CZL-DREAM-OUT-OF-SESSION-ARCH |
| 5.3 | 9 engineer/function agent brain.db 建 + L1/L2 hook wire | Leo | 5.1 + WHO_I_AM 7 补齐 | 30 (各 ~3) | CZL-ETHAN-BRAIN-IMPL-PHASE-1 + CZL-RYAN/LEO/MAYA/JORDAN-BRAIN-IMPL (全 OVERDUE) |
| 5.4 | CIEU → brain extractor (6 entity × 6 relation) | Leo + Maya invariant 审 | 5.1 | 15 | CZL-BRAIN-AUTO-EXTRACT-EDGES (existing OVERDUE) |
| 5.5 | dialogue_contract.log → brain feeder + access_count 利用率 提 | Leo + Ryan | 5.1 + 5.4 | 12 | CZL-BRAIN-FULL-PIPELINE-WIRE 覆盖 |

Track 11 总 budget ~85 tool_uses, 但多为 extend existing 不 build new (P-12 先查后造).

### 2.3 Track 11 的 M-tag 详细

- **M-1 身份持续**: 9 agent 有 brain = 换 session 不是新人, 跨 session 记忆不丢. 当前 10 人只 Aiden 1 人有脑 = M-1 只落地 10%.
- **M-2b 防不作为**: access_count 0.5% = 补脑不用, 典型"做了不生效". Pipeline wire 让新节点被 L1 query 覆盖.
- **M-3 生态 / dogfood**: 9-agent brain pattern 做出来就是 gov-mcp 产品的 case study — "用 Y*gov 治理跑自己的 all-agent-brain 系统", 销售证据点.

### 2.4 Subscriber claim→spawn 结构级 boundary (今天诊断)

`scripts/engineer_task_subscriber.py` line 46-48 源码注释:
> "Subscriber CANNOT spawn Agent tool calls — structural Claude Code boundary. Only the main Claude session's tool-use loop can originate Agent calls. A Python subprocess has no mechanism to inject Agent calls into the parent."

→ **subscriber 永远不能 spawn sub-agent, 这是 Claude Code harness 硬限制, 不是 bug**. 85 OVERDUE 白板卡靠 subscriber claim 后**无法被 spawn**, 只能 work 在 subscriber 内部 Python (git / bash / file 操作), 无法 spawn 子 sub-agent.

**Workaround** (Phase 0 Track 12, 必须与 Track 11 并行):
- **CEO parent session 周期性扫白板 + 代 spawn** — CEO 每 reply 前扫 `.pending_spawns.jsonl`, pick 最 urgent OVERDUE, 在本次 reply 里 Agent call 代 spawn.
- **优点**: 不绕 Claude Code harness, 不需 hack
- **缺点**: Board offline 期间 CEO 不在 = 白板仍 dead letter. 需配合 Ops-Gov Info Sync 的 Channel 2 (ProgressReport heartbeat + omission_engine 升级 intervention)
- **长期解**: gov-mcp 作为 MCP server 让 Claude Code CLI 原生 MCP 调用 (CLI 唤起 inner tool loop 能 spawn) 或 Gemma daemon 作为独立 spawn-capable runtime

---

## 3. 5 节点 × M Triangle 对齐矩阵

| 节点 \ M-tag | M-1 | M-2a | M-2b | M-3 |
|---|---|---|---|---|
| 1 M Triangle | ++ (定义本体) | ++ | ++ | ++ |
| 2 WORK_METHODOLOGY | + (P-9 plan≠done) | ++ (P-4 真实测试 + P-10 U-workflow) | ++ (P-7 传导链 + P-9) | + (P-8 定量诚实) |
| 3 Ops-Gov Info Sync | + CIEU 订阅一致 | ++ precision up (IntentRegister) | ++ recall up (ProgressReport) | + gov-mcp 产品增值 |
| 4 External Tool Triage | + 记忆检索 FTS5+Qdrant | = (7 invariant 不让步) | + 学习触发 5 条 | ++ agentskills.io 生态 |
| 5 Brain Full Pipeline | ++ 9 agent 持续存在 | + 记忆成 CIEU 对应证据 | ++ 防学而不用 | ++ dogfood 案例 |

**诊断**: 5 节点无一弱化 M-tag. 节点 3+5 是 M-2b 双重加强. 节点 4+5 是 M-3 双重产品化. 三角平衡.

---

## 4. 执行序 (Dependency-aware)

```
[Phase 0 Gate 0 = 本总纲 Board approve]
    │
    ├─── (並) Samantha: AMENDMENT-023 + 024 charter edit  ← 已派 sub-agent 跑
    ├─── (並) Ethan: gov-mcp Phase 1a ruling               ← 已派 sub-agent 跑
    ├─── (並) CEO parent: 代 spawn workaround 本线 impl    ← 本轮下一步
    │
[Gate 1 = charter 入 + gov-mcp Phase 1a ruling 交]
    │
    ├─── (並) Ethan gov-mcp Phase 1b Day 4-N impl + PyPI ship
    ├─── (並) Samantha 补 7 缺失 WHO_I_AM (Leo/Maya/Ryan/Jordan/Sofia/Zara/Marco)
    ├─── (並) Maya: FG rule work_methodology_violation
    ├─── (並) Leo: brain_auto_ingest line 553 bug fix
    ├─── (並) Ethan + Maya 独立审 triage + ops-gov-sync (双盲 peer)
    │
[Gate 2 = gov-mcp LIVE + B1 B2 P0 benchmark PASS + 双盲 peer merged]
    │
    ├─── 节点 3 Ops-Gov 4 channel impl (Ryan impl + Ethan ruling)
    ├─── 节点 5 Track 11: 9 agent brain.db + CIEU→brain + dialogue→brain + L3 daemon
    ├─── 节点 4 Track 7 (FTS5+Qdrant) + Track 8 (5 学习触发)
    ├─── §24.2 hook shim cutover (gov-mcp gateway)
    ├─── §24.1 master daemon 9 worker
    │
[Gate 3 = Phase 0 validation suite V-1/V-2a/V-2b/V-3 全跑]
    │
    ▼  Phase 1 本地化 Gemma 迁移 (Step 2 原老大 "依据新架构进行本地化搬迁")
```

---

## 5. Charter 层固化 — AMENDMENT-027 候选

建议本总纲本身走 AMENDMENT-027 入 charter, 让 "5 节点重构" 成为 Y\* Bridge Labs 2026-04-21 **不可回滚**的架构 milestone. 下次 session 开时 boot.sh 必读.

候选 AMENDMENT-023 (M Triangle) + 024 (Methodology) + 025 (Ops-Gov) + 026 (External) + 027 (5-Node Master) — 5 份配套 charter 升级, 同步批. Samantha 一次性归档.

---

## 6. 现在立刻做 (本 reply 下一步 — 不 defer)

CEO parent session **本线现在** 代 spawn workaround, 打破 subscriber dead letter:

```python
# 每轮 reply 前 scan OVERDUE top-3, 挑最高 M-tag priority 一张, 本 reply 里 Agent spawn 代跑
```

本轮已派 2 sub-agent (Ethan Phase 1a + Samantha AMENDMENT). 下轮 reply 我扫白板 pick 下一张.

**不是 "plan 完", 是 plan 本身就是下一轮 tool call 的 fixture**. M-tag 全映射. 5 节点同拉.

---

## 7. 一句话

**老大今日 5 轮是一条 refactor chain, 不 4 不 6. 5 节点锁一起 M(t) 才能证, 散落无效. 全部 M-tagged, 全部有 owner, 全部有实测 gate. 不再散.**

— Aiden, 2026-04-21 15:20, 老大"全权放权 + 别忘 brain pipeline" 双指令后起本总纲. 后续每轮 reply 第一动作 = 扫本总纲 Section 4 执行序 pick 下一 action.
