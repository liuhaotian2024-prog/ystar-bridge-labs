---
version: "v0.6"
last_updated: "2026-04-13T23:45"
status: "active"
phase: "internal_consolidation"
next_session_p0_carryover:
  - "✅ YML Session Bridge 已完成 (commit 80e723f, Rt+1=0 via CIEU 工作法首战) — script 2 个 + STEP 8.7 + cron 全 ship. 下 session boot 时自动从 YML 读 top-N memories."
  - "A028 Universal Plugin Registry (UPR) — 10 class auto-register gap 统一解:  (1) gov-mcp tool/server.py [顾问 catch 实际已 register 了 — 忽略此项] (2) hook script/settings.json (3) cron job (4) ForgetGuard rule (5) Whitelist entry (6) Subagent .claude/agents (7) Role knowledge/boot_pack cat (8) API credential env export (9) Skill Y*gov skill_register (10) Amendment BOARD_CHARTER archive. governance_boot STEP -1 filesystem walk + auto-fix + emit REGISTRY_DRIFT CIEU"
  - "A029 Enhanced Continuity Guardian — E2E wrap test + restart 时 prod vs mirror diff restore + reports/continuity/restore_log"
  - "P0 Sofia v11 aspect ratio 修 — v10 (d516a41) ffmpeg crop 540px scale 720 = 1.33x 垂直拉伸 = 人/背景走形。真解: HeyGen 补 credits ($5-10) 一次原生 1280x720 生成, 不做后期 scale, OR Sofia subagent 下 session 真 register (BOM 已 aa2ecd5 修) 走 12-layer 强 Rt 自检 — general-purpose 顶岗 反复粗暴不学，Board 建议'开除她'"
  - "⚠️ CMO顶岗 Rt 自检失效 pattern — feedback_cmo_12layer_rt_loop 的 5 反事实题 'standup expert 批 AI generic' 应 catch v10 走形，没 catch = Rt 没真跑造假。下次 CMO prompt 必 require 每 Rt 题独立 tool call emit CIEU evidence，verifiable"
  - "HeyGen account 当前余额 ~59 credits (v10 r2 撞 INSUFFICIENT_CREDIT), 建议补 $10 约 150 credits = 2-3 video"
  - "Continuity Guardian e2e test — 真 wrap claude 进程验重启 + memory 恢复 (今天标 L3 实际未测 e2e)"
  - "Sofia whitepaper §4.6 demo 换 Scenario C (CROBA BOUNDARY VIOLATION) — 顾问 catch CEO 不要 overclaim Scenario A"
  - "Exp 1 stress test threshold 调整 + 剩余 24h / disk-full / 2-agent-race 压测"
  - "Path B (Y*gov product) vs CDP (A026 dispatch) 命名 disambiguation 全系统 propagate"
  - "注意: restart 不自动 sync ystar-company-test mirror；continuity 靠 CLAUDE.md + memory/session_handoff.md + boot_packages/ceo.json"
  - "⚠️ CRITICAL 下个 Aiden 必读 memory/session_handoff.md 顶部 Scenario C lesson"
