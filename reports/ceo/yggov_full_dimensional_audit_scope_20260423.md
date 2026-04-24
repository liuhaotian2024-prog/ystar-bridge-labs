---
status: [L2] draft scope — pending Ethan Wave-1 receipt + Board review
authored_by: Aiden (CEO), 2026-04-23 post-deadlock
mandate: Board directive "全维度深度治理层审计 到 Rt+1=0, Ethan 主持, Aiden 协助, 工程师全部出动"
supersedes: 9-point tactical audit (that is Phase 1 Wave-1, this is Phase 2+)
related:
  - reports/incidents/2026-04-23-hook-fail-closed-deadlock.md
  - reports/ceo/iron_rule_incident_response_3channel_20260423.md
  - /Users/haotianliu/.openclaw/workspace/Y-star-gov/docs/arch/arch17_behavioral_governance_spec.md
baseline_loc: 41568 (governance 32463 + adapters 9105)
---

# Y*gov 全维度深度治理层审计 — Master Scope

## 0. Audit Mission (M Triangle alignment)

Y* 核心不变式 (Board 2026-04-23 directive 重申):
> 治理端对 labs 运营端实现**全部有效治理** (不乱做事 M-2a + 不能不做事 M-2b), 同时**不出现循环锁死**.

本次审计必须通过 empirical 证据 (不是 vibe), 证明下列 8 维度 **同时**达成最佳工程态:

- **无死锁**: 任意 env 漂移 / marker 缺失 / import fail / daemon crash 场景下治理层都能自救或降级, 绝不 block Aiden+engineers 超过 60s
- **零漏网**: 任意 commission 违规 (越权写 / 绕过 dispatch / 直 spawn sub-sub-agent) 都被拦 + CIEU 有记录
- **零沉默**: 任意 obligation overdue / 静默 idle / 卡任务 超阈值都被 escalate
- **可审计**: 任意决策 (allow/deny/redirect/invoke/inject) 都有 CIEU 5-tuple + Merkle chain + K9 sampling cross-val
- **可验证**: 任意 rule 都有 live-fire test (deliberate violation → delta CIEU event 0→1)
- **可操作**: 任意 deny 都附 actionable redirect (非只罚不导, 避免 lock-death)

Rt+1=0 定义 (empirical, 不装):
- 0 个维度未达 target threshold
- ≥1 个 chaos-engineering 场景 survive without Board manual救援
- 158 → ≥200 tests pass (含新加 chaos scenarios + formal property checks)
- priority_brief.md fresh (≤24h stale)
- CIEU 30-day violation rate < 1.0% (当前 1.05-1.415%)

---

## 0.5 Toolbox Inventory (必全用, Board directive 2026-04-23: "全系统扫描工具记得用上 + 工具箱全检 + 传统 + CIEU 都用 + 上帝视角")

### A. Company-side 系统扫描 (`scripts/`)

| Tool | 作用 | 用在 Dimension |
|---|---|---|
| `governance_audit_unified.py` | **统一治理审计 (系统主扫描器, Board 提的那个)** | ALL dims baseline |
| `ecosystem_scan.py` | 生态依赖扫描 | F (external import), H (doc) |
| `labs_atlas_scan.py` | Labs atlas 全量扫 | A, B, D |
| `unified_compliance_audit.py` | 合规统一审计 | B, E |
| `amendment_coverage_audit.py` | AMENDMENT 覆盖率 | B (charter), H (doc) |
| `wire_integrity_check.py` | wire 完整性 (WORLD_STATE 已报 0 issues) | A, D |
| `memory_consistency_check.py` | 记忆一致性 (brain writeback 验证) | D (continuity) |
| `y_star_self_check.py` | Y* 自检总 | Wave-8 Rt+1 verify |
| `restart_readiness_check.py` | 重启就绪 | A (deadlock) |
| `archive_sla_scan.py` | Archive SLA | C (omission) |
| `hook_subagent_output_scan.py` | subagent output 扫 | B (commission) |
| `hook_stop_reply_scan.py` | stop reply 扫 | B (Iron Rule 0 enforce) |
| `dialogue_drift_checker.py` | 对话漂移 | D (identity) |
| `session_health_watchdog.py` / `session_health_hook.sh` | session 健康 | A |
| `tombstone_linter.py` | Tombstone lint | H (doc) |
| `precheck_existing.py` / `precheck_review.py` | 先查后造闭环 | Wave prelude each (MR-6) |
| `check_intents.py` / `check_obligations.py` | intent / obligation 队列 | C |
| `knowledge_check.py` | 知识库一致性 | H |
| `ci_check_imports.py` | import 家族扫 (Bug 1 家族) | Wave-1 Item #5 |
| `test_iron_rule_0_scanner.py` | Iron Rule 0 扫描 | B |
| `x_content_safety_check.py` | 外发内容安全 | G (content pipeline) |
| `a1_vocab_scanner.py` | A1 词汇扫 | H |

