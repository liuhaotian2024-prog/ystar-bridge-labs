# Feedback: 下一轮 Session 重启协议（env var 身份锁解锁 + 接续任务）

**类型**: feedback（操作规范）
**立约**: 2026-04-13 Board session 末尾
**触发条件**: CEO session 内需要 scripts/ / .ystar_session.json / governance/ 写权限但 hook identity_detector 仍认定 agent=ceo

---

## 1. Why（为什么需要本协议）

Hook identity_detector.py 按 7 级优先级检测 agent 身份：
1. payload.agent_id
2. payload.agent_type（subagent type mapping）
3. YSTAR_AGENT_ID env
4. CLAUDE_AGENT_NAME env
5. session_id 提取
6. transcript_path 提取
7. `.ystar_active_agent` marker 文件

Claude Code 在启动时锁定 agent 身份（可能通过 CLAUDE_AGENT_NAME 或 session_id pattern）。session 进行中**不能翻转身份**——即使 `echo eng-platform > .ystar_active_agent` 也只切到优先级 #7，被前面的 env 覆盖。

这是 AMENDMENT-009 §2.5 Board shell escape hatch 要解决的 bug 本身。在 AMENDMENT-009 代码实装之前，唯一解锁路径 = **重启 Claude 并注入 YSTAR_AGENT_ID env**。

## 2. Procedure（重启协议——Board 严格按步执行）

### Step 1：重启前 CEO 必须完成
- [ ] 更新 `reports/priority_brief.md` v0.2（加 `next_session_action_queue`）
- [ ] 写 `knowledge/ceo/skills/ceo_session_boot_recovery.md`（Hermes 格式）
- [ ] 写 `knowledge/ceo/lessons/session_{YYYY_MM_DD}_*.md`（本轮教训）
- [ ] 写 `knowledge/ceo/dead_paths/*.md`（本轮证实的死路）
- [ ] 写 `knowledge/ceo/board_mental_model.md`（Board 最新观察）
- [ ] 本 feedback 已存在
- [ ] session_close 跑 `python3 scripts/session_close_yml.py ceo "<summary>"`（锁记忆）
- [ ] 确认 DNA / Charter / Role Mandate 等永久档未被本 session 污染

### Step 2：Board 在 terminal 执行
```bash
# 在当前 Claude session 里执行
/exit

# 回到 terminal（zsh），执行
cd /Users/haotianliu/.openclaw/workspace/ystar-company
YSTAR_AGENT_ID=eng-platform claude
```

注意：
- `YSTAR_AGENT_ID=eng-platform` 必须在同一行 `claude` 命令前（inline env 注入，不 export）
- 否则 Claude 启动后 env 继承不到
- 一定要 cd 到 ystar-company 目录，否则 CLAUDE.md 不加载

### Step 3：新 session 启动后 Board 第一句话
建议原句：
```
Ryan 实装 AMENDMENT-009 + AMENDMENT-010 全部代码。参照 reports/priority_brief.md v0.2 next_session_action_queue 段。
```

新 session 的顶层 agent 身份 = `eng-platform`（YSTAR_AGENT_ID 优先级 #3），可以直接写 `scripts/` 和 `.ystar_session.json`。

### Step 4：新 session 第一个 tool call 必须是
```bash
bash scripts/governance_boot.sh eng-platform
```

这会：
- 加载 eng-platform 的 role_definition
- 读 priority_brief.md v0.2
- 加载 AMENDMENT-009 + 010 待实装清单
- hook daemon 重启

### Step 5：Ryan 实装完成后切回 CEO
实装 4+16 项代码后：
```bash
# 在当前 eng-platform session 内
/exit

# terminal
YSTAR_AGENT_ID=ceo claude
```

或不加 env var 直接 `claude`（CLAUDE_AGENT_NAME 默认会回到 ceo）。

## 3. Pitfalls

### 坑 A：`export YSTAR_AGENT_ID=eng-platform` 然后 `claude`
zsh 中 `export` 后启动子进程应该能继承，但 Claude Code 某些版本不读该 env。**用 inline 形式** `YSTAR_AGENT_ID=eng-platform claude` 最可靠。

### 坑 B：忘了 cd 到 ystar-company
Claude Code 只在 CWD = ystar-company 时加载本项目 CLAUDE.md。否则治理约束全失。

### 坑 C：新 session Board 问候"你是谁"，eng-platform agent 回复"我是 Aiden"
eng-platform 不是 Aiden（Aiden 是 CEO）。eng-platform 应回复"我是 Ryan (Platform Engineer)"。

### 坑 D：重启后 Board 又忘了说"Ryan 实装..."，新 session 闲置
本协议 Step 3 原句应复制粘贴，不要依赖记忆。

### 坑 E：Ryan 在 eng-platform session 越权写战略文档
eng-platform 的写作域：scripts/ + .ystar_session.json + governance/（有限授权）+ knowledge/eng-platform/ + reports/experiments/
**不能写** knowledge/ceo/ / reports/priority_brief.md / reports/proposals/（那是 CEO 和 Secretary 的）

## 4. Verification

重启 + Ryan 实装完成后：
- [ ] `bash scripts/governance_boot.sh ceo` 按 11 gate 全通过
- [ ] CEO session 讲 "明早" → hook DENY
- [ ] CEO > 200 字 response 60s 内无 ARTICLE_11_PASS → 下一次被 DENY
- [ ] 跨岗位派活无 RAPID → DENY
- [ ] 派工程 brief 非 6-pager v2 → DENY
- [ ] `memory/boot_packages/ceo.json` 存在且含 11 类全部字段

## 5. 长期方向（AMENDMENT-010 §7 兼容）

一旦 Secretary 在 AMENDMENT-010 S-3 下获得对 `.ystar_session.json.session_env_override.YSTAR_AGENT_ID` 写权，重启 Claude 就不再必要——Secretary 可自主注入 env override，hook 读该字段。彻底消除 Board shell 依赖。

在此之前，本协议是唯一解锁路径。

## 6. 版本
v0.1 — 2026-04-13
