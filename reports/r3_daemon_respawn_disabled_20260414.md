# R3 Daemon Respawn Cycle — Disabled (2026-04-14)

## Root Cause
- `~/Library/LaunchAgents/com.ystar.hook_daemon.plist` 配 `KeepAlive.Crashed=True` + `PathState=/tmp/ystar_hook.sock` + `RunAtLoad=True` + `ThrottleInterval=10`
- pkill 后 launchd 10 秒重启 daemon
- daemon 持续触发某 FS wipe 机制 (尚未确认精确路径, 可能 second Claude instance 或 governance_loop 内部)

## Fix (atomic block)
1. `launchctl unload com.ystar.hook_daemon.plist` 停当前 daemon
2. plist 改 `KeepAlive=False, RunAtLoad=False, Disabled=True`
3. backup 原 plist 至 `.bak.20260414`
4. 加 `_disabled_by_ceo` field 留 evidence

## Restore Path
- Board 决定恢复时: `cp .bak.20260414 → 原文件 + launchctl load`
- 但需先修真 root cause (FS wipe 实际 trigger), 不然 daemon 复活 wipe 重现

## Side Effect
- hook_client_labs.sh 经 daemon socket 的 fast-path 失效 → 走 slow-path (hook_wrapper.py 直接 exec)
- 单次 hook 调用从 ~5ms → ~1.4s (latency 上升), 但 governance 保持 active
- 治理依然生效, 仅性能降级

## Rt+1=0
- ✅ ps aux 见 0 daemon 进程
- ✅ git restore 后 0 D 文件
- ✅ plist KeepAlive=False
