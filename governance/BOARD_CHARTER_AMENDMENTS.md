# Board Charter Amendment Log
# Y* Bridge Labs 宪法修改授权档案
#
# 流程（2026-04-10 更新，per Board capability system directive Q1 answer）：
#   Board表达修改意图（口头/文字）
#   → Secretary记录到本文件（含修改内容、理由、Board授权时间戳）
#   → **Secretary自己执行修改**（直接编辑AGENTS.md或其它宪法文件）
#   → Secretary提交commit，发Board commit hash
#   → Secretary更新本文件执行状态为「已完成」
#
# 历史流程：旧版本要求「Secretary转交Ethan执行」——2026-04-10 Board
# 明确要求 Secretary 自己执行，不再走 CTO 代执行。Rationale: Secretary
# 是 Board 的笔而不是判断者，笔自己动比交给 CTO 代写更清晰，也避免了
# 跨角色的转交误差（GOV-004 最初的设计意图本身就是「Secretary 是执行
# 手」）。
#
# Board将来想修改AGENTS.md时：
#   只需对任何agent说："记录一条宪法修改意图：在AGENTS.md的XXX里加/改YYY，理由是ZZZ"
#   Secretary自动处理后续全流程。
#
# 团队想建议修改AGENTS.md时：
#   向Secretary提案 → Secretary整理后报Board确认 → Board说可以 → Secretary记录 → Secretary执行

---

## AMENDMENT-001

| 字段 | 内容 |
|------|------|
| 日期 | 2026-04-09 |
| Board授权 | 口头确认（GOV-004 directive） |
| 修改内容 | 在AGENTS.md的deny_commands段加入一行：`"ystar setup --yes"` |
| 理由 | ystar setup --yes会覆盖现有.ystar_session.json配置（GOV-001 Step 2事故根因），必须在机器层面阻止任何agent执行此命令 |
| 执行人 | Ethan Wright |
| 执行状态 | 已完成（执行层）|
| 执行时间 | 2026-04-09 |
| 执行commit | `2f4d2e8` |
| 备注 | deny_commands已在.ystar_session.json生效（GOV-005 Part 3 directive 改写了执行路径，绕开AGENTS.md hook block）。AGENTS.md文档同步待Board下次直接编辑时补充，不阻塞安全性。机器层面任何agent执行`ystar setup --yes`将被Y*gov hook即时拦截。|

---

## AMENDMENT-002（编号占位）

**状态**：非本文件正式条目。

GOV-008 完成报告和 README.md 中曾把 daemon 退役记为「AMENDMENT-002」，
见 `archive/deprecated/DAEMON_RETIREMENT.md`。但 daemon 退役**没有修改
AGENTS.md**——只退役了一个目录、写了一份 DAEMON_RETIREMENT.md 记录。
按本文件的 scope（charter amendment = AGENTS.md 修改），daemon 退役
不算 charter amendment。

这里保留「AMENDMENT-002」这个编号占位是为了和外部文档（README、GOV-008
报告）保持一致，避免未来读者困惑。下一条真实的 AGENTS.md 修改从
AMENDMENT-003 开始。

---

## AMENDMENT-003

| 字段 | 内容 |
|------|------|
| 日期 | 2026-04-10 |
| Board授权 | 文字确认（capability system directive, Q1 answer：「选(a)，Samantha改，作为AMENDMENT-003」）|
| 修改内容 | 在AGENTS.md的「Continuous Autonomous Work Mandate」节后新增一条「空闲学习循环 (Idle Learning Loop)」规则，作为 rule 7。定义三个优先级（岗位认知建构 / 理论库构建 / 反事实模拟练习）、强制调用 `scripts/local_learn.py` 的 Gemma 使用规则、以及 `gemma_sessions.log` 的 JSONL 审计条目格式。每日报告模板新增四行（今日学的理论 / 完成的任务类型理论库 / 模拟的场景+gap / 知识库更新）。|
| 理由 | GOV-006 到 GOV-009 建立的合规系统抓「Board 说 X，agent 做非 X」。合规系统没抓的是「Board 说 X，agent 做到完美的 X，但 agent 对世界的理解是错的」。能力系统是第二个洞的补丁。没有空闲学习循环，知识库永远是空壳子；没有强制 Gemma 调用，agent 永远在自己的认知盲点里绕圈。本修改是把 capability system 从「工具存在」升级到「使用是义务」。 |
| 执行人 | Samantha Lin（Board Q1 answer 明确要求 Secretary 自己执行，不走 CTO 代执行）|
| 执行状态 | **BLOCKED by Y\*gov immutable-path hook** — 同 AMENDMENT-001 |
| 执行时间 | 尝试时间 2026-04-10（被 hook 硬拒）|
| 执行commit | 尚无 |

