# K9 Daily Patrol — 升级方案 + 执行 Protocol (2026-04-15)

**Trigger**: Board 2026-04-15 "K9 这只小警犬还是比较有能力的. 让 CTO 团队针对性升级, 每天巡逻, 发现问题上报 CTO+CEO, 合理就执行."

## 1. K9 当前能力 (今天实测)

| 模块 | 状态 | 实证 |
|---|---|---|
| `k9_repo_audit.py` 5 rule | ✅ | 42 violations 扫 ystar-company (commit 74f1abd3) |
| `CausalChainAnalyzer.build_causal_dag` | ✅ | 645 事件 DAG, pinpointed PID 53871 signature (commit 89e36ed1) |
| `CausalChainAnalyzer.find_root_causes` | ❌ schema bug | violations list[dict] vs 我们 CIEU JSON string 不兼容 |
| K9 自身 CIEU emit (dogfood) | ✅ | 自跑 76 violation 自 emit 到 ~/.k9log/ |

## 2. 升级目标 (每日巡逻必做)

### 巡逻任务清单 (daily)

| # | 巡逻内容 | 用 K9 哪块 | 产物 |
|---|---|---|---|
| P1 | 3 repo residue 扫 (company/Y-gov/gov-mcp) | k9_repo_audit 5 rule + 加 rule 6-10 | daily diff vs yesterday |
| P2 | CIEU DAG 异常频率检测 | build_causal_dag + 加 frequency outlier detector | 单一 event_type >100/h 告警 (如昨 zombie watcher 每 16s 发 MIRROR_SYNC) |
| P3 | Orphan process detect | 扫 ps aux 找"script on disk 已删但 process 仍活" | zombie PID 列表 |
| P4 | Untracked critical file scan | find 所有 .md/.py/.json/.sh 未 commit + critical path | 丢失风险表 |
| P5 | Hardcoded secret/path scan | grep -rE api_key + /Users/haotianliu/ | 可迁移性评分 |
| P6 | Bare except/fail-open count | 今 247 基线, 每日 diff | fail-closed 新增 |
| P7 | Multi-clone detection | ystar-* 多 dir 含同 remote? | canonical drift 警 |
| P8 | Launchd/cron duplicate | plist + crontab 重复/孤儿 | 清理建议 |

### 升级代码层

1. **K9 CausalChainAnalyzer schema adapter**: CIEU `violations` column 是 JSON string, 先 parse 后喂 K9. 修 causal_analyzer.py:243 expected type check OR 写 adapter `scripts/k9_cieu_export.py`.
2. **新 rule 6-10**: 
   - Rule 6 ORPHAN_PROCESS (P3)
   - Rule 7 UNTRACKED_CRITICAL (P4)  
   - Rule 8 HARDCODED_PATH (P5 sub)
   - Rule 9 FAIL_OPEN_SURGE (P6 sub)
   - Rule 10 MULTI_CLONE (P7)
3. **Daily cron**: `*/1440 bash scripts/k9_daily_patrol.sh` (每日 06:00 前) → 跑 8 巡逻 → 生 `reports/k9_daily/YYYYMMDD.md`
4. **Digest generator**: K9 报告太长, 自动 summarize top-5 actionable 到 CEO + CTO dashboard. 写 `scripts/k9_digest.py`.
5. **Severity classifier**: 每 finding 打 P0/P1/P2/P3. P0 立刻推送, P1-P2 daily digest, P3 周总结.

## 3. 执行 Protocol (K9 发现问题 → 处理链)

```
K9 daily patrol 6:00 AM
  ↓
发现 problem X
  ↓
emit CIEU event type "K9_FINDING" + severity label
  ↓
severity P0 → 即时 push 到 DISPATCH.md top + sound/notification
severity P1-P2 → 进 reports/k9_daily/{date}.md digest + BOARD_PENDING.md 追加 entry
severity P3 → 周 digest
  ↓
CTO/CEO 审 digest (7:00 AM 早读)
  ↓
判合理 → 3 路:
  (a) K9 可自主 fix (纯 read-only 类如: git restore / 清 orphan txt / 标 TODO)
      → K9 emit "K9_AUTO_EXECUTED" + commit 可 revert
  (b) 派工程师 (代码改)
      → Ethan 写 task card + dispatch Leo/Maya
  (c) 不处理 (已知 known / defer)
      → emit "K9_FINDING_ACKNOWLEDGED_DEFER"
```

### K9 自主权限边界 (防 Ryan 灾害重演)

K9 **能自主做**:
- git restore (回退 working tree 到 HEAD, 不破坏 git history)
- rm 纯 artifact (*.tmp / *.bak, 且 git-ignored)
- touch canary/marker 文件
- 只读扫 (grep/ps/ls/find)

K9 **禁止自主做**:
- 任何 destructive commit / history 改写 (git reset --hard / push --force)
- 修改 .claude/agents/*.md (immutable, 走 Samantha override)
- 修改 .ystar_session.json (half-immutable, schema guard 保护)
- rm -rf / rsync --delete 任何路径
- 派 sub-agent

### 上报 channel

- `BOARD_PENDING.md` 追加 section "K9 Daily Findings {date}"
- `DISPATCH.md` 加 section "K9 Actionable Items"
- `reports/k9_daily/` 每日存原 report
- CEO + CTO 早读 protocol: 每日第一条 task 读 K9 digest (10 min)

## 4. CTO 升级任务清单 (派单用)

派 Ethan-CTO 分派:
- **Leo**: CausalChainAnalyzer schema adapter (violations str→list parse)
- **Maya**: 新 rule 6-10 implementation in k9_repo_audit.py
- **Jordan**: K9 digest generator + severity classifier
- **Samantha**: cron install + BOARD_PENDING channel integration
- **Ethan 本人**: 测 end-to-end + commit

## 5. 交付物 (Rt+1=0 定义)

1. `scripts/k9_daily_patrol.sh` cron 每日跑, CIEU events 记录执行
2. 新 rule 6-10 真实在 K9 代码库 (Y-gov adapter or 独立 fork)
3. CausalChainAnalyzer schema bug 修 + PR 回 K9 maintainer
4. digest + severity + escalation 3 channel 通
5. `reports/k9_daily/YYYYMMDD.md` 至少产 1 份真 daily report

## 6. 长期愿景 (vs Board 期望)

K9 从"按需 audit tool" → "24/7 自主巡逻 + 自主 minor fix 的 watchdog agent". 与 Board 原话吻合: "多了一个好助手".

一季度后评估: K9 发现的真 P0 数 / 自主 fix 成功率 / CTO-CEO 干预次数 decrease 曲线.
