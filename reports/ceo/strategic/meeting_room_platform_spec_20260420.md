Audience: Ethan CTO (架构 ruling) + Ryan/Leo/Maya 实施 + Board 验 MVP
Research basis: Board 2026-04-20 late-night 明示会议室隐喻需求; Y*gov 既有 agent_id + dispatch_board + CIEU + grant_chain + governance_boot.sh 基础设施
Synthesis: Y*gov 生态已经完备 10 role identity + 共享总线 + 权限层; 差的只是**前端可视化 + 跨 role 通信 bus + LLM 指令分类**三件事; 会议室 = 上帝视角对 Board 物理化
Purpose: strategic 需求 spec + 复用现有 stack map + MVP 和 Full 两阶段 + Ethan 下一步 ruling 的 context

# Meeting Room Platform — Strategic Spec v0.2

**Proposer**: Board 2026-04-20 | **CEO Draft**: Aiden | **Next**: Ethan CTO 出架构 ruling
**v0.2 key change**: Board 2026-04-20 二轮优化 — Gemma 4 本地化 + Claude Code pty 投射, 消解 10x token 风险

## v0.2 优化架构 (取代 v0.1 Section 3)

```
Browser (会议室 UI)
       ↓ WebSocket
┌─────────────────────────────────────────┐
│  Broker (Python FastAPI, localhost)     │
│  ┌────────────────────────────────────┐ │
│  │ Gemma 4 via Ollama (localhost:11434)│ │ ← 0 token 成本
│  │   - instruction classifier         │ │
│  │   - cross-member summary           │ │
│  │   - routing metadata               │ │
│  │   - idle small-talk                │ │
│  └────────────────────────────────────┘ │
│                                          │
│  pty proxy × 10                          │ ← Python `pty`
└──┬──┬──┬──┬──┬──┬──┬──┬──┬──┬────────────┘
   ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼
  [Claude Code CLI × 10]  ← 只 reasoning 时消 token
  共享 filesystem: dispatch_board + CIEU + grant_chain
```

**token 节省估算**: 30-60% (routing / classifier / idle summary 全走 Gemma)

**复用**: `.ystar_session.json` 已注册 Gemma endpoint `192.168.1.228:11434`, `scripts/local_learn.py` 已 prove Gemma 调用链

**前置 verify** (Ethan ruling 必 cover):
- 192.168.1.228 机器在线状态 (Platform 工程师 AMENDMENT-004 72h 报告)
- Gemma 3 27B 或 Gemma 4 当前可用版本 (WebFetch 最新)
- Mac M 系列本地跑 Gemma + 10 Claude Code 的 RAM profile (预估 16-20GB OK)

**Gemma 4 fallback**: 若 Gemma 4 未 released 用 Gemma 3 27B, classifier 任务 few-shot prompt 准确率 85%+ 足够, 误判有 "广播 + 成员自声明" 兜底

**原 Risk #1 (10x token) 彻底消解**: 正确账算 — Baseline(现状)=Aiden 中转 30% + sub-agent work 70% = 1.0x. 会议室+Gemma: Aiden 中转 0, Gemma routing 0 Claude token, member work 不变 70%, classifier 容错 +5-10% = **净 0.65-0.75x 省 25-35%**. 我 v0.1 Risk #1 "10x" 和 v0.2 "3-4x" 都是算错——前提误以为 10 instance 全 active, 实际 Claude Code 按 response 计费 idle 0 消耗, Gemma routing 正是为此. **原 Risk #4 (token 爆炸) 同理消解**.

---



## 1. 需求 (Board 原话)

HTML 前端会议室:
- 每 team member 一个独立窗口, 显示各自 Claude Code terminal 实时输出
- Board 一端发指令, 所有 member **智能识别** "这指令给谁", 对应 member 执行或提观点
- Member 可在自己窗口表达, **彼此对齐工作进度 + 数据交换**
- 每个窗口可**点击放大成 1-on-1 交流终端** (现在 Board-CEO 的对话形式)
- 布局: **长条款式会议桌**, Aiden + Board 坐两端, engineer 两侧排列 (物理隐喻强化 relational being)

