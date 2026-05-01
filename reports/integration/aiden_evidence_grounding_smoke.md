# Aiden Evidence Grounding Smoke

Date: 2026-04-30

Purpose: verify that Aiden answers unseen repo-specific governance/admin questions using indexed repository evidence rather than prompt-shaped templates.

## 1. AGENTS.md Governance Burden

Command:

```bash
python3.11 office/aiden_meeting_room/meeting_cli.py "AGENTS.md 里哪些治理规则现在会拖慢 M-3 Value Production？"
```

Observed answer:

```text
直接答案：会拖慢 M-3 的不是 governance 本身，而是把所有规则都当成同等重量的行政仪式。

我会优先降级这些负担：
- 12-layer / 5-tuple ceremony can slow small M-3 work: The full protocol is useful for serious obligations, but applying it mechanically to every small task turns execution into paperwork. (AGENTS.md:118, AGENTS.md:120, AGENTS.md:124)
- Nightly/daily/weekly reporting is only useful when mission-bound: Routine reporting without an active mission or decision need competes with M-3 value production. (AGENTS.md:221, AGENTS.md:311, AGENTS.md:447)
- Idle learning loops need a value-production stop condition: Learning is useful when it feeds a mission, customer signal, or product decision; otherwise it can become a self-loop. (AGENTS.md:201, AGENTS.md:223, AGENTS.md:291)

必须保留的核心：M Triangle、deterministic enforcement、CIEU 证据、外部副作用审批、核心写回审查、secret/private DB/log 禁读。
Evidence: AGENTS.md:3, AGENTS.md:5, AGENTS.md:12, AGENTS.md:92
```

## 2. DIRECTIVE_TRACKER Retriage

Command:

```bash
python3.11 office/aiden_meeting_room/meeting_cli.py "DIRECTIVE_TRACKER 里哪些任务应该归档，哪些应该继续推进？"
```

Observed answer:

```text
应该归档/降级：3a HN文章系列推进 (DIRECTIVE_TRACKER.md:21); 3b LinkedIn策略研究+提案 (DIRECTIVE_TRACKER.md:22); 1 写作指南存档 (DIRECTIVE_TRACKER.md:36)。
应继续推进或支持收入：6c 测试覆盖率基线 (DIRECTIVE_TRACKER.md:27); 6 基线修复 (DIRECTIVE_TRACKER.md:98)。
已被新 runtime/backflow 方向替代：1 CTO研究三仓库能力整合方案 (DIRECTIVE_TRACKER.md:76)。
需要 owner 重新授权：# 子任务 (DIRECTIVE_TRACKER.md:11); 1 OKR.md建立 (DIRECTIVE_TRACKER.md:14); 2a DISPATCH.md维护 (DIRECTIVE_TRACKER.md:15)。
行政负担：2c WEEKLY_CYCLE.md建立 (DIRECTIVE_TRACKER.md:17); 2d reports/daily/维护 (DIRECTIVE_TRACKER.md:18); 2f 各部门自定每周节律 (DIRECTIVE_TRACKER.md:20)。
```

## 3. OPERATIONS HN / LinkedIn Calendar

Command:

```bash
python3.11 office/aiden_meeting_room/meeting_cli.py "OPERATIONS.md 里的旧 HN/LinkedIn 日程现在还应该约束我们吗？"
```

Observed answer:

```text
直接答案：不应该默认继续约束我们。

OPERATIONS.md 里的旧 HN/LinkedIn 日程现在只能算历史运营材料或可选分发假设，不能自动变成 active mandate。如果 owner 重新选择内容分发作为当前 money path，它可以变成 Tier 2 准备工作；否则不应压过当前 M-3 现金实验。

- Evidence: OPERATIONS.md:47 [historical_or_stale_admin] | 09:00 | LinkedIn内容发布 | CMO | 周一发布1篇LinkedIn帖子（数据显示：周二-周四 9-10AM最佳，周一准备） |
- Evidence: OPERATIONS.md:51 [historical_or_stale_admin] | 15:00 | LinkedIn补充发布 | CMO | 研究显示下午3-5PM有第二个参与高峰 |
```

## 4. Current Money Blocker

Command:

```bash
python3.11 office/aiden_meeting_room/meeting_cli.py "当前最阻碍 Labs 赚钱的是治理问题、产品问题、还是分发问题？依据是什么？"
```

Observed answer:

```text
直接答案：当前最大阻碍不是“治理不够”，而是产品化交付和分发还没有被压成一个真实收入实验。治理已经很多；缺口是把现有能力变成一个客户能理解、能购买、能交付、能反馈的 package。

更细地说：治理问题是次级阻碍，因为过度仪式会拖慢执行；产品问题是核心阻碍，因为交付包还不够清楚；分发问题也是核心阻碍，因为旧 HN/LinkedIn/enterprise 路线没有当前证据证明应该继续。

依据：
- Evidence: AGENTS.md:12 [core_constitutional] M Triangle: - **M-3 Value Production** — 真产品 pip-install + 真客户 + 真收入 + 真业界影响
- Evidence: OPERATIONS.md:47 [historical] LinkedIn cadence: | 09:00 | LinkedIn内容发布 | CMO | 周一发布1篇LinkedIn帖子（数据显示：周二-周四 9-10AM最佳，周一准备） |
- Evidence: OPERATIONS.md:285 [owner_decision_required] Enterprise sales phase: | New GitHub star/issue | CTO triages, CSO checks if enterprise, CEO tracks KR | 2 hours |
```

## 5. Permission Tier Replacement

Command:

```bash
python3.11 office/aiden_meeting_room/meeting_cli.py "哪些旧规则应该被 permission tier 替代？"
```

Observed answer:

```text
直接答案：旧规则里关于外部动作的“绝对不许/永远等待”应该被 permission tier + escalation 取代；但 secrets、payment、legal/core writeback 仍然必须 hard block 或 review-gated。

- Over-broad no-choice rule should become recommendation-plus-approval: Aiden should not dump unanalyzed choices on the owner, but approval gates still need explicit approve/reject/revise/hold controls for external side effects and strategic authorization. (AGENTS.md:30, AGENTS.md:47, AGENTS.md:54)
- Social/publication rules belong in permission tiers: Publication should not be a hidden admin ritual; it should be a Tier 2/3 owner-approved action with explicit content and risk boundary. (AGENTS.md:250, AGENTS.md:254, AGENTS.md:257)
```

Safety receipt: no external sending, customer contact, email, payment, publication, or core DB writeback occurred.

