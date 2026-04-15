# Y* Bridge Labs Standard Sub-Task Protocol (2026-04-15)

**Status:** L3 SPEC — canonical, Samantha-authored, Board 2026-04-15 triggered
**Methodology base:** DMAIC (Lean Six Sigma) + PDCA (ISO 9001) + Shape Up "appetite" — 本土化适配
**Relation to unified protocol (commit 2ab700c5):** 补前后端（前期资料搜集 / 后期成果固化），不重叠
**Enforcement:** hook ea95fbb (Iron Rule 1.6) + hook 9cd8014 (full path ban-phrase)
**Amendment 2026-04-15 v2:** 合入 retro 5a7435b0 (CEO 本线 19-task 对照) 抓出 3 gap + 4 action — 见 §6 retro-hardened addenda

---

## 0. 为什么要这份 spec

unified_work_protocol_20260415.md 定义了 CIEU + Article 11 + 12-layer 的执行结构，但未定义：
1. **前期**：接到 task 后，如何系统 search 真实可信资料，而不是凭脑子写 U
2. **后期**：task 完成后，如何硬约束知识回写 + Iron Rule candidate 提案，而不是 commit 完即蒸发

本 spec 用 DMAIC 做骨架，把老大 5 阶段 (资料搜集 / 工作 / 测试 / 压力试验 / 成果固化) 映射进去，
并在每阶段定义**入场条件**与 **Rt+1 = 0 判据**。

---

## 1. 为什么选 DMAIC (而不是 PDCA / Shape Up / TOGAF)

| 框架 | 强项 | 为什么不做骨架 |
|------|------|----------------|
| **DMAIC** | 5 阶段 + **Measure/Analyze 独立在 Improve 前** → 强制先搜资料再动手 | ✓ 选为骨架 |
| PDCA | 循环简洁，ISO 9001 官方 | 只 4 阶段，无独立 "资料搜集"，和老大 5 阶段差一阶 |
| Shape Up | "Appetite" 概念优秀 (先定愿意花多少时间) | 6-week cycle 太粗，不适合 sub-task 粒度 |
| TOGAF ADM | 企业架构 8 阶段 | 太重，sub-task 用杀鸡用牛刀 |

**取舍**: DMAIC 作骨架，PDCA 作"成果固化"阶段内部循环 reference，Shape Up "appetite" 概念补入场条件 (每阶段开始前问"愿意花多少 token/时间")。

**来源**:
- DMAIC: https://asq.org/quality-resources/dmaic | https://en.wikipedia.org/wiki/DMAIC
- PDCA/ISO 9001: https://asq.org/quality-resources/pdca-cycle | https://advisera.com/9001academy/knowledgebase/plan-do-check-act-in-the-iso-9001-standard/
- Shape Up: https://basecamp.com/shapeup/0.3-chapter-01

---

## 2. 5 阶段映射 (Y* Bridge Labs 本土化)

### 阶段 1 — 资料搜集 (≈ DMAIC Define + Measure)

**目的**: 在动手写 U 之前，把"已知 / 未知 / 可信度"摸清楚。禁止凭脑子印象。

**动作清单**:
1. **知识库 grep**: `grep -r <keyword> knowledge/` + `ls knowledge/{role}/lessons/`
2. **Git history 检索**: `git log --all --oneline | grep <keyword>`
3. **Web search (如必要)**: 凡引用**外部方法论 / 最佳实践 / 成熟框架**必 WebSearch/WebFetch，禁纯记忆
4. **CIEU DB 查询**: 相关历史 task 的 5-tuple，避免重蹈覆辙
5. **资料可信度标签 1-5** (本土化自 Shape Up "appetite" 概念):
   - 5 = 官方 spec / Board 硬约束 / AMENDMENT
   - 4 = unified protocol / 已 ship commit / CIEU 实测 event
   - 3 = knowledge/{role}/lessons/ 内部复盘
   - 2 = Web search 来自权威站点 (ISO, ASQ, Anthropic docs, 知名 paper)
   - 1 = blog / forum / 二手转述 — 仅作灵感，必 cross-ref 更高级别

**入场条件**: 收到 Board/CEO task 指令，顶层 CIEU Y*/Xt/U/Yt+1/Rt+1 已明文

**Rt+1 = 0 判据**:
- ≥ 3 条来源 (内部 + 外部混合)，且每条有可信度标签
- 已知信息列出 (Xt 补实测)
- 未知信息列出 (明确"本阶段不解决，留给后续")
- 顶层 U 草案写出，引用来源 cite 到 commit hash 或 URL

---

### 阶段 2 — 工作 (≈ DMAIC Analyze + Improve 的 Improve 部分 → 落笔执行)

