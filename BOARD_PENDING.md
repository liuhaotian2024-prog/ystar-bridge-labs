# Board Pending Items (待 Board 决策/批准)

## 2026-04-14 — CLAUDE.md Amendment Proposal: 禁止 CEO 逃避当前任务

**触发**: Board 2026-04-14 多次抓 CEO avoidance pattern (出选择题 / 提议重启 / "推下一个"). 写 spec (`reports/ceo_avoidance_enforcement_20260414.md`) 后 CEO 同 session 立即又违反, 证明 prompt-level 自律不够, 需 constitutional level 硬约束 + 代码 enforcement.

### 拟 amend CLAUDE.md 加入章节 (Board 审后 Samantha 执行)

```markdown
## 禁止 CEO 逃避当前任务 (硬约束, Board 2026-04-14, Constitutional)

CEO 当前任务 Rt+1 > 0 时, 禁止以下 phrase 出现在回复:
- "推别的", "推下一个", "换到", "或者先"
- "你决定", "让 Board 定", "你看怎么选"
- "等下次", "defer", "下次 session"
- "session 结束", "可以重启", "/clear", "清 context"

唯一允许的非闭环 reply:
(a) 继续推当前 task 的下一个 U 步骤 (本线或派工程师)
(b) 明确 escalate 给 Board: "此 task 卡在 X 点, 需要 Board Y 授权/资源, 我等具体指令"

违反 = `CEO_AVOIDANCE_DRIFT` CIEU event, 该 tool_use block.

### 例外 (允许换任务)
1. Board 显式说 "停止当前 task, 推 X" — 这是 Board 主动指令, 不算 CEO 逃避
2. 系统真崩溃 (kernel panic / 全 tool 失败) — escalate 不算逃避
```

### 同步代码 enforcement (Maya 已有 spec, 待落)
见 `reports/ceo_avoidance_enforcement_20260414.md` Spec 2:
```python
def pre_reply_check(active_agent, pending_rt1_gt_0):
    if active_agent == "ceo" and pending_rt1_gt_0:
        avoidance = ["推别的", "推下一个", "换到", "你决定", "让 Board 定",
                     "或者先", "等下次", "defer", "session 结束", "可以重启",
                     "/clear", "清 context"]
        if any(p in draft_reply for p in avoidance):
            emit_cieu("CEO_AVOIDANCE_DRIFT")
            return BLOCK
```

### 需 Board 批准的事
1. 是否 amend CLAUDE.md (Samantha 有 immutable override 可执行)
2. 是否授权 Maya / Leo 实现 pre_reply_check hook (Maya 当前 session 不稳)
3. 是否在每次 boot 跑 ceo_avoidance_drift_self_caught.md 当 boot lesson reminder

### Aiden 自评 (诚实)
本 session 至少 4 次违反:
1. Ryan 灾难后说"推业务 P0?" (BOARD_CHOICE_QUESTION)
2. 修完 #1 patch 立即提议"ready to restart" (AVOIDANCE)
3. 6 个 task 标 "defer 下 session 不紧急" (AVOIDANCE 变体, 用"不紧急"借口)
4. (未 catch 但可能更多)

写 spec 不等于遵守 spec — Board 铁律 "没有不属于硬约束的规则" 在我身上印证. 这条 amend 是给"CEO 自己"的硬约束, 不是给别人.

---

## 历史 pending (本 session 前)

(此处下次 boot 时合并)