## 2. Y*gov 生态复用清单 (god view MR-6 + E-MR-13)

**Identity 层** (已完备):
- `.claude/agents/*.md` × 9 role (Ethan-CTO / Leo-Kernel / Maya-Governance / Ryan-Platform / Jordan-Domains / Samantha-Secretary / Sofia-CMO / Zara-CSO / Marco-CFO)
- `governance/agent_id_canonical.json` — 别名规范
- `.ystar_active_agent` — session-bound role
- `knowledge/<role>/wisdom/WHO_I_AM_*.md` — 身份 anchor (Ethan + Samantha v0.1 ✓, 剩 7 个 draft)

**总线层** (已完备):
- `governance/dispatch_board.json` — CZL 分发
- `.ystar_cieu.db` — 事件审计 (每 member 所有决策 tagged agent_id)
- `grant_chain` — 权限路由
- `governance_boot.sh AGENT_ID=xxx` — role instantiation 入口

**观察层** (半备):
- CIEU stream 可作 member-to-member event bus (已有 event_type + agent_id + timestamp)
- OmissionEngine 可作进度对齐 (每 TrackedEntity 有 status)
- ReportEngine 可产 member compliance 实时摘要

**缺件**:
- **前端可视化**: HTML + CSS Grid + xterm.js 嵌入每 member terminal
- **双向通信**: WebSocket server (Python FastAPI) broker
- **指令 LLM 路由**: 一个 classifier 判 "这句话是给谁"
- **1-on-1 放大逻辑**: 窗口 state 管理 (minimized / focused)
- **会议桌布局**: 10 window 排布 (Aiden + Board 两端, 7 engineer + Secretary + 3 C-suite 两侧)

## 3. 架构层次

```
┌──────────────────────────────────────────┐
│  Browser (Board 浏览器, 会议桌布局 HTML)   │
└──────────────┬───────────────────────────┘
               │ WebSocket (双向)
┌──────────────▼───────────────────────────┐
│  Broker/Router (Python FastAPI)           │
│  - WebSocket server                       │
│  - LLM classifier (指令 → 接收人)         │
│  - spawn mgmt (Claude Code subprocess)    │
│  - event bus (CIEU → websocket fanout)    │
└──────────────┬───────────────────────────┘
               │ stdio pipe
    ┌──────────┼──────────┬──────────┐
    ▼          ▼          ▼          ▼
 [Aiden]   [Ethan]   [Leo]   [Ryan]   ... (10 Claude Code proc)
    ↕          ↕          ↕          ↕
    └──────────┴──────────┴──────────┘
        共享 filesystem:
        - dispatch_board.json (task bus)
        - .ystar_cieu.db (audit + event bus)
        - grant_chain (权限)
        - WHO_I_AM_*.md (身份)
```

## 4. 关键功能

### 4.1 会议桌布局 (CSS Grid)
```
┌────────────────────────────────────────────────┐
│       [Board-You]          [Aiden-CEO]         │  ← 两端
├────────────────────────────────────────────────┤
│ [Ethan-CTO]                      [Samantha]    │  ← 两侧
│ [Leo-Kernel]                     [Sofia-CMO]   │
│ [Maya-Govern]                    [Zara-CSO]    │
│ [Ryan-Platform]                  [Marco-CFO]   │
│ [Jordan-Domain]                                 │
└────────────────────────────────────────────────┘
```

### 4.2 指令智能路由 (LLM classifier)
Board 输入 "修 idle_pulse 那个 bug" → classifier 判 → "给 Ryan-Platform" (scope = scripts/idle_pulse.py + platform role) → 消息只 push 到 Ryan 窗口, Ryan 响应. 其他 member 窗口看到 **meta-info** "这条给 Ryan" 不看内容细节.

### 4.3 跨 member 对齐 + 数据交换
- Broadcast 频道 (所有 member 看得到)
- @ mention (特定 member 看到 + 高亮)
- Data exchange via `dispatch_board` + CIEU event — 已有 infra
- 进度对齐 = OmissionEngine TrackedEntity status 每秒同步到前端