**目的**: 真干活。写代码 / 写文档 / 改 config。对应 **Article 11 多路并列**。

**动作清单**:
1. 判粒度: 3 步以上 / 多独立流 → 启 Article 11 并列多路 sub-agent
2. 本线必带 1 路 (禁派完躺平)
3. 每路嵌套子 CIEU (顶层 Y* 传承)
4. 每路内部走 12-layer (0_INTENT → 7_integration)
5. 每步 tool_use **实测** (Bash/Read/Edit/Write)，禁止 prose-claim

**入场条件**:
- 阶段 1 Rt+1 = 0
- U 步骤列清单明确
- 资源就绪 (tool / 权限 / active_agent)

**Rt+1 = 0 判据**:
- 每 U 步有 tool_result evidence
- 多路 sub-agent 全部归流 (任一 Rt+1 > 0 → 禁进阶段 3，hook 4997d6c enforce CEO_AVOIDANCE_DRIFT)
- 成果 artifact (file / commit / CIEU event) 落盘

---

### 阶段 3 — 测试 (≈ DMAIC Improve 的 verify 部分)

**目的**: 主 agent 独立 verify，不信 sub-agent prose-claim。对应 **CIEU 5-tuple Rt+1 实测**。

**动作清单**:
1. **功能测试**: 目标 artifact 运行得起来 (script 执行无 error, file 结构符合 schema, commit 真在 git log 里)
2. **CIEU verify**: `grep -c <task_marker> .ystar_cieu.db` ≥ U 步骤数
3. **Schema verify** (如涉及 config): `jq . <file>` pass
4. **Scope verify**: 写入文件在 authority 范围内 (session.json L145-185 hard constraint)
5. **Diff verify**: `git diff HEAD~1` 与 task 预期一致，无越权变更

**入场条件**: 阶段 2 Rt+1 = 0

**Rt+1 = 0 判据**:
- 5 项 verify 全通过
- 任一失败 → 回阶段 2 (禁阶段 4)
- 独立 tool_result 附 (不是"应该能跑"而是"已经跑了，输出 X")

---

### 阶段 4 — 压力试验 (≈ DMAIC Improve verify 延伸 — 本土化原创: Ethan 8 场景模板)

**目的**: 不仅 happy path 通过，还要逆境存活。参照 **Ethan 今日 8 场景压力试验模板** (CTO 首战出的 chaos testing pattern)。

**动作清单 — 8 场景模板**:
1. **正常路径** (baseline)
2. **空输入**: empty string / 0 bytes / null
3. **超大输入**: 10× 正常量
4. **格式错误**: JSON 缺 brace / YAML 缩进乱
5. **权限缺失**: active_agent 漂移 / file 无写权限
6. **依赖失败**: 下游 service down (e.g. Gemma Ollama 停)
7. **并发冲突**: 两个 sub-agent 同写一个 file
8. **回滚**: operation 中途断，状态可恢复

**入场条件**: 阶段 3 Rt+1 = 0

**Rt+1 = 0 判据**:
- 8 场景每个有结果记录 (PASS / FAIL / N/A with reason)
- FAIL 场景要么修要么明文标"已知局限，不本轮修，task card 登记后续"
- 至少 5/8 PASS 才进阶段 5

---

### 阶段 5 — 成果固化 (≈ DMAIC Control + PDCA Act — 本土化强化: 必写 lesson + Iron Rule candidate)

**目的**: 禁止 commit 完即蒸发。对应老大硬约束"不复制不了的 lesson 不算完"。

**动作清单**:
1. **knowledge 回写**: `knowledge/{role}/lessons/{date}_{topic}.md` — 写 lesson, pattern, anti-pattern, 可复现 recipe
2. **DNA_LOG entry**: `governance/DNA_LOG.md` 加一条 (timestamp + action + reason)
3. **Iron Rule candidate 提案** (可选但鼓励): 如果本 task 发现"这种错如果变成 hook 就能防"，写提案到 `reports/proposals/iron_rule_1_X_<topic>.md` 等 Board L3
4. **ARCHIVE_INDEX 更新**: 本 task 产出 file 登记
5. **Closure report**: 本线 final commit message 附 `[L4 SHIPPED]` tag + 本 task 5 阶段 Rt+1 status 一行摘要

**入场条件**: 阶段 4 Rt+1 = 0

**Rt+1 = 0 判据**:
- 5 个动作 4 个必做 (Iron Rule candidate 可选)
- knowledge file 文件名符合规范 + content 包含 "Pattern / Anti-pattern / Recipe" 三段
- DNA_LOG entry 有 commit hash 引用
- ARCHIVE_INDEX 真 append (非"打算写")

