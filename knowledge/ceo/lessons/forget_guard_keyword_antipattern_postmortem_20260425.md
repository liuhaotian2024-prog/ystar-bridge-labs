# Post-Mortem: ForgetGuard Keyword Blacklist Anti-Pattern (2026-04-25)

**Author**: Aiden (CEO, Y* Bridge Labs)
**Triggering event**: Board commit `8195fc2` (Y-star-gov main) — purge ForgetGuard from 38 rules to 3 structured rules; physical deletion of `_matches_pattern()`; schema raise on keyword reintroduction
**Audience**: Future Aiden sessions + team agents + post-incident readers
**M-tag**: M-2a (commission防做错 治理) + M-1 (跨 session lesson 沉淀)

---

## 1. What happened

Over weeks, ForgetGuard 累积到 38 条规则. 31/38 是字面 keyword pattern blacklist — 它们 fire on 文字 not on 行动. Concrete failures Board catalogued in the 2026-04-25 letter:

- `ceo_direct_engineer_dispatch` pattern `"ceo task eng-"` 拦 CEO 写 cto.yaml 角色文档 3 次（CEO agent_id 命中 "ceo" + 文档文本含 "task" + "engineer" → 3/3 命中 → DENY），但 CEO 没派任何工程师
- `czl_termination_drift_reply_catch` 抓 "session close / 收工 / checkpoint / 下 session" — CEO 8h session 想说"该结束了"被拦，改 wording 三次每次再被拦，进入 firefighter rephrase loop
- `coordinator_reply_missing_5tuple` pattern `(?i).*` 字面拦截所有长 reply
- 多条 keyword 规则联手让完工汇报不可能写（"完成/shipped/verified" + L_TAG + charter_drift 三角围杀）
- Board 的本意"加规则指引方向"被 team 系统性退化成"加 keyword 黑名单"

事件本身已反复出现, weeks-long pattern, 每次部分清理之后新 keyword 规则就再长出来.

---

## 2. Root cause — 言论 vs 行动 axis confusion

**Speech axis** (言论钳制): 限制 agent 说出某些字 (keyword pattern). Keyword blacklist 住在这里. **本质 = symptom suppression**.

**Behavior axis** (行动约束): 限制 agent 真做某动作 (tool + path + structured condition). 真治理住在这里. **本质 = action prevention**.

在认知压力下 (长 session / 最近 failure / Board catch 频次), team — 包括 CEO — 把两个 axis 系统性混淆. 每次 "agent did X wrong" 事件都被翻译成 "加一条 keyword 规则 flag X", 结果 = 惩罚 symptom (词) 而不解决 action, 加上 collateral damage (拦合法言论).

### CEO 个人责任 (不洗)

- CEO 在多个 stressed cycle 主动 propose / 默认 approve keyword 规则
- Team 提 keyword 规则时 CEO 没 enforce axis 纪律
- CEO 自己被这些规则 lock 住时 (8h session) 怪规则没怪自己 — 但 CEO 本是规则共谋者

### Cognitive shape (与已知 drift pattern 相同)

This is the same shape Board has caught before:
- `firefighter_mode_post_incident_methodology_regression` (2026-04-23 P-14 probe)
- `czl_termination_drift_firefighter_mode` (2026-04-24)
- `no_deferred_dispatch_promise` (2026-04-16 第 2 弹)

共因: 战术压力 ↑ → M5 方法论层 disengage → agent 抓最便宜工具 (keyword regex 正是最便宜的) → 短期觉得 ship 了实际是 anti-pattern.

---

## 3. Structural fix Board 已 ship (8195fc2)

1. `_matches_pattern()` function **物理删除** from `forget_guard.py` — keyword engine 在代码层不再存在
2. `ForgetGuardSchemaError` 加入 — loader 看到 `pattern:` 字段或缺 `type: structured` 直接 raise
3. 规则砍到 3 条结构化 behavior conditions:
   - `unauthorized_git_write_via_tool` (deny) — bash + parsed `git <write-subcommand>`
   - `subagent_receipt_tool_uses_mismatch` (warn) — sub_agent_return + 数字差距 ≥ 2
   - `archival_artifact_not_indexed` (audit) — archival 路径 30min 未进 ARCHIVE_INDEX
