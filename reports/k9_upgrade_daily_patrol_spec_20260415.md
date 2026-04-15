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

---

## 7. K9-Adapted Unified Work Protocol (Board 2026-04-15)

Board 原话: "新综合工作法变成包括你在内的每时每刻必须能力, 不是可选. 最高原则之一."

K9 是 Python tool 非 prompt agent, 但升级后"巡逻+判断+上报+有限自主 fix"已是 agent 行为. 必须 adapt unified 协议.

### 7.1 CIEU 5-tuple — K9 每 patrol 必 emit

Python stub:
```python
def k9_daily_patrol_entry():
    cieu_emit("K9_TASK_START", 
        Y_star="当前巡逻发现所有 new violations since yesterday",
        Xt=read_yesterday_snapshot(),
        U=["scan repo", "analyze DAG", "detect orphan", "check untracked", "scan secrets", "audit bare except", "detect multi-clone", "check cron dup"],
        Yt_plus_1="8 rule scan 全跑 + digest 生",
        Rt_plus_1_initial="full findings count unknown yet"
    )
```

### 7.2 Article 11 — 顶层 N/A, 自然 parallel

K9 不 dispatch sub-agent. 8 巡逻任务是内部 rule runner 并行运行 (thread/async). 顶层 Article 11 不适用, 但遵守其**精神**: 不串行阻塞, 不派完躺平 (K9 自始至终工作).

### 7.3 12-layer 简化 (for deterministic tool)

K9 的"任务"即单次 daily patrol. 适用层:
- ✅ L0_INTENT_RECORDED: 发 K9_TASK_START CIEU event
- ❌ L1_gemma_questions: K9 无 reflective question (deterministic rules)
- ❌ L2_vector_search: K9 无 knowledge search (deterministic rule set)
- ✅ L3_exec_plan: rule list 作为 plan (hard-coded)
- ✅ L4_exec_start: 开 8 rule scan
- ✅ L5_mid_check: 每 2 rule 完 emit K9_LAYER_STEP event
- ❌ L6_pivot: deterministic tool 不 pivot
- ✅ L7_integration: merge 8 rule findings
- ✅ L8_exec_complete: 全 rule done
- ❌ L9_human_review: 这层对 tool 不适用, auto proceed
- ✅ L10_self_eval: K9 自 audit (今天 76 violations dogfood)
- ❌ L11_board_approval: deferred per autonomous mode
- ✅ L12_knowledge_writeback: 写 `reports/k9_daily/{date}.md` + commit

Implemented layers: 7/12 (58% of full protocol).

### 7.4 CIEU DB 桥接 (必改)

当前 K9 emit 到 `~/.k9log/logs/k9log.cieu.jsonl`, 公司 `.ystar_cieu.db` 里 0 K9 事件. 升级**必须**加 adapter:
```python
# scripts/k9_cieu_bridge.py
# watch ~/.k9log/logs/*.jsonl, tail new records, translate to CIEU schema, INSERT into .ystar_cieu.db
```
Bidirectional: K9 发现 → CIEU DB → CEO/CTO dashboard 可查. 全司一个审计 source of truth.

### 7.5 K9 权限边界 (严于 general agent)

因 K9 可自主执行 fix, 权限更严:
- Allowed: git restore / rm *.tmp *.bak / touch canary / 只读 scan
- Denied: rm -rf / rsync --delete / git reset --hard / history rewrite / 改 .claude/agents/* / 改 .ystar_session.json / modify AGENTS.md

Enforce 方式: K9 使用和 Agent 同一 `Bash` tool, 已经通过 router._WRITE_PATTERNS (commit 63e6760) + deny_commands (12c13839) 被全局 block. 额外保险: K9 运行时 `.ystar_active_agent` set 为 `k9-auditor` 身份, 其 write_paths 只 reports/k9_daily/ + git restore 凭证路径 whitelist.

### 7.6 Rt+1 度量 — K9 适配版

per daily patrol:
- Rt+1 = 8 rule 全跑 + digest 生 + CEO/CTO 反馈回路闭 (0 未响应 P0)
- ≠ 0: 新增未 ack P0 finding / scan error / CIEU bridge 失败

### 7.7 验收 (K9 升级完成条件)
1. K9 adapter 代码落盘 + commit
2. K9_TASK_START/K9_LAYER_STEP/K9_TASK_END 事件在 `.ystar_cieu.db` 真见
3. 跑一次 daily patrol 产 `reports/k9_daily/20260415.md`
4. K9 的 76 self-violation 通过 bridge 进 company CIEU
5. CEO+CTO 审报 OK