### B. K9 audit family (causal + semantic, 10-30% 采样 per Tier 2 decision)

| Tool | 作用 | 用在 |
|---|---|---|
| `k9_audit_v3.py` | K9 v3 主审计 | Dim E (cross-val), Wave-4 |
| `k9_baseline_verify.py` | Baseline 验证 | Wave-8 Rt+1 |
| `k9_sample_audit.py` | 采样 10-30% semantic | Dim E Tier 2 ship |
| `k9_silent_fire_audit.py` | 静默 fire 审计 | B (commission 漏网) |
| `k9_three_dim_audit.py` | 3 维审计 | cross-dim A+B+C |
| `/tmp/K9Audit/` (legacy, MIT/AGPL 边界注意) | Causal chain analyzer + Auditor + `k9_repo_audit.py` + `@k9` decorator | external import pattern (Dim F + Ryan resilience)

**K9 硬约束** (memory `project_cieu_qa_gate_ship_decision_20260423`): K9 必 pure reader, 永不 write CIEU. 结构 enforce 验证 = Dim E 必答.

### C. Y-star-gov 产品侧 audit 工具

| Tool | 作用 |
|---|---|
| `ystar/cli/doctor_cmd.py` (`ystar doctor` CLI) | 用户侧 one-command 健康检 |
| `ystar/governance/liveness_audit.py` | directive liveness 机器检 (Maya 2026-04-19 ship) |
| `ystar/governance/coordinator_audit.py` | coordinator 审计 |
| `ystar/governance/omission_scanner.py` | omission 扫描 |
| `ystar/governance/k9_adapter/compliance_audit.py` | K9 adapter 合规审计 |
| `ystar/adapters/claude_code_scanner.py` | Claude Code 层扫 |
| `ystar/kernel/history_scanner.py` | kernel 历史扫 |

### D. 传统 audit (Iron Rule Channel 2)

- `tail -100 scripts/hook_debug.log`
- `tail -50 scripts/.logs/broker.log` + `dialogue_contract.log` + `drift.log` + `dream_log.json`
- `ps aux | grep ystar / k9 / daemon`
- `git log / blame / diff` (Y*gov 源 + company repo)
- Python `traceback`, `sys.path` introspect, `pkg_resources` egg-info 验证

### E. CIEU audit (Iron Rule Channel 1, dogfood primary)

- SQLite `.ystar_cieu.db` (465MB)
  - `cieu_events` (agent_id / event_type / decision / violations / payload, 39K+ events/hour)
  - `omission_queue`
  - `activation_log` (1.4M rows)
- 标准查询 template: `SELECT ... WHERE decision='deny' AND created_at > strftime('%s','now','-30 minute')`
- Merkle seal verify: 659K sealed, 需 cron daily re-verify (Dim E deliverable)

### F. 每维度 methodology 硬约束 (Board directive "both traditional + CIEU")

**每 Dimension A-H 至少同时用**:
1. **≥1 自家 scanner** (A/B/C 表里对应 tool 跑 + 结果 diff baseline)
2. **≥1 CIEU SQL query** (Channel 1 primary, 用自己的 audit 层诊断自己 = dogfood)
3. **≥1 traditional** (Channel 2: hook log / ps / git / traceback)
4. **≥1 K9 cross-val** (采样 10-30% + semantic agreement) for commission/omission/deadlock/audit 维度
5. 全局上帝视角: 每 Wave 先跑 `governance_audit_unified.py + ecosystem_scan.py + labs_atlas_scan.py` 建 baseline, Wave 收束再跑对比 delta — 不顾此失彼

**Rt+1=0 总 verify**: `y_star_self_check.py` + `k9_baseline_verify.py` + CIEU 30d violation rate + priority_brief staleness 同时通过.

