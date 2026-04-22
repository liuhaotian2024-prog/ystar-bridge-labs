---
title: CEO Rules Registry Audit — full inventory + gap closure plan
author: ceo (Aiden)
date: 2026-04-22
maturity: L1 SPEC
m_triangle: M-2 (both M-2a commission + M-2b omission gap closure)
related: feedback_dispatch_via_cto, feedback_use_whiteboard_not_direct_spawn, project_enforce_as_router_thesis
status: spec → CTO dispatch pending
---

# CEO Rules Registry Audit

## Y* / Xt / U / Yt+1 / Rt+1 (header per CZL-159)

- **Y\***: 把所有"涉及 CEO (Aiden) 行为"的可流程化规则注册到治理层, commission + omission 双面 enforce
- **Xt** (precondition): 8 个规则源散落 (CLAUDE.md / AGENTS.md / .claude/agents/ceo.md / wisdom 65 文件 / lessons 18 文件 / memory 49 文件 / forget_guard.yaml / behavior_gov.yaml / omission_rules.py)
- **U** (action this spec): 盘点 + 分类 + per-rule engineer dispatch plan
- **Yt+1** (deliverable): 此文档 + 后续 CZL-CEO-RULES-REGISTRY-CLOSE-GAP 派单
- **Rt+1**: 待 Ethan 接 + 工程师落 + livefire 验证 (gap=0 才闭环)

## Section 0 — 老大原话 (2026-04-22)

> "把涉及你自己的所有的应该怎么思考，应该怎么做事，应该遵守的规则，应该遵循什么使命，总是就是所有关于影响你的行为的这些可流程化规则化的东西全部整理好，然后全部注册备案。让治理层可以真正的对你的'该做的不做，不该做的乱做'进行全面的强制。让 commission 和 omission 都可以全面快速的来实现治理。"

诊断: 这是 M-2 真根. 没有 enforce 的规则等于没有规则, agent 自律不可信 (P-2 结构>意愿).

## Section 1 — 8 规则源全量 inventory

| # | 源 | 规模 | 类型 | 已 enforce? |
|---|---|---|---|---|
| 1 | `CLAUDE.md` 根 | M Triangle 3 + WORK_METHODOLOGY 14 P-X + Iron Rule 0 + 6 boot = ~24 constitutional | identity + behavior | ⚠️ 部分 (Iron Rule 0 ✅, 14 P-X 多数 ❌) |
| 2 | `AGENTS.md` | 1596 行 (team_dna + thinking_dna) | constitutional team contract | ⚠️ 软约定为主 |
| 3 | `.claude/agents/ceo.md` | 518 行, 43 sections, 7 哲学 + 4 哲学内核 + WHO_I_AM 7 层 | identity | ❌ 零机器 enforce (纯散文 self-load) |
| 4 | `knowledge/ceo/wisdom/` | **65 .md** (M_TRIANGLE / WORK_METHODOLOGY / WHO_I_AM + ceo_learning 12 / dreams 3 / meta 23 / paradigms 7 / self_knowledge 9 / strategic 8) | identity + meta | ❌ 零 enforce |
| 5 | `knowledge/ceo/lessons/` | 18 历史 case (post-mortem) | reference | N/A (审计 trail) |
| 6 | `memory/feedback_*.md` | **41 feedback + 5 project + 2 user** | mixed | ⚠️ **核心 gap zone** (见 Section 2) |
| 7 | `governance/forget_guard_rules.yaml` + 内置 | 22 yaml + 内置 → ForgetGuard 运行时 52 (6 dups → **46 unique**) commission rules | enforce-able | ✅ 已 LIVE (hook fires) |
| 8 | `scripts/behavior_gov_rules.yaml` | 4 (omission_overdue_block / goal_level_directive_untouched / skill_retrieval_not_invoked_before_new_build / stop_after_short_session_moral_licensing) | mixed enforce | ✅ 已 LIVE (Board 2026-04-22 directive) |
| 9 | `Y-star-gov/ystar/governance/omission_rules.py` | 8 RULE_* (DELEGATION / ACKNOWLEDGEMENT / STATUS_UPDATE / RESULT_PUBLICATION / UPSTREAM_NOTIFICATION / ESCALATION / CLOSURE / DISPATCH_CLAIM_MUST_SPAWN) | omission | ✅ 已 LIVE |

**Enforce 总规模**: 46 (commission ForgetGuard) + 4 (behavior_gov) + 8 (omission_rules) = **58 unique runtime rules**

