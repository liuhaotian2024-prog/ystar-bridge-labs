# 6-pager v2 — AMENDMENT-009 实装派活

| 字段 | 内容 |
|---|---|
| Dispatch ID | D-009-RYAN-IMPL-001 |
| Drafter | CEO (Aiden) |
| Date | 2026-04-13 |
| RAPID Role | **P**erform = Ryan (Platform Engineer) |
| Principal (R/D) | CEO (R) + Board (D — 已 verbal "动手吧") |
| Agree (A) | Secretary（post-hoc charter archive）+ Maya（CIEU/enforcement plane 影响评估） |
| Input (I) | Leo（wisdom_extractor 扩读实现建议）/ CTO（监督） |
| Authority chain | `gov_delegate ceo→cto` (chain_depth=1, is_valid=true) / CTO 可 redelegate 给 Ryan |
| Pre-requisite | active_agent marker 切到 `eng-platform`（需 Board shell 或 secretary 协助） |

---

## 1. Problem（50 字内）

CEO 2026-04-13 session boot 时把 Y*Defuse 30天战役当战略主轴，被 Board 打断。根因：优先级判断没落到强制 artifact + hook enforce，DISPATCH/BOARD_PENDING/handoff 三文件互相矛盾，新 Aiden 抓最显眼的当主轴。同时 A2 硬约束（第十一条每次 run）无 hook 强制，CEO 本轮违反 2 次。

## 2. Customer（谁受益）

- **主要用户**：下一轮启动的 Aiden（避免重复踩坑）
- **次要用户**：Board（减少"为什么又失忆"的纠错成本）
- **系统受益方**：Continuity Guardian v2（获得 Tier 1.5 pointer 层 + 扩读数据源）

## 3. Solution（具体代码改动，4 项）

### 3.1 `scripts/governance_boot.sh`：加 STEP 0
- **插入位置**：第 29 行 `FAILURES=0` 之后，第 31 行 `# 1. 设置agent identity` 之前
- **内容**：读 `reports/priority_brief.md`；缺失 / mtime > 48h / 含 `{{TODO}}` 或 `_stub_unfilled_` → `exit 1`；通过则 `cat` 全文
- **完整代码**：见 `reports/proposals/charter_amendment_009_priority_brief_tombstone_escape_hatch.md` §2.2

### 3.2 `scripts/session_close_yml.py`：加 `update_priority_brief()` 检查
- **插入位置**：`main()` 第 380 行 `return 0` 之前
- **行为**：若 `reports/priority_brief.md` mtime < session_start（本轮未更新）→ stderr 警告 `PRIORITY_BRIEF_STALE=1` 写入 `.ystar_session_flags`；若文件不存在 → 生成 stub（全部字段 `{{TODO}}`）
- **CIEU**：每次 close 时 emit `event_type=PRIORITY_BRIEF_CHECK, decision=allow|warn`

### 3.3 `.ystar_session.json`：restricted_write_paths 加 priority_brief
- **位置**：第 309 行 `restricted_write_paths` 字典
- **内容**：追加 `"reports/priority_brief.md": ["ceo"]`
- **语义**：只允许 ceo 写，其他 agent DENY；所有 agent 可读

### 3.4 `scripts/session_wisdom_extractor.py`：扩读 5 个新数据源
新增 extractor 函数（EXP-6 红队修订）：
- `extract_experiments()`：读 `reports/experiments/*.md` 的 verdict 段
- `extract_role_knowledge()`：读 `knowledge/*/feedback/*.md` + `decisions/*.md` + `lessons/*.md` + `theory/*.md`
- `extract_git_diff_stat()`：`git diff HEAD~3..HEAD --stat`（非 full diff）
- `extract_proposals()`：读 `reports/proposals/*.md` 的 summary + status
- `extract_priority_brief()`：读 `reports/priority_brief.md` **整份注入 wisdom_package 顶部（最高权重）**

### 3.5 （AMENDMENT-009 §2.5a 补丁）Article 11 pre-response hook
新增 `scripts/article11_compliance.py`，接入 `hook_client_labs.sh` 前置链。详见 charter amendment §2.5a。本项**不在本次 Ryan dispatch scope 内**，单独派（复杂度高），列在这里只为完整性。

## 4. Strategy（为什么现在做）

- 今晚 Board session 已暴露 brief 缺失 → 造成对外发布误冲突直接代价
- Board 已给 verbal D（"动手吧"）→ 不等 charter 正式批
- priority_brief v0.1 已落盘 → boot STEP 0 一接入即可生效（零冷启动成本）
- delegation chain 刚 reset + re-validate → 授权链路处于最干净状态，此刻实装阻力最低

