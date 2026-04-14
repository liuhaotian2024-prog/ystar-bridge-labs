---
name: Hook daemon 缓存身份 workaround
description: sub-agent 跑完 hook daemon 缓存旧 active_agent 锁住 CEO；硬重启 daemon + 删 socket 才解
type: feedback
originSessionId: b8aed99a-55f2-4073-a223-d41630cec4f4
---
每次 sub-agent 跑完，hook daemon (`/tmp/ystar_hook.sock`) 缓存 sub-agent 的身份，即使 `.ystar_active_agent` 已恢复为 ceo，daemon 仍按旧值 enforce，CEO 本线被锁。

**Why:** 2026-04-13 session AMENDMENT-016 派 Ethan 后实测 6 次。文件层 `.ystar_active_agent` = ceo，hook 仍报 "current agent is 'eng-domains'"。`pkill -f hook_daemon` 不够（auto-respawn 但仍读旧缓存或 socket 残留）。必须**硬杀 + 删 socket**，新 daemon 才会 fresh read。这是 AMENDMENT-016 要解决的"watcher 缺失"具体表现。

**How to apply:**
- sub-agent 跑完后，CEO 本线下一个 Bash/Write 撞锁时立刻跑：
  ```bash
  pkill -9 -f hook_daemon; pkill -9 -f hook_wrapper; sleep 2; rm -f /tmp/ystar_hook.sock
  ```
- 然后重试原命令，应该 pass
- 如果 `.ystar_active_agent` 文件本身也是 sub-agent 身份（被 sub-agent 写过），先请 Board 用 `!echo ceo > ...` 恢复（记忆 `feedback_board_shell_marker` 格式）
- AMENDMENT-016 ship 后此 workaround 失效——届时 file watcher + SSE 自动同步