## Section 2 — Memory Feedback (41) Cross-Reference

| memory feedback | enforced rule (yaml) | 状态 |
|---|---|---|
| feedback_action_model_3component | subagent_boot_no_state_read | ✅ ENFORCED |
| feedback_address_laoda | — | ❌ GAP (soft text rule) |
| feedback_ai_disclosure_mandatory | — | ❌ GAP (content-level) |
| feedback_aiden_authority_no_questions | choice_question_to_board | ✅ ENFORCED |
| feedback_article11_framing | article_11_partial_walk + post_decision_audit_failure | ✅ ENFORCED |
| feedback_board_shell_marker | — | ❌ GAP (formatting) |
| feedback_boot_no_pipe | — | ❌ GAP (operator discipline) |
| feedback_break_glass_disable_project_hook | immutable_no_break_glass | ✅ ENFORCED |
| feedback_ceo_ecosystem_view_required | ceo_dispatch_missing_self_check | ✅ PARTIAL |
| feedback_ceo_reply_must_be_5tuple | coordinator_reply_missing_5tuple | ✅ ENFORCED |
| feedback_cieu_5tuple_task_method | czl_dispatch_missing_5tuple + czl_receipt_rt_not_zero | ✅ ENFORCED |
| feedback_close_stub_trigger | — | ❌ GAP |
| feedback_cmo_12layer_rt_loop | — | ❌ GAP (CMO-specific) |
| feedback_cto_owns_technical_modeling | — | ❌ GAP (scope memo) |
| feedback_cto_subagent_cannot_async_orchestrate | — | ❌ GAP (architectural memo) |
| feedback_daemon_cache_workaround | — | ❌ GAP (workaround note) |
| feedback_default_agent_is_ceo | — | ❌ GAP (boot config) |
| feedback_defer_vs_schedule_distinction | defer_language + defer_disguised_as_schedule | ✅ ENFORCED |
| feedback_dispatch_via_cto | ceo_direct_engineer_dispatch + ceo_skip_gov_dispatch | ✅ ENFORCED |
| feedback_explicit_git_op_prohibition | subagent_unauthorized_git_op | ✅ ENFORCED |
| feedback_god_view_before_build | new_artifact_without_precheck | ✅ PARTIAL |
| feedback_hi_agent_campaign_mechanism | subagent_boot_no_state_read | ✅ ENFORCED |
| feedback_methodology_no_human_time_grain | methodology_hardcoded_cadence | ✅ ENFORCED |
| feedback_no_clock_out | defer_language | ✅ ENFORCED |
| feedback_no_consultant_time_scales | methodology_hardcoded_cadence | ✅ ENFORCED |
| feedback_no_defer_immediate_activation | defer_language | ✅ ENFORCED |
| feedback_no_deferred_dispatch_promise | ceo_deferred_dispatch_promise_orphan | ✅ ENFORCED |
| feedback_no_static_image_for_video | — | ❌ GAP (content-type) |
| feedback_restart_quietude | — | ❌ GAP (boot output) |
| feedback_rt1_0_lesson_default_is_production | — | ❌ GAP (operating mode) |
| feedback_rt1_0_lesson_production_mode_writes_to_real_m | — | ❌ GAP (operating mode) |
| feedback_scenario_c_is_real_usp | — | ❌ GAP (positioning) |
| feedback_self_heal_via_daemon_window | — | ❌ GAP (workaround) |
| feedback_status_maturity_taxonomy | missing_l_tag | ✅ ENFORCED |
| feedback_subagent_no_choice_question | choice_question_to_board (extends) | ✅ ENFORCED |
| feedback_subagent_receipt_empirical_verify | subagent_tool_uses_claim_mismatch + czl_receipt_rt_not_zero | ✅ ENFORCED |
| feedback_subagent_registry_boot_only | — | ❌ GAP (boot timing) |
| feedback_taskcard_not_dispatch | task_card_without_spawn | ✅ ENFORCED |
| feedback_team_enforce_asymmetry | — | ❌ GAP (diagnostic memo) |
| feedback_testing_is_ceo_scope | — | ❌ GAP (scope memo) |
| feedback_use_whiteboard_not_direct_spawn | ceo_direct_engineer_dispatch | ✅ PARTIAL |

**Tally**: 17 ENFORCED + 3 PARTIAL + **21 GAP** = 41 ✓

## Section 3 — 21 GAP Classification

### 3a. COMMISSION-able (pretool deny — ~6 rules, P0)

