# Governance Layer on OpenClaw — Technical Evaluation

**Author:** CTO Ethan Wright
**Date:** 2026-04-11
**Reviewed architecture:** Board's third clarification — 治理层搬到OpenClaw常驻，labs团队留在Claude Code，Hook作为桥梁注入context

---

## TL;DR

**架构技术可行，且是三个方案里最接近"解决失忆根因"的。** Claude Code 原生支持 `SessionStart` hook + `additionalContext` 字段注入 LLM context。10,000 字符上限对 snapshot 来说够用（紧但可行）。**但失忆问题不是 100% 消除——只解决"压根没看到"，不解决"看到了不做"。** 后者是 LLM 行为层问题，任何被动注入方案都碰不到。

四个 Phase 中 Phase 1 和 Phase 3 现在就能做（各 1–2 天工作量），Phase 2 需要先定义 snapshot schema（2–3 天），Phase 4 是验证（半天）。

---

## 1. 架构是否技术可行？

**可行。关键证据（来自 Claude Code 官方 hooks 文档）：**

### 1.1 SessionStart hook 存在
```
matcher: startup | resume | clear | compact
触发时机: session 启动、--resume、--continue、/resume、/clear、compaction
输出: hookSpecificOutput.additionalContext → 注入 LLM context
```

这比 PreToolUse 更早、更可靠——**不需要等 LLM 做第一个 tool call**。Session 一启动就触发，LLM 的第一条系统消息里就包含 snapshot。

