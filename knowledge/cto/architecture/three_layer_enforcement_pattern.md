# Three-Layer Enforcement Pattern (三层保障)
**Author**: CEO (architectural primitive, 2026-04-13)
**Status**: L1 SPEC — to be wired into ForgetGuard rule schema by Ethan-CTO
**Applied first in**: AMENDMENT-023 (Article 11 → CEO OS integration)

## 命题

任何治理 / 强制 / 学习机制要真"保障到位"，必须**同时**实现 3 层：

| 层 | 时机 | 作用 | 失败模式 (单层缺) |
|---|---|---|---|
| **L_PRE 事前 (Proactive Injection)** | agent 即将做某行为之前 | 把规则 + 上下文 inject 进 attention，使 agent **想起来** | 缺则全靠 agent 自己记得 = 不可靠 (LLM 没持续身份) |
| **L_MID 事中 (In-Flight Enforcement)** | agent 行为执行过程中 | hook 拦截 / warn-with-recipe / emit progress event | 缺则 agent 错了不知道 / 错了无审计 |
| **L_POST 事后 (Post-Audit & Drift)** | 行为完成后 + 周期性扫描 | 检测累积 drift, spike alerts, secretary auto-fix | 缺则一次性失败可放过, 系统性问题滞后发现 |

## 必须 3 层并存的原因

只 L_PRE = 没真强制（agent 可忽略 reminder）
只 L_MID = 救火式被动（不预防, 不学习）
只 L_POST = 完全 reactive（错误已发生）
2 层 = 仍漏一种失败模式

**3 层并存** = 闭环：预防 → 拦截 → 审计 + 修复 → feedback 回 L_PRE 强化 reminder

## 已应用 3 层的现有机制

| 机制 | L_PRE | L_MID | L_POST |
|---|---|---|---|
| A019 maturity gate | hook_user_prompt_tracker 注入 L-tag reminder ✓ | ForgetGuard `missing_l_tag` rule warn ✓ | hourly drift summary cron ✓ |
| A018 whitelist | UserPromptSubmit 注入 WHITELIST_HINT ✓ | hook_client_labs.sh emit MATCH/DRIFT ✓ | daily coverage cron + GAP event ✓ |
| A020 ForgetGuard | (依赖 hook 触发) | 5 rules emit warn-with-recipe ✓ | forget_guard_summary hourly ✓ |
| A022 dialogue→contract | (依赖 hook 触发) | dialogue worker emits CONTRACT_DRAFT ✓ | drift_checker 5min cron ✓ |
| A023 Article 11 (待 ship) | hook_user_prompt_tracker 注入 7-layer reminder | article_11_tracker emit LAYER_X_COMPLETE | hourly ARTICLE_11_DRIFT_SPIKE |

## 强制规则 (适用于所有未来 amendment)

**任何新 enforcement amendment 6-pager §2 提议必须明确给出 3 层各自实现路径**。否则 6-pager L1 → L2 时被 ForgetGuard 拒（待添加新 rule `enforcement_amendment_missing_three_layers`）。

## ForgetGuard 集成 (待 Maya 实现)

`governance/forget_guard_rules.yaml` 加：
```yaml
- id: enforcement_amendment_missing_three_layers
  trigger:
    tool: ["Write", "Edit"]
    conditions:
      - type: path_match
        pattern: "reports/proposals/charter_amendment_.*\\.md"
      - type: content_missing
        keywords: ["L_PRE", "L_MID", "L_POST", "事前", "事中", "事后"]
        all_required: true  # 三个都缺才 trigger
  action: warn
  recipe: "Per knowledge/cto/architecture/three_layer_enforcement_pattern.md, every enforcement amendment must specify L_PRE + L_MID + L_POST implementation. See A019/A018/A020/A023 examples."
  cieu_event: ENFORCEMENT_PATTERN_INCOMPLETE
```

## 元根因

LLM agent 没有持续身份 → 任何机制只靠"agent 记得规则"必然失败。3 层是绕过这个限制的工程方法：把"记得"分散到 attention injection + tool call hook + cron audit 三处，任一处覆盖即可生效。

**原创性声明**: 这不是从外部框架抄的 (LangChain/AutoGen/Anthropic guardrails 都没有此 pattern)。是 Y* Bridge Labs 实战 (2026-04-13 session) 经过 5+ 次"装了 enforcement 但 agent 仍漏" 的失败后总结的。