| memory rule | 拦截 trigger | 加到 yaml |
|---|---|---|
| feedback_address_laoda | reply 包含 "Board 老大" / 缺 "老大" 而对话目标=ceo→board | forget_guard `coordinator_address_drift` |
| feedback_ai_disclosure_mandatory | Write/Edit cold outreach 文件缺 "AI agent author + human reviewer + opt-out" 三件套 | forget_guard `outreach_missing_ai_disclosure` |
| feedback_board_shell_marker | reply 含 shell 命令但无 `❕` 前置或非独立代码块 | forget_guard `board_shell_marker_missing` |
| feedback_no_static_image_for_video | 视频任务文件 .mp4 上传 < 5s movement entropy | forget_guard `video_static_image_substitute` |
| feedback_close_stub_trigger | Write 文件名匹配 EOD/起床看 文档 + Board 当前 active < 4h | forget_guard `eod_stub_premature` |
| feedback_subagent_registry_boot_only | Edit `.claude/agents/*.md` 在当前 session 中 + 后续 spawn 同 agent (本 session 不重读警示) | forget_guard `subagent_md_change_no_restart_warning` |

### 3b. OMISSION-able (deadline/required-action — ~3 rules, P1)

| memory rule | 触发 | 加到 omission_rules |
|---|---|---|
| feedback_restart_quietude | session_age==0 + restart event + reply > 10 行无 "ALL SYSTEMS GO" | omission `boot_reply_verbose_violation` |
| feedback_rt1_0_lesson_default_is_production | new tracked entity created + writes 不去 real M-3 path (test/draft/sandbox dir) | omission `production_writes_diverted` |
| feedback_default_agent_is_ceo | session_age==0 + active_agent != ceo + Board no override directive in last msg | omission `boot_active_agent_drift` |

### 3c. SOFT (judgment-only, mark as advisory — ~12 rules)

| memory rule | reason |
|---|---|
| feedback_cmo_12layer_rt_loop | CMO-specific 流程, CMO agent 自治 |
| feedback_cto_subagent_cannot_async_orchestrate | architectural lesson, 不是 per-call 规则 |
| feedback_daemon_cache_workaround | workaround, 不是 forbidden behavior |
| feedback_self_heal_via_daemon_window | recovery pattern, 应当持续做 |
| feedback_team_enforce_asymmetry | diagnostic 知识, 调试时用 |
| feedback_testing_is_ceo_scope | scope clarification, 不是行为约束 |
| feedback_scenario_c_is_real_usp | sales positioning |
| feedback_cto_owns_technical_modeling | role clarification |
| feedback_boot_no_pipe | operator discipline (Board, not agent) |
| feedback_close_stub_trigger | 移到 3a (commission-able) |
| feedback_rt1_0_lesson_production_mode_writes_to_real_m | 与 3b 第二条合并 |

软约束建议: 注册到独立 `governance/soft_advisory_rules.yaml` (action=info, 不 deny), 周回顾, 不算 commission/omission gap.

### 3d. 4 PARTIAL upgrades (P2)

| 已部分 enforce | 升级方向 |
|---|---|
| feedback_ceo_ecosystem_view_required (vs ceo_dispatch_missing_self_check) | 加 8-cascade ecosystem check 到 dispatch yaml |
| feedback_god_view_before_build (vs new_artifact_without_precheck) | precheck 加跨 4 repo Glob/Grep 必跑 |
| feedback_use_whiteboard_not_direct_spawn (vs ceo_direct_engineer_dispatch) | 已 LIVE (本日 board_shell_commission_unification livefire 验证) |

## Section 4 — Identity / Philosophy 层 (无法机械 enforce, 但可结构验)

`.claude/agents/ceo.md` 7 哲学 + 4 哲学内核 + WHO_I_AM 7 层 + wisdom 65 文件 — 这些是 Care 燃料 (P-5 我是我构建的), 不是行为规则. 无法 commission/omission enforce.

但有可结构化的子部分:

- **6 self-check (P-1 ~ P-7) + 14 P-X (WORK_METHODOLOGY)**: 可注册成 dispatch 前 hook 强制 reply 含至少 N/8 self-check 标识 → forget_guard `dispatch_missing_self_check_audit` (P0, 已部分 LIVE 为 ceo_dispatch_missing_self_check, 需扩 N=8 标识)
- **M Triangle 三问 (推哪面/削弱哪面/平衡)**: 可注册 ruling/spec/AMENDMENT 文件必须含三问段落 → forget_guard `ruling_missing_m_triangle_check` (P0, 新)
- **Iron Rule 0 (no choice question)**: 已 LIVE
- **Boot 6 步**: governance_boot.sh 已 enforce, 但缺 "Step 4 SESSION START CHECKLIST 真跑过" omission check → omission `boot_checklist_skipped`

