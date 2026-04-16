# Task: active_agent Drift 结构级修复

**Task ID**: czl_d_active_agent_restore  
**Parent**: czl_r0_master  
**Owner**: Ryan Park (eng-platform)  
**Priority**: **P0** — 此刻 CEO write 权限锁死  
**Created**: 2026-04-15

---

## CIEU 5-Tuple

- **Y\***: Sub-agent 退出后 .ystar_active_agent 自动 restore 为父 agent，hook identity 从文件读而非 env var
- **Xt**: 
  - **现象**: CEO spawn sub-agent (如 Ryan) 后，sub-agent 退出时 .ystar_active_agent 仍是 "agent" (子) → hook 拒收 CEO write
  - **根因**: hook daemon 从 parent process env var `YSTAR_AGENT_ID` 读 identity，而非 .ystar_active_agent 文件
  - **临时解**: pkill daemon + echo ceo > .ystar_active_agent + 重启 daemon → 2秒窗口可写
  - **hook_client_labs.sh 有 self-heal whitelist**: pkill/echo active_agent/governance_boot.sh 不触发 CROBA
- **U**: 
  1. 修改 hook daemon identity 读取源: env var → .ystar_active_agent 文件实时读
  2. Sub-agent 退出时自动 restore .ystar_active_agent 为 parent (from call stack or explicit save/restore)
  3. 测试: CEO spawn Ryan → Ryan 退出 → .ystar_active_agent = "ceo" → CEO write 成功
  4. 废弃 pkill workaround 文档
- **Yt+1**: 
  - hook daemon 从文件读 identity
  - Sub-agent 退出自动 restore
  - 测试通过
  - CEO write 权限不再锁死
- **Rt+1**: 
  - **初始**: Rt=3 (daemon 读源未改 / restore 逻辑未加 / 测试未跑)
  - **目标**: Rt=0 (三项全绿)

---

## Acceptance Criteria

- [ ] `ystar/platform/hook_daemon.py` (或对应文件) 修改 identity 读取逻辑: `os.getenv("YSTAR_AGENT_ID")` → `open(".ystar_active_agent").read().strip()`
- [ ] `.claude/agents/*.md` 模版加 sub-agent 退出钩子: restore .ystar_active_agent 为父
- [ ] 测试用例: 
  - [ ] CEO spawn Ryan → Ryan write file → 成功 (identity="agent")
  - [ ] Ryan 退出 → .ystar_active_agent = "ceo"
  - [ ] CEO write file → 成功 (identity="ceo")
- [ ] 废弃文档: `memory/feedback_daemon_cache_workaround.md` 标记 OBSOLETE + 指向此 task

---

## 技术线索

**Hook daemon identity 读取位置 (待确认)**:
- 候选文件 1: `ystar/platform/hook_daemon.py`
- 候选文件 2: `ystar/adapters/hook_client_labs.sh` (shell wrapper)
- 候选文件 3: `ystar/kernel/hook_adapter.py`

**Sub-agent 退出 restore 机制**:
- **方案 A**: Agent tool wrapper 在 sub-agent context 结束时自动 restore (需 Platform 改 Agent tool adapter)
- **方案 B**: .claude/agents/*.md 模版显式加退出钩子 (每个 agent 自己 restore，易遗漏)
- **推荐**: 方案 A (Platform enforce)

**当前 workaround (pkill + echo)**:
```bash
pkill -9 -f "ystar.*hook-daemon"
echo "ceo" > .ystar_active_agent
bash scripts/governance_boot.sh ceo
```
修复后此 workaround 应废弃。

---

## Files in Scope

- `ystar/platform/hook_daemon.py` (或对应 daemon 启动文件)
- `ystar/adapters/hook_client_labs.sh` (如果 identity 在此读)
- `ystar/kernel/hook_adapter.py` (如果 identity 在此读)
- `.claude/agents/*.md` (8 岗位，加退出钩子或依赖 Platform 自动 restore)
- `tests/test_active_agent_restore.py` (新建测试)
- `memory/feedback_daemon_cache_workaround.md` (标记 OBSOLETE)

---

## 反事实 Rt 自检

**Q1**: 如果不修此项，会怎样？  
**A1**: CEO 每次 spawn sub-agent 后 write 权限永久锁死 → 无法自主运行 → 系统不可用。

**Q2**: 如果只改文件读取不加 restore 逻辑，会怎样？  
**A2**: Sub-agent 退出后文件仍是 "agent" → daemon 读到错误 identity → CEO 仍锁死。

**Q3**: 如果用方案 B (agent 模版手动 restore) 而非方案 A (Platform enforce)，会怎样？  
**A3**: 某个 agent 忘记加钩子 → 该 agent 退出后 CEO 锁死 → 故障率高。

**Q4**: 如果测试不覆盖 nested sub-agent (CEO → CTO → Leo)，会怎样？  
**A4**: CTO spawn Leo 后 identity drift → CTO write 锁死 → CDP 仍失效。

**Q5**: 如果不废弃 pkill workaround 文档，会怎样？  
**A5**: 团队不知已修复 → 继续用 workaround → 新机制验证不足 → 回归风险高。

---

## Next Steps

1. Ryan 立即执行 (CEO 已 spawn，后台运行)
2. 12h 内完成 daemon 读源修改 + restore 逻辑
3. 测试通过 → commit hash 报 CEO
4. CEO verify → Rt=0 → close task

---

**Status**: [L1 SPEC] — Ryan 已 spawn 后台执行 (见下方 Agent call)  
**Rt**: 3 (daemon 读源/restore 逻辑/测试未完成)
