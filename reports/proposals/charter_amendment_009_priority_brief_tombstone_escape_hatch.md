# AMENDMENT-009 — Priority Brief + Tombstone + Escape Hatch

**Status**: PENDING BOARD APPROVAL
**Proposer**: CEO (Aiden / 承远)
**Date**: 2026-04-13
**Depends on**: AMENDMENT-004 (单机原则)
**Superseded-by**: —
**Related**: AMENDMENT-005/006/007/008, EXP-6 (Continuity Guardian)

---

## 1. Problem Statement (why now)

2026-04-13 session boot 时 CEO 把 Y*Defuse 30天战役 Day 3 MVP 当成当前战略主轴，派 Marco/Sofia/Zara 全面冲对外发布，被 Board 打断。事后复盘：

- `session_handoff.md` 是脚本 dump，**不做优先级判断**
- `BOARD_PENDING.md` 只 append 不 expire，deprecated 条目（搬家 / Phase 1）留在头部当噪音误导 boot
- `DISPATCH.md` 挂着 30天战役倒计时，但 Labs 阶段已变为"内部完善期"，DISPATCH 没 update
- Boot 时 3 份文件互相矛盾，新 Aiden 抓最显眼的（Y*Defuse 倒计时）当主轴

Continuity Guardian v1 的 wisdom_extractor 已知漏扫 70% 产出（EXP-6 红队 No-Go）。这不是"某个 agent 记错了"，是**机制层的断层**：没人在 close 时判断"下次 boot 该优先什么"，没人在 boot 时把那份判断摆到最前面。

---

## 2. Proposal

### 2.1 新增 artifact：`reports/priority_brief.md`（CEO 产物）

CEO 在 session close 时**手写**（脚本只生成 stub）。必填字段：

```
1. 当前 Labs 阶段       # 必须从枚举选：创立内部完善期 / MVP 冲刺 / 对外发布 / 规模化
2. Top-5 真实优先级     # 按因果不按时间；每项有 P0-N 编号 + 责任岗位 + 阻塞依赖
3. DEPRECATED 清单      # 明确标出 handoff/BOARD_PENDING/DISPATCH 里已作废的条目
4. 下次 boot 不要做什么 # 明确负向约束
5. Board shell 解锁清单 # 列出哪些动作需要老大手动（身份锁等）
6. 本 brief enforce 规则
```

本文件优先级 **高于** `session_handoff.md` / `DISPATCH.md` / `BOARD_PENDING.md`。如有矛盾，以本文件为准。

v0.1 示例：`reports/priority_brief.md`（已由 CEO 落盘 2026-04-13）。

### 2.1a GitHub-first boot snapshot（新增 STEP -1）

**缺口**：Boot 只读本地文件（handoff.md / DISPATCH.md / BOARD_PENDING.md），这些文件易污染、易 stale。GitHub 仓库 `liuhaotian2024-prog/ystar-bridge-labs` 是真 truth source——commit history 不可篡改，Board session checkpoint (`545f600` 等) 是最权威的阶段定位。Board 2026-04-13 指出：每次重启都该查 GitHub。

**机制**：`scripts/governance_boot.sh` 加 **STEP -1**（最早一步，先于 priority_brief）：

```bash
# STEP -1: GitHub-first snapshot (AMENDMENT-009 §2.1a)
echo "[\u2212/7] GitHub snapshot:"
git fetch origin --quiet 2>/dev/null
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "?")
BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "?")
echo "  local vs origin/main: ahead=$AHEAD behind=$BEHIND"
echo "  recent 10 commits on origin/main:"
git log origin/main -10 --oneline 2>/dev/null | sed 's/^/    /'
if command -v gh >/dev/null 2>&1; then
  echo "  open issues (top 5):"
  gh issue list --limit 5 --json number,title -t '{{range .}}    #{{.number}} {{.title}}{{"\n"}}{{end}}' 2>/dev/null
  echo "  open PRs (top 5):"
  gh pr list --limit 5 --json number,title -t '{{range .}}    #{{.number}} {{.title}}{{"\n"}}{{end}}' 2>/dev/null
fi
```

**Drift 校验**（priority_brief vs GitHub）：
- priority_brief §3 DEPRECATED 清单里的"搬家/Phase 1/Y*Defuse 战役"等条目，若在 `git log -20 origin/main` 中最近 72h 仍有 active commit 提及，触发 WARN（不 FAIL，只提醒 CEO 更新 brief）
- `gh issue list` open issue 中任一 `label:p0` 或 `label:critical` 但**未在 priority_brief §2 出现** → WARN

**Offline 降级**：无网络 / gh 未装 / 未登录 → 跳过 STEP -1（不 FAIL），记录 CIEU `GITHUB_SNAPSHOT_SKIPPED`。

### 2.2 Boot 协议改动：`scripts/governance_boot.sh` STEP 0

在 STEP 1（agent identity）**之前**插入 STEP 0：

```bash
# STEP 0: Priority Brief (CEO-authored strategic compass)
BRIEF="$YSTAR_DIR/reports/priority_brief.md"
if [ ! -f "$BRIEF" ]; then
  echo "[0/7] PRIORITY BRIEF: MISSING — boot FAIL (AMENDMENT-009)"
  exit 1
fi
# Stale check: mtime > 48h → FAIL
BRIEF_AGE_HOURS=$(( ($(date +%s) - $(stat -f %m "$BRIEF")) / 3600 ))
if [ "$BRIEF_AGE_HOURS" -gt 48 ]; then
  echo "[0/7] PRIORITY BRIEF: STALE (${BRIEF_AGE_HOURS}h old, limit 48h) — boot FAIL"
  exit 1
fi
# Stub-未填 check: 若包含 "{{TODO}}" 或 "_stub_unfilled_" 字样 → FAIL
if grep -qE "\{\{TODO\}\}|_stub_unfilled_" "$BRIEF"; then
  echo "[0/7] PRIORITY BRIEF: STUB NOT FILLED — CEO must update — boot FAIL"
  exit 1
fi
echo "[0/7] Priority Brief: LOADED (age ${BRIEF_AGE_HOURS}h)"
cat "$BRIEF"
```

