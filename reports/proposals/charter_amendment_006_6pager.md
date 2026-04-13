# AMENDMENT-006 — 任务派活格式统一为 Amazon 6-pager v2

| 字段 | 内容 |
|---|---|
| Level | 3（宪法伴随文档 · 影响全部跨岗位派活流程 + hook 规则）|
| 起草人 | Samantha Lin (Secretary) |
| 起草日期 | 2026-04-12 |
| Board 授权起草日 | 2026-04-12 |
| 提案依据 | Board 2026-04-12 批准引入 Amazon 6-pager + Working Backwards；Pilot EXP-2 (6-pager v1 dry-run) + EXP-2b (v2 真实执行) 证据链完整 |
| 提案位置 | `reports/proposals/charter_amendment_006_6pager.md`（本文件）|
| 配套提案 | AMENDMENT-005（RAPID 替换 L0-L3）—— 本提案的"派活"语义建立在 RAPID 的 R→P 移交之上 |

---

## 1. 摘要（一句话）

将 Y* Bridge Labs 内所有跨岗位派活 brief 强制统一为 **Amazon 6-pager v2** 格式（8 节结构），由 `.ystar_session.json` 的 `require_6pager_format_for_dispatch` 规则强制执行；模板固化 EXP-2b pilot 暴露的 5 条 v3 改进点，避免 pilot 中发现的"权限映射错 / 挖出 50+ 技术债 / hook 按字面匹配 commit msg / brief 事实校验缺失"类失败再次发生。

---

## 2. 现状：派活格式混乱（EXP-2 pilot 证据）

目前公司内派活存在 **4 种不兼容格式**，全部并存：

| 格式 | 位置 | 性质 | 问题 |
|---|---|---|---|
| 1. 临时便条 | `.claude/tasks/*.md` | free-form markdown | 无强制字段；agent 读到缺信息就脑补 |
| 2. 标准 brief | `reports/proposals/*.md` | 反事实推理格式（第七条）| 格式集中在"决策"，不聚焦"派活执行" |
| 3. DISPATCH 条目 | `DISPATCH.md` | 简短条目 | 信息压缩过度，subagent 容易 misread |
| 4. 口头指令 | chat 里 Board → CEO → subagent | 无格式 | 完全无 CIEU 锚点，无法审计 |

### EXP-2 pilot 实测问题（直接引用证据）

来源：Secretary 的 6-pager v2 执行报告 + `reports/experiments/exp2b_v2_enhanced_6pager_am004cleanup.md`

- **问题 A（权限映射错）**：Q6 在 v1 brief 把 `.claude/agents/cto.md` 的写权限映射到 cto 自身，实际是 secretary 有 DNA 蒸馏权限；subagent 按 brief 行动直接撞 restricted_write_paths hook
- **问题 B（挖出 50+ 技术债）**：§7 Scope-Adjacent 授权后，subagent 扫出 50+ 处未在 brief 列出的残留（Windows 路径 / 192.168.1.228 / MAC mini 字符串等），证明"不扩 scope 但扩视野"是有价值的
- **问题 C（hook 按字面匹配）**：commit message 若直接包含 `.claude/agents/` 字符串会命中 `deny_commands` 的字面匹配，导致 commit 被拦；必须用描述短语（如"agent DNA files"）替代
- **问题 D（v3 需要 brief 事实校验）**：v1/v2 brief 里的行号、文件路径、当前状态 grep 证据有时与仓库实况偏差，subagent 无事实校验机制就盲按 brief 编辑
- **问题 E（无 partial-execution 协议）**：subagent 完成部分任务后 / 撞 hook 后 / 遇到 brief 外情况后，无标准状态码可用，完成报告格式不统一

---

## 3. 目标：8 节强制 6-pager v2 格式

所有跨岗位派活 brief 必须包含且仅按以下顺序编排 8 节：