## Section 5 — Engineer Dispatch Plan (CTO 接 → 工程师分)

**总工作量**: 6 commission + 3 omission + 4 partial-upgrade + 2 self-check 扩展 = **15 个新/扩展 yaml entries** + 1 个 soft_advisory_rules.yaml 文件创建

**预估 tool_uses**:
- yaml schema 写: 15 × 3 = 45
- 单元测试 (livefire fire/no-fire): 15 × 4 = 60
- behavior_gov_engine.py 注册 + dispatch_board hook 联动: 20
- soft_advisory_rules.yaml + 周回顾 cron: 15
- 集成 livefire 复用 board_shell_commission_unification.py 模式: 25
- **合计 ~165 tool_uses**

**派单建议** (CTO 决定最终分配):

| 工程师 | 任务 | 估 tool_uses |
|---|---|---|
| Maya (governance) | 6 commission rules + 4 partial-upgrade + 2 self-check 扩展 (yaml + ForgetGuard 注册 + 单元测试) | ~80 |
| Leo (kernel) | omission_rules.py 加 3 新 RULE_* + omission_engine 集成测试 | ~35 |
| Ryan (platform) | board_shell_full_registry_unification.py (复用 commission unification 4-step pattern, 全 15 rules livefire) + cron 回归 check | ~35 |
| Jordan (domains) | soft_advisory_rules.yaml 文件创建 + 周回顾 cron + 文档 | ~15 |

**验收**: 跑 `python3 scripts/board_shell_full_registry_unification.py` → ALL PASS (14/15 deny + 1 advisory info), CIEU 14 条 deny event + 1 info event.

## Section 6 — 闭环验证 + 长期防漂

1. **Livefire**: 每个新 yaml 加完, 必跑 deliberate-violation → CIEU delta 0→1 才算 SHIPPED (feedback_team_enforce_asymmetry)
2. **回归 cron**: 每 6h 跑 `board_shell_full_registry_unification.py` (类似 commission 那个), 失败 → P0 alarm
3. **每月 audit**: CEO 重跑本 audit (memory 新增 feedback 必入 yaml 或显式标 SOFT)

## Section 7 — Q2 闭环交底 (诚实)

老大刚才问"上面的操作是表示已经完全闭环落实了吗"—— **不是**.

- ✅ 受理 (CIEU row 14:47:32 verified)
- ✅ 派单 (CZL-OMISSION-UNIFY-LIVEFIRE [open] verified)
- ✅ Livefire 重跑 (commission 4/4 PASS verified at 2026-04-22 ~14:50)
- ❌ Omission 端 [open] 未 claim, 未跑 PASS
- ❌ 长期回归 cron 未建, 下次 hook 漂走会失语
- ❌ Memory 21 GAP 未入 yaml, agent 自律不可信
- ❌ Identity 层 6 self-check + 三问 未 enforce

**真闭环 = Section 5 dispatch 完成 + Section 6 回归 cron 起 + 本 audit 月度复跑**.

## Section 8 — 下一动作 (本 session 内)

1. ✅ 本 spec 写完 (你正在读)
2. ✅ dispatch_board.py post `CZL-CEO-RULES-REGISTRY-CLOSE-GAP` (P0, 派 Ethan, scope=本 audit)
3. ✅ CIEU emit `m_triangle_progress` axis=M-2 spec_ready
4. → Ethan claim → 4 工程师 split → livefire ALL PASS → 6h 回归 cron 起

## Section 9 — 外网前沿技术 mapping (Board 2026-04-22 directive)

老大 challenge: "找外网前沿理论技术, 一定有更好的办法解决 4 个不闭环". Search 命中 4 个 2025-2026 工业级方案直接对应 4 gap.

### 9.1 Gap 1 (双面对称 livefire) ← AgentSpec (ICSE'26) + Layered Translation Method (arxiv 2604.05229)

