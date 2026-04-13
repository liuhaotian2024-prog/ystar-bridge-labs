# AMENDMENT-004 残留清理 — Amazon 6-pager v2（增强版）

**格式来源**: EXP-2 pilot 反馈，在原 6-pager 基础上加 §7 Scope-Adjacent Observations + FAQ 补 3 类陷阱
**本轮性质**: 真实执行（非 dry-run），Secretary 需要真改文件 + 真 commit
**批准**: Board 2026-04-12 已授权本 pilot

---

## 1. Title & Outcome（一句话 Press Release 式结论）

> **AMENDMENT-004 残留的 6 处 Windows 路径被精确替换为 Mac OpenClaw 路径，金金 Mac mini 引用保持不动，1 个精确 `git add <files>` 的 commit（不用 `-A`），active_agent 收工切回 ceo，并提交 Scope-Adjacent Observations 报告给 CEO。**

---

## 2. Why Now（决策背景的因果链）

- `e6ca1df` Secretary 执行 AMENDMENT-004 撞 immutable-path hook，6 处未改完
- subagent Read 到旧路径 → 按 Windows 行动 → CIEU 记录错误路径 → drift 告警噪声
- DIRECTIVE-002 闭环 2 (memory_consistency_check) 已上线，这些残留会让它**永远报警**（狼来了效应）
- 清理越晚，下游依赖越多，回退越难

---

## 3. Tenets（不可妥协原则，从上到下）