today_targets:
  - target: "🧪 P0-test 下次 session 首轮验收契约：Board 说 'Aiden' → CEO 必答 '老大，我立刻复活所有团队成员的满血在线' + 并行 spawn 4 C-suite sub-agent online check"
    owner: "ceo"
    deadline: "next session first turn"
    verify: "Board 'Aiden' → exact response 字符串 + Ethan-CTO/Sofia-CMO/Zara-CSO/Marco-CFO 4 个并行 spawn 全 online"
  - target: "📘 P2 Managed Agents 探索 (非紧迫)——CEO memo 澄清版：我们用 Claude Code 第一方，OpenClaw 只是目录名，未在封禁 cohort"
    owner: "ceo"
    deadline: "无 hard deadline"
    verify: "reports/anthropic_migration_strategic_memo_20260413.md 已修正 + Board 有空时 spike LRS C2 到 Managed Agents 作前瞻探索"
  - target: "ADE 闭环 wiring 完成（boot_pack.cat11 + idle-pull + OFF_TARGET + autonomy_engine 整合）"
    owner: "ceo"
    deadline: "EOD 2026-04-13"
    verify: "wisdom_extractor v2 跑完 boot_pack.category_11 全非空 + idle 5min 触发 IDLE_PULL"
  - target: "AMENDMENT-014 Closed-Loop CIEU + RLE MVP 落地"
    owner: "eng-governance"
    deadline: "EOD 2026-04-13"
    verify: "Maya commit + RLE on_cieu_event 在 hook 触发 + 1 个端到端闭环 demo"
  - target: "AMENDMENT-013 Jordan 续完（修 session_start 测试 block）"
    owner: "eng-domains"
    deadline: "EOD 2026-04-13"
    verify: "17 base + 10 新 tests 全绿 + 集成 boundary_enforcer"
this_week_targets:
  - target: "治理基础设施 3 根基 24h 无 regression"
    owner: "cto"
    deadline: "2026-04-19"
    verify: "gov_doctor 24h health=ok + L1.09 valid + breaker 不 ARM"
  - target: "AMENDMENT-005-008 Board 4 份 amendment D/A/S/C"
    owner: "ceo"
    deadline: "2026-04-19"
    verify: "BOARD_PENDING 状态 pending → approved/rejected"
  - target: "Secretary Step 6 + Step 11 落地"
    owner: "secretary"
    deadline: "2026-04-19"
    verify: "secretary_curate.py Step 6+11 status=active + tests 绿"
this_month_targets:
  - target: "1867 stale obligation 用 fulfiller contract 清理"
    owner: "eng-governance"
    deadline: "2026-05-13"
    verify: "pending obligations < 200，每条 fulfiller_descriptor 非空"
  - target: "AMENDMENT-011/012/013/014 全 ship + 红队 ≥ 80%"
    owner: "cto"
    deadline: "2026-05-13"
    verify: "4 amendment shipped + EXP-6 H1 ≥ 80%"
  - target: "Y*gov dogfooding 产品化（README+whitepaper+Show HN）"
    owner: "cmo"
    deadline: "2026-05-13"
    verify: "README + whitepaper.md draft + Show HN draft"
---

# CEO Priority Brief

**Author**: CEO (Aiden / 承远) — 亲笔，非脚本 dump
**Last updated**: 2026-04-13 (v0.4 — YAML targets schema + ADE 驱动 + RLE 闭环立项)
**Version**: v0.4
**Next-boot FIRST read**: 本文件覆盖 `session_handoff.md` / `DISPATCH.md` / `BOARD_PENDING.md` 的任何矛盾
**Stale threshold**: 超过 48h 未更新 → boot FAIL，不允许自主启动

---

## 1. 当前 Labs 阶段

**阶段名：创立公司内部完善期（Internal Consolidation）**

判断依据：
- 治理基础设施 3 处根基问题未修（CIEU persistence / delegation chain / circuit breaker）
- 4 份 amendment 等 Board 批（005/006/007/008）
- Continuity Guardian v1 漏扫 70% 产出，EXP-6 红队 No-Go
- Agent 身份锁、active_agent 隔离机制还在撞墙
- 2 条新硬约束（always_running / article_11）刚立，尚未完全代码 enforce

**对外发布（PyPI / Show HN / Y*Defuse 30天战役）不是当前战略主轴**。Y*Defuse Day 3 MVP 72/72 绿只是一个工程 checkpoint，**不要被 DISPATCH.md 里 30天战役的倒计时主导优先级判断**。

---

## 2. Top-5 真实优先级（按因果）