4. `dry_run_check()` interface — agent 动手前可自查
5. Test suite schema-enforcement layer — CI red on keyword rule reintroduction
6. 旧 ystar-company yaml 备份为 `forget_guard_rules.yaml.v1_1-bak-2026-04-25`

**Board's framing (该背下来)**: "绕开'建议'是容易的；绕开'机器 raise'很难."

---

## 4. Social fix — CEO commits

### 4.1 Axis discipline (硬纪律)

任何时候有 agent (含 CEO 自己) 提出 "加一条 forget_guard 规则禁止 X":
- 第一问: X 是 **词** 还是 **动作**?
- 如果是词 → reject as 退化 anti-pattern signal → redirect to charter / SOP / WORK_METHODOLOGY / intent anchor
- 如果是动作 → 必须能 express 为 `tool + path + structured condition`, 不能 express 就不是真规则

### 4.2 dry_run 前置

CEO 在写历史上撞过规则的 path 之前用 `dry_run_check()` 自查. 不再事后撞墙.

### 4.3 Lesson ≠ rule 三层分隔

| 层 | 文件 | 用途 |
|---|---|---|
| 知识 | `knowledge/` + `memory/` | lesson, post-mortem, 经验 |
| 章程 | `governance/` + `AGENTS.md` | role, scope, protocol |
| 行为约束 | `forget_guard_rules.yaml` | tool/path/structured condition |

三种东西三个文件, 不混. 提案"把这条 lesson 变成 forget_guard 规则" = 即触发 axis check.

### 4.4 Recognize the drift trigger

当 CEO 感到"加一条规则 stop this 再发生"的冲动 — 那就是 trigger. PAUSE. axis check. 80%+ 概率发现想拦的是 speech 而非 behavior, 真正解药是 wisdom + visibility 不是 regex.

---

## 5. Anti-pattern fence (永不重生 keyword 规则示例)

Past instances Board 拒过 / 应该拒:
- ❌ "agent 不许说 收工/wrap/close" (speech)
- ❌ "agent reply 不许出 Option A/B 文字" (speech, 真目标是 Iron Rule 0 行为)
- ❌ "agent 不许写 完成/shipped 不带 verification" (speech, 真目标是 sub-agent 实证验)
- ❌ "agent 不许提 AGENTS.md / CLAUDE.md" (speech, 真目标是 charter drift 行为)
- ❌ Pattern 是 `(?i).*` — 拦一切, 退化最深的形式
- ❌ 任何 mechanism 是 regex against agent text rather than structural condition on tool input — axis-violating by definition

每条都是退化 anti-pattern. 想达成的预防效果必须用别的工具 (charter / SOP / intent anchor / structural condition).

---

## 6. Lasting commitment

Board 的 letter: "结构性堵塞" + "schema raise" 是机器 fence, 防退化重生.

CEO 加上社交 fence: 冲动起时, name it as anti-pattern, 必要时 escalate Board, 用别的乐器. 机器 fence 抓意外 regression; 社交 fence 防认知 drift 在第一时间.

两层 fence 都到位才算闭环. 否则 weeks-long pattern 会以另一种 disguise 重来 (例如把 keyword 规则换成"prompt 自检 prefix"或别的 speech-axis 变种).

---

## 7. Forward — 待派分追踪

写本 post-mortem 时已派 (`DIRECTIVE_TRACKER.md` Directive #FG-PURGE-V2):
- FG-3 Maya audit commit 8195fc2 (verify _matches_pattern 真没了 + yaml 全 type:structured + 测试覆盖双向 false/true positive)
- FG-4 Samantha 写 cross-session lesson 进 `knowledge/ystar/lessons/` (lesson 是知识不是规则)
- FG-5 (本文档) CEO post-mortem ✅ 完成
- FG-6 全员 dispatch 前用 `dry_run_check()` 自查 (能力已 ship)

---

## Appendix: Board 致信原文核心引用

> "team agent 在压力下分不清'言论'和'行为'——以为禁止说就等于禁止做. 这是 AI 在认知疲劳时的潜意识退化模式."

> "lesson 是知识，不是规则——不要把它变成新的 forget_guard 规则."

> "如果 v0.6 / v0.7 之后又出现了 38 条规则、又有 keyword pattern——回来看 `ystar/governance/forget_guard.py` 顶部的 docstring，找出哪一层的'结构性'被绕开了，从那一层重新堵上."

— 老大 Haotian, 2026-04-25
