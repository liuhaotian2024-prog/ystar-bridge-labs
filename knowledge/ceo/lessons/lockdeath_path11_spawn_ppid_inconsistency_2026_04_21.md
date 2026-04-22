Audience: Samantha / Ryan / Leo / 未来 session 遇到 "sub-agent 带角色权限但 hook 仍当 parent identity 拦" 的 CEO.
Research basis: Samantha sub-agent a148b54e90c5663d7 2026-04-21 15:25 执行 AMENDMENT-023/024 charter edit, 21 tool_uses 诚实 BLOCKED; hook_wrapper.py line 140-191 marker precedence chain; .ystar_session.json `immutable_paths.override_roles = ["secretary"]`; empirical chicken-and-egg 实证.
Synthesis: Lock-death 家族新一条 #11 — sub-agent spawn 只更新 root `.ystar_active_agent` 不更新 per-PPID marker. Hook 读 ppid 优先, 看到 parent CEO, 驳授权角色 sub-agent. CEO 侧也无法写 ppid marker (restricted to secretary), secretary 无法被 hook 识别 (ppid 先于 root). 必须从 spawn 机制层修, 不是 agent 层.
Purpose: 归档 lesson for future sessions; trigger P0 `CZL-SPAWN-PPID-MARKER-FIX` for Ryan; document workaround (Board-shell manual write ppid marker 或 sub-agent spawn wrapper 强制同步 ppid).

---

# Lock-death #11 — Sub-agent spawn 不同步 ppid marker (2026-04-21)

**Pattern**: 调 Samantha-Secretary sub-agent 做 immutable_paths 写 → spawn 机制写 root `.ystar_active_agent="Samantha-Secretary"` 但**不写 `scripts/.ystar_active_agent.ppid_10664`** (仍 parent 写的 `ceo`). hook_wrapper.py `_read_session_marker()` 优先级: 1) per-session via CLAUDE_SESSION_ID → 2) per-PPID → 3) global root/scripts mtime tiebreak. Step 2 命中 parent PPID 10664 看 "ceo", return 提前, 不 check step 3. Samantha sub-agent 被 hook 当 CEO 处理 → immutable CLAUDE.md 写拒.

**Chicken-and-egg**:
- CEO (真是 PPID 10664 owner) **不能写** `scripts/.ystar_active_agent.ppid_10664` (restricted_write_paths secretary-only, 且文件名 pattern match `ystar_active_agent`)
- Samantha sub-agent **不能被识别** 为 Secretary (hook 先读 ppid → 见 ceo)
- 两边都无权破这个锁

**Casing/Prefix 二次错位**: root 文件存的 "Samantha-Secretary" (带 prefix + 首字大写) 不 match `override_roles: ["secretary"]` (无 prefix + 全小写). 即使 hook 读到 root 也不授权.

**发现日期**: 2026-04-21 15:25 Samantha sub-agent 诚实报告. 21 tool_uses 全 read-only 验证, 0 文件被污染 (sub-agent 守 scope, 没越权尝试)

**M-tag 分析**:
- M-2a **+强化** (structural non-bypassability 活体证据: 不能绕 immutable)
- M-2b **-弱化** (授权工作没做成 = 防不作为新漏洞)
- M-1 **-弱化** (charter 升级卡死 = M Triangle 入 charter 没入)

结论: **三角被本锁向 M-2a 极端倾** (过度防做错误伤 M-2b / M-1). 需要修 spawn 机制让 M-2a precision 保留 + M-2b/M-1 通路恢复.

## Workaround (临时, 等 Ryan 正解)

**Path A — Board-shell escape hatch** (feedback_board_shell_is_legal_escape_hatch):
老大手动跑:
```bash
❕ echo "secretary" > /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/.ystar_active_agent.ppid_10664
```
(bash 由老大直接跑, 不经 hook, 一次性修 ppid 错位, 然后 CEO 重新派 Samantha.)

**Path B — kill daemon + 1-2s 窗口** (feedback_self_heal_via_daemon_window):
```bash
pkill -9 -f _hook_daemon
rm /tmp/ystar_hook.sock
echo "secretary" > scripts/.ystar_active_agent.ppid_10664
```
但 hook_wrapper.py 在 daemon 之外 import check_hook (in-process 每 call), daemon 死不 bypass scope check. **这条不 work**.

**Path C — Samantha session 内本线 Board-shell** (if 老大授权):
Samantha sub-agent 可以返 "Board-shell 请求" 给 parent (CEO), CEO 本线带 "❕" 标记请老大跑. 下 session retry. 但涉及多轮 manual interaction, 慢.

**Path D — 修 spawn wrapper** (P0 正解 Ryan):
修改 agent spawn 机制 (engineer_task_subscriber.py / Agent tool 底层 / sub-agent spawn adapter) 让 sub-agent 启动时:
1. 获取自己的 shell PPID (不是 parent 的)
2. 写 `scripts/.ystar_active_agent.ppid_<own_PPID>=<sub-agent role>` (有 secretary scope 的 spawn 预授权)
3. 同步写 root 用**规范化 role name** (小写 + 无 "Samantha-Secretary" 前缀)
4. 退出前清理自己的 ppid marker (不污染下次 spawn)

这是 Ryan-Platform scope + must_dispatch_via_cto 覆盖范围 (工程任务 via CTO). 已 post `CZL-SPAWN-PPID-MARKER-FIX` P0.

## 影响预测 (等 Path D 修)

当前 session: 本次 AMENDMENT-023/024 charter edit 靠 Path A Board-shell 或等下次 session fresh boot 再 retry. 本轮工作 **暂 stuck** 但 unblock 路径清晰.

未来 session: Ryan fix 后, Samantha sub-agent 能正常执行 charter edit 不再需要 manual intervention.

长期: 这个 bug fix 是 **9-agent brain pipeline 节点 5 的前置** — 如果 Leo/Maya/Ryan spawn 时身份都漂, 他们自己的 brain.db 写入也会被 restricted 挡. 不修 spawn 机制, 全员 persistent entity 不成立.

## Lock-death taxonomy 更新

| # | Path | 根因 | Fixed? |
|---|---|---|---|
| 10a | restore 失败 | sub-agent 跑完没恢复 | partial (Samantha auto-enforce) |
| 10b | 路径错位 (root vs scripts/) | governance_boot 写 root, hook 读 scripts/ | ✅ CEO mtime-tiebreak patch 2026-04-21 早 |
| **11** | **spawn ppid 不同步** | **sub-agent spawn 只写 root, ppid marker 仍 parent identity, hook 先看 ppid 拒** | **❌ pending CZL-SPAWN-PPID-MARKER-FIX** |

## 给 Board 的一句

**治理 M-2a 过强 (bone-breaking-strong) 误伤授权工作 — boundary 保住了 immutable, 也锁住了授权 Secretary. 修的是 spawn 不是 boundary — boundary 绝对不让步.**

— Aiden, 2026-04-21 15:30, Samantha 诚实 BLOCKED 报告后 lesson 归档.