且 boot 完成后**第一句话**必须 echo：

```
当前 Labs 阶段 = <§1 值>
今天第一要务 = <§2 P0-1 第一项>
```

echo 内容与 brief 对不上 → FAIL。CEO 读到后以此为准，不再以 DISPATCH 为主轴。

### 2.3 Close 协议改动：`scripts/session_close_yml.py`

在 `main()` 末尾加 `update_priority_brief()` 步骤：

- 若 `reports/priority_brief.md` 不存在 → 生成 stub（所有字段填 `{{TODO}}`），提示 CEO 必须手写
- 若存在但 mtime < session_start_time → 提示 CEO 未更新，要求手写
- CEO 填完后才允许 close 成功

### 2.4 Deprecation Tombstone 机制

`BOARD_PENDING.md` / `DISPATCH.md` 中所有条目必须有前置 frontmatter：

```yaml
---
status: active | resolved | deprecated
deprecated_at: YYYY-MM-DD   # 仅 deprecated 条目必填
deprecated_reason: "..."    # 仅 deprecated 条目必填
---
```

Boot 时只读 `status: active` 条目，其他折叠为"N deprecated items hidden"。

本 amendment 生效时，CEO 立即 tombstone：
- BOARD_PENDING.md 头 60 行 "搬家 BLOCKED 选项 A/B/C"
- DISPATCH.md "Y*Defuse 30天战役" 整块
- 任何 "192.168.1.228 MAC mini" "双机分工" 引用

### 2.5a Article 11 Pre-Response Hook（A2 硬约束代码 enforce）

EXP-5A 审计结论："规则没有 hook 强制 = 装饰"。A2 硬约束（任何回答前跑第十一条 7 层）在 2026-04-12 立约后**未 codify**，2026-04-13 CEO 两次违反（session boot 时 + 本轮对话初期）。机制化：

- 在 hook_client_labs.sh 前置链加 `article11_compliance.py`
- 每次 CEO agent 产生 substantive response（非纯 tool call、非 ≤50 字 ack）前，必须在最近 60s CIEU 流中有 event_type=ARTICLE_11_PASS 记录
- 缺失 → hook emit soft warning，连续 3 次缺失 → 强制 DENY 下一次 response 直到 CEO emit `mcp__gov-mcp__gov_article11_pass` 事件
- "substantive" 判定：response 长度 > 200 字 或 包含决策/派活/战略判断关键词（正则 `派|决定|优先级|战略|动手|启动`）

配套 MCP 工具：`gov_article11_pass(layer_1_intent, layer_2_context, ..., layer_7_execution)` 一次性提交 7 层内容，hook 校验字段非空 + 长度 ≥ 20 字/层。

### 2.5 Board Shell Escape Hatch（active_agent 锁）

`.ystar_active_agent` 当前只能 secretary 写，导致 CEO 切不到其他岗位（身份锁）。新增 escape hatch：

```
环境变量 YSTAR_BOARD_SHELL=1 存在时，允许 hook 接受任意 active_agent 切换，
但每次切换 emit CIEU 事件 type=BOARD_SHELL_OVERRIDE，记录前/后 agent + 时间戳。
```

老大从 terminal 运行时可 `export YSTAR_BOARD_SHELL=1`；Claude Code session 内的 agent 无法设置该变量（环境隔离），因此不会被滥用。

---

## 3. 代码改动清单（需 eng-platform 实装）

- [ ] `scripts/governance_boot.sh`：加 STEP 0 + 第一句话 echo
- [ ] `scripts/session_close_yml.py`：加 `update_priority_brief()` 函数
- [ ] `scripts/tombstone_linter.py`（新）：扫 BOARD_PENDING/DISPATCH，统计 active/deprecated 条目
- [ ] `scripts/session_wisdom_extractor.py`：扩读 `reports/experiments/` + `knowledge/{role}/{feedback,decisions,lessons,theory}/` + `git diff HEAD~3..HEAD` + `reports/proposals/` + `reports/priority_brief.md`
- [ ] `.ystar_session.json`：`restricted_write_paths` 加 `reports/priority_brief.md`（只 CEO 可写）
- [ ] `governance/priority_brief_spec.md`（新）：schema 定义

预计工作量：4-6 小时。Ryan 主做，Leo 协助 wisdom_extractor 扩展。

---

## 4. 失败模式防护

- **CEO 偷懒只改 timestamp 不改内容** → enforce 策略：stub 未填字段检查 + CIEU 记录 brief diff（close 时比对上一版本）
- **Brief 内容与实际行为矛盾** → boot 第一句话 echo 必须与 brief §1/§2 一致，drift 进 CIEU
- **Brief 本身被 DEPRECATED 污染** → brief 结构是固定 schema，不是 append-only，每次 close 整份重写

---

## 5. Board 需批示

- [ ] 通过 / 通过需修订 / 驳回
- [ ] 优先级：P0（本 session 内批）/ P1（24h 内批）/ P2

批准后 CEO 派 eng-platform 实装（需 Board shell 切身份）。