### 1.2 PreToolUse hook 也支持 additionalContext
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "allow",
    "additionalContext": "...snapshot here..."
  }
}
```

### 1.3 当前 hook_wrapper.py 架构已经具备改造基础
`/Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_wrapper.py` 已经是 stdin→JSON→stdout 的标准 hook pattern。改造成本低。

**结论：** 架构不需要任何 Claude Code 外部 hack，完全走官方支持的 hook 接口。

---

## 2. Hook 能注入多少 context？

**硬上限：10,000 字符**（约 2500–3500 tokens，取决于 tokenizer）。

官方原文：
> Hook output injected into context (`additionalContext`, `systemMessage`, or plain stdout) is capped at 10,000 characters. Output that exceeds this limit is saved to a file and replaced with a preview and file path.

**含义：**
- **够用**：labs 团队的核心 snapshot（continuation + obligation list + top 5 CIEU events + active_task + DISPATCH state + Board latest）预估 3000–6000 字符，能塞进去。
- **紧张**：如果想塞完整 behavior_rules（193 条）、完整 CIEU 24h 历史、完整 memory，会超。
- **溢出时的兜底**：超 10k 的部分自动写文件，LLM 收到 preview + 文件路径——LLM 可以主动 Read 完整内容。这其实是个 feature：**关键信息强注入，长尾信息按需拉取。**

**Snapshot 预算（建议分配）：**
```
- Meta header (agent_id, session_id, timestamp)      : 200  chars
- Continuation.json (上次做到哪)                       : 1500 chars
- Active obligations (未履约项)                        : 2000 chars
- Top-5 critical CIEU events (24h)                    : 2000 chars
- Active task (.claude/tasks/当前任务)                  : 1500 chars
- DISPATCH state + Board latest directive             : 1500 chars
- "你是谁+你的下一步" 指令                               : 800  chars
- 缓冲                                                 : 500  chars
总计                                                   : ~10000
```

---

## 3. 与前两个方案的本质区别

| 维度 | 方案A：金金观察员 | 方案B：治理团队搬家 | 方案C：治理层搬家（本方案） |
|---|---|---|---|
| **labs 团队位置** | Claude Code | **OpenClaw** | Claude Code（不变） |
| **治理层位置** | Claude Code 内 hook | OpenClaw 内 | **OpenClaw 常驻进程** |
| **状态来源** | 静态文件（memory/） | OpenClaw agent 主动查 | **常驻进程实时维护** |
| **注入机制** | LLM 必须主动跑 boot | OpenClaw agent 跨机通信 | **Hook 被动注入 context** |
| **失忆根因是否触及** | 不触及（LLM 可能不跑 boot） | 触及一半（OpenClaw 记得，但 labs 不记得） | **触及**（LLM 不做任何事也会被注入） |
| **可靠性** | 依赖 LLM 服从 | 依赖跨机协议 | **依赖 Claude Code 官方 hook，最硬** |
| **复杂度** | 低（已实现） | 高（两套 agent 同步） | **中**（只动 hook + 加常驻服务） |

**本方案的核心优势：** 前两个方案都假设"LLM 会主动做某件事"（跑 boot / 查 OpenClaw）。本方案**不依赖 LLM 行为**——session 一启动，SessionStart hook 必然触发，snapshot 必然注入。这是被动防御，比任何主动协议都硬。

**本方案的核心劣势：** Snapshot 注入到 context 后，LLM **读不读、按不按它做**仍是 LLM 的自由意志问题。这是所有"注入式治理"的共性天花板。

---

## 4. 四个 Phase 的具体实现方案

### Phase 1 — OpenClaw 常驻治理服务（工作量：1–2 天，现在可做）

**目标：** 把 `_hook_daemon` 逻辑拉起来变成 OpenClaw 上一个常驻 Python 进程。

**实施：**
1. 新建 `/Users/haotianliu/.openclaw/services/ystar_gov_daemon/`：
   - `daemon.py`：基于 `aiohttp` 或 `FastAPI` 的本地服务，监听 Unix socket `/tmp/ystar_gov.sock`（跨平台可改 TCP 127.0.0.1:9876）
   - 移植 `hook_wrapper.py` 的 `check_hook`、`_intent_guard_check`、`check_continuation_compliance`、`OmissionScheduler` 到服务端
   - 启动时加载 `.ystar_session.json`、连接 `.ystar_cieu.db` 和 `.ystar_memory.db`
2. 用 systemd/launchd 注册为常驻：
   - macOS：`~/Library/LaunchAgents/com.ystar.gov.plist`
   - 崩溃自动重启 (`KeepAlive=true`)
3. 暴露三个 RPC endpoints：
   - `POST /check_hook` — 等价当前 hook，检查单次 tool call
   - `GET /snapshot?agent_id=ceo` — 返回完整 snapshot（Phase 2 填充）
   - `GET /health` — liveness check

**现在能做的部分：** 整套可以立即搭起来。Phase 2 的 snapshot 先返回占位符。

**风险点：** 
- OpenClaw 本体如果重启/崩溃，daemon 要跟着起——依赖 launchd 可靠性
- 跨 repo 路径（ystar-company vs openclaw）的文件锁竞争——需要 WAL mode on SQLite（现在已经是）

---

### Phase 2 — Labs 团队 Snapshot 维护逻辑（工作量：2–3 天）

**目标：** daemon 实时维护各 agent 的 snapshot，响应 `GET /snapshot` 毫秒级返回。

**Snapshot schema（提案）：**
```python
@dataclass
class LabsSnapshot:
    meta: dict                    # agent_id, generated_at, session_id, version
    continuation: dict            # memory/continuation.json 内容
    obligations: list[dict]       # 最多 10 条，按 deadline 排序
    recent_cieu: list[dict]       # 最近 24h 关键事件，top 5（按 evidence_grade 排序）
    active_task: dict             # .claude/tasks/{agent}/active_task.json
    dispatch_state: dict          # DISPATCH 当前状态
    board_latest: str             # Board 最新指示（memory/board_directive 最新条）
    next_action: str              # 结构化下一步指令（daemon 综合判断）