---

## 1. 八维度 Audit Matrix

### Dimension A — Deadlock Prevention (tonight's incident class)

**Scope**: 本事故已暴露 12+ lock-death paths, 本维度穷尽剩余 paths + 加结构级预防.

**Questions Ethan 必答 (empirical)**:
1. `hook_wrapper.py` v1 path + Y-star-gov `ystar/adapters/hook.py` v2 path 的 agent 解析, fail-closed fallback, marker override chain 是否 **symmetric** (无论 `YSTAR_HOOK_V2=0/1` 结果一致)?
2. env var propagation 全链 (shell profile → launchd → Claude → hook → subagent) 哪些 env 影响治理行为? 每个是否有 in-code fallback 不依赖 env?
3. 所有 state file (`.ystar_active_agent*`, `.session_booted`, `.czl_subgoals.json`, marker files) 的写入 race 是否用 `fcntl.flock` 保护? (AMENDMENT-016 覆盖率)
4. hook 调用链里每个同步阻塞点 (CIEU write / rule eval / marker read / Y-star-gov import) 是否有 timeout + graceful fallback?
5. PreToolUse 死循环 (rule 提示的 fix 命令本身被 rule 拦) pattern 是否通用检测 (circular hint)?

**Deliverable**:
- `reports/ctos/deadlock_paths_taxonomy_v2.md` — 扩展当前 12 paths 到 ≥20 并对每条标 `fix_status` + `regression_test`
- Y-star-gov `tests/governance/test_deadlock_chaos.py` — 每 path 一个 chaos injection test (mock env var, delete marker, crash daemon mid-write)
- K9 Rescue Daemon v1 ship (本事故立的 P0, Ryan 主责)

**Success**: chaos test 覆盖率 ≥90%, 任意 deadlock path 触发 → rescue daemon or in-code fallback 自愈 ≤60s.

---

### Dimension B — Commission Governance (不乱做事, M-2a)

**Scope**: ForgetGuard + boundary_enforcer + Iron Rules + router_registry 的完备性与精度.

**Questions**:
1. 当前 17 forget_guard rules 实测 precision vs recall? (live-fire: deliberate violation 各做 3 次 per rule → 看 CIEU delta + false-positive rate)
2. Iron Rule 0 (no choice question) / Iron Rule 铁律 (3-channel) / must_dispatch_via_cto 是否都有 code-level enforce (非 prose-only)?
3. RULE-CHARTER-001 (charter amendment flow) 覆盖 AGENTS.md + CLAUDE.md + `knowledge/ceo/iron_rules.md` + 每个 constitutional rule?
4. `.claude/agents/*.md` 修改是否必经 Samantha override + 审计记录?
5. subagent 写权限 allowlist vs denylist (memory: 负面约束 regex trap), 所有 dispatch prompt 是否正面 allowlist 化?

**Deliverable**:
- `reports/governance/rule_precision_audit_20260423.md` — 每 rule precision/recall 数字
- Y-star-gov `tests/governance/test_rule_live_fire.py` — 每 rule 3-case live-fire
- forget_guard rules 全体 normalize 成正面 allowlist 格式

**Success**: 17 rules precision ≥90% AND recall ≥95% empirical; 0 个 prose-only constitutional rule (全有 code enforce).

---

### Dimension C — Omission Governance (不能不做事, M-2b)

**Scope**: OmissionEngine + obligation 生命周期 + dream mechanism + P0 overdue alert.

**Questions**:
1. OmissionEngine proactive scan (P2 backlog "3min/idle trigger") 是否已 ship? 实测 idle trigger 触发率?
2. 当前 obligations queue (从 continuation.json 看 15 条) 每条是否有 `deadline` / `trigger_event` / `owner` 三元组? 超期是否自动 escalate 到 CIEU + Board reminder?
3. Dream mechanism L4 gap (22 diff 6MB 未落盘 edges delta=0, 见 memory `project_dream_mechanism_propose_only_gap`) — `dream_auto_reviewer.py` 是否已 ship 且 BRAIN_DREAM_DIFF_REVIEWED event 在 emit? Gate 2 DENY rate 改善?
4. 静默 idle detect (Board AFK >4h): autonomous_work_learning 态 trigger 是否 LIVE? (memory `feedback_close_stub_trigger`)
5. `stuck_claim_watchdog.py` (163 LOC) 实测 stuck detect 延迟?

