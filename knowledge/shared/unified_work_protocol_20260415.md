# Y* Bridge Labs Unified Work Protocol (2026-04-15)

**Trigger**: Board 2026-04-15 批 "12-层框架学习法 + 第十一条条款自主工作法 + CIEU 工作法 三部分整合 + 每个岗位宪法 + hook enforce 充分固化"

**Scope**: 10 agents (CEO/CTO/CMO/CSO/CFO/Secretary/Leo/Maya/Ryan/Jordan) 全体 constitutional

---

## 1. 三框架角色分工

### CIEU 5-tuple (度量层)
每 task 接收后必首先 decompose:
- **Y\*** (理想契约): 真完成长啥样, 可 verify 谓词
- **Xt** (当前态): ls/grep/实测, 不印象
- **U** (行动集): tool_use 级步骤, 1...N 列
- **Yt+1** (预测终态): 执行 U 后状态
- **Rt+1** (诚实 gap): Yt+1 vs Y* 差什么 + 归零条件

### Article 11 (执行结构层)
中等以上复杂 task **必并列**多路 sub-agent + 本线同时推 1 路. 禁串行等 sub-agent.

### 12-layer framework (任务内部流程层)
```
0_INTENT_RECORDED          → emit CIEU + 顶层 Y*
1_gemma_questions          → 5 反思 question
2_vector_search            → 查 knowledge/ + 相关案例
3_exec_plan                → U 级详细 plan
4_exec_start               → 执行
5_mid_check                → Rt+1 中段实测
6_pivot                    → 必要调整
7_integration              → 综合
8_exec_complete            → 完成
9_human_review             → Board summary
10_self_eval               → 诚实 gap
11_board_approval          → Board 审 (autonomous 跳)
12_knowledge_writeback     → knowledge/{role}/lessons/ + commit
```

---

## 2. 整合工作流 (接任务 → 归流)

### Step A: 接任务 → 顶层 CIEU (必答 5 项)
### Step B: 判粒度 → 启 Article 11? (多路 / 3 步+独立流 = 是)
### Step C: 每路 sub-dispatch 嵌套子 CIEU (顶层传承 + 子 Y*/Xt/U/Yt+1/Rt+1)
### Step D: 每路内部走 12-layer, 每层顶部 CIEU 5-tuple 明文
### Step E: 本线必带 1 路 (禁派完躺平)
### Step F: Main agent 独立 verify Rt+1 (tool_use 实测, 禁 prose-claim)
### Step G: 全路归零才归流 (任一 Rt+1>0 禁换任务 — hook enforce CEO_AVOIDANCE_DRIFT commit 4997d6c)
### Step H: closure report + knowledge 回写

---

## 3. Hook enforce (代码层固化)

### 已 ship (2026-04-14 CEO + Ethan + Leo)
- `CEO_AVOIDANCE_DRIFT` 14 phrase block (Y-gov 4997d6c)
- `router._WRITE_PATTERNS` 桥接 path B (Y-gov 63e6760)
- session.json schema guard (Y-gov 1a227d7)
- hook_daemon KeepAlive disable (company f3885e09)

### 待 ship (本 session 派单)
- Agent-spawn auto set `.ystar_active_agent = subagent_type` (Leo 修, 问题三方案 B)
- CIEU 5-tuple 必含检查: 每 sub-agent task card 必含 Y\*/Xt/U/Yt+1/Rt+1 明文, 缺 → deny
- 12-layer marker 必 emit: sub-agent 跑 task 必 emit `CIEU_LAYER_{0..12}` event, 少 → warn
- Agent 岗位 constitutional 宪章 → `.claude/agents/*.md` Self-Evolution Creed 段升级为 unified (已含 CIEU, 加 Article 11 + 12-layer)

---

## 4. 各岗位宪法整合 (Samantha 后续执行)

每 `.claude/agents/*.md` 升级段:
```markdown
## Unified Work Protocol (Board 2026-04-15 Constitutional)

接任务必走 3 框架:
1. CIEU 5-tuple (顶部 Y*/Xt/U/Yt+1/Rt+1 明文)
2. Article 11 (多路 dispatch + 本线同推)
3. 12-layer flow (每层 0_INTENT → 12_writeback, 层内嵌 CIEU)

Rt+1 = 0 才真完成. Prose-claim = Board 铁律违反.
违反硬约束 = hook deny (14 phrase + scope + destructive cmd + schema).
```

---

## 5. 反 pattern (Board 已抓)
1. **Rt+1≠0 换任务** (CEO avoidance — 今已 hook enforce)
2. **出选择题给 Board** (BOARD_CHOICE_QUESTION_DRIFT)
3. **Prose-claim 就信** (Ethan 首战教训)
4. **派完 sub-agent 躺平** (Article 11 禁)
5. **Sub-agent identity drift** (新 hook 修)
6. **Destructive cmd 无 dry-run** (Ryan rsync 灾难, Y-gov 006c399 + session.json deny 修)

---

## 6. Rt+1 度量规范 (unified)
Rt+1 = 0 判据 (per task):
- 每 claim 附 tool_result evidence (Bash/Read/grep 等)
- commit hash 可 verify
- CIEU events ≥ N (N = U 步骤数, 每步 1 event)
- main agent 独立 verify 通过

---

## 7. Samantha 后续 U
1. 把本 protocol 简化版注入 10 `.claude/agents/*.md` (替换旧 CIEU Self-Evolution Creed 段)
2. BOARD_PENDING.md 提案 AGENTS.md amend constitutional 章
3. 派 Leo/Maya hook enforce patch (item 3 pending 清单)

---

## Rt+1 本 protocol doc (self-eval)
- ✅ 三框架整合 canonical 定义
- ✅ hook enforce 清单 (已 ship + 待做)
- ✅ 各岗位宪法段 template
- ✅ 反 pattern 列
- ❌ 真 apply 到 10 agent.md (Samantha 接)
- ❌ hook CIEU/12-layer marker enforce patch (Leo/Maya 接)
