---
Audience: Ethan Wave-2 primary (Axis-A/B/C Guard+Guide refactor mandate) + Maya Wave-2 (forget_guard 中坚) + Board review
Research basis: `governance/forget_guard_rules.yaml` (37 rules empirical grep) + `scripts/behavior_gov_rules.yaml` (4 rules) + `scripts/amendment_coverage_audit.py` output (42 rules audited, 19 Remediation / 0 Fulfiller / 42 Test)
Synthesis: Preliminary Axis-A/B/C classification of 41 explicit rules + 2639 LOC boundary_enforcer. Saves Ethan Wave-2 ~8-10 tu enumeration overhead; Ethan refines with precision/recall live-fire.
Purpose: Start-data for "Guard+Guide Refactor" Wave-2 (replaces "Great Prune"). Each rule annotated with preliminary (a) LLM bias suppressed, (b) M-alignment, (c) REDIRECT actionable? — all three must be answered per Board 2026-04-24 directive.
---

# Rule Inventory — Preliminary Axis-A/B/C Classification

**Total explicit rules**: 37 forget_guard + 4 behavior_gov = **41 yaml rules** + 2639 LOC boundary_enforcer Python + 17 Iron Rules (CLAUDE.md + knowledge/ceo/iron_rules.md) + CZL-159 U-workflow + 42 amendment_coverage

## Axis-A (反 LLM 训练偏好) — KEEP + STRENGTHEN + 必补 REDIRECT

| Rule ID | LLM Bias Suppressed | REDIRECT Status | Action |
|---|---|---|---|
| missing_l_tag | anti-LLM-optimism-about-done | 无 (只警告 "加 L-tag") | **补**: L-tag template 自动 suggest |
| defer_language | anti-LLM-vague-time-estimate | 无 | **补**: 替换命令 "用 tool_uses 单位" |
| defer_language_in_commit_msg | 同上 | 无 | 同上 |
| defer_language_in_echo | 同上 | 无 | 同上 |
| choice_question_to_board | Iron Rule 0 anti-avoid-conflict | 有 (recipe: "pick best + execute") | **LIVE LOCKED** |
| czl_dispatch_missing_5tuple | anti-LLM-verbose + 强制结构 | 部分 (5-tuple template) | **补**: YAML frontmatter schema |
| czl_receipt_rt_not_zero | anti-LLM-optimism (hallucinated done) | 无 | **补**: empirical verify checklist |
| subagent_no_commit_after_5_writes | anti-LLM-over-autonomous (git op 冲动) | 有 | **LIVE LOCKED** |
| backlog_as_defer_disguise | anti-LLM-avoidance | 无 | 补 |
| ceo_no_midstream_checkin | anti-LLM-over-consultative | 无 | 补 (定义 checkpoint 条件) |
| dialogue_contract_drift | anti-LLM-context-drift | 无 | 补 |
| ceo_p1~p14 + m_triangle_three_question_claim_no_evidence (15 条) | anti-LLM-claim-without-evidence (P-4/P-14 各变体) | 无 | 批量补同一 REDIRECT template: "附 artifact ref (commit / pytest / ls 输出 / CIEU event_id)" |

**Axis-A 小计**: ~28 rules (含 15 条 ceo_pN 批量), 全部 KEEP, ~70% 缺 REDIRECT 需补

## Axis-B (M-aligned product core) — KEEP + 每条 DENY 必配 actionable REDIRECT