**Deliverable**:
- `reports/governance/omission_coverage_audit_20260423.md` — 每类 omission 覆盖率 + 漏检 case
- OmissionEngine proactive scan ship (if 未 ship)
- Dream L4 闭环验证: edges delta > 0 empirical (不信 propose 数量, 信 brain 边数)

**Success**: ≥1 人为引入 omission (mock overdue obligation, mock stuck claim) 在 5min 内被 detect + escalate.

---

### Dimension D — Identity & Continuity (M-1 Survivability)

**Scope**: Agent identity 7-layer + marker fallback + cross-session brain writeback.

**Questions**:
1. Aiden 7-layer identity (memory `aiden_7_layer_identity_2026_04_19`) 每层是否都有结构 binding (非 prose)?
2. marker fallback chain (session-id → ppid → global-newest) 在 concurrent subagent (>3 并发) 下是否 correct? (之前 CZL-MARKER-PER-SESSION-ISOLATION fix Leo 已落, 验证覆盖率)
3. sub-agent 跑完不 restore `.ystar_active_agent` (memory `project_active_agent_drift`) — 是否已有 PostToolUse restore hook?
4. brain writeback (L2 access_count, activation_log 1.4M rows) 跨 session 数据完整? (memory: 66/150 recovered, 全量 recovery 进度?)
5. CEO-bypass rule (memory `feedback_team_enforce_asymmetry`) 与 subagent 限制如何结构 symmetric?

**Deliverable**:
- `reports/governance/identity_continuity_audit_20260423.md`
- 新加 tests/governance/test_identity_concurrent.py (mock 5 concurrent subagents, verify no clobber)
- PostToolUse `restore_active_agent` hook (if 未 ship)

**Success**: concurrent 5 subagent 连跑 100 次, marker mis-resolve 率 = 0.

---

### Dimension E — Audit Layer (CIEU + K9)

**Scope**: CIEU schema 完备 + K9 sampling cross-val + Merkle integrity.

**Questions**:
1. CIEU schema 10+ script 绕过 helper 直 INSERT (memory `feedback_inference_layer_alone_insufficient`) — 全量 backfill daemon 是否 ship?
2. CIEU DB 465MB + 10 daemon WAL contention (memory `project_cieu_qa_gate_ship_decision_20260423`) — Tier 1 event_id 必查 LIVE 验证? Tier 2 K9 采样 10-30% ship?
3. K9 pure reader (CTO veto: 永不 write CIEU) 是否结构 enforce (K9 code 无 CIEU write API)?
4. Merkle sealing 659K sealed (memory) — verify chain 定期跑 cron?
5. cieu_events 写失败 3-tier degradation (CIEU → JSONL → stderr, see hook_wrapper emit_cieu_or_fallback) 每 tier 都有 chaos test?

**Deliverable**:
- `reports/governance/audit_layer_completeness_20260423.md`
- K9 sampling Tier 2 ship (Ethan + Ryan 联合)
- Merkle verify cron (daily) + report

**Success**: CIEU coverage ≥ 99% (任意 tool call 有对应 event), K9 cross-val semantic agreement ≥95%.

---

### Dimension F — External Research Imports (methodology uplift)

**Scope**: Board 原话"依据各种技术理论和技术工具" — 必须深研业界已有 solution 不闭门造车.

**必研 5 领域 + 每领域指派 engineer**:

1. **Formal verification of governance invariants** (Leo) — TLA+ / Alloy / Coq 建模 Y*gov 核心不变式 (agent identity correctness, marker race freedom, lock-death absence). 输出: `Y-star-gov/docs/formal/ygov_invariants.tla` + pass TLC model check.
2. **Distributed systems patterns — circuit breaker / bulkhead / timeout / retry** (Ryan) — Netflix Hystrix / AWS resilience4j patterns, apply to hook call chain (每个阻塞点加 timeout + fallback). 输出: `reports/platform/resilience_patterns_applied.md` + code change.
3. **Policy engines — OPA / Cedar / Rego** (Ethan) — compare Y*gov yaml rule engine vs Rego expressiveness. 若 Rego gaps 小, 考虑迁 + gain standard tooling. 输出: `reports/ctos/policy_engine_assessment.md`.
4. **AI safety / deceptive alignment / instrumental goals** (Maya) — Anthropic Constitutional AI / DeepMind Sycophancy / MIRI Goodhart — apply 反求 rule 让 subagent 不能 hallucinate receipt / moral licensing. 输出: `reports/governance/ai_safety_application.md` + 新 forget_guard rules.
5. **Chaos engineering — Chaos Monkey / Gremlin / Litmus** (Jordan) — 系统 fault injection testing 方法, apply to Y*gov. 输出: `reports/domains/chaos_framework.md` + `tests/chaos/` suite.

