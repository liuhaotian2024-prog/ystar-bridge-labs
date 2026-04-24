---
status: Board-ratified 2026-04-23
scope: All agents (CEO/CTO/CMO/CSO/CFO/Secretary/Engineers)
enforcement: Iron Rule — non-violable
---

# Iron Rule 铁律 — 事故响应 3-channel 顺序

## Rule (Board 2026-04-23 立)

任何**事故 / lock-death / 重要事件**发生时必按此顺序 3 路响应:

### Channel 1: CIEU 追溯 (primary)
```sql
SELECT datetime(created_at,'unixepoch','localtime'), agent_id, event_type, decision, violations 
FROM cieu_events 
WHERE decision='deny' AND created_at > strftime('%s','now','-30 minute') 
ORDER BY created_at DESC LIMIT 20;
```
Dogfood: 用自己的 audit 层诊断自己.

### Channel 2: Traditional (secondary)
- `tail -100 scripts/hook_debug.log`
- `tail -50 scripts/.logs/broker.log`
- `ps aux | grep ystar`
- Python traceback / 源码 grep
**仅当 CIEU 触不到时用** — CIEU 触不到本身也是 signal.

### Channel 3: K9 外救 (tertiary — 当内部 tool lock 死)
通过 FIFO `/tmp/ystar_rescue_fifo` 投递白名单 recovery ID (R-001 ~ R-007).
**不等 Board 上线手动救** — 自治底线.

## 违反铁律代价

- 违 #1 (不先 CIEU 就 grep): dogfood 违反, HP 扣分
- 违 #2 (跳 traditional 直接叫 Board): 浪费 Board 精力 + agent 退化
- 违 #3 (有 K9 外救不用坐等): Board AFK 时 team 被困 = 自治失败

## 每次事故 checklist

```
[ ] Step 1: 跑 CIEU SQL 查 deny/violation events last 30min
[ ] Step 2: 如 CIEU 不足, tail hook_debug.log / broker.log
[ ] Step 3: 如 tool lock 死, FIFO 发 K9 rescue command ID
[ ] Step 4: 只有 K9 也失败时才 ask Board host-shell intervention
[ ] Step 5: 恢复后 write reports/incidents/<date>-<slug>.md 归档 (Samantha scope)
[ ] Step 6: 更新 knowledge/ceo/iron_rules.md 如有新教训 (Secretary scope)
```

## 配套 P0: K9 Rescue Daemon (Board 2026-04-23 directive)

5 design 原则:
1. 物理隔离 (launchd 独立 service)
2. 零依赖治理层
3. 白名单驱动 (硬编码)
4. FIFO 单向通信
5. 可审计 (独立 rescue-chain Merkle)

v1 白名单 7 动作 (R-001 ~ R-007): pycache clear / pkill hook / import check / ps grep / dedupe heartbeat / read active_agent / kill specific pid.

## 立律 precedent: 2026-04-23 CEO lock-death

`reports/incidents/2026-04-23-hook-fail-closed-deadlock.md` 立律 precedent. 3h 锁死 → Board 2 轮 manual shell 救援 → 立律 + P0 K9 daemon.

Board 原话: "我不在你们不接被困死了嘛".