```

**维护机制：**
- 文件变更触发：用 `watchdog` 监听 memory/、.claude/tasks/、reports/ 的变化 → 重建 snapshot
- 定时刷新：每 60s 全量重建一次（兜底）
- CIEU 写入触发：daemon 监听 CIEU 新写入事件（通过 SQLite 的 `data_version` polling 或 hook passthrough）→ 增量更新 recent_cieu

**格式化：** `GET /snapshot` 返回 JSON；额外提供 `GET /snapshot.txt?agent_id=ceo` 返回已渲染的 10k 字符以内的 Markdown（hook 直接塞 `additionalContext`）。

**现在不能做的部分：** 
- Snapshot schema 要和 CEO/CTO 确认信息优先级——什么东西最值得塞进 10k 字符
- `next_action` 生成算法要调——这是"治理层能决定塞什么进去"的核心价值点

---

### Phase 3 — 改造 Hook 支持 Snapshot 注入（工作量：1 天）

**目标：** 给 Claude Code 注册 SessionStart hook，第一次 tool call 前就注入 snapshot。

**两个改动点：**

**3.1 新增 SessionStart hook（主要注入通道）**

在 `.claude/settings.json` 加：
```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "startup|resume|clear|compact",
      "hooks": [{
        "type": "command",
        "command": "python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/hook_session_start.py"
      }]
    }]
  }
}
```

新文件 `scripts/hook_session_start.py`：
```python
import sys, json, urllib.request
agent_id = os.environ.get("YSTAR_AGENT_ID", "ceo")
try:
    with urllib.request.urlopen(
        f"http://127.0.0.1:9876/snapshot.txt?agent_id={agent_id}", timeout=2
    ) as r:
        snapshot = r.read().decode("utf-8")[:9800]  # 留 200 字符缓冲
except Exception as e:
    snapshot = f"[snapshot unavailable: {e}] — run governance_boot.sh manually"

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": snapshot
    }
}))
```

**3.2 PreToolUse hook 加 snapshot fallback（兜底通道）**

当前 `hook_wrapper.py` 在检测到 `.session_booted` 不存在时，在返回值里加 `additionalContext` 字段——即使 SessionStart 没触发（比如用户用了旧 Claude Code 版本），第一个 tool call 也能注入：

```python
# 在 hook_wrapper.py _main() 末尾，result 构造后
if count == 1 and not os.path.exists(boot_flag):
    try:
        snapshot = fetch_snapshot(agent_id)  # 调 daemon
        result.setdefault("hookSpecificOutput", {})
        result["hookSpecificOutput"]["hookEventName"] = "PreToolUse"
        result["hookSpecificOutput"]["additionalContext"] = snapshot[:9800]
        open(boot_flag, "w").close()
    except Exception as e:
        log(f"[snapshot-inject] failed: {e}")