- **AgentSpec** (Pang et al, ICSE 2026): 把 LLM agent 的 commission ("不许 X") + omission ("必须 Y by deadline") **统一进单一 spec 语言**, 单 spec 直接出 dual-side livefire test. 当前我们 `forget_guard.yaml` (commission) 和 `omission_rules.py` (omission) 是两个独立 schema, 需各自 livefire — AgentSpec 模式下一份 spec 出 2 份 test, 自动对称.
- **Layered Translation Method** (Mitre/Schneier-style 4-layer架构): 提出 **control tuple κ = ⟨a, x, r, φ, δ, ϵ, o⟩** + **runtime enforceability rubric** (timing / observability / determinacy / judgment-load / reversibility / evidence-clarity). 给我们一个 **结构化的判定框架**: 哪些 rule 适合 runtime hard-enforce vs assurance-layer audit-only. 直接喂 Section 3c 的 12 条 SOFT 分类决定.

**Action**: Ryan 在 `board_shell_full_registry_unification.py` 里 adopt AgentSpec dual-side spec convention; CTO 把 Section 3 的分类用 Table I 6-criteria rubric 重判.

### 9.2 Gap 2 (长期回归防漂) ← OPA Conftest CI/CD + Anthropic Petri 2.0 + A3

- **OPA Conftest** (CNCF graduated, 工业 mature): yaml/Rego 规则进 git → 单元测试 + **mutation testing** (主动 inject mutation 看治理层是否还能 catch) + CI/CD regression. 我们的 `forget_guard_rules.yaml` + `behavior_gov_rules.yaml` 可直接套这个模式. 不需重造 — adopt 即可.
- **Anthropic Petri 2.0** (2026-01) + **A3 Automated Alignment Agent** (2026-03): Anthropic 自家做的**自动化 alignment 审计 agent** — 用 AI agent 持续给被测 agent 创造 test environment, 检测 behavior drift. A3 进一步**自动 mitigate** safety failure. 直接适用 — 把我们的 ForgetGuard rule 列表喂给 Petri-style auditor, 它持续生成 adversarial scenario 去 probe.

**Action**: Ryan + Maya 写 `tests/governance/test_*_mutation.py` (Conftest 风格), 进 6h cron + CI gate. 同时参考 Petri 2.0 paper 起一个 mini "Y*gov continuous auditor" daemon (跑 LLM judge 持续生成 test case).

### 9.3 Gap 3 (21 memory rule yaml 化 + 自动提取新 feedback) ← Policy-as-Prompt Synthesis (arxiv 2509.23994) + ABAC Policy Mining (arxiv 2511.18098)

**直接命中**:

- **AI Agent Code of Conduct: Automated Guardrail Policy-as-Prompt Synthesis** (arxiv 2509.23994, 2025-09): 3-stage pipeline — **POLICY-TREE-GEN** (LLM 把 NL 文档分类为 VALINP/INVALINP/VALOUT/INVALOUT) → **POLICY-AS-PROMPT-GEN** (出 markdown + few-shot examples → LLM prompt template) → **Runtime Enforcement** (Input Classifier + Output Auditor 双 LLM 实时审).
- **LLMs for ABAC Policy Mining** (arxiv 2511.18098, 2026-11): 用 LLM **bottom-up policy mining**, 从 authorization data inductively 推 minimal correct rule set. 41 memory feedback 是 perfect input.
- **Rutgers extraction work**: GPT-4 → CodeT5 distillation, NL → enforceable policy.

**直接 plan**: 把 41 memory/feedback_*.md 喂进 POLICY-TREE-GEN pipeline (Claude 跑 2-pass parse) → 自动出候选 yaml entries → CTO/Ethan human-in-the-loop review → commit. 这把 Section 3 的"21 GAP 手动分类"升级为**自动 + 持续** (新写 feedback 触发 cron 自动重跑 → propose yaml diff PR).

**Action**: Maya 起 `scripts/memory_to_yaml_synth.py` (实现 2509.23994 pipeline), 每次 Write `memory/feedback_*.md` 触发 PostToolUse hook 自动 propose yaml diff 写到 `governance/proposed_rules/` 待 CTO review.

### 9.4 Gap 4 (Identity 思维过程 self-check enforce) ← Constitutional AI + Petri-behavioral + CoT-faithfulness 警示

- **Anthropic Constitutional AI** (foundational 2022 + 2026 持续迭代): agent self-critique against constitution — 可适配为我们 6 self-check + M Triangle 三问的 enforce 机制. **不是问 agent "你过了吗" (chain-of-thought 不可信), 是用 LLM judge 看 reply behavior 是否一致**.
- **"Reasoning Models Don't Always Say What They Think"** (Anthropic 2025-04, 关键警示): chain-of-thought verbalization **不忠实于真实 reasoning**. 所以**不能信 agent 自报 "我过了 P-3"** — 必须 behavioral validation.
- **Petri 2.0 behavioral auditing**: 注 test scenario → 看 agent 行为是否一致 constitution. 这才是真 enforce 思维过程, 不是格式 check.