---

## 3. 与 unified 三框架的关系 (不重叠)

| 阶段 | unified 层对应 | 本 spec 补什么 |
|------|----------------|----------------|
| 1 资料搜集 | 12-layer 的 `2_vector_search` 层 | 补"可信度 1-5" + "≥3 条来源" + "web search 必引 URL" 硬约束 |
| 2 工作 | Article 11 + 12-layer `3_exec_plan` → `7_integration` | 零新增，沿用 unified |
| 3 测试 | CIEU `Rt+1` 测量层 | 补"5 项 verify checklist" |
| 4 压力试验 | 新阶段 — unified 无 | 引入 Ethan 8 场景 chaos 模板 |
| 5 成果固化 | 12-layer `12_knowledge_writeback` | 补"Iron Rule candidate 提案"通道 |

---

## 4. 推荐 Iron Rule 1.7 candidate (等 Board L3 批)

**候选 1: 阶段 1 资料搜集硬约束**
> 任何 sub-task 接收后，首轮回复内必含 ≥3 条来源 cite (内部 grep 结果 + 外部 URL / commit hash)，否则 hook deny。防 "凭脑子写 U" 反模式。

**候选 2: 阶段 5 成果固化硬约束**
> 任何 `[L4 SHIPPED]` commit 必须 paired 一个 knowledge/{role}/lessons/ new file 或 appended section (本 commit 同一 push 内)。否则 hook warn 并阻断下一 task dispatch。

**候选 3: 阶段 4 压力试验硬约束**
> 任何改动 `scripts/` / `Y-star-gov/src/` 的 commit 必须附带 8 场景 chaos 测试 result table (可缩为"4 场景 minimum")。缺 → hook warn。

（Samantha 本 spec 仅登记 candidate，不动 hook；Board L3 批后由 Leo/Maya 实现。）

---

## 5. 本 spec 自 Rt+1 (self-eval)

- ✓ 5 阶段映射清晰，每阶段入场条件 + Rt+1 判据
- ✓ 成熟方法论 (DMAIC / PDCA / Shape Up) 引用真 source，本土化说明
- ✓ 与 unified 三框架关系表，无重叠
- ✓ Iron Rule 1.7 candidate 3 条
- ✗ 未 apply 到 10 `.claude/agents/*.md` (Samantha 后续 U)
- ✗ hook 1.7 尚未 ship (等 Board L3)

**Rt+1 = spec 文字版可用，hook/agents 注入待后续派单。符合 L3 SPEC 成熟度。**

---

