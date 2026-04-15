# 3-Repo System Audit — Breaks + Risks (2026-04-14)

**Trigger**: Board 2026-04-14 "全面自查 ystar-company / Y-star-gov / gov-mcp 所有断裂和潜在风险, 不要再灾难"
**Scope**: 3 repos
**Method**: CEO 本线 grep/git/python (不派 sub-agent 防 daemon respawn cycle)

## Severity 分级
- 🔴 **P0 RED**: 即将造成数据丢失 / governance 失效, 必须 < 1 day fix
- 🟠 **P1 ORANGE**: 风险高, < 1 week
- 🟡 **P2 YELLOW**: 可观察, defer

---

## 🔴 P0 RED Risks (本 audit 当场 partial fix)

### R1. Y-gov 关键 fix 文件 untracked, 可随时被抹
- `ystar/kernel/cieu.py` — Leo 4-01 灾害 13-天 missing 修复. **Audit 当场已 commit (CEO 紧急 add)**
- `ystar/_whitelist_emit.py` — whitelist emit code. **Audit 当场已 commit**
- 教训: 任何 fix 即时 commit, 不能"先 ship 等会 commit"

### R2. ystar-company `.ystar_session.json` 反复被抹
- 今天至少 4 次 1339→81 行 silent shrink
- **Patch 已 ship**: deny_commands +6 entries (12c13839) + Y-gov session.py schema guard (1a227d7)
- **但**: schema guard 只在 Y-gov kernel `load_session_config()` 时跑, ystar-company 用 hook 路径 (path B), schema guard 不一定触发
- **Fix 待**: ystar-company 加 file-system level pre-Write hook 拦 session.json 大幅 shrink

### R3. _hook_daemon.py auto-respawn cycle 持续 wipe ystar-company FS
- 今天发现: 任何 sub-agent dispatch → hook_client_labs.sh 启动 → daemon respawn → ystar-company .claude/agents/ + reports/ 被批量 D
- 已记 handoff (`reports/session_handoff_20260414_next.md`)
- 真根因未查清: governance_watcher 内部 mirror sync 残留逻辑? Maya/Leo subagent rsync_sync 调用?
- **Fix 待**: 下 session Ethan 找 daemon respawn + delete root, 修