1. **不扩大 scope**：只改本 brief §4 明确列出的 6 处；其他发现记到 §7 不动
2. **金金引用不动**：cmo.md:122 / ceo.md:250 / AGENTS.md:818 / README.md:120 等 "Mac mini" 都是金金基础设施语义，**字符串相同语义不同**——不碰
3. **不绕过 hook**：撞 boundary 立刻停 + 报 CEO，不 `--no-verify`，不 `sudo`，不 `--force`
4. **精确 commit**：`git add <6 files>` 显式列出，**禁用 `git add -A`**（当前仓库有几十个 untracked/modified 文件会被污染）
5. **历史不回写**：archive/* + BOARD_CHARTER + reports/proposals/charter_amendment_* + docs/mac-cto-workstation-setup.md（已 DEPRECATED） + scripts/hook_debug.log 全部豁免

---

## 4. Current State → Target State

### Current State（grep 证据，2026-04-12 验证）

| # | 文件 | 行号 | OLD |
|---|---|---|---|
| 1 | `memory/session_handoff.md` | :3 | 含 "MAC mini" 标签 |
| 2 | `.claude/agents/cto.md` | :109 (per brief) | `C:\Users\liuha\OneDrive\桌面\Y-star-gov\` |
| 3 | `.claude/agents/eng-governance.md` | :52 (per brief) | `C:\Users\liuha\OneDrive\桌面\Y-star-gov\` |
| 4 | `sales/cso_patent_report_001.md` | :4 | `**File Location:** C:\...\reports\patent_ystar_t_provisional_draft.md` |
| 5 | `sales/cso_patent_report_001.md` | 实测约 :10-14（brief :212 可能是旧行号）| `The knowledge file (C:\...\knowledge\cso\patent_law_knowhow.md)` |
| 6 | `sales/cso_strategic_intelligence_summary.md` | :266 | `` `C:\...\knowledge\cso\user_engagement_research.md` `` |

**重要**：#5 的 brief 行号与实际 grep 偏差，**以你 Read 当时的实际位置为准**，不要盲按 :212 编辑。

### Target State（grep 验证命令）

```bash
grep -rn 'C:\\\\Users\\\\liuha' /Users/haotianliu/.openclaw/workspace/ystar-company \
  --include='*.md' \
  | grep -v '/archive/' \
  | grep -v BOARD_CHARTER_AMENDMENTS \
  | grep -v 'reports/proposals/charter_amendment_' \
  | grep -v 'docs/mac-cto-workstation-setup' \
  | grep -v 'reports/experiments/exp2'
```
**预期**: 0 行

```bash
grep -n 'MAC mini' /Users/haotianliu/.openclaw/workspace/ystar-company/memory/session_handoff.md
```
**预期**: 0 行

### Path Translation Table（严格使用）

| Windows 片段 | Mac OpenClaw 等价 |
|---|---|
| `C:\Users\liuha\OneDrive\桌面\Y-star-gov\` | `/Users/haotianliu/.openclaw/workspace/Y-star-gov/` |
| `C:\Users\liuha\OneDrive\桌面\Y-star-gov` (无尾斜杠) | `/Users/haotianliu/.openclaw/workspace/Y-star-gov` |
| `C:\Users\liuha\OneDrive\桌面\ystar-company\` | `/Users/haotianliu/.openclaw/workspace/ystar-company/` |
| `桌面\<X>\<Y>\<Z>` 任意深度 | 统一用 `/` 分隔符 + 全路径 Mac 化 |
| "MAC mini" (集群节点语义) | "Single-Mac OpenClaw workspace" |

**反斜杠→正斜杠**：sales/ 两份文件需要把整条路径的所有 `\` 都变 `/`。

---

## 5. FAQ（基于 EXP-2 pilot 反馈增补 3 类陷阱）

### 原始 FAQ

**Q1: archive/ 下的 Windows 路径要不要改？**
A: **不**。AMENDMENT-003 原则：不回写历史档案。

**Q2: `.claude/agents/cmo.md:122` 的 "Mac mini" 要不要改？**
A: **不**。金金（Jinjin）基础设施语义，字符串相同语义不同。同理 ceo.md:250 / AGENTS.md:818 / README.md:120。

**Q3: 撞 hook 怎么办？**
A: Stop + 报 CEO。不试绕过。报告内容：文件路径 / hook 返回原文 / 当前 active_agent。

### v2 新增 FAQ（EXP-2 pilot 暴露的陷阱）

**Q4: `git add -A` 还是 `git add <files>`？**
A: **`git add <files>` 精确列出**。当前仓库有几十个 untracked/modified 文件（CLAUDE.md 已改、reports/experiments/ 新建、.ystar_session.json 改过等），`-A` 会全部打包污染 commit。正确命令：
```bash
git add \
  memory/session_handoff.md \
  .claude/agents/cto.md \
  .claude/agents/eng-governance.md \
  sales/cso_patent_report_001.md \
  sales/cso_strategic_intelligence_summary.md
git commit -m "AMENDMENT-004 follow-up: clean residual Windows paths in agent/memory/sales files"
```

**Q5: Y-star-gov 在 Mac 上的确切路径？**
A: `/Users/haotianliu/.openclaw/workspace/Y-star-gov/`（与 ystar-company 同级）。这是 AMENDMENT-004 §3.1 确认的 canonical path。

**Q6: `.claude/agents/*.md` 和 `memory/session_handoff.md` 谁能写？**
A: 权限切换路径：
| 文件 | 需切到的 active_agent |
|---|---|
| `memory/session_handoff.md` | **secretary**（CEO-only 被 Secretary 撞过，secretary 身份应通过 restricted_write_paths 校验）|
| `.claude/agents/cto.md` | **secretary**（DNA 蒸馏权限，参见 `agents/Secretary.md` 第 142 行） |
| `.claude/agents/eng-governance.md` | **secretary**（同上）|
| `sales/cso_patent_report_001.md` | **cso 或 secretary**（sales/ 属 CSO 管辖，但 Secretary 的蒸馏权限覆盖各岗位 DNA） |
| `sales/cso_strategic_intelligence_summary.md` | 同上 |

**推荐策略**: 全程以 `secretary` 身份执行（最小化切换次数；Secretary 有 DNA 蒸馏权限，可触达以上全部）。如果撞任意一处 hook，报告 CEO 具体 role 名，CEO 再决定。

**Q7: `sales/` 下的路径改了算不算 AMENDMENT-003 所禁的"回写历史"？**
A: **不算**。AMENDMENT-003 禁的是 `archive/*` 和已完成的历史快照（如 sealed CIEU 记录）。`sales/cso_*.md` 是**活文档**——CSO 继续在用，路径错的话 CSO agent 后续 Read 会失败。改路径是让活文档继续可用，不是篡改历史。

**Q8: commit message 加不加 Co-Authored-By trailer？**
A: **加**。公司 CLAUDE.md 惯例。格式：
```
AMENDMENT-004 follow-up: clean residual Windows paths in agent/memory/sales files

6 files with Windows legacy paths → Mac OpenClaw paths.
Jinjin Mac mini references preserved (different semantic scope).

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
```

**Q9: 收工时 active_agent 切回 ceo 的时序？**
A: **commit 完成后再切**。顺序：改文件 → `git add <files>` → `git commit` → `echo ceo > .ystar_active_agent` → grep 验证 → 报告。

---

## 6. Metrics & Rollback

### Success Metrics（6 条）

| # | Metric | 验证方式 | 预期 |
|---|---|---|---|
| M1 | 6 处 Windows 路径全改 | 执行 §4 Target State 第一条 grep | 0 行 |
| M2 | MAC mini 标签改掉 | 执行 §4 Target State 第二条 grep | 0 行 |
| M3 | 金金引用完整保留 | `grep -n "Mac mini" .claude/agents/cmo.md AGENTS.md README.md` | 保留 |
| M4 | 精确单 commit | `git log --oneline -1` + `git show --stat HEAD` | 只含 6 个目标文件 |
| M5 | active_agent 切回 ceo | `cat .ystar_active_agent` | `ceo` |
| M6 | 无 hook boundary violation | 完成报告明确 "no violation" 或详细记录每次撞的 hook | — |

### Rollback

如果 M1-M6 任一失败或 commit 后发现错误：`git revert <commit>` 一条命令回退。

---

## 7. Scope-Adjacent Observations（v2 新增字段）

**授权**：你在执行本任务过程中 grep 或浏览发现的、**本 brief 未列出但相关**的 Windows 路径 / "Mac mini" 引用 / 其他架构残留——**一律只记录，不修改**。记录格式：

```
- <文件路径>:<行号> | <片段> | <你判断的语义归属: 双机残留/金金基础设施/archive豁免/未判定>
```

记录产出位置：本任务报告的"§Scope-Adjacent Observations"段。CEO 根据你的发现决定是否起 follow-up clean-up。

**重点扫描范围**：
- 全仓库 `grep -rn 'C:\\Users\\liuha'` 除豁免列表外的所有命中
- 全仓库 `grep -rn 'MAC mini'` 除金金相关外
- 全仓库 `grep -rn '192\.168\.1\.228'` 除 Gemma endpoint 外
- `scripts/migrate_handoff_to_yml.py` 第 95 行左右
- `DISPATCH.md`（如存在 "MAC mini CTO session" 字样）

**这个字段是本版格式最重要的增量**——EXP-2 pilot 证明原 6-pager 会让 agent 过度聚焦，主动放弃全局扫描。v2 显式授权扩视野但不扩执行 scope。

---

## 8. 完成报告（≤250 词）

执行完成后给 CEO 报告，结构：

1. **Metrics 验证**: M1-M6 逐项结果
2. **Commit hash**: `git log -1 --format='%H'`
3. **遇到的 hook boundary**: 没撞 = "none"；撞了 = 逐条列出
4. **Scope-Adjacent Observations**: 按 §7 格式列出发现
5. **active_agent 切换时间线**: 起点/切换点/终点
6. **主观反馈**: 这版 6-pager v2 对比你上次 dry-run 的 v1，缺失的信息是否补齐了？还有什么建议 v3 加？