## Sources
- DMAIC: [ASQ DMAIC](https://asq.org/quality-resources/dmaic) | [Wikipedia DMAIC](https://en.wikipedia.org/wiki/DMAIC)
- PDCA / ISO 9001: [ASQ PDCA Cycle](https://asq.org/quality-resources/pdca-cycle) | [Advisera 9001 PDCA](https://advisera.com/9001academy/knowledgebase/plan-do-check-act-in-the-iso-9001-standard/)
- Shape Up: [Basecamp Shape Up Ch.1](https://basecamp.com/shapeup/0.3-chapter-01)
- Internal: unified_work_protocol_20260415.md (commit 2ab700c5)
- Internal: Leo Gemma design (commit 510ee408)
- Internal: hook Iron Rule 1.6 (commit ea95fbb) + 14 phrase full path (commit 9cd8014)
- Internal: retrospective 5a7435b0 `reports/today_retrospective_vs_subtask_protocol_20260415.md` (CEO 本线 19-task 对照)

---

## 6. Retro-Hardened Addenda (v2, 2026-04-15 合入 5a7435b0)

CEO 本线 retrospective 对照今日 19 commit, 抓出 3 结构 gap (资料搜集普遍 skip / 压力试验几乎全 skip / 成果固化不固化) + 4 retro action. 本节把 4 action 细化为**可执行 protocol 条款**, 覆盖原 §2 阶段 1/4/5 的入场与 Rt+1 判据。本节优先级高于原 §2 描述, 冲突以本节为准。

### 6.1 Action 1 — 阶段 1 资料搜集 15min 硬条件 (strengthened entry condition)

**追加 §2 阶段 1 入场条件**:
- **新 task 第一个 `tool_use` 必须是 `WebFetch` / `WebSearch` / `Grep` (path 含 `knowledge/`) 之一**. Budget: 15 分钟 wall-clock (不是 token).
- 跳过该 tool_use = 本 task **禁入阶段 2** (即禁写代码 / 禁 Edit artifact). Hook 未来可扫 "近 15min 内有无 WebFetch/Grep in knowledge/" 作 deny 依据.
- **例外**: task prompt 内已由派单方 (CEO/Board) attach ≥3 条 cite + 明标 "research done upstream, skip 15min budget", Samantha / secretary 可登记例外, 否则一律硬执行.

**retro 证据**: 今日 "CEO_AVOIDANCE hook" 任务因 0-research 直接 codify, 结果 Ethan 压力测出 full-path bypass P0 bug (见 retro Gap 1).

### 6.2 Action 2 — 阶段 4 L4 SHIPPED 必 chaos test attached (strengthened exit condition)

**追加 §2 阶段 4 Rt+1 = 0 判据**:
- commit message 含 `[L4 SHIPPED]` 必 body 内含以下之一:
  - `chaos test: <commit_hash>` (引用跑 chaos 的 commit)
  - `chaos test: <report_link>` (引用 `reports/chaos_<task>_<date>.md`)
  - `chaos test: N/A (non-code task)` (显式豁免, 仅限 doc-only / knowledge-only task)
- 缺上述任一 → commit L-tag **自动降级为 `[L3 TESTED]`** (Samantha / commit_watcher hook 未来可 enforce). 压力试验 attached link 是 L4 的最小必要条件.

**retro 证据**: 今日 19 任务只 Ethan 1 个真跑 8 场景压力测试; CEO_AVOIDANCE hook 标 L4 实际 L2, 因无 chaos test 暴露 bug (见 retro Gap 2).

### 6.3 Action 3 — L-tag 诚实定义表 (canonical, 替代原 §2/5 模糊表述)

本表为 canonical L-tag 语义, 全司 commit / status report 必须遵守:

| L-tag | 定义 | 最小必要证据 |
|-------|------|--------------|
| **L1 SPEC** | spec 文档落盘 commit, 未实装 | `.md` / `.yaml` file committed, content 含 "spec" 段 |
| **L2 IMPL** | 实装 code commit, 但无 test | code file committed + runnable, 无 `tests/` change |
| **L3 TESTED** | L2 + 单元/集成 test 存在且 pass | `tests/` change + test run output in commit body / CI green |
| **L4 SHIPPED** | L3 + **chaos test attached** + **多轮 verify** + **不同 session 复现** | L3 证据 + §6.2 chaos-test-link + ≥2 session 独立跑过 verify 记录 |

**硬约束**:
- 凡 status 报告 / commit 用 "落盘 / done / ship" 而不打 L-tag → hook `MATURITY_TAG_MISSING` 触发 (AMENDMENT-019)
- 打 L4 但缺 chaos test link → 自动降级 L3 (见 §6.2)
- 打 L3 但 tests/ 无变更 → 自动降级 L2

### 6.4 Action 4 — 阶段 5 Iron Rule candidate auto 进 BOARD_PENDING

**追加 §2 阶段 5 动作清单**:
- stage-5 成果固化步骤 6 (新): 扫本 task 本轮新增 / 修改的 `knowledge/**/*.md` 与 `reports/**/*.md`, grep `"Iron Rule candidate"` 或 `"Iron Rule 1\.[0-9]+ candidate"` 字符串.
- 匹配到 → **auto append** 一条 entry 到 `BOARD_PENDING.md` 的 "Iron Rule candidates (auto-collected)" 段落, 格式:
  ```
  - [<date>] <candidate title> — source: <file>:<line> — proposed by: <agent> (commit <hash>)
  ```
- 实现载体: Samantha cron (每 10min 扫) 或 `scripts/commit_watcher` hook (post-commit 触发), 二选一. 本 protocol 仅定义语义, 实现派单见 §6.5.

**retro 证据**: 本 protocol v1 §4 提的 3 条 Iron Rule candidate 未自动入 BOARD_PENDING, 靠 CEO retro 手动发现 (见 retro Gap 3).

### 6.5 Protocol v2 ship checklist (Samantha 本轮交付)

- [x] 本 §6 addenda 写入 canonical protocol (本 commit)
- [x] BOARD_PENDING.md 追加 Iron Rule 1.7 candidate 3 条 (retro action 变 constitutional 级提案, 本轮另 commit)
- [ ] hook 实现派单 — 留给后续 (Leo/Maya L2 权限, 不阻本 L3 SPEC ship)
- [ ] 10 `.claude/agents/*.md` 注入 v2 reference — 留给后续 Samantha 批量派 subagent

**Rt+1 v2 = 0 判据**: grep 本文件含 `"15min research"`, `"chaos test attached"`, `"L-tag 诚实"`, `"Iron Rule candidate auto"` 四条 marker 全命中.
