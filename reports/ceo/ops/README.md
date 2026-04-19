# Scheduling Install Guide (CZL-WIRE-2 deliverable)

**Audience**: Board (Haotian) to install. Primary CEO scope produces these artifacts; Board runs the install step because schedule registration lives outside CEO write paths (Launch Agents directory + crontab require system-level wire).

**Research basis**: macOS native scheduling primitives (launchd + cron). Industry precedent: systemd timers on Linux; Windows Task Scheduler. All 3 goal dashboards and the heartbeat emission use the same "run at interval, log output" pattern.

**Synthesis**: Ryan's `hook_daemon_wrapper.py` and the two `run_daily()` entry points (`rule_lifecycle_observer.run_daily`, `liveness_audit.run_daily`) are standalone functions. This directory packages them as launchd + cron config ready for install. Once installed, Goal 1 daemon_heartbeats_7d stays positive, Goal 3 rule coverage dashboard refreshes daily, and Goal 4 module liveness audit refreshes daily.

---

## 1. Install hook_daemon heartbeat (Goal 1)

Copy the plist to the user LaunchAgents directory and load it:

```
cp /Users/haotianliu/.openclaw/workspace/ystar-company/reports/ceo/ops/launchd_ystar_daemon.plist ~/Library/LaunchAgents/ystar.daemon.heartbeat.plist
launchctl load ~/Library/LaunchAgents/ystar.daemon.heartbeat.plist
launchctl list | grep ystar.daemon
```

Expected: `launchctl list` shows `ystar.daemon.heartbeat` with a PID, emitting `DAEMON_HEARTBEAT` CIEU events every 60s.

Unload when needed: `launchctl unload ~/Library/LaunchAgents/ystar.daemon.heartbeat.plist`

## 2. Install daily governance dashboards (Goal 3 + Goal 4)

Append to existing crontab:

```
(crontab -l 2>/dev/null; cat /Users/haotianliu/.openclaw/workspace/ystar-company/reports/ceo/ops/crontab_ystar_daily.txt) | crontab -
crontab -l
```

Expected: `crontab -l` shows 2 lines running 03:00 and 03:05 nightly. Output logs to `scripts/.logs/rule_lifecycle_cron.log` and `scripts/.logs/liveness_audit_cron.log`.

## 3. Verification

Next-day morning:

```
cat reports/cto/rule_coverage_daily.md    # should show current date
cat reports/cto/ystar_liveness_daily.md   # should show current date
python3 reports/ceo/demonstrators/goal_1_hook_coverage_measure.py | grep daemon_heartbeats
# expected: daemon_heartbeats_7d ≥ 30 (one every 60s for 30+ minutes should accrue)
```

## 4. Rollback

- launchd: `launchctl unload ~/Library/LaunchAgents/ystar.daemon.heartbeat.plist && rm ~/Library/LaunchAgents/ystar.daemon.heartbeat.plist`
- cron: `crontab -e` then remove the 2 lines we added

## 5. Why not in scripts/ops/

This directory sits under `reports/ceo/ops/` because CEO write scope is `./reports/`; eng-platform subagent with `scripts/` scope was unable to complete the task today due to identity resolution lock. The install-target paths inside these files still point to `scripts/.logs/` etc., so the actual runtime uses the standard `scripts/` tree once Board runs steps 1-2.
