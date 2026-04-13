# EXP-2 Part B — Amazon Narrative Memo: AMENDMENT-004 残留清理

**日期**: 2026-04-12
**实验**: EXP-2 任务派活格式对比（B 组：Amazon 6-section Narrative Memo）
**派活对象**: 未命名 subagent（测试用，不绑定具体 agent）

---

## 1. Title & Outcome（一句话 Press Release 式结论）

> **AMENDMENT-004 残留的 6 处 Windows 路径全部被清理，git 树上 `grep "C:\\Users\\liuha"` 只剩 archive 和 historical amendments 的保留引用，金金基础设施相关的 "Mac mini" 提法保持不动。完成 1 个 commit，切回 active_agent=ceo。**

如果读完这一句你就想直接开干，下面 5 节是支撑材料。

---

## 2. Why Now（决策背景的因果链）

- `e6ca1df` Secretary 执行 AMENDMENT-004 时，`.claude/agents/*.md` 等路径撞 Y*gov immutable-path hook 被拦，未改完
- 这些残留文件被其他 subagent Read 时会**按 Windows 路径行动**（今天 CTO subagent 踩过一次双机分工坑就是同类症状）
- 每多一个 session 读到旧路径 → 多一次误操作风险
- DIRECTIVE-002 Memory 闭环 2 已上线，包含 "关键路径存在性" drift 检测——这些 Windows 路径残留会让 memory_consistency_check 永远报警（狼来了效应）

**因果链深度**：残留路径 → subagent 误读 → 执行路径错误 → CIEU drift → 告警噪声 → agent 忽视告警 → 真实 drift 被埋没。

---

## 3. Tenets（本任务不可妥协的原则，优先级从上到下）

1. **不扩大 scope**：只改 AMENDMENT-004 §5.2 清单里明确列出的 6 处；发现其他 Windows 路径残留记录到 finding list，但本 commit 不改
2. **金金引用不动**：cmo.md:122、ceo.md:250 等 "Mac mini" 是金金基础设施上下文（Mac mini 是金金自己的物理机），不属 AMENDMENT-004 scope
3. **不绕过 hook**：遇 boundary violation 停下报 CEO，不 `--no-verify`，不 `sudo`
4. **单 commit**：6 处一次性改完一个 commit，不拆——方便 git revert

---

## 4. Current State → Target State（Working Backwards）

### Current State（grep 证据）

```
./memory/session_handoff.md:3               | MAC mini reference
./.claude/agents/cto.md:109                  | C:\Users\liuha\OneDrive\桌面\Y-star-gov\
./.claude/agents/eng-governance.md:52        | C:\Users\liuha\OneDrive\桌面\Y-star-gov\
./sales/cso_patent_report_001.md:4           | C:\Users\liuha\OneDrive\桌面\ystar-company\reports\patent_ystar_t_provisional_draft.md
./sales/cso_patent_report_001.md:212         | C:\Users\liuha\OneDrive\桌面\ystar-company\knowledge\cso\patent_law_knowhow.md
./sales/cso_strategic_intelligence_summary.md:266 | C:\Users\liuha\OneDrive\桌面\ystar-company\knowledge\cso\user_engagement_research.md
```

### Target State（grep 验证）

```
grep -rn "C:\\\\Users\\\\liuha" . --include="*.md" | grep -v archive | grep -v BOARD_CHARTER_AMENDMENTS | grep -v charter_amendment
```

**预期结果**：0 行输出。

```
grep -rn "MAC mini" memory/session_handoff.md
```

**预期结果**：0 行输出。

### Path Translation Table

| Windows 片段 | Mac OpenClaw 等价 |
|---|---|
| `C:\Users\liuha\OneDrive\桌面\Y-star-gov\` | `/Users/haotianliu/.openclaw/workspace/Y-star-gov/` |
| `C:\Users\liuha\OneDrive\桌面\ystar-company\` | `/Users/haotianliu/.openclaw/workspace/ystar-company/` |
| "MAC mini" (作为集群节点语义) | "Single-Mac OpenClaw workspace" |

---

## 5. FAQ（Working Backwards from subagent 可能的误解）

**Q1: 我是不是应该顺带把 archive/ 下的 Windows 路径也改？**
A: **不**。archive/ 是历史归档，按 AMENDMENT-003 原则不回写。

**Q2: `.claude/agents/cmo.md:122` 的 "Mac mini" 要不要改？**
A: **不**。那是金金（Jinjin）基础设施上下文——金金住在自己的 Mac mini 上是独立事实，不是双机分工语义。grep 时会看到但不要碰。

**Q3: 如果我撞 immutable-path hook 怎么办？**
A: Stop。报告给 CEO：撞的是哪个文件、hook 返回什么消息。**不试**绕过、不试 `--force`、不试 `sudo`、不拆分 commit 侥幸过关。

**Q4: `memory/session_handoff.md:3` 的 Y*gov hook 拦 Secretary 写，怎么办？**
A: Secretary 身份依然应该能写 memory/（从之前 Secretary 的 AMENDMENT-004 report 看，这一行是 CEO-only restricted，不是 immutable）。再试一次，如果还拦，报告 CEO + 该路径的实际 owner role，CEO session 内自己改。

**Q5: 我做完后 `active_agent` 要切回什么？**
A: `ceo`。你开工前切到 `secretary`（或按实际撞到哪个文件的 owner 切），收工切回 `ceo`。

**Q6: sales/ 下的两份 cso 报告里的路径引用改了之后会不会破坏什么 CSO 工作流？**
A: 不会——那些路径本来就是 Windows 写法，现在系统根本找不到那些路径。改 Mac 路径后 CSO agent 下次 Read 才能实际打开文件。

**Q7: commit message 我应该写什么？**
A: `AMENDMENT-004 follow-up: clean residual Windows paths in agent/memory/sales files`。

---

## 6. Metrics & Rollback

### Success Metrics（按完成顺序）

| # | Metric | 验证方式 |
|---|---|---|
| M1 | 6 处 Windows 路径全改 | grep 验证 0 输出 |
| M2 | MAC mini 标签改掉 | grep memory/session_handoff.md |
| M3 | 金金引用完整保留 | grep 保留 `.claude/agents/cmo.md:122` 等行 |
| M4 | 单 commit | git log --oneline -1 |
| M5 | active_agent 切回 ceo | cat .ystar_active_agent |
| M6 | 无 hook boundary violation | 完成报告里明确 "no violation" |

### Rollback

如果发现改错：`git revert <this_commit>`，一条命令回退。

---

**执行完成后给 CEO 200 词内报告**，含：commit hash、M1-M6 逐项验证结果、任何 finding（发现的 scope 外 Windows 路径清单，不修但记录）、active_agent 最终状态。