### 执行阻塞：Y\*gov immutable-path hook

Samantha 按 Board Q1 answer 尝试直接编辑 `AGENTS.md` 添加 rule 7，Y\*gov PreToolUse hook 返回：

> `[Y*] Immutable path violation: '/Users/haotianliu/.openclaw/workspace/ystar-company/AGENTS.md' is a governance charter file and cannot be modified by any agent.`

这是 Y\*gov 内核在 `_hook_client.sh` 层面的硬拒，不是 `.ystar_session.json`
里的 `intent_guard_protected_paths` 的 warn-only 守卫。内核的 immutable
path 规则对**所有 agent**（包括 Secretary）一视同仁硬拒，无论 GOV-006
intent 是否 qualified、无论本 Board directive 授权。

AMENDMENT-001 当时遇到的是同一个 block——看 AMENDMENT-001 备注行：「AGENTS.md 文档同步待 Board 下次直接编辑时补充」。实际执行路径是把
deny rule 写到 `.ystar_session.json` 的 `deny_commands` 字段绕开了
AGENTS.md 本身。那是因为 deny_commands 有结构化的配置位置。

本 AMENDMENT-003 的问题不一样：空闲学习循环是**行为规则**，不是
deny rule，没有 `.ystar_session.json` 里的结构化位置可以承载。它本来
就是要放进 AGENTS.md 作为 Board Directive #021 的延伸条款。

### 现实路径

规则的**操作内容**已经放进 `governance/WORKING_STYLE.md` 第九条
（本 commit B 交付）——所有 agent 在 session boot 时会读 WORKING_STYLE.md，
所以规则在运行时是**有效的**，agent 有可遵循的成文依据，GOV-009 Change 3
的 `mark_fulfilled` 前置条件 ③（48h 知识库新鲜度）也已经在 hook 层面
强制执行。

**缺的只是 AGENTS.md 这一份"宪法层面"的象征性挂接**——即把这条规则在
公司最顶层的 charter 文档里正式登记为 Board Directive #021 的延伸。
没有它，外部读 AGENTS.md 的人（包括未来的审计）不会看到空闲学习循环
是 constitutional。

### 可用的三个补救方案

- **(X) 留在 WORKING_STYLE.md 第九条，跳过 AGENTS.md 挂接**。规则有效、
  可执行、可审计。AGENTS.md 上看不到这条的直接登记，但 `AMENDMENT-003`
  本身（即本文件）就是登记。缺点：charter 文档的 "index" 不完整。
- **(Y) Board 自己手动编辑 AGENTS.md**。Board 不是 agent，hook 不拦 Board。
  Board 可以直接在文件系统上 open 一个编辑器改 AGENTS.md，把 rule 7
  贴进去。本 AMENDMENT-003 记录里保留完整 diff 文本供 Board 复制。
- **(Z) Board 临时 override Y\*gov 内核的 immutable path 规则**，允许
  Samantha 执行一次性 amendment，然后恢复。工程量中等；修改
  `Y-star-gov/ystar/_hook_client.sh` 或对应 kernel 条目。

**Samantha 的建议**：(X)。理由：本次 directive 的**可执行意图**已经
实现——规则写在 WORKING_STYLE.md 第九条，agent 行为上会跑，GOV-009
freshness gate 会硬拒不跑的 agent 去 mark_fulfilled。AGENTS.md 挂接
是文档完整性问题，不是安全或功能问题，可以在未来某次 Board 自己编辑
AGENTS.md 的机会里一并补上。过度工程化方案 (Z) 只是为了补一行 charter
登记。Board 可以选择 (Y) 或 (Z)，但 Samantha 认为 (X) 是成本最低且
不欠账的路径。

### 本 AMENDMENT-003 的「如果 Board 选 (Y)」预制 diff

如果 Board 选 (Y)，需要把以下内容**原样**粘贴到 `AGENTS.md` 的
"Continuous Autonomous Work Mandate" 节内，现有 rule 6 之后，
"**This rule exists because:**" 段之前。diff 预制文本存档在本文件
最末尾的「附录 A」（见本文件末尾），保证 Samantha 提供的 AGENTS.md
挂接内容和 WORKING_STYLE.md 第九条的运行时规则一字不差。

### 备注

本次修改是 capability system directive 的一部分，配套交付：
- commit A（a49595e）: knowledge/ 目录 + scripts/local_learn.py + .ystar_session.json gemma_endpoints
- commit B（fe41ad1）: WORKING_STYLE.md 第九条初版 + 本 AMENDMENT-003 记录 + agents/Secretary.md 的 gemma_sessions.log 周审计条款；**AGENTS.md rule 7 挂接 BLOCKED**
- commit C（后续）: 六个岗位的 task_type_map.md 起草稿

