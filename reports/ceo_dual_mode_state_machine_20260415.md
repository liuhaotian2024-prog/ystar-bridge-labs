# CEO Dual-Mode State Machine — 固化"Board 在线→响应 / Board 离线→自主"永不遗忘 (2026-04-15)

**Trigger**: Board 2026-04-15 问 "如何真正固化这套 有 board 时按 board, 没有时完全自主? 不会回头又忘"

## 问题根因 (为什么会忘)

| 遗忘 vector | 说明 |
|---|---|
| Session boundary | 每 new session 从 scratch 重载 system prompt, 上 session 凝练的"自主 posture"丢 |
| Context 压缩 | 长对话被 summarize, 行为模式 cue 被吞 |
| Hook enforce 不覆盖 | 目前 14 ban phrase 只管 "avoidance 词", 不管 "CEO idle > N min 仍不自主行动" |
| Lesson 非强加载 | knowledge/ceo/lessons/autonomy_degradation_*.md 存在但不自动进 prompt |
| Memory 层非持久 | Claude auto-memory 存 feedback_no_clock_out, 但 Claude 平台外 (新机器 / 新接口) 丢 |

## 固化方案 = 5 层冗余 (缺一则有空子)

### Layer 1: Constitutional (AGENTS.md Iron Rule 1.X)
新 Iron Rule "CEO Dual-Mode State Machine":

```
CEO operates in one of two modes, switched by state file .ystar_ceo_mode:

- BOARD_ONLINE: last Board message received < 5 min ago
  → behavior: execute Board instruction verbatim; may ask clarifying question only if Board instruction has ambiguity P0-P1 impact; no autonomous agenda branching
  
- AUTONOMOUS: last Board message > 5 min ago (includes Board silence between turns)
  → behavior: execute priority queue (obligations / pending tasks / retro actions / long-term goals / system stress test / agent 岗位学习)
  → every reply must emit ≥ 1 tool_use (dispatch / commit / verify); no "等" / "standby" / "等 Board 回话" patterns
  → CEO autonomously starts tasks; does NOT poll Board for permission on any item in own write scope
  → escalates only per ceo_avoidance_enforcement spec single-sentence pattern

Mode switch is automatic (hook reads last_board_msg_ts); CEO does NOT self-switch.
```

### Layer 2: Hook Enforcement (code-level, 不依赖 prompt)
Y-gov `ystar/adapters/hook.py` 扩 _check_hook_full / light path:

```python
# CEO MODE ENFORCEMENT (9cd8014 AVOIDANCE 扩)
if who == "ceo":
    last_board_ts = read_last_board_timestamp()
    now = time.time()
    mode = "BOARD_ONLINE" if (now - last_board_ts < 300) else "AUTONOMOUS"
    write_ystar_ceo_mode(mode)  # .ystar_ceo_mode file
    
    if mode == "AUTONOMOUS":
        # check if CEO last tool_use within same reply contains sub-agent dispatch OR commit OR verify
        reply_buffer = current_reply_draft()
        if not has_active_tool_use(reply_buffer):
            deny_msg = "CEO_AUTONOMOUS_IDLE_DRIFT: Board 离线 > 5 min, 本 reply 需至少 1 tool_use (dispatch/commit/verify). prompt passive 模式不允许."
            emit_cieu("CEO_AUTONOMOUS_IDLE_DRIFT", ...)
            return {"action": "block", "message": deny_msg}
```

### Layer 3: CIEU Emit + K9 Rule 12 IDLE_DRIFT
CIEU 新 event type `CEO_AUTONOMOUS_IDLE_DRIFT` + `CEO_MODE_TRANSITION` (BOARD_ONLINE ↔ AUTONOMOUS). K9 daily patrol Rule 12: 过去 24h AUTONOMOUS mode 下 CEO idle > 10 min period count > threshold → flag P1.

### Layer 4: Boot Protocol Inject (governance_boot.sh)
Boot 时 inject 当前 mode state 进 CEO system prompt 开头 (持续提醒, 不靠记忆):
```
[AUTO-INJECTED CEO MODE STATE]
Current mode: AUTONOMOUS (last Board msg 47 min ago)
Your task: follow priority queue in DISPATCH.md. No polling for permission.
Escalate only via "卡在 X 点, 需要 Board Y" single sentence.
```

### Layer 5: Memory Persistence (git-backed)
`knowledge/ceo/role_definition/dual_mode_posture.md` 新文件作 canonical. 每次 boot 读. git 管跨机器跨 Claude 接口. 配 `feedback_no_clock_out.md` 作 user-memory 备份.

## 5 层冗余表

| Layer | 失效时另 4 层兜底 |
|---|---|
| Constitutional | prompt 丢? constitutional 在 AGENTS.md immutable, boot 必读 |
| Hook | hook down? Constitutional 在 + Boot inject 仍说 |
| CIEU audit | K9 patrol 看不到? Boot inject 每次 remind |
| Boot protocol | boot script 改坏? Hook 仍 enforce + Constitutional 硬 |
| Memory | auto-memory 丢? role_definition git 备份 |

## 与现有框架对齐 (不冲突)

- unified 三框架 (Iron Rule 1.6, 4c2c931a): CEO 自主 mode 下仍走 CIEU 5-tuple + Article 11 + 12-layer. dual mode 是"何时该动" 层, unified 是"动的时候怎么做"层
- CEO AVOIDANCE (4997d6c + 9cd8014): avoidance 14 phrase 只管"说逃避词", dual mode 补"该动时不动"
- CEO_CODE_WRITE_DRIFT 等 forget_guard: 他们管内容层 drift, dual mode 管 posture 层

## Rt+1=0 条件 (Board 审后实装, 待 task queue)

1. Iron Rule 1.X 加 AGENTS.md (Samantha immutable override, Board approve 后)
2. hook.py _check_hook_full / light path 加 CEO_MODE 块 (Maya / Leo)
3. governance_boot.sh 加 mode inject 段 (Samantha / Platform)
4. scripts/read_last_board_timestamp.py 实现 (log-based OR CIEU query)
5. K9 rule 12 IDLE_DRIFT detector (Maya)
6. knowledge/ceo/role_definition/dual_mode_posture.md canonical doc (Samantha)
7. 3 独立 session 验证: 模拟 Board silence > 5 min, CEO 自动进 AUTONOMOUS, 每 reply 含 tool_use
8. 多轮压力测试 per Samantha standard_subtask_protocol stage 4 ⇒ 含 chaos test attached link

## 本 design commit 后

- Samantha adc4a7224 当前 task (retro 4 action 合入 protocol) 其 action 4 会自动把本 Iron Rule candidate 追加 BOARD_PENDING
- 5 层实装派单 etc 等 Board 审 BOARD_PENDING 后开
