# Maya — AMENDMENT-016 Rule Mirror Sync Pilot Experiment

**Owner**: Maya-Governance
**Approved by**: Ethan-CTO (per AMENDMENT-016 6-pager `bfe66b1`)
**Spawned by**: CEO (Ethan blocked on Write lock — infra workaround)
**Deadline**: EOD 2026-04-15
**Workspace**: `/Users/haotianliu/.openclaw/workspace/ystar-company-test/` (NEW; rsync from prod, NEVER touch prod during experiment)

## Goal

Prove rule-mirror-sync architecture viable in our environment by hitting a real
end-to-end scenario:

> 手改 AGENTS.md 里某条规则文本 → ≤5 秒内 hook 行为变化 + 新 sub-agent 立刻可见

## Deliverables

1. **Test workspace bootstrap script** `scripts/exp7_bootstrap.sh` — rsync prod
   to `ystar-company-test/`, isolate hook socket path, isolate CIEU db
2. **Watcher prototype** — pick one (inotify via watchdog / fsevents / poll
   2s) and justify; wire into hook daemon to invalidate identity & rule cache
   on `.ystar_active_agent` and `AGENTS.md` change
3. **End-to-end demo** — manual rule edit → hook denial behavior changes within
   5s, demonstrated with 3 scripted cases (add rule / modify rule / remove rule)
4. **Latency table** — propagation delay measured per layer (file write →
   watcher fire → daemon reload → next hook call enforcing new rule)
5. **Failure mode enumeration** — what breaks: editor swap-file races, rapid
   successive edits, daemon crash mid-reload, partial writes
6. **Report** at `reports/experiments/exp7_rule_mirror_sync_pilot.md`

## Constraints

- Production仓 NEVER modified during experiment
- Use `pkill -9 -f hook_daemon && rm -f /tmp/ystar_hook.sock` between iterations
  if needed (per `feedback_daemon_cache_workaround` memory)
- Do NOT write to `.ystar_active_agent` from sub-agent — CEO-owned restore
  is the protocol until AMENDMENT-016 ships
- If you撞 lock, report to CEO (not Board) — CEO handles daemon cache reset

## Acceptance

- Demo video / log showing 3 scripted edits each propagating ≤5s
- Failure mode count ≥5 (we want to know what breaks before we ship)
- Recommendation: ship-ready / needs more eng / abandon (with reason)