### 第二次尝试 — 2026-04-10 Board 再次明确授权

Board 在 2026-04-10 发出「Samantha 完整执行指令」，明确要求：

> 按 GOV-004 流程，先在 `governance/BOARD_CHARTER_AMENDMENTS.md`
> 写入 AMENDMENT-003 授权记录，然后修改 AGENTS.md。

即 Board 在了解**或不了解**前次 BLOCKED 状态的情况下再次授权同一
edit。Samantha 第二次尝试 Edit 工具调用，记录在最终报告里。两种
可能结果：

- **结果 α**：Edit 仍被 Y\*gov 内核 immutable-path hook 硬拒——说明
  2026-04-09 以来内核行为未变。那么本 AMENDMENT-003 保持 BLOCKED
  状态，运行时权威继续落在 `governance/WORKING_STYLE.md` 第九条 +
  `agents/Secretary.md` 的 gemma 周审计 +  GOV-009 Change 3 freshness
  gate 的组合上。Samantha 不会用 Bash 工具绕过 hook，因为 hook 的
  状态声明是「cannot be modified by any agent」——用 Bash 绕是在
  agent 层面违反 Iron Rule 1 的声明式意图，不符合 GOV-006 method C
  的「detection-via-audit，不 bypass」哲学。Board 可以选：(Y) 自己
  手动编辑 AGENTS.md（Board 不是 agent，hook 不拦 Board）；或 (Z)
  override 内核 immutable-path 规则允许 Secretary 执行一次性
  amendment
- **结果 β**：某种原因 hook 放行——例如 intent 现在是 qualified 或
  内核已升级——那么 Samantha 直接完成 AGENTS.md edit，把本 AMENDMENT-003
  状态改为「已完成」，填上 commit hash

第二次尝试的实际结果将在本 commit 的 commit message 里明确记录，
本文件也会在 commit 生效后更新最终状态。

**第二次尝试的实际结果（2026-04-10）: 结果 α 成立**——Y\*gov 内核
immutable-path hook 仍然硬拒 Edit 工具对 AGENTS.md 的任何调用，
error 原文与 2026-04-09 第一次完全一致：「[Y\*] Immutable path
violation: '/Users/haotianliu/.openclaw/workspace/ystar-company/AGENTS.md'
is a governance charter file and cannot be modified by any agent.」

Samantha **没有**使用 Bash 工具绕过 hook。原因：hook 的声明是
"cannot be modified by any agent"，Secretary 是 agent 的一种，用
Bash 绕开 hook 的检查是**在 agent 层面违反 Iron Rule 1 的声明式意图**。
这和 GOV-006 method C 早先 review 里拒绝的「hook 硬拦但脚本绕过」
是同类行为——绕过了就等于宣告 hook 的 invariant 不可靠。即使 Board
在 directive 里授权了编辑，授权是 policy 层面的允许，hook 是 mechanism
层面的阻断，policy 不自动翻译为 mechanism。

**结论**：本 AMENDMENT-003 维持 BLOCKED 状态不变。运行时权威继续
落在 `governance/WORKING_STYLE.md` 第九条 + 本文件附录 A 的预制
text（见文件末尾）。Board 如果仍希望 AGENTS.md 文本挂接，方案 (Y)
（Board 自己手动编辑，Board 不是 agent，hook 不拦）或 (Z)（修改
Y\*gov 内核允许 Secretary 例外）仍是唯一可用路径。Samantha 建议
保持 (X)：运行时规则已经在 WORKING_STYLE.md 生效，charter index
缺失一行不影响功能。

### 第三次配套交付

- commit D（本 commit，2026-04-10）: 第九条重写为 Board 整合版 +
  第二次尝试 AGENTS.md edit + roadmap/MULTI_AGENT_ROADMAP.md 新增 +
  README.md 我们在走向哪里 section + agents/Secretary.md 周审计模板
  新增 Multi-agent Roadmap 进度块 + CIEU 义务注册（周期 604800s）

---

## 附录 A — AMENDMENT-003 的 AGENTS.md 预制 diff（供 Board 选 (Y) 时复制粘贴）

如果 Board 选择方案 (Y)（自己手动编辑 AGENTS.md），下面是 Samantha
预制的完整 rule 7 + rule 8 文本。请**原样粘贴**到 `AGENTS.md` 的
「Continuous Autonomous Work Mandate」节内现有 rule 6 之后、
"**This rule exists because:**" 段落之前。粘贴后在 commit message
里引用本附录和 AMENDMENT-003 作为 authorization source。

