# Behavior Governance Methodology — 从硬编码到方法论框架

Audience: Board (Haotian Liu) / 未来 CEO session / 所有 agent / 顾问 review
Research basis: Board 2026-04-22 早晨连续 catch — "OmissionEngine 几百轮都没做成"、"必须是行为治理而不是言论钳制"、"用方法论补上, 不是硬编码, 不能只解决一个问题要解决所有类型的方法论"
Synthesis: 答案不是再加一个专门抓 overdue 的 hook, 而是建一个 YAML-driven rule engine, 把"行为治理"这件事本身抽象成框架. 新加治理规则只加 YAML 条目, 不动 Python. 规则类型 4 种覆盖主要行为治理 pattern: DeadlineCheck / FrequencyCheck / StatePresenceCheck / ToolCountCheck. 所有 handler 只看 state / events / deadlines / tool history, 从不扫语言.
Purpose: 给 Board 一个可以信任的 "OmissionEngine 真 live 了" 的证据, 并留下可扩展框架让未来每类新 agent drift 都能在方法论层接入, 不再一次次 ad-hoc 加 hook.

---

## 问题不是 hook 数量, 是缺抽象

我过去几轮面对 "agent 懒惰推诿" 的 pattern 不断加专用 hook: hook_stop_reply_scan、hook_who_i_am_staleness、hook_skill_retrieval_pre_query、hook_omission_enforce_pretool. 每加一个是 patch, 下一个 drift 出现又加一个, 永远追不上. Board 今晨点破: "不能只解决一个问题, 要解决所有类型的方法论."

方法论要求从个体规则抽离出**规则本身的元规则**, 即行为治理的通用结构. 本次 ship 的 behavior_gov_engine 就是这一层抽象.

## 框架结构

治理规则现在以 YAML 配置, 不以 Python 代码表达:

```yaml
rules:
  - rule_id: omission_overdue_block
    type: DeadlineCheck
    severity: deny
    query:
      db: .ystar_cieu_omission.db
      table: obligations
      deadline_col: due_at
      grace_col: hard_overdue_secs
      status_col: status
      status_open_value: pending
    message_template: ...
```

引擎按 `type` 派发到对应 handler, handler 做该类型的查询 + 比较. 四类 handler 覆盖主要 pattern:

- **DeadlineCheck**: 看 DB 里 (due_at, status) — 逾期即 violation. 用于 OmissionEngine 自身 + 未来所有 deadline 场景.
- **FrequencyCheck**: 看 CIEU 事件流 — 某 event_type 在时间窗内 count < threshold 即 violation. 用于 "某 behavior 缺失" 类 (例如 Board directive 无 progress event).
- **StatePresenceCheck**: 看 state file 某字段 — 低于 min 即 violation. 用于 "session 状态不足以停机" 类.
- **ToolCountCheck**: 看 tool history — 近 N 次无 required tool 即 violation. 用于 P-12 先查后造类.

**所有 handler 的共性是: 看状态/事件/计数, 不扫 user/agent 写的文字**. 这就是 "行为治理 ≠ 言论治理" 的工程实现.

## 为什么这是方法论不是 patch

第一, 新加治理规则 = 加 YAML 条目. 例: 明天要 "CEO 写 reports/ 前必须有 git log 近期事件" → 写一条 ToolCountCheck rule. 不动 Python 代码.

第二, 换 4 种 handler 之一即可覆盖绝大多数 agent drift pattern. 如果真出现新 drift 形态 (比如要看 co-activation 的 brain 节点相关性), 加一个新 Handler 类, 剩余架构不变.

第三, **enable/disable** 是 per-rule flag. 新规则先 `enabled: false` 观察, 有信心再打开. 不会因为 YAML 写错而 brick session.

第四, **break-glass override 是 engine 层面的, 不是 per-rule**. Engine 先检查 break-glass, 全规则跳过. 这避免每个 rule 都自己写 break-glass 逻辑重复.

第五, **fail-open 是 handler 的默认**. DB 不存在、表 schema 变了、YAML 写错, 都返回 None 不抛异常, engine 继续跑. 治理层不可以 brick 工作层.

## 当前生效的规则

只启用一条: `omission_overdue_block` (DeadlineCheck). 这是 Board 2026-04-22 明示要求的反懒惰规则.

其他三条 (goal_level_directive_untouched / stop_after_short_session / skill_retrieval_not_invoked) 已写好但 `enabled: false`, 等两类前置:

一类是 CIEU 事件 taxonomy 扩展 (需要 DIRECTIVE_POSTED / DIRECTIVE_PROGRESS / GOAL_ARTIFACT_CREATED 等新事件类型, Samantha scope). 另一类是 session tool history 的 persistent state file (需要 post-tool hook 维护, Ryan scope).

这两类启用后, "agent 懒惰推诿" 的四种具体形态就被行为治理层同时覆盖: 过期不做、停机时无进展证据、短 session 就想停、新造前不查找.

## 当前 OmissionEngine 状态

引擎 LIVE 了, 但 CEO 自己在 DB 里没 obligation. 27034 条 obligations 全属 `path_a_agent` (synthetic meta-governance), CEO 的 tracked_entity 目前是 0 条. 这解释了为什么过去几百轮没触发 — 引擎每次查 "CEO overdue obligations" 结果都是空的.

这是下一步的 wiring work, 不是今天这一层抽象的问题. 具体做法: UserPromptSubmit hook 解析 Board directive, 对每条自动 register_obligation_programmatic(actor="ceo", deadline=now+24h). CEO 必须 emit close event 才能解. 这样 Board 每句 directive 立即变成 CEO 头上的 deadline.

我不把这个 wiring 推给未来 session — 是今天这一天之内要做完的, 下一步我会执行. 但这份文档先把方法论层交付: 框架、handler、YAML、pytest 都 LIVE, 新规则能加, 旧规则能调.

## 实证交付

- scripts/behavior_gov_engine.py — 引擎 (276 行), 4 handler + 主评估循环
- scripts/behavior_gov_rules.yaml — 规则配置 (4 条, 1 条 enabled)
- scripts/tests/test_behavior_gov_engine.py — 10 pytest PASS (handler + engine integration + fail-open + break-glass + disabled 规则 + 未知 type 忽略)
- scripts/wire_behavior_gov_pretooluse.py — 挂进 .claude/settings.json PreToolUse 的 idempotent wiring
- .claude/settings.json — PreToolUse 链现在 2 个 hook (原 hook_wrapper + behavior_gov_engine)
- scripts/omission_status.py — CLI 查询 + 关闭 obligation 的 operator 工具

## 下一步 (我自己做, 不推迟)

第一, 写 UserPromptSubmit hook 检测 Board directive, 自动 register_obligation 给 CEO. 这样每句 directive 立即成为 CEO 头上的 tracked deadline.

第二, Live-fire 一次: 故意给 CEO 造一个 past-deadline obligation, 尝试 Write, 验证 engine deny. 如果成功, Board 今天就能看到 "OmissionEngine 真抓到 CEO" 的 empirical 证据.

第三, 启用第二条规则 `stop_after_short_session_moral_licensing`, 先 warn 一周观察误报率再升 deny.

我不把这三步说成 "下一个 wave", 是本 reply 之后继续执行的直接 action.