| Rule ID | M-alignment | REDIRECT Status | Action |
|---|---|---|---|
| enforcement_gap_persistent | M-2b (omission 持续检) | 有 (指向 auto_enforce_meta.md 决策树) | **LIVE LOCKED** — 本 rule 就是 Guard+Guide 范本 |
| immutable_no_break_glass | M-2a charter 保护 | 无 (只 DENY) | **补**: "走 AMENDMENT flow, see RULE-CHARTER-001" |
| article_11_partial_walk | M-2a + M-2b Article 11 完整性 | 部分 | 补 |
| decision_without_article_11 | M-2b (必走 Article 11) | 部分 | 补 |
| article_11_post_decision_audit_failure | M-2b (post-audit) | 无 | 补 |
| realtime_artifact_archival_sla | M-2b (artifact 落盘 SLA) | 无 | 补 |
| cto_hourly_patrol_missed | M-2b (CTO 主动巡逻 schedule) | 无 | **审视**: 这是 Axis B 还是 C? 若 "CTO 小时级巡逻" 不防 M harm, 可能降 Axis C |
| cmo_weekly_readme_audit_missed | 同上 | 无 | 同上审视 |
| session_age_concurrency_cap | M-2a (concurrent spawn cascade risk) | 有 (cap 定义) | **LIVE LOCKED** |
| **behavior_gov: omission_overdue_block** | M-2b (omission 硬拦) | 有 | **LIVE LOCKED** |
| **behavior_gov: goal_level_directive_untouched** | M-2b (目标传导链) | 有 | **LIVE LOCKED** |
| **behavior_gov: stop_after_short_session_moral_licensing** | M-2a + anti-LLM-moral-licensing | 有 | **双轨 Axis A+B LOCKED** |
| **behavior_gov: skill_retrieval_not_invoked_before_new_build** | M-2a (P-12 先查后造) | 有 | LOCKED |

**Axis-B 小计**: ~13 rules, 全 KEEP, 80% 有 REDIRECT 或 partial (behavior_gov 4 条质量高, 是 Wave-2 的 quality benchmark)

## Axis-C (纯行政 ghost — DELETE 候选)

| Rule ID | 为什么是 Axis C? | 替代 |
|---|---|---|
| **must_dispatch_via_cto** | 防"CEO 绕 CTO" 但无 M harm 证据 (CTO 已 author task card 时 CEO 代 spawn 是 legitimate 路径); redirect 指向未 deploy 的 `gov_delegate` tool | **删** OR 加 "pre-authored task card 白名单 exception" |
| ceo_writes_code | 防 CEO 越权写代码, 但如果 CEO 跑 empirical verify script 也拦 — false-positive 率未知 | **审视**: 要么删, 要么加 "read-only + verify script" exception |
| ceo_engineering_boundary | 同上 | 同上 |

**Axis-C 小计**: ~3 确定 + 2 候选, 需 Wave-2 live-fire 确认 false-positive 率再删

## 不在 YAML 的 rule 层 (Wave-2 加扫)

- **boundary_enforcer.py 2639 LOC**: Python 硬编码 rule, 需 Maya (AMENDMENT-022 Step 3 directive) 迁 YAML. 预估 18-22/25 migratable.
- **Iron Rules** (CLAUDE.md charter 里): Iron Rule 0 / 1.5 / 3 + 铁律 3-channel — 全 Axis A+B LOCKED, 不动.
- **CZL-159 CEO PRE-OUTPUT BLOCK** (U-workflow header): Axis A (anti-verbose-no-audience), 但今晚 git commit msg false-pos, 降级成 scope="knowledge/ + reports/ctos/"(doc only), 不 enforce git commit msg.
- **42 amendment_coverage rules**: 42 Test ✓ / 19 Remediation / 0 Fulfiller — 20 条有 rule 但无 remediation(REDIRECT)是 Wave-2 核心 gap

## Wave-2 Ethan 执行 checklist

1. 对 A 轴 20 条待补 REDIRECT: 每条写 actionable recipe string (参 `enforcement_gap_persistent` 格式)
2. 对 B 轴 2-3 条待补 REDIRECT: 同上
3. 对 C 轴候选 5 条: live-fire precision 测 (7d CIEU false-positive sample), >20% false-pos 立删
4. 对 boundary_enforcer.py 迁 18-22/25 rule 到 YAML
5. 对 42 amendment_coverage Fulfiller 0/42 gap: 每条补 "满足该 rule 的 positive action" spec
6. 加 live-fire 覆盖率 target: 每 rule 必有 deliberate-violation test → CIEU delta 0→1 empirical
7. 加 Microsoft AGT OWASP 10 agentic risk mapping (AGT-MAPPING-1)

## 诚实 gap

本 preliminary classification 是 CEO 3-tool-use 过 yaml 头 + 直觉分类, **未 Ethan peer review + 未 live-fire 验**. 每条的 final Axis 归属以 Wave-2 Ethan 实测为准. 如 `cto_hourly_patrol_missed` 可能其实是 Axis C (admin 巡逻流程而非 M-2b 真 omission), 需 empirical 数据决.