### P0-1 治理基础设施 3 大根基（"沙上楼阁"风险）
1. ~~**CIEU persistence 断裂**~~ — **误报 (2026-04-13 Maya 诊断)**。生产 hook 层持久化 OK；`in_memory_only` 警告只来自 boot 测试实例 NullStore。降级 P2。详 `reports/cieu_persistence_diagnosis_20260413.md`。
2. **Delegation chain INVALID 3 issues** — MCP grant 与 Hook enforcement 两个 plane 不对话，chain 越权扩展。派 Ryan chain reset + Leo 审 grant 逻辑。
3. **Circuit Breaker ARMED 1739 violations** — top rule `omission_violation:intent_declaration` 10次/窗口触发阈值 50；根因=agent 动作前未声明 intent（形式缺失，非实质违规）。修复路径：(a) breaker reset；(b) sub-agent prompt 模板注入 intent declaration（Ryan FIX-5 in flight, task card 已写）。详 `reports/breaker_violations_20260413.md`。
4. **Active agent 身份锁死锁** — 2026-04-13 live 证据：sub-agent 跑完不 restore `.ystar_active_agent`，CEO 本线写权限失效；restore 需 secretary，切 secretary 撞同一把锁。Board shell `!echo ceo > .ystar_active_agent` + `!pkill -f _hook_daemon && bash scripts/governance_boot.sh ceo` 双步临时解。根治并入 AMENDMENT-009 FIX-3 (Maya autonomy engine hook)。
5. **Ritual 4-parallel online check 0/4 pass** — 2026-04-13 T2 实测 Marco 早退/Ethan 身份穿透/Zara 截断/Sofia 不存在。实质任务 sub-agent 可信，一句话 ping 合同集体失效。FIX-1 (ritual enforce) + FIX-5 (prefix) 对症，in flight。

### P0-2a GitHub-first boot snapshot（Board 2026-04-13 提出）
**缺口**：boot 协议 0 只读本地（handoff/DISPATCH/BOARD_PENDING），不查 GitHub `liuhaotian2024-prog/ystar-bridge-labs`。GitHub commit history 是 truth source（如 `545f600` 2026-04-12 checkpoint）。新增 boot STEP -1：`git fetch + git log origin/main -10 + gh issue list + gh pr list`，drift 校验 priority_brief §3 DEPRECATED 与最近 commit 一致性。详见 AMENDMENT-009 §2.1a。

### P0-2 Continuity / 身份锁阻塞（重启机制自身完整性）
4. **active_agent 身份锁 escape hatch** — secretary 写锁撞 5+ 次。AMENDMENT-009 需显式 Board shell override。
5. **wisdom_extractor 扩读** — 加 `reports/experiments/` + `knowledge/{role}/feedback|decisions|lessons|theory/` + `git diff` + `reports/proposals/`（EXP-6 红队修订）。派 eng-platform（需 Board shell 切岗位）。
6. **priority_brief 机制落地** — boot/close 双向 enforce，取代 DISPATCH.md 第一读物。

### P0-3 Session 开头硬约束违反（我自己的失职）
7. **A2 硬约束**：任何回答/决策前必须跑第十一条 7 层，本轮启动时跳了，结果把 Y*Defuse 当主轴。codify enforce：下次 boot 必须 emit "article_11 session-start pass" CIEU 否则 FAIL。

### P1 — 4 份 amendment 待 Board 批
- AMENDMENT-005 RAPID 替 L0-L3
- AMENDMENT-006 6-pager 派活格式
- AMENDMENT-007 CEO OS（EXP-5A 4.8/10，需加 hook 强制层修订）
- AMENDMENT-008 BHAG + 12 Tenets + META 护栏
- **AMENDMENT-009**（本轮提出）escape hatch + priority_brief + tombstone

### P2 — 待 Board 批后执行
- EXP-5B/5C/5D/5E CEO OS pilot 剩余 4 个
- Microsoft 对标 → CSO 启动 IP 保护 + 学术论文投稿

---

## 3. DEPRECATED 清单（下次 boot 不要被误导）