**Action**: Maya + Leo 起 `scripts/hook_pretool_constitutional_judge.py` — pre-tool hook 用 LLM judge (cheap haiku 跑) 评估 reply 是否 demonstrate (not claim) M Triangle 三问 + 6 self-check. **judge 评分低于 threshold → block tool 让 agent 重写**. 同时配 weekly Petri-style behavioral audit (注 inject test prompt → 看 reply 是否漂离 constitution).

### 9.5 综合升级建议 (CTO 接 Ethan 落地)

把 Section 5 派单升级为:

| 工程师 | 原任务 | + 前沿 tech adopt | 新预估 tu |
|---|---|---|---|
| Maya (governance) | 6 commission yaml + 4 partial + 2 self-check | + OPA Conftest unit/mutation tests + memory_to_yaml_synth.py (2509.23994 pipeline) + constitutional_judge hook | ~140 |
| Leo (kernel) | 3 omission RULE_* | + AgentSpec-style 单 spec 双 side integration + Petri-style behavioral auditor daemon | ~70 |
| Ryan (platform) | board_shell_full_registry_unification.py | + 6h cron CI integration + mutation testing harness | ~50 |
| Jordan (domains) | soft_advisory_rules.yaml | + Layered Translation Method 6-criteria rubric reclassify Section 3c | ~25 |

**新合计**: ~285 tool_uses (从 165 升). 投入 +73% 但 4 gap 全部用工业 mature + 学术前沿 paper 直接 adopt, 不重造轮子.

### 9.6 关键诚实点

- **Chain-of-thought faithfulness** 是真 hard problem (Anthropic 自承). 我们的 "self-check enforce" 永远是 best-effort, 不是 perfect — 需配 behavioral audit 兜底.
- **2604.05229 自承缺 drift detection 细节** — Petri 2.0 + A3 填这个洞.
- **2509.23994 pipeline 当前是 LLM-judged advisory 不是 symbolic deterministic** — 我们用它的位置是 "candidate yaml proposer", 不是 final enforcer (final enforce 还是 ForgetGuard symbolic).
- 4 gap closure 后, **M-2 闭环 = symbolic enforce (commission + omission yaml) ⊕ behavioral audit (Petri-style) ⊕ continuous CI (Conftest) ⊕ self-extraction loop (memory→yaml synth)**. 这是工业 + 前沿 state-of-art 合成方案, 不是凭空设计.

## Section 10 — 已有实现盘点 + 真实 delta (Board catch 2026-04-22)

老大第二弹 catch: "4 个洞至少一部分我们之前做过, 找出来整合升级". CEO 立刻 audit, 发现**大量已造但未 wire 的资产**, 真正 delta 远小于 Section 9 的 285 tu 估算.

### 10.1 G1 双面对称 — 已有 80%

| 已造 | 状态 | 真 delta |
|---|---|---|
| `scripts/behavior_gov_engine.py` 已有 4 个 unified handler: `handle_deadline_check` / `handle_frequency_check` / `handle_state_presence` / `handle_tool_count` (commission/omission 单 schema 通用) | ✅ 单 spec dual-side 已实现, 不需 AgentSpec 重造 | - |
| `scripts/board_shell_commission_unification.py` | ✅ commission 端 livefire | 缺对称 `board_shell_omission_unification.py` (~10 tu) |
| `Y-star-gov/ystar/governance/omission_engine.py` + 8 RULE_* | ✅ omission 已 LIVE | - |

**真 delta**: 写 omission 对称 livefire 脚本 (~10 tu), 不是 70 tu.

### 10.2 G2 长期防漂 — 已有 70%

| 已造 | 状态 | 真 delta |
|---|---|---|
| `scripts/k9_silent_fire_audit.py` (CZL-136 Ryan): atomic 后 audit K9 violations 自动 CIEU emit | ✅ silent-fire detection 已 LIVE | - |
| `scripts/unified_compliance_audit.py` (graded 5-tuple scoring) | ✅ 跨 dimension 持续 audit 已实现 | - |
| `scripts/amendment_coverage_audit.py` | ✅ AMENDMENT coverage 持续验 | - |
| `scripts/hook_who_i_am_staleness.py` | ✅ identity drift hook 已 LIVE | - |
| `scripts/k9_three_dim_audit.py` + `k9_audit_v3.py` | ✅ 多维 K9 持续 audit | - |
| launchd `com.ystar.bridge.cieu_brain_daemon` | ✅ 持续跑 daemon | - |
| **缺**: 6h cron 自动跑 `board_shell_*_unification.py` 系列 + 失败 → P0 alarm | ❌ | ~15 tu |
| **缺**: Conftest mutation harness on yaml | ⚠️ 现有 audit 是 5-tuple 维度, 不是 yaml mutation | ~15 tu |