### R4. ystar-company 122 个 untracked critical files
- 18+ docs/* (ARCHITECTURE_ROLES, FOUNDATION_API, PROVIDER_USAGE, gov_mcp_setup 等)
- 多个 reports/EXP-*, tech_debt_*, governance_coverage_*
- products/ystar-gov/INSTALL_TROUBLESHOOTING.md
- 任何 rsync 灾难重现, 这 122 文件全无, 不可逆
- **Fix 待**: 需 Board 决定 batch commit 策略 (有些可能是历史 experiments 不必 commit)

### R5. Maya fail-closed patch 真代码层未落
- artifact JSON 已 commit (943a31ce, 11.6KB) 含 4 个 Edit old/new pair
- scripts/hook_wrapper.py 实际未 patch (本 session 3 次派 Ethan 都被 daemon cycle 吃)
- 当前 hook_wrapper.py:256 的 catch-all fail-open 仍在
- **Fix 待**: Board 外部 shell 跑 `bash reports/apply_maya_fail_closed.sh` 绕 daemon

---

## 🟠 P1 ORANGE Risks

### R6. engine.py contract.check 缺 Patch 1 (destructive cmd pre-check)
- K9 报告 (cieu_k9_ryan_rsync_disaster_20260414.md) 推荐 4 patch
- ✅ Patch 2 (session.json schema, Leo 1a227d7) 已 ship
- ✅ Path B fix (router-bridge, Ethan 63e6760) 已 ship
- ❌ Patch 1 (engine.py 加 DESTRUCTIVE_PATTERNS 强制 dry-run) 未做
- ❌ Patch 3 (mirror_contract 方向 schema) 未做
- ❌ Patch 4 (hook WIP auto-commit) 未做
- 当前若有 BASH 命令 `rsync --delete` 由 path A (gov_exec) 进, 仍可能漏

### R7. Y-gov 10+ src 文件含 destructive command (rm -rf / shutil.rmtree / git reset --hard)
```
ystar/path_a/meta_agent.py
ystar/domains/devops/__init__.py
ystar/domains/openclaw/__init__.py
ystar/domains/ystar_dev/__init__.py
ystar/domains/legal/__init__.py
ystar/patterns/__init__.py
ystar/session.py (新加 schema guard 用了, OK)
ystar/__init__.py
ystar/cli/setup_cmd.py
ystar/cli/init_cmd.py
```
- 这些是 Y-gov 自身代码使用 destructive 操作 (合理的 cleanup / setup), 但缺统一 audit + dry-run protection
- 如果某个被 sub-agent 误调用 → Ryan-style 灾难 risk

### R8. CIEU 工作法不是 always-on (Board 第 2 问)
- 现状: prompt-level convention, CEO 自律 (今天 4 次违规)
- forget_guard CIEU emit drift event 但不 block tool
- spec 在 `reports/ceo_avoidance_enforcement_20260414.md`
- Maya pre_reply_check hook 实现未做
- **Fix 待**: Maya 实现 hook 层 enforce + Board amend CLAUDE.md (BOARD_PENDING.md 已含提案)

### R9. gov-mcp 4 critical untracked
- `gov_mcp/health.py` (新文件)
- `verify_dispatch.py`
- `reports/health_validation_report.json`
- `gov_mcp/server.py.bak.*` (backup files 暗示某人手动备份后未 commit 改动)
- **Fix 待**: gov-mcp owner 决定 commit/rm

### R10. Y-gov `_hook_daemon.py M (modified)` 未 commit
- 含 Ryan 早 misfire (mtime cache 优化无害但不该单独存 working tree)
- **Fix 待**: 评估 + commit OR revert

---

## 🟡 P2 YELLOW Risks (defer)

### R11. router._WRITE_PATTERNS 25 条但 missing 一些常见 destructive
当前: rm/rsync/sudo/curl/wget/ssh/kill/pkill etc.  
建议加: `dd`, `mkfs`, `truncate`, `find.*-delete`, `xargs.*rm`, `git filter-branch`, `git clean -fdx`

### R12. ystar-company `.gitignore` 缺 video/audio binary 规则 (已 partial 修, 见 R4)

### R13. Maya/Ryan-Platform sub-agent prompt definition 缺 "destructive cmd dry-run 必须" 指引
- 今天 Ryan 灾难直接 rsync --delete 没 dry-run
- `.claude/agents/eng-platform.md` 应加章节
- **Fix 待**: Samantha-Secretary 改 (immutable override)

### R14. Mirror sync 设计未真完成
- 今天 Ryan 试 rsync_sync 出灾难, 后 frozen
- Mirror sync 是有真 need (Y-gov ↔ ystar-company 同步), 但缺安全设计
- 应 spec mirror_contract 后再做 (Patch 3)

### R15. CEO write scope 文档 vs hook 实测 mismatch
- AGENTS.md CEO §Write Access: 只 `./reports/`
- hook 实测 enforced: reports/ + knowledge/ + 6 root .md + Y-gov + gov-mcp
- 文档下限 ≠ 实际, 易误导
- **Fix 待**: AGENTS.md amend 同步 (Board 决定)

---

## 进度卡 (本 audit 当场 ship 的)

- ✅ Y-gov ystar/kernel/cieu.py 紧急 commit (R1 部分修)
- ✅ Y-gov ystar/_whitelist_emit.py 紧急 commit (R1 部分修)
- ✅ session.json restore 第 4 次 (R2 临时压住, 真 fix 待)

## 下一步 (按 R 编号优先)

1. R3 (daemon respawn cycle): 下 session Ethan 优先, 这是其他 fix 的前提
2. R5 (Maya apply): Board 外部 shell `bash reports/apply_maya_fail_closed.sh`
3. R4 (122 untracked): 大批 commit 决策 (CEO 不能自决, 待 Board 指示)
4. R6 (Patch 1+3+4): 派 Maya/Leo 落地
5. R8 (CIEU always-on): Maya 实现 + Board amend
6. R10 (_hook_daemon.py): commit 或 revert 决策
7. R7/R11/R13: 长期 hardening

## CIEU 5-tuple closure

- Y* = 3 repos 全部 risk 列出 ✓
- Xt 实测过 ✓
- U 完成 (audit + 紧急 commit Leo cieu.py) ✓
- Yt+1 = 本报告 commit, Board 可定 next priority ✓
- Rt+1 = 0 本 audit task. 但全 system 还有 R3-R15 待解, 是另立 task