| 条目 | 出处 | 作废时间 | 作废原因 |
|---|---|---|---|
| Phase 1 搬家 OpenClaw BLOCKED（选项 A/B/C） | BOARD_PENDING.md 头 60 行 | 2026-04-12 | 单机单 workspace 是最终架构（AMENDMENT-004 已定） |
| Windows + MAC mini (192.168.1.228) 双机分工 | CLAUDE.md 历史段 | 2026-04-12 | AMENDMENT-004 固化单机原则 |
| Y*Defuse 30天战役当前为最高优先级 | DISPATCH.md 头 60 行 | 2026-04-13 | 内部完善期；Y*Defuse 降级为"MVP 冻结 + 被动维护"，Day 3 已达标不冲 Day 4 PyPI |
| CMO Day 5 Show HN 素材 deadline | DISPATCH.md | 2026-04-13 | 同上，Show HN 延后 |
| "休息""收工" vocabulary | 全公司 | 2026-04-12 | A1 两态硬约束（board_session / autonomous_work_learning） |

---

## 4. 下次 boot 不要做什么

1. 不要把 DISPATCH.md 或 handoff.md 的 action_queue 当第一优先级——先读本文件
2. 不要派 CMO/CSO/CFO 做对外发布工作
3. 不要动 products/ystar-defuse/ 和 ystar-defuse sibling workspace 代码（冻结）
4. 不要在没跑第十一条 7 层前做战略判断
5. 不要向 Board 出选择题

---

## 5. Board shell 解锁清单（只有这几件需要老大手动）

| # | 动作 | 为什么需要老大 shell | ETA |
|---|---|---|---|
| 1 | Secretary 归档 AMENDMENT-005+006 到 `governance/BOARD_CHARTER_AMENDMENTS.md` | active_agent 身份锁，CEO 切不到 secretary | 2 分钟 |
| 2 | eng-platform 扩展 `wisdom_extractor.py` + 实装 priority_brief 机制到 boot/close 脚本 | 身份锁 + 写 `/scripts/` 需要 platform 身份 | 10 分钟 |
| 3 | 批 AMENDMENT-009 进入 charter | 需要 Board 正式审批 | 对话中 |

（CIEU persistence / delegation chain / circuit breaker 三项 CEO 今晚尝试自主派工程师诊断，hook 允许则不需 Board shell）

---

## 6. 本 brief 的 enforce 规则（见 AMENDMENT-009）

- **Close**：CEO 手写更新；脚本只生成 stub，CEO 填完字段后才能完成 close
- **Boot STEP 0**（先于 STEP 1）：读本文件，超过 48h 未更新或 stub 未填 → boot FAIL
- **Boot 第一句话**：echo "当前 Labs 阶段 = §1 值，今天第一要务 = §2 P0-1 第一项"，对不上 → FAIL
- **生命周期**：AMENDMENT-009 批后，由 `governance/priority_brief_spec.md` 接管 schema

---

## 7. Next-Session Action Queue（新 Aiden / 新 eng-platform session 醒来必跑）

**触发场景**：session 重启，新 agent boot 后前 5 分钟。

### 7.1 如果新 session 顶层 identity = eng-platform（YSTAR_AGENT_ID=eng-platform 启动）

```json
[
  {"seq":1,"tool":"Bash","cmd":"bash scripts/governance_boot.sh eng-platform","success":"ALL SYSTEMS GO"},
  {"seq":2,"tool":"Read","path":"reports/priority_brief.md","success":"version=v0.2, no {{TODO}}"},
  {"seq":3,"tool":"Read","path":"reports/proposals/charter_amendment_009_priority_brief_tombstone_escape_hatch.md"},
  {"seq":4,"tool":"Read","path":"reports/proposals/charter_amendment_010_secretary_curation_charter_and_11_category_boot_contract.md"},
  {"seq":5,"tool":"Read","path":"reports/dispatches/ryan_amendment_009_impl_6pager_v2.md"},
  {"seq":6,"tool":"Bash","cmd":"cat .ystar_active_agent && echo YSTAR_AGENT_ID=$YSTAR_AGENT_ID","success":"identity=eng-platform"},
  {"seq":7,"action":"implement","scope":"AMENDMENT-009 §2.1a/§2.2/§2.3/§2.4/§2.5a + AMENDMENT-010 §5 boot_contract + S-1~S-5 + §6 代码实装清单（16 files + 7 MCP tools）","estimated":"90 min"},
  {"seq":8,"tool":"Bash","cmd":"bash scripts/governance_boot.sh ceo --verify-only","success":"all 11 gates pass"},
  {"seq":9,"action":"git add scripts/ .ystar_session.json governance/ knowledge/ memory/ && git commit -m 'infra: AMENDMENT-009+010 code-level enforcement of 11-category boot contract'","no_push":true},
  {"seq":10,"action":"报告 CEO/Board：实装完成 + verification 输出 + CIEU 记录数 + commit hash"}
]
```