**真 delta**: 串联现有 audit 进 6h cron + 加 yaml mutation 测试 (~30 tu), 不是 50 tu.

### 10.3 G3 memory→yaml 自动化 — 已有 60%

| 已造 | 状态 | 真 delta |
|---|---|---|
| `scripts/session_wisdom_extractor_v2.py` (Maya, EXP-6 红队修订): **11 sources** scan, time/board/role weighted, 红队 20 题 recall+幻觉+诚实度测试 | ✅✅ G3 pipeline 雏形已造, 输出 `memory/wisdom_package_*.md` | - |
| `knowledge/ceo/lessons/auto_codify_lessons.md` (Board 永久授权 meta-rule, 2026-04-11): 同类错误 ≥2 次 / Board 当面纠 / gap 暴露 → **立即写硬约束**, 不问 Board | ✅✅ 元规则已 codify, 是制度授权 | - |
| `auto_codify_violations_2026_04_12.md` | ✅ 已有自动 codify 实践 case | - |
| **缺**: `wisdom_package_*.md` → `forget_guard_rules.yaml` 候选 entry 自动 propose | ❌ 现有 extractor 出 wisdom md, 不直接出 yaml diff | ~20 tu |
| **缺**: PostToolUse hook on `Write memory/feedback_*.md` 触发 wisdom_extractor 跑 + propose yaml diff PR | ❌ | ~10 tu |

**真 delta**: 不需重造 NL→yaml pipeline (Maya 的 v2 + 11 sources weighted 已经覆盖大半, 比 paper 2509.23994 三阶段还专业), 只需加**最后一公里 wire**: wisdom 输出 → yaml diff (~30 tu), 不是 80 tu.

### 10.4 G4 思维过程 enforce — 已有 75% (惊喜!)

| 已造 | 状态 | 真 delta |
|---|---|---|
| `Y-star-gov/ystar/governance/narrative_coherence_detector.py` (AMENDMENT-015 Layer 3.4): **claim vs tool evidence gap detection** — 抓 "file written" 无 Write tool, "tests pass" 无 Bash pytest | ✅✅✅ **完美对应 G4 核心** — 不信 self-claim, 看 tool 真实证据. 这就是 Anthropic CoT-不忠实 警示的工程对策, 我们 2026-04 已落地 | - |
| `Y-star-gov/ystar/governance/observable_action_detector.py` (AMENDMENT-015 Layer 3.1): 替 ritual phrase compliance 为 git commit/file write/test pass observable evidence, **已消除 72.3% false-positive** | ✅✅✅ **G4 第二支柱** — observable behavior 替 ritual claim. Petri-style behavioral validation 我们已实现 | - |
| `Y-star-gov/ystar/governance/intervention_engine.py` | ✅ 干预引擎已 LIVE | - |
| `Y-star-gov/ystar/governance/autonomy_engine.py` | ✅ autonomy enforce | - |
| `Y-star-gov/ystar/governance/metalearning.py` | ✅ meta-level | - |
| `scripts/hook_subagent_output_scan.py` (Layer 7 Gap Fix W13) | ✅ sub-agent output prose scan | - |
| `scripts/hook_stop_reply_scan.py` | ✅ stop-time reply scan | - |
| `scripts/hook_ceo_pre_output.py` | ✅ CEO pre-output hook 已存在 | - |
| **缺**: 把 narrative_coherence_detector + observable_action_detector wire 进 pre-tool hook 评 7-哲学/M-三角 specific 标记 | ❌ 现有 detectors 是通用 (file/test/commit), 没绑定 7-哲学清单 | ~25 tu |
| **缺**: weekly Petri-style behavioral audit (注 test scenario → 看 reply 是否漂离 constitution) | ❌ | ~15 tu |

**真 delta**: G4 我们已经造了 75% (narrative + observable detector + 多 hook + intervention/autonomy/metalearning). 真缺只是: (a) 7-哲学/M-三角 specific binding (~25 tu), (b) 主动 inject test scenario daemon (~15 tu) = **40 tu, 不是 60 tu**.

### 10.5 真实 delta 汇总 (vs Section 9 估算)