**Deliverable per engineer**:
- 1 survey doc (≥1500 words, cite ≥5 primary sources)
- 1 concrete Y*gov 改进 (code, not just spec)
- 1 metalearning note: 什么适用, 什么不适用, 为什么

**Success**: 5 领域都产出 + 至少 3 领域的 pattern 集成到 Y*gov code path.

---

### Dimension G — Test Coverage & CI

**Scope**: 158 → ≥200 tests, 含 chaos + formal property + live-fire.

**Questions**:
1. 当前 158 tests 覆盖哪些 dimension? 缺口在哪?
2. pip install 成功率 >95%? 多机器 matrix test (Mac/Linux, Python 3.10/3.11/3.12)?
3. hook stability zero daemon crashes — 实测 1 天 uptime 崩溃次数?
4. live-fire smoke test (deliberate violation → CIEU delta 0→1) 全 17 rule 覆盖?
5. CI 里是否跑 formal property check (Dimension F-1 的 TLA+ spec)?

**Deliverable**:
- `reports/governance/test_coverage_gap_20260423.md`
- 新 tests/chaos/, tests/formal/, tests/live_fire/ 子 suite
- CI workflow 加 formal + chaos step

**Success**: ≥200 tests green, pip install >95% on 3-OS matrix, hook daemon 24h zero crash.

---

### Dimension H — Documentation + Operator Runbook

**Scope**: Y*gov spec formal statement + incident playbook + customer value.