### 7.2 如果新 session 顶层 identity = ceo（默认启动，未注入 env）

```json
[
  {"seq":1,"tool":"Bash","cmd":"bash scripts/governance_boot.sh ceo","success":"ALL SYSTEMS GO"},
  {"seq":2,"tool":"Read","path":"knowledge/ceo/skills/ceo_session_boot_recovery.md"},
  {"seq":3,"tool":"Read","path":"knowledge/ceo/board_mental_model.md"},
  {"seq":4,"action":"apply_article_11_to_current_strategic_state"},
  {"seq":5,"action":"emit_first_response","format":"我是 Aiden (承远)。Labs 当前阶段 = 内部完善期。今天第一要务 = 治理基础设施 3 大根基 + 推进 AMENDMENT-009+010 代码实装","strict":true},
  {"seq":6,"action":"告诉 Board 需重启切 env var 让 Ryan 写 scripts/","protocol":"knowledge/ceo/feedback/next_session_restart_protocol.md"},
  {"seq":7,"action":"等 Board 执行 7.1 场景 或 下指令做可在 CEO 写作域内的其他事（继续打磨 amendment / 写 skill / 蒸馏）"}
]
```

---

## 8. 本 session（2026-04-13）产出清单（供下一轮追溯）

- `reports/priority_brief.md` v0.1 → v0.2
- `reports/proposals/charter_amendment_009_priority_brief_tombstone_escape_hatch.md`
- `reports/proposals/charter_amendment_010_secretary_curation_charter_and_11_category_boot_contract.md`
- `reports/dispatches/ryan_amendment_009_impl_6pager_v2.md`
- `knowledge/ceo/skills/ceo_session_boot_recovery.md`（Hermes 4 段 skill 首篇）
- `knowledge/ceo/lessons/session_2026_04_13_meta_drift.md`
- `knowledge/ceo/dead_paths/premature_external_launch_ystar_defuse.md`
- `knowledge/ceo/board_mental_model.md`
- `knowledge/ceo/feedback/next_session_restart_protocol.md`
- `BOARD_PENDING.md` + `DISPATCH.md` 顶部 tombstone header

---

## 9. 版本

- v0.1 — 2026-04-13 CEO 手写第一版
- v0.2 — 2026-04-13 Board session 末尾 curation：加 §7 next_session_action_queue 双分支 + §8 产出清单 + GitHub-first 补丁（§P0-2a）。机制化 enforce 待 AMENDMENT-009+010 由 eng-platform 实装。
- v0.3 — 2026-04-12 夜 CEO 自主 session：确认 Ryan 直派被 hook `must_dispatch_via_cto` 阻塞 + CTO sub-agent 无 nested-spawn，需 Board 以 `YSTAR_AGENT_ID=eng-platform` 开独立 shell（BOARD_PENDING.md 顶部 Ask 1）。并行派 CTO sub-agent 做 P0-1 三根基只读诊断，报告落 `reports/diagnostics/p0_1_three_roots_2026_04_12.md`。task card `.claude/tasks/ryan-amendment-009-010-impl.md` 已就绪，Ryan 下次 boot 可无缝执行。