## 5. Tenets / 硬约束对齐

- **A1 两态**：本改动不引入"休息"概念，所有 daemon 保持 always_running
- **A2 第十一条**：本 brief 由 CEO 跑过 7 层后落盘（上一轮对话内已 emit）
- **Article 11 pre-response hook（§3.5）**：直接 enforce A2，是本 amendment 的主要贡献之一
- **EXP-5A 教训**：规则必配 hook，本 brief 的 §3.1/3.2/3.3 都是 hook 层 enforce，不是文档层装饰

## 6. FAQ（6-pager v2 强制段 — 预答 subagent 会问的）

**Q1：`stat -f %m` 是 macOS 语法，Linux 不兼容？**
答：本公司单机 macOS（AMENDMENT-004），不支持 Linux。若未来 CI 需要，包一层 `if [[ "$OSTYPE" == "darwin"* ]]; then stat -f %m; else stat -c %Y; fi`。

**Q2：`stub` 判定 regex 是否会误伤 brief 内容里正常的 `{{` 字符？**
答：CEO 手写 brief 内容不允许含 `{{TODO}}` / `_stub_unfilled_` 字面量。若将来 brief schema 需要模板占位符，重命名为 `⟨TODO⟩` 等不冲突字符。

**Q3：wisdom_extractor 扩读会不会让 wisdom_package 爆体积？**
答：git diff 只 `--stat`（KB 级）；experiments/knowledge 只取 verdict/summary 段（非全文）；priority_brief ≤8KB。预计扩读后包大小从当前 ~6KB → ~14KB，仍在 LLM 上下文预算内。

**Q4：restricted_write_paths 加 priority_brief 后，Secretary 能读不能写，日后若需 Secretary 归档旧版本怎么办？**
答：归档走 `reports/priority_brief_archive/YYYY-MM-DD.md`（新路径，默认 secretary 可写）。priority_brief.md 本体只 CEO 可写。

**Q5（权限事实校验，v3 改进点）**：subagent 收到本 brief 后是否需要先 grep 验证插入点行号？
答：**必须**。`governance_boot.sh` 第 29 行的 `FAILURES=0` 在本 brief 写作时经 Read 工具确认（2026-04-13 当日内容），但派活到执行间可能被并发改动。执行前用 `grep -n "FAILURES=0" scripts/governance_boot.sh` 验证，不一致则停下问 CEO。

**Q6（partial-execution 协议，EXP-2b 改进点）**：若 4 项中 2 项完成、2 项撞 hook 怎么办？
答：按本协议退出码报告：`0`=全绿；`1`=部分完成（列出每项 DONE/FAIL）；`2`=pre-req 未满足（active_agent 不对、chain invalid 等）；`3`=brief 事实校验失败（行号对不上）。**严禁绕过 hook、严禁 chmod / sudo**。

## 7. Scope-Adjacent 授权（EXP-2b §7）

允许 Ryan 在本 dispatch scope 内**扩视野但不扩 scope**：
- 若发现 scripts/ 下其他文件引用 `.ystar_active_agent` 读写但未走 hook → **只记录不修改**，作为后续 dispatch 输入
- 若发现 `.ystar_session.json` 里有其他疑似 stale 的 restricted_write_paths → **只记录**
- 不允许触发本 brief 未列出的文件修改

## 8. Appendix

**A. Pre-req 验证（执行前必 check）**
```bash
cat .ystar_active_agent  # 必须 = eng-platform
# 若不是：Board shell 切或 secretary 协助
```

**B. CIEU emit 模板**
```python
_write_session_lifecycle("AMENDMENT_009_IMPL", "eng-platform", sid, cieu_db,
    {"item": "3.1|3.2|3.3|3.4", "status": "DONE|FAIL", "blocker": "..."})
```

**C. 完工交付**
- 4 个文件 diff + 3 个 verification 输出（`bash scripts/governance_boot.sh ceo --verify-only` / `python3 scripts/session_close_yml.py ceo "test"` dry-run / wisdom_extractor 跑一次）
- 4 条 CIEU AMENDMENT_009_IMPL 记录
- ≤200 字完工报告给 CTO，CTO 汇总给 CEO

**D. 失败回滚**
所有改动走 git add + commit（不 push），若 verification 失败 → `git reset --hard HEAD~1` 并 CIEU emit `AMENDMENT_009_IMPL_ROLLBACK`。

---

**执行触发**：本 brief 落盘后，active_agent 切到 eng-platform 的瞬间，Ryan 读本 brief 直接执行。CEO 不再介入中间步骤，只在完工报告时验收。