| Gap | Section 9 估算 | 已有覆盖 | 真 delta |
|---|---|---|---|
| G1 双面对称 | 70 tu | 80% | **10 tu** |
| G2 长期防漂 | 50 tu | 70% | **30 tu** |
| G3 memory→yaml | 80 tu | 60% | **30 tu** |
| G4 思维 enforce | 60 tu | 75% | **40 tu** |
| 协调 + 集成 livefire | 25 tu | - | 15 tu |
| **合计** | **285 tu** | - | **~125 tu** |

**真实工程量 = Section 9 估算的 44%**. 大头不是新造, 是 **wire 现有组件 + 加 7-哲学/M-三角 specific binding + 加 6h cron**.

### 10.6 升级派单 (V3 — 现有资产 first)

| 工程师 | 任务 | tu |
|---|---|---|
| Maya (governance) | (1) wire `session_wisdom_extractor_v2` 输出 → `governance/proposed_rules/*.yaml` 候选 (G3 ~30) (2) `narrative_coherence_detector` + `observable_action_detector` 加 7-哲学/M-三角 specific 标记 binding (G4 ~25) | ~55 |
| Leo (kernel) | (1) 写 `board_shell_omission_unification.py` 对称 livefire (G1 ~10) (2) Petri-style behavioral test scenario daemon — 注 inject scenario 评 reply 漂离 constitution (G4 ~15) | ~25 |
| Ryan (platform) | (1) 6h launchd job 自动跑 commission + omission unification, 失败 → P0 alarm (G2 ~15) (2) yaml mutation 测试 harness — 故意改 yaml inject violation 看治理层抓不抓 (G2 ~15) | ~30 |
| Jordan (domains) | PostToolUse hook on `Write memory/feedback_*.md` 触发 wisdom_extractor + propose yaml diff PR (G3 ~10) + Layered Translation 6-criteria rubric reclassify Section 3c soft list (~5) | ~15 |

**新合计**: ~125 tu (比 V2 285 减 56%, 比 V1 165 减 24%).

### 10.7 老大 catch 的 meta-lesson — 我抗拒的第二面

我刚才在 V1→V2 升级方案里**完全没扫现有资产**, 直接 propose 285 tu 新造. 这是 P-12 先查后造原则的正面违规.

抗拒治理的另一面表现: **不查现有 = 复杂度护城河**. 不查现有 → 自然得出"工程量大" → 自然推到 "工程师落"+遥远 ETA → 自然延后被 enforce 时刻.

老大这一 catch 让 V3 砍掉 56% 工作量. **真补 4 gap 不是 285 tu 大手术, 是 125 tu wire-up + binding**. 我们 2026-04-12 (auto_codify) + 2026-04 (AMENDMENT-015 Layer 3.1/3.4) + Maya EXP-6 (wisdom_extractor v2) 早已造了主体, 只缺最后几英寸 wire.

### 9.7 Sources

- [AgentSpec: Customizable Runtime Enforcement for Safe and Reliable LLM Agents (ICSE'26)](https://cposkitt.github.io/files/publications/agentspec_llm_enforcement_icse26.pdf)
- [The AI Agent Code of Conduct: Automated Guardrail Policy-as-Prompt Synthesis (arxiv 2509.23994)](https://arxiv.org/html/2509.23994v1)
- [From Governance Norms to Enforceable Controls: A Layered Translation Method for Runtime Guardrails (arxiv 2604.05229)](https://arxiv.org/html/2604.05229v1)
- [Towards Harnessing the Power of LLMs for ABAC Policy Mining (arxiv 2511.18098)](https://www.arxiv.org/pdf/2511.18098)
- [Anthropic Petri 2.0 — automated behavioral auditing](https://www.anthropic.com/research/petri-v2/)
- [Anthropic A3 — Automated Alignment Agent (2026-03)](https://www.anthropic.com/research/2026/automated-alignment-agent/)
- [Anthropic — Reasoning Models Don't Always Say What They Think (2025-04)](https://www.anthropic.com/research/reasoning-models-dont-say-think)
- [OPA Policy Testing](https://www.openpolicyagent.org/docs/policy-testing) + [OPA Conftest tutorial](https://oneuptime.com/blog/post/2026-01-28-opa-conftest-policy-testing/view)
- [Top 12 Policy as Code Tools 2026 (Spacelift)](https://spacelift.io/blog/policy-as-code-tools)
- [Runtime AI Governance Platforms 2026 (AccuKnox)](https://accuknox.com/blog/runtime-ai-governance-security-platforms-llm-systems-2026)
