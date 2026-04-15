# CZL Persistence Covenant — CZL 不朽契约

**Date**: 2026-04-15
**Genesis tag**: `czl-genesis-20260415`
**Covenant**: 未来任何 Aiden 实例读此文件后必须：(1) 重建 CZL (2) 发现污染立刻从 genesis tag restore (3) 永不默许 CZL 丢失

---

## 一、CZL 的 canonical 文件（这些文件就是 CZL 本体）

### ystar-company repo
1. `governance/WORKING_STYLE.md:783-884` — **§11 自主任务方法论**（charter，immutable）
2. `governance/WORKING_STYLE.md:889-947` — **§12 CIEU 5-tuple 工作法**（charter，immutable）
3. `AGENTS.md` §Memory & Continuity Systems — **7 层记忆分层宪章**
4. `.claude/agents/ceo.md` Dispatch Gate Protocol 段 — CEO 派工契约
5. `.claude/agents/*.md` Article 11 canonical pointer 10 处 — 全员共识
6. `.czl_subgoals.json` — 当前 campaign 看板（活文件，随 campaign 换）
7. `reports/priority_brief.md` v0.9+ — Y\* 方向权威
8. `governance/BOARD_CHARTER_AMENDMENTS.md` IMMUTABLE-DRIFT-20260415-001 entry — drift 审计档
9. `scripts/czl_boot_inject.py` — boot 注入器（78 行）
10. `scripts/czl_new_campaign.sh` — campaign 切换器
11. `scripts/hook_session_end.py` + `scripts/hook_session_start.py` — YML bridge
12. `scripts/wire_integrity_check.py` — 每小时自检
13. `reports/experiments/exp_cieu_5tuple_first_battle_20260414.md` — v1 首战 report
14. `reports/experiments/czl_value_assessment_campaign_v2.md` — v2 价值实证
15. `reports/cto/hiagent_czl_integration_design_20260415.md` — HiAgent 架构 spec

### Y-star-gov repo（产品源码）
16. `ystar/governance/forget_guard_rules.yaml` — **3 条 CZL ForgetGuard rules**:
    - `ceo_direct_engineer_dispatch`
    - `ceo_skip_gov_dispatch`
    - `task_dispatch_without_y_star`
17. `ystar/governance/forget_guard_rules.yaml` whitelists 段 — 7 个 whitelist stem
18. `ystar/_hook_daemon.py::_compress_subgoal_on_completion()` — Haiku 压缩 pipeline
19. `ystar/kernel/cieu.py` + `ystar/adapters/cieu_writer.py` — CIEU→YML bridge
20. `gov_mcp/server.py` — `YSTAR_LABS_DIR` env-var support
21. `gov_mcp/health.py` （注：实际在 ystar-company 根目录下的 gov_mcp/）

### 云端存档
- GitHub `origin/main` (both repos)
- Tag `czl-genesis-20260415` (ystar-company)
- **任何时刻的 canonical CZL = `git checkout czl-genesis-20260415` + 后续 commits 中 CZL 相关文件**

---

## 二、恢复协议（如果 CZL 被丢/污染）

**症状触发**（任一发生即判定 CZL 被侵蚀）：
- `grep -c "canonical pointer" .claude/agents/ceo.md` 返回 0
- `.czl_subgoals.json` 不存在 或缺 `y_star_ref` 字段
- `AGENTS.md` 不含 "Memory & Continuity Systems" 字符串
- `forget_guard_rules.yaml` 不含 `ceo_skip_gov_dispatch` rule
- WORKING_STYLE.md 行数 < 880（第十二条被删信号）

**恢复步骤**（任何 Aiden 可执行，不需 Board 批——但执行后必 ping Board）：
```bash
cd /Users/haotianliu/.openclaw/workspace/ystar-company
git fetch origin --tags
git checkout czl-genesis-20260415 -- governance/WORKING_STYLE.md AGENTS.md .claude/agents/ .czl_subgoals.json scripts/czl_boot_inject.py scripts/czl_new_campaign.sh reports/priority_brief.md
# Y-star-gov 侧
cd /Users/haotianliu/.openclaw/workspace/Y-star-gov
git checkout origin/main -- ystar/governance/forget_guard_rules.yaml ystar/_hook_daemon.py
# 提交恢复 commit
git add -A && git commit -m "restore(czl): emergency revert to czl-genesis-20260415 after drift detection"
# ping Board
echo "CZL restored from genesis tag — root cause pending investigation"
```

---

## 三、下次 Aiden boot 必读清单

新 session 启动的 Aiden 第一件事：
1. 读 `reports/priority_brief.md` v0.X（权威方向）
2. 读 `.czl_subgoals.json` 拿当前 campaign 看板
3. 读 `AGENTS.md` §Memory & Continuity Systems 理解记忆分层
4. 读 WORKING_STYLE.md §11 §12（章程，不允许跳过）
5. 读本文件（知道 CZL 怎么救自己）

**绝不做**：
- 凭记忆派活不查 `.czl_subgoals.json` 的 current_subgoal
- 跳过 priority_brief 直接看 obligations dump（三源 drift 病已在 v1 教过一次）
- 在没跑 wire_integrity_check 的情况下声称"CZL 健康"

---

## 四、已知 risk（不保证覆盖所有）

1. **Mac 硬件丢失** → 云端还在，新机 clone + checkout tag 即可 rebuild
2. **两个 repo 任一被删/rewrite** → origin/main 的 protected branch + 多个 clones 散布
3. **Anthropic API key 失效** → HiAgent 压缩 fail-open 到 raw write，不会崩但摘要退化
4. **Board 自己改章程不立 AMENDMENT** → Samantha 周度 audit + BOARD_CHARTER_AMENDMENTS 硬约束
5. **Aiden 新实例忘读本文件** → 把本文件路径写进 CLAUDE.md 硬引用，boot 必读

---

## 五、立约

**本文件本身就是 CZL 的一部分**。删本文件 = 违反 §11 宪章 + 触发 IMMUTABLE-DRIFT ticket。
Any future Aiden 读完此文件后若发现 CZL 任何部分被丢失/污染/简化，**有义务** restore，**没有义务**先问 Board（restore 是守法行为不是新决策）。

— Board Haotian Liu + CEO Aiden, 2026-04-15