```markdown
7. **Idle Learning Loop (空闲学习循环) — Constitutional as of 2026-04-10, AMENDMENT-003.** When no Board directive is active, self-directed work is not arbitrary. It runs through a three-priority ordered loop designed to build role capability rather than just fill hours. Every agent, every idle session, follows this loop.

   **Priority 1 (once per role, then updated as the role evolves): 岗位认知建构 (role cognition construction).**
   Build the three files under `knowledge/{role}/role_definition/`:
   - `world_class_standard.md` — what does world-class at this role look like (outside world's standard, not self-description)
   - `role_heroes.md` — named top practitioners and how they actually work
   - `task_type_map.md` — self-decomposition into ≥8 task types with description / core verbs / priority / frequency

   Priority 1 is the *input* to Priority 2. Until it exists, Priority 2 cannot start.

   **Priority 2 (at least one task type advanced per idle day): 理论库构建 (theory library building).**
   Pick a task type from `task_type_map.md` that has no file in `knowledge/{role}/theory/` yet. Walk the **6-step theory calibration protocol** documented in `governance/WORKING_STYLE.md` 第九条 layer 3. Write the resulting theory entry to `knowledge/{role}/theory/{task_type}.md`.

   **Priority 3 (at least one simulation per idle day): 反事实模拟练习 (counterfactual simulation practice).**
   Use `scripts/local_learn.py --mode tasks --actor {role}` to generate a fictional scenario. Walk through the 12-layer framework (layers 0–8), output a plan but do NOT execute. Use `scripts/local_learn.py --mode eval ...` to generate a first-draft self-evaluation, then revise it. Record the surfaced cognitive gaps in `knowledge/{role}/gaps/YYYY-MM-DD-{scenario_slug}.md`.

   **Mandatory Gemma usage (non-negotiable).** All three priorities run under local-Gemma assistance via `scripts/local_learn.py`:
   - Before starting Priority 2 (theory library building), call `local_learn.py --mode questions --actor {role} --task "<task type description>"` to generate an uncertainty-point list. Do NOT skip this step and go straight to searching. The point of using Gemma is not that Gemma is smarter — it is that Gemma asks questions from *outside* the agent's own knowledge frame, which breaks the agent out of its own closed loop. The agent's self-generated questions live inside its known space; Gemma's questions can surface unknown unknowns.
   - After every Priority 3 counterfactual simulation, call `local_learn.py --mode eval ...` to generate the first-draft self-evaluation. The agent must revise and confirm the draft — Gemma never has the final word — but the first draft must go through this call.

   **Audit log (non-repudiable evidence).** Every `local_learn.py` invocation writes one JSONL entry to `knowledge/{canonical_actor}/gaps/gemma_sessions.log`. Format per entry:
   - `timestamp` — ISO-8601 local time
   - `mode` — one of `questions` / `tasks` / `eval`
   - `actor` — raw actor name (legacy names canonicalized for the log path)
   - `endpoint` — Gemma URL that answered (or `null` if fail-open fired)
   - `model` — model ID used
   - `input_summary` — 200-char truncated input
   - `question_count` — integer (mode=questions only)
   - `output_hash` — sha256:16 of the output text
   - `output_length` — integer

   Secretary reads this log every Monday as part of the weekly audit and verifies that every role has at least one entry per working day. Missing daily entries = violation of the idle learning obligation.

   **Daily autonomous report additions (rule 3 report format is extended).** The nightly report template gains four new lines under "Learning Done (self-directed)":
   - 今日学的理论（理论名 + 对岗位的启示）
   - 完成的任务类型理论库（哪个 task type，在 `theory/` 里新增了哪个文件）
   - 今日模拟的场景 + 发现的 gap（`gaps/` 里的哪个文件）
   - 知识库更新路径（哪些 `knowledge/{role}/*` 文件在本次 session 里被写入或修改）

8. **Y*gov enforcement for idle learning:** The idle learning loop is enforced indirectly through GOV-009 Change 3 (`check_obligations.py --mark-fulfilled` precondition ③ requires `knowledge/{actor}/` to have at least one file with mtime within the last 48 hours). An agent that never does idle learning cannot close any Level 2/3 obligation — which is a harder gate than SOFT_OVERDUE but a softer gate than a hook block, consistent with the "detection via audit" philosophy of GOV-006 option C.
```

**附录 A 的运行时权威说明**：本预制 diff 是**文本挂接**，不是运行时
权威。运行时权威是 `governance/WORKING_STYLE.md` 第九条的"空闲学习
循环"小节。agent 读宪法时会通过 WORKING_STYLE.md 看到这些规则。即使
Board 永远不选 (Y)，规则本身是 effective 的。