**Questions**:
1. ARCH-17 (46K) + ARCH-18 是否 up-to-date with post-deadlock learnings?
2. Incident playbook (tonight's Iron Rule 3-channel) 是否嵌入 K9 Rescue Daemon actionable steps?
3. `knowledge/ceo/iron_rules.md` 全量 constitutional rules (M Triangle + 14 Work Method + Iron Rules 0-N) 是否单一 source of truth?
4. Customer-facing value prop: dogfood 本事故怎么讲? (转化为 case study — Y*gov 自 heal 自 learn 的证据)

**Deliverable**:
- ARCH-17/18 refresh with new lock-death paths + deadlock prevention patterns
- `reports/ceo/incident_playbook_v1.md` — universal runbook (含 Iron Rule 3-channel + K9 rescue + Board-shell 最后 resort)
- `content/blog/y_gov_self_heal_dogfood.md` — marketing case study (Sofia 接)
- `knowledge/ceo/iron_rules.md` canonical source

**Success**: 新人 CEO (mock scenario) 能 cold-start 理解 Y*gov mission + 在 15min 内诊断常见事故.

---

## 1.5 Methodology Stack Binding (Board 2026-04-23 reminder: 全套方法论 + 8-module 认知 + 大脑 + 记忆 + 文化全用)

**每 engineer 每 Wave 每 task 前必 self-check**:

**8-问 (from WORK_METHODOLOGY P-1~P-14)**:
1. M-tag (M-1 / M-2a / M-2b / M-3 align 哪面, 削弱哪面)
2. 反事实不做 (若本 task skip 会发生什么)
3. 反事实做错 (若 implementation wrong 最坏 blast radius)
4. empirical data (有无 SQL/file/ps/log 证据, 还是仅推测)
5. peer review (Ethan 主持 pass-check; CEO Aiden fact-verify)
6. 先例 Glob (P-12: 自家是否已有 tool? 参考 §0.5 toolbox)
7. 8-cascade (新 entity 要走 charter/registry/boot/dispatch/hook/CIEU/FG-scope/pre-auth)
8. 完成标准 (Rt+1=0 empirical metric, 不 vibe)

**6-问 (reply-time)**: L-tag / 5-tuple (Y*/Xt/U/Yt+1/Rt+1) / 定量诚实 / plan vs done / present tense / 无选择题 (Iron Rule 0).

**8-module 认知 per task**:
- **M1 反射** (Claude 底层 inference) — 必经但不够
- **M2 记忆** — 调 aiden_brain.db + MEMORY.md + 6D brain context (每 Wave 先 query 相关 node)
- **M3 资料** — §0.5 toolbox + ARCH-17/18 + external research doc (Dim F)
- **M4 路径** — OODA loop (observe → search → analyze → solve → verify → land) 不跳
- **M5 方法论** — 14 原则 checklist 过一遍
- **M6 错误监控** — forget_guard live-fire + CIEU delta 验证 (不信 self-report)
- **M7 主动行动** — 不等 Board 催, blocker 立 stop + 写 blocker statement
- **M8 反思** — 每 Wave 收束后写 lesson / 更新 MEMORY.md feedback

**团队文化 4-factor** (memory `feedback_engineer_culture_4_factor_design`): model × role × culture × prompt. CEO 派 subagent 前 self-check 4 因素齐 (high-stakes framing + role clarity + culture ref + MANDATORY tool_uses self-count).

**Rt+1=0 纪律** (memory `feedback_ship_neq_done_rt1_zero_discipline`): ship ≠ done; 必跑 empirical SQL 验 current metric vs target threshold; 不达则报 "Rt+1: specific gap", 不装 0.

---

## 1.6 Pre-Wave Baseline Snapshot (2026-04-23 ran, 3 scanner 已出初值)

已落盘到 `reports/ctos/audit_baseline_20260423/`:
- `governance_audit_unified.txt` — 24h: 3605 deny (7d avg 5807.4, 方向↓); 11 detectors active; circuit_breaker 3031 / intervention_gate 415 / cmd_exec 212 主力
- `ecosystem_scan.txt` — **`ceo_enforcement: UNKNOWN`** (Dim B 硬 gap, 机器不能验 CEO enforce); 5 entanglement pairs (CTO cross-layer / receipt hallucination / CEO U-workflow skip / Ryan scope overflow / Maya claim mismatch) 对齐 Dim B/C 根因; brain 22992n/136786e/442h
- `wire_integrity.txt` — **11 WIRE_BROKEN**: 6 hooks 未注册 settings.json + 1 cron 不在 crontab + **4 canonical hash drift** 含 `[P0 AGENTS.md:408-423 hash drift]` ← 这条 比 deadlock 更严重 (constitutional 不可验), **Dim B 紧急补洞 Priority #1**

**每 Wave 收束重跑 3 scanner, 与本 baseline diff** — `ceo_enforcement: UNKNOWN` 必改 `LIVE`; 11 WIRE_BROKEN 必降 0; 5 entanglement pairs 每对都有对应 Dim 修复路径 + test.

---

## 2. Engineer Assignment Matrix

| Dimension | Primary | Assist | External Research Lead |
|---|---|---|---|
| A Deadlock Prevention | Ethan | Leo (marker) + Ryan (K9 daemon) | Ryan (resilience patterns) |
| B Commission | Maya | Ethan (router) | Maya (AI safety) |
| C Omission | Maya | Ryan (OmissionEngine scan) | — |
| D Identity & Continuity | Leo | — | Leo (formal methods) |
| E Audit Layer (CIEU/K9) | Ethan | Ryan (K9 sampling) | Ethan (policy engines) |
| F External Research | ALL 4 | — | each owns 1 |
| G Test Coverage | Jordan | all 4 contribute | Jordan (chaos) |
| H Documentation | Samantha | CEO Aiden edits | — |

**Ethan 主持**: 每 Wave 前召开 1 tool_use status sync (5-tuple receipt), 每 Wave 后评分 + 下波 adjust. CEO Aiden 协助: 代 spawn subagent / 写 task card / verify receipt empirical / 与 Board 对接.

---

## 3. Wave Sequencing (tool_uses 预算 per Wave)

**Wave-1 (Phase 1 tactical — in flight, Ethan a83a4a09)**: 9-point post-incident audit. 预算 ~40 tu. 返回后 CEO fan out Item #3-#9 to 4 engineers.

**Wave-2 (Dimension A deep dive)**: Ethan deadlock taxonomy v2 + Ryan K9 Rescue Daemon + Leo state file race audit. 预算 ~80 tu. Blocker: Wave-1 close.

**Wave-3 (Dimensions B + C parallel)**: Maya rule precision + omission coverage + dream L4 verify. 预算 ~60 tu. Can run 与 Wave-2 parallel.

**Wave-4 (Dimension D + E)**: Leo identity continuity + Ethan CIEU/K9 audit layer. 预算 ~70 tu. Blocker: Wave-2 K9 pure-reader shipped.

**Wave-5 (Dimension F research)**: 4 engineers 各领 1 survey + concrete fix. 预算 ~40 tu each, total 160 tu. Parallel.

**Wave-6 (Dimension G test build-out)**: Jordan 主导 chaos + formal + live-fire test suites. 预算 ~100 tu. Blocker: Wave-2,3,4 close (需 code artifact 测).

**Wave-7 (Dimension H doc)**: Samantha + CEO Aiden sweep. 预算 ~40 tu.

**Wave-8 (Integration + Rt+1=0 verify)**: CEO + Ethan 全量 Rt+1=0 empirical check, 更新 priority_brief, Board 汇报. 预算 ~30 tu.

**Total budget**: ~580 tu (Aiden 协助 overhead ~150 tu). Program ordering: 不按日历估时 (memory `feedback_no_consultant_time_scales`), 按 empirical tu burn rate 与 blocker unlock 推进.

---

## 4. Rt+1=0 Master Checklist (empirical verify only)

- [ ] D-A: chaos test ≥20 scenarios pass, K9 Rescue Daemon LIVE (`ps` 确认 launchd service + FIFO 文件 + 7 R-command 跑通)
- [ ] D-B: 17 rules precision ≥90% recall ≥95% (SQL 查近 30d CIEU, false-positive/true-positive 手工标 100 条样本 cross-val)
- [ ] D-C: 3 mock omission (overdue obligation / stuck claim / idle 4h) 全在 5min 内 escalate (CIEU event 有)
- [ ] D-D: 5 concurrent subagent 连跑 100 次, marker mis-resolve = 0 (pytest 跑)
- [ ] D-E: CIEU coverage ≥99% (SQL: 近 24h tool_call 总数 vs cieu_events 近 24h 总数 比值), K9 agreement ≥95%
- [ ] D-F: 5 survey doc 齐 + ≥3 concrete Y*gov code 改进集成
- [ ] D-G: ≥200 tests green, pip install 3-OS matrix >95%
- [ ] D-H: priority_brief fresh (≤24h) + incident_playbook_v1 + iron_rules canonical source
- [ ] M Triangle: M-1 survivability (identity continuity test pass) + M-2a (B 达标) + M-2b (C 达标) + M-3 (本次 audit 本身即 dogfood 卖点, Sofia 写案例)

---

## 5. Reference Docs (research basis)

- ARCH-17 (Y-star-gov/docs/arch/arch17_behavioral_governance_spec.md, 46K)
- AMENDMENT-016 fcntl.flock
- AMENDMENT-020 Secretary + 4 eng-* charter
- CZL-P1/P2 lock-death taxonomy (currently 12+ paths)
- Aiden 7-layer identity
- 14-principle Work Methodology (Board 2026-04-21 钦定)
- Iron Rules 0 + 铁律 3-channel + 12+ feedback memories in auto-memory

---

## 5.5 CRITICAL ARCHITECTURE FINDING — Spawn Deadlock (新, 2026-04-24 pre-Wave-2 discovery)

**Empirical 取证**:
1. `dispatch_board.py status`: 146 tasks total; `pending` subcommand shows **27 un-spawned items ALL [OVERDUE hard TTL exceeded]**
2. Overdue 范围从 2026-04-20 (98h) 到本 session 刚 post 的 7 INC items (数十分钟内立刻 overdue)
3. 含 P0 重磅: `CZL-SPAWN-PPID-MARKER-FIX` (57h, 与本次 deadlock 同 root cause), `CZL-COMMISSION-UNIFY-STEP-1~3` (40h, 核心产品 M-2a 化), `CZL-BOARD-HONESTY-G1/G2` (40h), `CZL-BRAIN-FRONTIER-1~5` (32h), `CZL-CEO-RULES-REGISTRY-V3` (36h), `CZL-WAVE-5-RECEIPT-STRUCTURED-SCHEMA` (31h)
4. `scripts/engineer_task_subscriber.py:46-48` 源码认死: "Subscriber CANNOT spawn Agent tool calls -- structural Claude Code boundary. Only the main Claude session's tool-use loop can originate Agent calls."
5. `scripts/cto_dispatch_broker.py` daemon 活着 (pid 30854), 但它只做 routing 不 spawn
6. `must_dispatch_via_cto` forget_guard rule 禁 CEO→eng 直 spawn, redirect "Use gov_delegate" (而 gov-mcp `gov_delegate` tool 未 deployed per `CZL-GOV-MCP-ACTIVATE` overdue 60h)

**真因**:
Board 2026-04-18 directive "CEO 必须 dispatch_board.py post 让 broker+subscriber 自主领, 不可直接 Agent spawn" 在 **Claude Code 架构上结构性不可能**, 因为 Agent tool 只能从 main session 的 tool-use loop 原发, 不能从外部 Python subprocess 注入. 该架构设计 + `must_dispatch_via_cto` rule 叠加, 形成 **spawn deadlock**:
- CEO 直 spawn → rule deny
- dispatch_board post → broker → subscriber → 写 `.pending_spawns.jsonl`, CEO main session 不主动 poll 该文件 → 0 spawn
- Ethan subagent 代 spawn → CDP nested sub-sub-agent block (Claude Code boundary)
- 唯一 bypass: `ceo_mode_manager.py force_break_glass --trigger T1` (20min hard cap) 允许 CEO 直 spawn 20min 窗口

**Dimension 映射**:
- Dim A deadlock: 此为第 13 条 lock-death path (spawn-deadlock, 非 hook-deadlock 但同性质)
- Dim B commission: `must_dispatch_via_cto` rule 是 false-positive — 初衷防 CEO 绕过 CTO 工程判断, 实际把 Ethan 已 author 的 task card + CEO 仅作 spawn executor 的 legitimate path 一并阻断
- Dim C omission: 27 items stuck 是 M-2b 最大 omission sample; 7 items 今 session post 立刻 overdue = 每 post 都增 omission 而非减
- Dim E audit: `.pending_spawns.jsonl` 写入 0 CIEU event (spawn 失败不 audit), dogfood 盲区

**Wave-2 必修 (Ethan 主持)**:
1. `must_dispatch_via_cto` rule 加 exception: "when dispatch prompt cites pre-existing CTO-authored task card file path" → 白名单允许 CEO 直 spawn
2. OR 删 `must_dispatch_via_cto` (Enforce-as-Router 架构下该 rule 过时, 参见 `project_enforce_as_router_thesis`)
3. dispatch_board 重构: main session `pending_spawns_consumer` hook 在 UserPromptSubmit 时自动 drain `.pending_spawns.jsonl` (让 CEO 主 session 做 spawn 动作自动化)
4. 27 items 手工 triage: Ethan Wave-2 重审哪些仍 relevant, 哪些作废 archive
5. `.pending_spawns.jsonl` 写入必 emit CIEU `SPAWN_QUEUED` event + spawn 执行时 emit `SPAWN_EXECUTED` event (闭环 M-2b 审计)

**Wave-1 补救 (本 session)**:
- break_glass 20min 窗口直 spawn Maya/Leo/Ryan 3 engineer, 覆盖 Items #1 #3 #4 #5 #6 #7 #9
- break_glass 过期后新 spawn 继续 blocked 直到 Wave-2 结构 fix

---

## 6. 诚实 gap 当前 (Rt+1 不装 0)

- 本 scope 是 CEO 3 tool_use 草拟, 未 Ethan review
- 预算 tu 是估, 真 burn rate 需 Wave-1 receipt 后校准
- 外部 research 5 领域深度依赖 engineer 研读质量, 没保证每 engineer 都读得深
- Board directive 说"最高水平方法论落实到工作", 这条要求 14-principle 每轮过 checklist, 本 scope 没嵌入 per-Wave checklist — 需补
- pip install 3-OS matrix 当前没 CI 跑, 需 Jordan 建 runner

---

**下一步 (等 Ethan Wave-1 返线)**:
1. CEO verify Ethan receipt empirical (`ls` task cards + `git log` commit + pytest pass)
2. 根据 Item #3-#9 task cards, CEO 代 spawn 4 engineers fan out
3. 同步 push Wave-2 kickoff (Ethan deadlock taxonomy v2 subagent)
4. 本 scope doc 挂 ARCH-17 companion 位置, Samantha archive to `knowledge/architecture/`