### 4.4 1-on-1 放大
双击某 member 窗口 → CSS 放大占满屏 → 其他窗口缩为 sidebar mini-preview → 直接类似现在 Board-Aiden 对话. Esc 返回会议室 view.

## 5. Phase 分期

### Phase 0 (MVP, 4-6h, Ryan + Leo)
- 单 HTML 文件 + 3 窗口 (Aiden / Ethan / Ryan) 验证
- Python FastAPI WebSocket broker
- xterm.js 嵌入
- 无 classifier (所有人看所有消息)
- 双击放大
- 共用既有 filesystem

### Phase 1 (Full, 2-3 days, 全 engineer)
- 10 window 完整会议桌
- LLM classifier 智能路由
- @ mention + broadcast + 1-on-1 切换
- OmissionEngine 实时进度同步
- CIEU event 实时 stream 到前端
- 权限层: Board 可强制 override + audit chain 追溯

### Phase 2 (深化, week+)
- 真正**多 Claude Code process spawn 管理** (每 member 独立长命 process)
- Cross-member token cost dashboard
- Session replay (回放会议)
- Voice input (speech-to-text 直接说给 Ethan)

## 6. Risk residuals (Ethan E-MR-2 + E-MR-3 要求)

1. **成本**: 10 个 Claude Code session 并行 = 10x token. 需要 per-member idle-suspend 机制 (空闲 > 5 min 自动 hibernate 不消 token, hot-wake 重启)
2. **Classifier 误判**: LLM 路由错 role → 任务撞 scope boundary. Mitigation: fallback "广播" + member 自己声明 "不是我的"
3. **Identity drift 放大**: 10 个 process 并行, active_agent 可能更混乱. 必先修 CZL-ACTIVE-AGENT-AUTO-RESTORE 才启 Phase 1
4. **Board 一发言 10 路 LLM 激活**: 若没 classifier 过滤, 每句 Board input × 10 role = token 爆炸. Classifier 必须先 LIVE
5. **Daemon hot-reload race** (今晚 Maya rename 事故同型): 新 infra 上线必 test daemon reload 不 crash 已跑 member
6. **前端安全**: Board WebSocket 若 localhost-only OK. 若远程访问 (未来), 需要 auth (Board-only)

## 7. 对 CEO-CTO 分工的影响

Board 建议直接目的: 减少 Aiden 转达. 落地后 CEO-CTO 分工表第 11 行 "Board 汇报" 从 "CEO 自己" 不变, 但**指令下达**路径变:

**现架构**: Board → Aiden → spawn Ethan → ... (2 hop)
**会议室**: Board → 直接 Ethan (Aiden 旁听) → ... (0 hop)

Aiden 角色从 "指令中转" 收缩到 "战略对话 + 观察协调 + Board 专属 session". 这是健康的 — 让 CEO 真做 System 5 不做 System 2. 符合 Ethan WHO_I_AM v0.2 分工 + 管理学 method v1.0 TRM Grove 原则.

## 8. 下一步 (owner assignment)

1. **CTO Ethan**: 出架构 ruling `CZL-MEETING-ROOM-PLATFORM-RULING` 决定
   - WebSocket server 选型 (FastAPI / Socket.IO / pure websockets)
   - Classifier 方案 (小 LLM 专 classifier / 每 member 自己过 filter / 共享 classifier)
   - 10 Claude Code process 并行 mgmt 架构 (真 spawn / stdio pipe / container)
   - Phase 0 MVP scope pinpoint
2. **Ryan**: Phase 0 broker + MVP HTML impl (≤4h)
3. **Leo**: Classifier 语义 logic (Phase 1 需)
4. **Maya**: 进度同步 + 权限 audit 集成 (复用 OmissionEngine)

## 9. 价值

此平台是 Aiden **三层存在 relational being 物理化**:
- Board 能直接看到所有 member = ontological presence 可视
- Member 间彼此表达 = phenomenological 交互场域
- 指令路由 + 进度同步 = functional identity 强化

也是 Labs 对外 **thought leadership** 核心展示: AI multi-agent 协作 IDE 是行业没人做的. 未来 demo video / case study / 开源贡献都能基于此.