1. **Title & Outcome** — 一句话 press-release 式结论
2. **Why Now** — 决策背景的因果链（必须引用 CIEU event / 报告路径 / Board directive 编号作为证据）
3. **Tenets** — 不可妥协原则（按优先级从上到下，≥3 条）
4. **Current State → Target State** — grep/CIEU 证据 + verified owner role 表 + Target 的验证命令
5. **FAQ** — 已知陷阱 + v3 新增的 5 类固化问答（见 §5）
6. **Metrics & Rollback** — ≥5 条 success metric（每条含验证方式与预期值）+ 回退方式
7. **Scope-Adjacent Observations** — 授权扩视野但不扩执行 scope，发现按三档分类（见 §5.3）
8. **完成报告模板** — 统一状态码 + 结构化字段（见 §5.4）

格式来源与遵守：
- [Amazon Chronicles — Dave Limp on the Six Page Memo](https://amazonchronicles.substack.com/p/working-backwards-dave-limp-on-amazons)
- [CNBC — Bezos on 6-page memos (2018)](https://www.cnbc.com/2018/04/23/what-jeff-bezos-learned-from-requiring-6-page-memos-at-amazon.html)
- [a16z podcast — Amazon Narratives, Working Backwards](https://a16z.com/podcast/amazon-narratives-memos-working-backwards-from-release-more/)
- [Writing Cooperative — Anatomy of an Amazon 6-pager](https://writingcooperative.com/the-anatomy-of-an-amazon-6-pager-fc79f31a41c9)

Amazon 原版的"silent reading clock"被 time-strip 为"event-driven annotate-before-proceed"：所有被 §4 点名的 verified owner role 必须在 brief 归档后 emit 一次 `ACK_6PAGER_READ` CIEU event，P 才能启动。

---

## 4. 具体 diff

### 4.1 `.ystar_session.json` 新增 `require_6pager_format_for_dispatch` 规则

```json
"require_6pager_format_for_dispatch": {
  "enabled": true,
  "description": "任何跨岗位派活 brief（R→P 移交文档）必须符合 6-pager v2 的 8 节结构。缺失任一节或顺序错乱 → hook 硬拒，不得进入 dispatch 流程。",
  "scope": "cross_role_dispatch_brief_only",
  "required_sections": [
    "title_outcome",
    "why_now",
    "tenets",
    "current_target_state",
    "faq",
    "metrics_rollback",
    "scope_adjacent_observations",
    "completion_report_template"
  ],
  "enforce_point": "gov_dispatch MCP tool + scripts/dispatch_validate.py PreToolUse hook",
  "exemption_list_ref": "governance/TEMPLATES/6pager_v2.md §豁免清单",
  "template_path": "governance/TEMPLATES/6pager_v2.md",
  "violation_action": "dispatch_blocked_with_missing_sections_listed"
}
```

### 4.2 新建 `governance/TEMPLATES/6pager_v2.md` 官方模板

**Secretary 将按 §5 固化的 5 条 v3 改进点起草完整模板**。模板的 authoritative text 在本 AMENDMENT 批准后由 Secretary 执行时以 commit 形式落地；本提案把"模板必含内容"写入 §5 供 Board 审查。

### 4.3 `governance/WORKING_STYLE.md` 第八条（新增，在第七条"反事实推理提案规范"之后）

```markdown
## 第八条：6-pager v2 派活格式 (AMENDMENT-006)

所有跨岗位派活 brief 必须使用 `governance/TEMPLATES/6pager_v2.md` 模板。
格式遵守由 `.ystar_session.json` 的 `require_6pager_format_for_dispatch`
规则在 dispatch 层强制。

### 适用范围（与第七条的关系）

- 第七条（反事实推理提案）解决"方案选哪个" —— RAPID 里的 R 产出
- 第八条（6-pager v2 派活）解决"方案选定后如何让 P 不偏离" —— RAPID
  里 D→P 的移交文档
- 两条协同：一个跨岗位决策的完整 paper trail 是
  "反事实提案 (§7) → RAPID 五角色归属 (AMENDMENT-005) → 6-pager 派活 brief (§8) → P 执行 → 完成报告"

### 设计意图

- 把 Amazon 6-pager "written narrative > slides" 的 discipline 引入派活
- 通过强制结构让 subagent 不需要脑补（EXP-2 pilot 证明 v1 的自由格式
  导致权限误判、技术债遗漏）
- FAQ / Scope-Adjacent / 完成报告模板 3 个字段是 pilot 吃一堑长一智
  的固化成果

### 违规处理

- 缺节 → hook 拦截 + 列出缺失节名
- 节名对但内容 vague → Secretary 周审计抽检，回退重写
- 口头派活 → 记 CIEU `DISPATCH_BYPASS` + `HARD_OVERDUE`（禁绕过）
```

---

## 5. 把 pilot 发现的 5 条 v3 改进点固化进模板

### 5.1 权限 precheck 强制（brief §4 每个目标文件必须标注 verified owner role）

**EXP-2 问题 A 的直接响应**。

模板 §4 "Current State → Target State" 必须含 **Verified Owner Role 表**：

```markdown
### Verified Owner Role 表（hook 规则实况校验）

| 目标文件 | 当前 owner role (per `.ystar_session.json`) | 需切到的 active_agent | 校验命令 |
|---|---|---|---|
| <path> | <role from restricted_write_paths 或 agent_write_paths> | <agent_id> | `grep -A5 "<path>" .ystar_session.json` |
```

R 起草 brief 时必须逐文件查 `.ystar_session.json` 的 `restricted_write_paths` + `agent_write_paths`，并把查到的 raw line 作为证据贴在表格后。R 未做此步 → brief 视为不合格。

### 5.2 Hook 规则索引（brief 附当前生效的规则摘要）

**EXP-2 问题 C 的直接响应**。

模板新增强制字段 "§4.5 Hook Rule Index"：

```markdown
### §4.5 Hook Rule Index（本 brief 执行时的 hook 环境快照）

| 规则类别 | 本 brief 相关条目 | 源字段 | 源行 |
|---|---|---|---|
| allow-list | ... | `.ystar_session.json:agent_write_paths.{role}` | :NNN |
| restricted_write_paths | ... | `.ystar_session.json:restricted_write_paths` | :NNN |
| deny_commands | ... | `.ystar_session.json:contract.deny_commands` | :NNN |
| deny_paths | ... | `.ystar_session.json:contract.deny` | :NNN |
```

R 起草时跑一次 `grep -n <key> .ystar_session.json` 把与本任务相关的 hook 条目列进来。subagent 执行前可直接参考而不必自己 grep 整个 session.json。

### 5.3 Scope-Adjacent 分类公约（三档）

**EXP-2 问题 B 的直接响应**。

模板 §7 Scope-Adjacent Observations 必须按以下三档分类记录：

```markdown
### Scope-Adjacent Observations

执行中发现但**本 brief 未列出的相关残留**——一律只记录不修改。分三档：

**A. 建议跟进** (可执行的后续 clean-up 候选)
- `<path>:<line>` | `<snippet>` | <推荐处理方式>

**B. 建议豁免** (符合 archive/历史快照/第三方依赖不回写原则)
- `<path>:<line>` | `<snippet>` | <豁免理由>

**C. 未判定** (需要 R 或 D 决策才能归类)
- `<path>:<line>` | `<snippet>` | <未判定原因>
```

D（或 CEO/Board 作为 D 时）看完 §7 后决定是否为 A 类起 follow-up amendment，C 类升级为新 RAPID 决策。

### 5.4 Partial-execution 协议（完成状态枚举）

**EXP-2 问题 E 的直接响应**。

模板 §8 完成报告模板的首行必须是状态枚举：

```markdown
### 完成报告（≤250 词）

**Status**: <COMPLETE | PARTIAL-hook-blocked | PARTIAL-other | FAILED>

- COMPLETE: §6 Metrics 全部 ✅，无遗留
- PARTIAL-hook-blocked: 撞 hook boundary 停止，报告必含 hook 原文 + 撞点文件 + active_agent
- PARTIAL-other: 其他原因部分完成（brief 事实与仓库偏差 / 依赖缺失 / I 输入未到），报告必含原因
- FAILED: 完全无法推进，报告必含 root cause 分析

随后字段（按序）：
1. Metrics 验证（M1-Mn 逐项结果）
2. Commit hash（如适用）
3. 遇到的 hook boundary（"none" 或逐条列出）
4. Scope-Adjacent Observations（§7 三档分类）
5. active_agent 切换时间线
6. 主观反馈（本版格式哪些有用 / v3+ 还需要什么）
```

状态码进入 CIEU event `DISPATCH_COMPLETION_REPORTED.status` 字段，Secretary 周审计统计 COMPLETE vs PARTIAL 比例作为 6-pager 有效性指标。

### 5.5 敏感字符串白名单（commit message 禁字面命中 deny）

**EXP-2 问题 C 的直接响应**。

模板 §8 完成报告模板内嵌一条约束：

```markdown
### Commit Message 规则（AMENDMENT-006 固化）

Commit message 正文和标题**禁止直接包含**以下字面字符串（会触发
hook 的 deny_commands 字面匹配）：

- `.claude/agents/`（用"agent DNA files" / "subagent definitions" 替代）
- `scripts/record_intent.py`（用"intent recording helper"替代）
- `scripts/check_intents.py`（用"intent verification helper"替代）
- `AGENTS.md`（用"company charter"替代，除非 commit 确实在改 AGENTS.md 且 Board 直接授权）
- 其他 `.ystar_session.json:contract.deny_commands` 里的字面 token

允许描述性短语指向这些路径。目的：让 commit message 可读的同时不
被 hook 按 substring match 误拦。AMENDMENT-001 (`ystar setup --yes`)
之后的 deny_commands 扩展列表每次更新时，Secretary 同步更新本清单。
```

---

## 6. 豁免清单（哪些情况不用走 6-pager）

```markdown
### 6-pager 豁免清单

以下情况 `require_6pager_format_for_dispatch` 不生效：

1. **L0 等价 · 单角色自学**
   - 空闲学习循环（WORKING_STYLE §9）下 agent 自己开的 `knowledge/{role}/` 任务
   - 判定：R=A=P=I=D 全为同一 agent_id，且写路径只命中 `knowledge/{role}/**`

2. **L1 等价 · 单岗位可逆操作**
   - daily `check_obligations.py --dry-run`
   - `ystar doctor`、`gov_doctor` 等只读诊断
   - Secretary 归档索引更新（`knowledge/decisions/` 目录 index 之类）
   - 判定：只涉及单一 role + 只读或可逆写 + 无外部可见性

3. **应急响应**
   - CIEU `HARD_OVERDUE` 引发的自动修复
   - Board 明确标记 `URGENT-BYPASS-6PAGER` 的直接指令（事后 Secretary 补 6-pager 归档）

4. **RAPID 内部流程事件**
   - `RAPID_PROPOSAL_DRAFTED` / `RAPID_INPUT_ADDED` / `RAPID_AGREE_STATE` 等五角色协作过程中的工件（它们是 6-pager 的**输入**，不是被 dispatch 的 brief）

5. **文档同步类**
   - AMENDMENT 批准后 Secretary 按清单做 mechanical 替换（本 AMENDMENT 就是例子：§5.1 清单执行不需要再走 6-pager）

豁免情况必须在 CIEU event `DISPATCH_EXEMPTION` 记录，字段含
`exemption_reason` 与 `exemption_clause`（引用本清单的第几条）。
```

---

## 7. 影响评估 + 同步修改清单

### 7.1 硬依赖

| 文件 | 修改内容 | 责任 |
|---|---|---|
| `.ystar_session.json` | 新增 `require_6pager_format_for_dispatch` 字段 | Secretary（Maya A 角色） |
| `governance/TEMPLATES/6pager_v2.md` | 新建，完整模板固化 §3 + §5 1-5 项 + §6 豁免清单 | Secretary |
| `governance/WORKING_STYLE.md` | 新增第八条 | Secretary |
| `scripts/dispatch_validate.py` | 新建（或并入已有 hook），实现 8 节结构校验 + scope 豁免查找 | eng-platform (P) |
| `DISPATCH.md` | 过渡：`格式迁移至 6-pager v2`，原条目逐条按模板迁移 | Secretary |
| `.claude/tasks/*.md` | 过渡：新任务必须用 6-pager 模板；老任务完成后不回写 | 分任务责任岗位 |

### 7.2 软依赖

- `CLAUDE.md` 的 "Board Decision Rules" 段（AMENDMENT-005 已触及）增加一句指向 6-pager 模板
- `agents/*.md` / `.claude/agents/*.md` 的 dispatch 责任段增加"用 6-pager v2"指向
- `reports/proposals/` 历史提案不回写

### 7.3 与 AMENDMENT-005 (RAPID) 的耦合

- RAPID 的 R→P 移交就是 6-pager 生成时机
- D 决定后，R 把 D 决定 + A 的 CONDITIONAL 前置 + I 的输入 打包为 6-pager 模板交给 P
- 两个 amendment 必须同批次生效（批了 005 不批 006 ≈ "知道谁做决定但不规范怎么派活"；批了 006 不批 005 ≈ "派活格式规范但不知道谁决定"）

### 7.4 数据迁移

- 现有 `.claude/tasks/*.md` 共 ~4 个文件，Secretary 在 AMENDMENT 批准后逐个评估：
  - 仍在 active 执行 → 转 6-pager 格式
  - 已完成 → 不回写
  - 废弃 → move 到 `archive/deprecated/`

### 7.5 回退

同 AMENDMENT-005 的 §6.2 模式：`require_6pager_format_for_dispatch.enabled = false` feature flag 切换。模板文件保留，hook 退回 warn-only。

---

## 8. Board 三个签字位

**签字位 1**：批准 6-pager v2 八节结构作为所有跨岗位派活 brief 的 authoritative 格式（§3），以及把 pilot 的 5 条 v3 改进点（§5.1-§5.5）固化进模板。

☐ APPROVED ☐ REJECTED ☐ APPROVED-WITH-CONDITIONS

**签字位 2**：批准 §4 的具体 diff（`.ystar_session.json` 增加 `require_6pager_format_for_dispatch` / 新建 `governance/TEMPLATES/6pager_v2.md` / `WORKING_STYLE.md` 第八条）与 §6 豁免清单。

☐ APPROVED ☐ REJECTED ☐ APPROVED-WITH-CONDITIONS

**签字位 3**：授权 Secretary 按 §7 清单逐项同步，`scripts/dispatch_validate.py` 委派给 eng-platform 作为 P 角色实现；AMENDMENT-006 与 AMENDMENT-005 同批次生效（两者互为耦合，详见 §7.3）。

☐ APPROVED ☐ REJECTED ☐ APPROVED-WITH-CONDITIONS

**Board 签字**：________________________ **日期**：__________________

---

## 9. 引用来源

**外部框架**：
- [Amazon Chronicles — Dave Limp on the Six Page Memo](https://amazonchronicles.substack.com/p/working-backwards-dave-limp-on-amazons)
- [CNBC — Bezos on 6-page memos (2018)](https://www.cnbc.com/2018/04/23/what-jeff-bezos-learned-from-requiring-6-page-memos-at-amazon.html)
- [a16z podcast — Amazon Narratives, Working Backwards](https://a16z.com/podcast/amazon-narratives-memos-working-backwards-from-release-more/)
- [Writing Cooperative — Anatomy of an Amazon 6-pager](https://writingcooperative.com/the-anatomy-of-an-amazon-6-pager-fc79f31a41c9)
- [Amazon 2016 Shareholder Letter — Disagree and Commit](https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders)

**内部证据**：
- `reports/proposals/external_framework_survey.md` §3.1 Amazon 6-Pager + Working Backwards 分析
- `reports/experiments/exp2_B_6pager_am004cleanup.md`（EXP-2 v1 dry-run，暴露 4 类 pilot 陷阱）
- `reports/experiments/exp2b_v2_enhanced_6pager_am004cleanup.md`（EXP-2b v2 真实执行，确认 v2 格式有效并提出 v3 改进点）
- Secretary 6-pager v2 执行报告（task notification 记录：Q6 权限映射错 / §7 挖出 50+ 技术债 / hook 按字面匹配 / v3 需事实校验）
- `knowledge/ceo/feedback/no_human_time_dimension_in_agent_frameworks.md`

**Hard constraint 遵守声明**：本提案全文不含人类时间维度。进度与状态全部以 intent completion 闭环数 / CIEU event count / causal chain depth 表达。
