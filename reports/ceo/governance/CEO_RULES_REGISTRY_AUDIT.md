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
2. → dispatch_board.py post `CZL-CEO-RULES-REGISTRY-CLOSE-GAP` (P0, 派 Ethan, scope=本 audit)
3. → CIEU emit `m_triangle_progress` axis=M-2 spec_ready
4. → TaskUpdate 标本 spec drafted, 依赖 Ethan claim
