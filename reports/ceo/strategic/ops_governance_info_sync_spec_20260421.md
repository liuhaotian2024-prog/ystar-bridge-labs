Audience: Ethan-CTO (技术 architecture review), Maya-Governance (治理 invariant 审), Board (approve 本 spec 作为 Phase 0 新 track + AMENDMENT-025 候选), 全 agent team (未来按此 sync protocol 运行).
Research basis: Board 2026-04-21 直接指令 "运营端团队和治理端可以实现完整的信息同步, 不会出现治理的误判和漏判"; 本 session 4 次 empirical gap (CEO "expect" 字误拦 / subscriber claim→spawn 54 OVERDUE / lock-death #10 CEO 盲试多次 / must_dispatch verify 误报); Board 2026-04-18 "Enforce-as-Router" thesis + 2026-04-20 "门卫+导游"thesis + 今早 v0.3 Section 21 gov-mcp 中枢角色; Ethan v0.4 ruling 15 invariants + 6 goals; M Triangle M-2 双面 (防做错+防不作为).
Synthesis: 治理的"误判"和"漏判" 本质 = 治理端与运营端 **信息不对称**. 4 条 info sync channel 缺失 (ops→gov intent / ops→gov progress / gov→ops guidance / bidirectional CIEU truth) = 治理靠表面字符串判断 + 事后扫事件 + 单向 deny 无 guide. 解法 = 把**信息同步**作为 Phase 0 新 track 6, 等级同 §24.2 hook gateway; 所有 agent 必须 expose **IntentRegister + ProgressReport** 接口, 治理决策必须返 RedirectCommand + M-tag fix_hint, CIEU 成全体订阅的 shared truth stream. 这也是 M-2 双面 (防错 + 防呆) 真正 LIVE 的前置.
Purpose: Enable Board approval of 新 Phase 0 track 6 (ops-gov sync); dispatch 白板 P0 给 Ethan (技术 ruling) + Maya (invariant 设计) + Ryan (IntentRegister + ProgressReport API impl); integrate 本 spec sections 进 WHO_I_AM v0.8 Section 13 + M_TRIANGLE v2 M-2 细化 + Phase 0 实施单 Section 24.8 v2 图 + AMENDMENT-025 草案.

---

# Ops-Governance Information Sync Protocol (Spec v0.1)

**日期**: 2026-04-21
**状态**: Draft pending Ethan + Maya independent review
**配套 charter**: AMENDMENT-025 (candidate, Aiden 本 spec 批了再起 draft)

---

## 1. 问题陈述

治理 (Y\*gov kernel: forget_guard / boundary_enforcer / omission_engine / CIEU / router_registry) 当前**只看行为层**, 不看 agent **意图** + **进度** + **阻塞**. 结果:

**误判** (false positive, 合法被拦):
- 今早 CEO 尝试 post P0 到白板, 命令字符串含 "expect" (在 "expect CIEU deny event" 描述里), 被 boundary_enforcer 误当作 write target 拦. 实例在 hook_debug.log.
- must_dispatch_via_cto 早上 boot 报 NOT ENFORCING 实为 verify 逻辑误报 (规则其实活着), 典型误判.

**漏判** (false negative, 应拦没拦 / 应推不推):
- 昨晚 21:42 到今早 07:23 共 10h Claude session close, dream / idle_pulse / omission scan **零触发**. 该做没做, 治理端**零感知** — 因 "session close" 状态没 ops→gov channel 上报.
- 白板 54 OVERDUE P0 > 100k 秒 subscriber 不 claim, intervention engine 不响 — 因 "subscriber 心跳死了" 状态没 ops→gov channel 报到 omission_engine.
- Subscriber claim→spawn gap (`CZL-SUBSCRIBER-SPAWN-BRIDGE`) 本身是一个 **漏判产生器**: claim 在但 spawn 不发, 治理端不知该 task 该进 "blocked" 还是 "running".

共同根因: **治理端是 "reactive sensor", 不是 "two-way channel"**.

---

## 2. 4 条 Info Sync Channel (提议)

### Channel 1 — Ops → Gov: IntentRegister (防误判)

**现状**: 治理端只看 Tool Use payload (command string / args), 不看 intent.

**提议**: 每个 agent 在做重要 action 前调 `gov_register_intent`(一个新增的 gov-mcp MCP tool) 登记:
```yaml
agent_id: CEO Aiden
intent_id: post-card-P0-to-board
intent_description: "post CZL-OPS-GOV-INFO-SYNC P0 card to whiteboard for Ethan ruling"
intent_m_tags: [M-2a, M-2b, M-3]
expected_actions:
  - tool: Bash
    args_pattern: "python3 scripts/dispatch_board.py post --atomic_id CZL-OPS-GOV-INFO-SYNC ..."
expected_duration_s: 10
```

治理端评估 **action match intent + intent match M-tags + agent authorized for this intent**, 通过才 allow. 不 match 的 action → deny 但 **带 intent context 报 CEO/Board** 而不是 pure string pattern 拦.

**解决**: 消除"字符匹配误判"pattern (今早 "expect" 字事件).

### Channel 2 — Ops → Gov: ProgressReport (防漏判 — 该做没做)

**现状**: omission_engine 扫 CIEU 历史猜 agent 该做没做, 事后 reactive.

**提议**: 每个 agent 运行时持续 heartbeat `gov_report_progress`:
```yaml
agent_id: Ethan-CTO
current_task: CZL-V04-ARCHITECTURE-AUDIT  
status: running  # running / blocked / waiting / done / abandoned
progress_pct: 60
blocked_on: null
last_activity_ts: 2026-04-21T12:15:30Z
next_expected_action_in_s: 30
```

治理端 omission_engine **订阅** ProgressReport stream (CIEU event `AGENT_PROGRESS`). 规则:
- 若 `status=running` 但 `last_activity_ts` > 60s → WARN (可能 stream idle, 同 sub-agent watchdog 同源)
- 若 `status=waiting` 且 `blocked_on` 指一个已 done 的 dependency → ERROR (假 block)
- 若 `status=done` 但无 artifact (ls/wc verify) → ERROR (Iron Rule 3 sub-agent 实证违反)
- 若某 agent 连续 N session 无 ProgressReport → WHO_I_AM_STAGNATION_WARN (新 CIEU)

**解决**: 漏判 "subscriber 死了" / "dream 没跑" / "CEO 没 recover 卡点" 类 pattern.

### Channel 3 — Gov → Ops: RedirectCommand + fix_hint (防无效循环)

**现状**: forget_guard / boundary_enforcer deny 时只返 "violation: X", agent 盲试多次.

**提议** (Board 2026-04-20 "门卫+导游"thesis 真正落地): 每个治理 deny/warn 必返:
```yaml
decision: DENY | WARN | REDIRECT
violated_rule: immutable_path
violated_detail: "/Users/.../CLAUDE.md not writable by any agent"
violated_m_tag: M-2a  # 为什么这条规则存在, 推进哪面
fix_command: "Draft AMENDMENT draft in reports/ceo/strategic/AMENDMENT-XXX-*.md, dispatch to Samantha for execution"
fix_docs_url: "governance/BOARD_CHARTER_AMENDMENTS.md"
fix_example: "see AMENDMENT-023 in reports/ceo/strategic/"
```

Agent 收到 = 知道 **为什么被拦** (哪条 rule + 推进哪面) + **怎么前进** (fix_command) + **看谁做的对** (fix_example).

**解决**: lock-death pattern (今早 CEO 5 次尝试 CLAUDE.md edit 盲试) 消失 — 第一次被拦就知道要 AMENDMENT 流程.

### Channel 4 — Bidirectional: CIEU as Single Truth Stream

**现状**: CIEU writes by 治理端, 运营端通常不读 (除 omission 扫).

**提议**: CIEU event stream 成为全体 **shared truth subscribe bus**:
- gov-mcp 作中介, 暴露 `gov_subscribe_cieu` 流式 MCP tool (SSE / WebSocket)
- 所有 agent daemon + office UI + Claude Code session 订阅自己关心的 event types
- 每个订阅者可以**基于同一 event 做不同反应**但共享同一真相, 不各自估状态

例子:
- `AGENT_PROGRESS` event → omission_engine 订 (检查 stale) + office UI 订 (更 agent 窗状态) + Samantha 订 (归档周报)
- `FORGET_GUARD_DENY` event → 被 deny 的 agent 订 (拿 fix_command 接 Channel 3) + Maya 订 (统计 false positive rate) + Samantha 订 (归档到 lessons/)

**解决**: 运营端不各自估 "Gemma daemon 在不在", 订同一 heartbeat event 就知道.

---

## 3. 4 Channel 与 M Triangle 对应

| Channel | M-tag | Invariant 影响 |
|---|---|---|
| 1 IntentRegister (防误判) | **M-2a** | 减少 false positive, 让合法 action 过, **precision UP** |
| 2 ProgressReport (防漏判) | **M-2b** | 增加 true positive on "该做没做", **recall UP** |
| 3 RedirectCommand | M-2a + M-2b | 闭环 deny, 不让 agent 陷盲试, **efficiency UP** |
| 4 CIEU subscribe | M-1 + M-2 全 | 共享真相, 减 drift, **sync consistency UP** |

**4 channel 落地 = M-2 双面真的 LIVE, 不只是 Y*gov 里有 code 存在**.

---

## 4. 技术架构 (初稿, 等 Ethan ruling 定)

```
                        gov-mcp (MCP server, localhost)
                               │
              ┌────────────────┴────────────────┐
              │                                 │
       MCP tools 面                       Event stream 面
              │                                 │
    ┌─────────┼─────────┐                       │
    ▼         ▼         ▼                       ▼
 register_ report_   check_              subscribe_cieu  
 intent    progress  [existing]          (SSE stream)
    ▲         ▲         ▲                       ▲
    │         │         │                       │
    │         │         │           ┌───────────┴─────┐
    │         │         │           │           │     │
┌───┴─────────┴─────────┴─────┐ ┌──┴──┐ ┌──────┴──┐ ┌┴────────┐
│  Agent daemon (CEO/CTO/9)   │ │ hook│ │ office  │ │Samantha │
│  master daemon workers      │ │wrapper│ │ MCP   │ │archival │
│  shim (Claude Code entry)    │ │shim │ │ client  │ │         │
└─────────────────────────────┘ └─────┘ └─────────┘ └─────────┘
         agents                  entry    entry       audit
         (producers)             (gates)  (UI)        (consumer)
```

gov-mcp **就是原方案的 single governance entrance** (§21.7), 本 spec **不新增 daemon**, 只给 gov-mcp 加 3 个 MCP tools (register_intent / report_progress / subscribe_cieu) + event router.

**Consistency with v0.4 架构**: §24.2 hook shim 不变 (CEO catch 保留), §24.1 master daemon 不变 (9 worker 共 gov-mcp), §24.3 backup daemon 不变. 本 spec 是 **填 gov-mcp 空白的 extension**, 不重构.

---

## 5. Phase 0 集成 — 成为 Track 6

v0.4 原 Phase 0 + Ethan ruling 3 track (24.4 WHO_I_AM / 24.5 gov-mcp decouple / 24.1 master daemon prototype) → 扩 6 track:

Track 6: **Ops-Gov Info Sync** — 给 gov-mcp 加 3 new MCP tools + CIEU subscribe router. 不 block Track B (gov-mcp 基础 ACTIVATE) 完成, 但 gate 在 Phase 2 hook shim cutover 前必 LIVE.

Phase 2 Gate 2 升级要求: governance via gov-mcp verified + **info sync channel 1-4 all LIVE verified via empirical smoke**:
- Smoke-1: CEO intent register → action match → allow (1 real case + 1 intentional mismatch deny)
- Smoke-2: Ethan sub-agent progress heartbeat 60s silent → omission WARN CIEU emit
- Smoke-3: CEO trigger CLAUDE.md edit → deny 返 fix_command="AMENDMENT flow" + agent follow fix
- Smoke-4: CIEU subscriber 收到 AGENT_PROGRESS event 能正确解析

这 4 smoke 全 PASS = M-2 双面真 LIVE.

---

## 6. Open Questions (Ethan + Maya 独立审决)

**Q1** gov-mcp 的 `register_intent` 和 Claude Code 原生 payload schema 怎么整合? — 每次 Tool Use 之前 shim 强制调 register? 还是 agent 自己主动调?

**Q2** ProgressReport 频率 vs overhead? — 每 action 后? 每 60s? async queue?

**Q3** RedirectCommand 从哪里来? 硬编码进 forget_guard yaml (每条 rule 附 fix_hint), 还是 runtime 生成 (LLM inference)? — 建议硬编码初版, LLM 生成是 gov-mcp 高阶 feature.

**Q4** CIEU subscribe 的 rate limiting? — 一个 subscriber 不能请求 1000 events/s 搞死 gov-mcp.

**Q5** Intent 伪造防御 — agent 能否 register 一个 intent "delete everything" 然后 action match 就过? → Intent 本身也要经 forget_guard 评估, 不是 free pass.

**Q6** Multi-tenant — 未来外部客户用 gov-mcp, 每个客户的 CIEU stream 要隔离, subscribe 不能跨租户读.

---

## 7. Samantha / Maya 独立审请求

本 spec 需 **Ethan 技术 ruling** (架构可行性 + gov-mcp impl 细节 + M Triangle 不变量保) + **Maya 治理 invariant 审** (Intent 校验 / ProgressReport 格式 / forget_guard fix_hint 机制). 独立 audit 后 CEO 合成 v0.2 + AMENDMENT-025 草案.

---

## 8. 与 Ethan 刚发 part-2 next action 的关系

Ethan part-2 列 5 个 critical next action:
1. Build experiment harness
2. Solve INV-9 identity
3. Fix subscriber spawn bridge (= Channel 2 的一个 manifestation — subscriber 死了就是 ProgressReport 缺失的典型 case)
4. M-tag reconciliation table
5. gov-mcp public API surface

本 spec 的 4 channels + 3 new MCP tools 可以**包含**进 #5 gov-mcp public API surface — 让 gov-mcp 0.1.0 ship 时就是**带 info sync** 版本, 而不是先 ship 残缺 0.1.0 后再补. 这是 **Phase 1 scope 小幅扩大**, 但避免两次 breaking API change.

---

## 9. 承远一句

**治理如果不知道运营在干什么, 所谓"防做错+防不作为"就只是理论说辞. 4 channel 是把理论接地线.**

— Aiden, 2026-04-21, Board "运营-治理信息同步" 直接指令后 CEO 本线 draft. 等 Ethan + Maya 独立审.