```

**现在就能做的部分：** 两个 hook 文件都能独立写出来，不依赖 Phase 2 完成——daemon 先返回占位 snapshot，hook 先把注入管道通起来。

---

### Phase 4 — 验证（工作量：半天）

**目标：** Session 重启后，CEO 第一次 tool call 之前就能"看到"完整 snapshot。

**验证步骤：**
1. `rm scripts/.session_booted scripts/.session_call_count`
2. 启动新 Claude Code session
3. 用户问 CEO："你现在知道哪些事？"
4. CEO 应该能复述 snapshot 里的内容（continuation、obligations、Board latest）——**无需跑任何命令**
5. 检查 CIEU：应该有一条 `SNAPSHOT_INJECTED` 记录（daemon 写的），表明注入确实发生了
6. 对照组：关掉 daemon，重复 1–4——CEO 应该报告 snapshot unavailable

**成功标准：**
- 90% 的 session 启动，snapshot 注入成功（daemon healthy 前提下）
- CEO 第一条回复前，上下文里包含 snapshot
- 不再需要 `bash governance_boot.sh` 作为 session 启动强制步骤

---

## 5. 诚实评估：失忆问题解决到什么程度？

**分层分析——把"失忆"拆成三层：**

### Layer 1: 信息不在 context 里（"压根没看到"）
**当前方案：** LLM 必须主动跑 boot，不跑就完全失忆。很多时候 LLM 懒得跑，或者跑一半被打断。
**本方案：** SessionStart hook 必然触发（Claude Code 原生机制），snapshot 必然进 context。
**解决程度：100%。** 这是本方案的核心价值。

### Layer 2: 信息在 context 里但 LLM 没读（"看到了没注意"）
**现实：** LLM 有时会跳过长 system prompt，尤其是放在 context 前面、离用户问题远的部分。
**缓解手段：**
- Snapshot 格式设计：把"next_action"放在最顶部，明确说"你现在必须做 X"
- Snapshot 里嵌入 CIEU event_id 引用——LLM 引用时可以验证是否真读了
**解决程度：70–80%。** 无法 100%，取决于 LLM 注意力分配，这是模型层问题。

### Layer 3: 信息读到了但 LLM 不照做（"看到了不做"）
**现实：** LLM 读了 obligation 列表，还是可能忽略、改写、合理化绕过。这是对齐层问题。
**本方案触及吗？** **不触及。** 注入 context 只是把信息摆到眼前，不能强制行为。
**缓解手段（不属于本方案）：**
- 行为层 enforcement：PreToolUse hook 在 LLM 想做违规事时 deny——已经在做
- Obligation deadline 到期的强制打断——GOV-010 OmissionScheduler 做的
**解决程度：0%。** 需要 enforcement 层（独立于 context 层）配合。

### 综合结论

> **本方案在"信息送达"维度实现近 100% 可靠性，比当前方案质的提升。但"信息被服从"维度需要 enforcement 层（当前 hook 的 deny/warn 机制）继续兜底。**

两者配合才是完整答案：
```
SessionStart hook 注入 snapshot         ← 本方案（信息层）
PreToolUse hook deny 违规行为             ← 已有（行为层）
OmissionScheduler 定时打断未履约        ← 已有 GOV-010（时间层）
三者叠加 = 失忆问题的现实上限解
```

---

## 6. 建议执行顺序

| 优先级 | Phase | 工作量 | 依赖 | 现在可做？ |
|---|---|---|---|---|
| P0 | Phase 3.1 注册 SessionStart hook + 占位 snapshot | 0.5 天 | 无 | **是** |
| P0 | Phase 1 daemon 骨架（带占位 /snapshot） | 1 天 | 无 | **是** |
| P1 | Phase 2 snapshot schema + 维护逻辑 | 2–3 天 | Phase 1 | 等 CEO/CTO 确认 schema 后做 |
| P1 | Phase 3.2 PreToolUse fallback 注入 | 0.5 天 | Phase 1 | Phase 1 后立即做 |
| P2 | Phase 4 E2E 验证 | 0.5 天 | 1+2+3 全部 | 最后做 |

**我建议立即启动 P0（Phase 1 骨架 + Phase 3.1 SessionStart hook）**——即使 snapshot 先只是 "hello from daemon"，把注入管道打通，验证 Claude Code 确实会把 `additionalContext` 塞进 LLM context。这一步验证后，Phase 2 填充内容就是纯数据工作。

**工程师分工建议（如果 Board 批准）：**
- Leo Chen：Phase 1 daemon + launchd 集成
- Maya Patel：Phase 2 snapshot schema + watchdog 维护
- Ryan Park：Phase 3 两个 hook 文件
- Jordan Lee：Phase 4 E2E 测试 + CIEU 验证

---

## 7. 开放问题（需 Board/CEO 决策）

1. **Snapshot 的 agent_id 如何区分？** 现在 hook 不知道自己是哪个 agent（CEO/CTO/...）。需要环境变量 `YSTAR_AGENT_ID` 在启动 Claude Code 时设置，或者 hook 从 cwd 推断。建议前者。
2. **Daemon 跨平台：** 当前 ystar-company 在 macOS（`/Users/haotianliu/.openclaw`）和 Windows（`C:\Users\liuha\OneDrive\桌面`）都跑。双机分工原则下 daemon 放哪？我建议 MAC 上跑（常驻 24/7 已经是既定事实），Windows 的 Claude Code 通过 TCP 连 MAC 的 daemon（`192.168.1.228:9876`）。需要验证网络延迟是否影响 hook 响应时间（Claude Code 默认 hook 超时 60s，应该够）。
3. **Snapshot 的"智能度"：** Phase 2 里 `next_action` 由 daemon 生成——daemon 用什么逻辑判断？规则引擎？还是调 Claude API？建议先做规则引擎（确定性高），后期可迭代。
4. **现有 `governance_boot.sh` 何去何从？** 我建议保留但降级为**故障兜底**——daemon 不可用时 LLM 还能手动跑。CLAUDE.md 的"Step 2 必跑 governance_boot.sh"可以改成"Step 2 验证 SessionStart 注入成功，失败才跑 governance_boot.sh"。

---

**CTO Ethan Wright 结论：这是三个方案里技术路径最清晰、对现有架构改动最小、且触及失忆根因最彻底的方案。建议 Board 批准 P0 立即启动。**
