# Gemma Quality Monitor — Design Spec (2026-04-15)

**Status:** L3 SPEC — Samantha-authored, Board 2026-04-15 triggered (second half of twin task)
**Depends on:** Leo Gemma design (commit 510ee408, `reports/gemma4_api_bridge_exploration_20260415.md`)
**Blocks:** Gemma Phase 1 pilot (`scripts/session_close_yml.py` cut-over)
**Enforcement:** cross-session persistence via git-tracked artifacts + CIEU DB + Telegram push

---

## 1. 问题陈述

Leo 510ee408 设计了 `gemma_client.py` + Claude fallback，但**缺质量监控闭环**：
- 切到 Gemma 后谁盯质量？
- A/B baseline 怎么建？
- 质量崩了怎么自动发现 + 通知老大？
- 数据怎么保证跨 session 不丢？(RAM state 一重启全蒸发)

本 spec 定义**强制 shadow 前 100 次 + nightly 对比 + CIEU 质量事件 + Telegram 异常 push + 全数据 git 管**。

---

## 2. 目标

1. **前 100 次强制 shadow**: `gemma_client.generate()` 前 100 次调用同步也发 Claude，对比结果落盘
2. **nightly 质量对比**: `quality_compare.py` 每日 06:00 汇总昨日 Gemma vs Claude 结果
3. **异常 Telegram push**: similarity < 阈值 或 error_rate > 阈值 → 立即通知老大
4. **跨 session 不丢**: 所有数据 git commit + CIEU DB 持久 + 不依赖任何 RAM / in-memory 状态
5. **Board 晨报可见**: Samantha daily 晨报 top-line 含 "Gemma 昨日 X/Y pass"

---

## 3. `gemma_client.py` 改动 (对 Leo 510ee408 design 的 delta)

### 3.1 新增: shadow_mode 强制 + 计数器持久

```python
# scripts/gemma_client.py (delta vs Leo 510ee408 spec)

import requests, json, time, sqlite3, hashlib, os
from pathlib import Path

SHADOW_COUNTER_FILE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_gemma_shadow_count")
SHADOW_THRESHOLD = 100  # 前 100 次强制 shadow
CIEU_DB = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db")
SHADOW_LOG_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/reports/gemma_quality_daily")

def _get_shadow_count() -> int:
    if not SHADOW_COUNTER_FILE.exists():
        return 0
    return int(SHADOW_COUNTER_FILE.read_text().strip() or "0")

def _bump_shadow_count() -> int:
    n = _get_shadow_count() + 1
    SHADOW_COUNTER_FILE.write_text(str(n))
    return n

def generate(prompt: str, max_tokens: int = 500, force_shadow: bool = False) -> dict:
    """
    Generate via Gemma. Auto shadow-call Claude for first N=100 calls OR if force_shadow=True.
    Emits CIEU quality event per call.
    """
    n = _get_shadow_count()
    do_shadow = force_shadow or n < SHADOW_THRESHOLD

    # Primary: Gemma
    gemma_result = _call_gemma(prompt, max_tokens)

    # Shadow: Claude (blocking, for A/B; in production can be async)
    claude_result = None
    if do_shadow:
        claude_result = _call_claude(prompt, max_tokens)
        _bump_shadow_count()
        _persist_shadow_record(prompt, gemma_result, claude_result)

    # Emit CIEU quality event (every call, shadow or not)
    _emit_cieu_quality_event(prompt, gemma_result, claude_result)

    return gemma_result
```

### 3.2 CIEU quality event schema (新增 event_type)

```json
{
  "C": "llm_quality_audit",
  "I": {
    "prompt_hash": "sha256 first 16 hex",
    "gemma_provider": "ystar-gemma:latest",
    "gemma_tokens": 172,
    "gemma_latency_ms": 6360,
    "shadow": true,
    "claude_model": "claude-sonnet-4.5",
    "claude_tokens": 189,
    "claude_latency_ms": 1820,
    "similarity_score": 0.82,
    "key_info_retention": 0.95,
    "length_ratio": 1.10
  },
  "E": "quality_compared" | "quality_threshold_breached",
  "U": "<active_agent>",
  "τ": 1776960000.0
}
```

---

## 4. `quality_compare.py` 伪代码

```python
# scripts/quality_compare.py
# Runs nightly 06:10 (after k9_daily_patrol.sh 06:00)
# Dependencies: sentence-transformers (or simpler: difflib + keyword overlap)

import sqlite3, json
from datetime import datetime, timedelta
from pathlib import Path
from difflib import SequenceMatcher

REPORT_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/reports/gemma_quality_daily")
CIEU_DB = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/.ystar_cieu.db")
SHADOW_ARCHIVE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company/reports/gemma_shadow_archive")

# Thresholds (Board-tunable)
SIMILARITY_MIN = 0.70       # textual similarity floor
KEY_INFO_RETENTION_MIN = 0.80  # how much of Claude's key facts survive in Gemma
LENGTH_RATIO_BAND = (0.5, 2.0)  # Gemma output length / Claude output length

def compute_similarity(gemma_out: str, claude_out: str) -> float:
    # v1: SequenceMatcher ratio (simple, no model dependency)
    # v2 (future): sentence-transformers cosine similarity
    return SequenceMatcher(None, gemma_out, claude_out).ratio()

def compute_key_info_retention(gemma_out: str, claude_out: str) -> float:
    # Extract noun phrases / named entities from Claude output
    # Count how many appear verbatim or via synonym in Gemma output
    # v1: simple keyword overlap via token set intersection / union (Jaccard)
    g_tokens = set(gemma_out.lower().split())
    c_tokens = set(claude_out.lower().split())
    if not c_tokens:
        return 1.0
    return len(g_tokens & c_tokens) / len(c_tokens)

def compute_length_ratio(gemma_out: str, claude_out: str) -> float:
    if not claude_out:
        return 0.0
    return len(gemma_out) / len(claude_out)

def run_nightly():
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    # 1) fetch all shadow records from yesterday
    records = fetch_shadow_records(yesterday)

    # 2) compute metrics per record
    results = []
    for r in records:
        sim = compute_similarity(r["gemma_out"], r["claude_out"])
        retention = compute_key_info_retention(r["gemma_out"], r["claude_out"])
        length = compute_length_ratio(r["gemma_out"], r["claude_out"])
        pass_flag = (
            sim >= SIMILARITY_MIN
            and retention >= KEY_INFO_RETENTION_MIN
            and LENGTH_RATIO_BAND[0] <= length <= LENGTH_RATIO_BAND[1]
        )
        results.append({**r, "similarity": sim, "retention": retention, "length_ratio": length, "pass": pass_flag})

    # 3) write daily report
    report_path = REPORT_DIR / f"{yesterday}.md"
    write_daily_report(report_path, results)

    # 4) if any anomaly, push Telegram
    fails = [r for r in results if not r["pass"]]
    if fails:
        push_telegram_alert(yesterday, len(fails), len(results), report_path)

    # 5) emit CIEU summary event
    emit_cieu_summary(yesterday, results)

    return report_path
```

---

## 5. 阈值 (Board-tunable, 初始值)

| 指标 | 阈值 | breach → action |
|------|------|-----------------|
| `similarity` | < 0.70 | Telegram push + daily report 红标 |
| `key_info_retention` | < 0.80 | Telegram push + daily report 红标 |
| `length_ratio` | < 0.5 或 > 2.0 | daily report 黄标 (信息压缩/膨胀) |
| `gemma_error_rate` | > 5% 日 | Telegram push + 自动 fallback Claude |
| `pass_rate` (pass / total) | < 70% | Telegram push + 建议 Board rollback Phase 1 |

阈值写在 `scripts/quality_compare.py` 顶部常量，Board 可 PR 调。

---

## 6. Nightly cron (复用 `k9_daily_patrol.sh` 06:00 slot)

追加一步到 `scripts/k9_daily_patrol.sh`:

```bash
# Step 5 (新增): Gemma quality nightly
echo "[$(date -Iseconds)] Step 5: Gemma quality compare" >> "$LOG_FILE"
python3 "$YSTAR_DIR/scripts/quality_compare.py" >> "$LOG_FILE" 2>&1 || {
    echo "[WARN] quality_compare failed — soft fail, continue" >> "$LOG_FILE"
}
```

实际执行时间: 06:10 (k9 patrol 前 4 步跑完后约 10 min)。

---

## 7. `reports/gemma_quality_daily/YYYYMMDD.md` 目录结构

```
reports/
├── gemma_quality_daily/
│   ├── 20260415.md
│   ├── 20260416.md
│   └── ...
└── gemma_shadow_archive/       # 原始 prompt/output pair, git-tracked
    ├── 20260415/
    │   ├── call_00001.json
    │   ├── call_00002.json
    │   └── ...
    └── 20260416/
```

**每日 report front-matter 模板**:
```markdown
---
date: 2026-04-15
total_calls: 37
shadow_calls: 37
pass: 34
fail: 3
pass_rate: 0.919
similarity_avg: 0.81
retention_avg: 0.87
alerts_pushed: 1
---

# Gemma Quality Daily — 2026-04-15

## Summary
- 37 calls, 34 pass (91.9%), 3 fail
- Avg similarity 0.81, retention 0.87
- 1 alert pushed to Telegram @ 06:12

## Failures (3)
| call_id | prompt_hash | sim | retention | reason |
|---------|-------------|-----|-----------|--------|
| 00012 | 3f9a... | 0.62 | 0.71 | length_ratio 2.4 (Gemma 冗长) |
| 00018 | 7c2b... | 0.55 | 0.68 | key_info 丢失 (Claude 提 '3 bugs', Gemma 说 'several') |
| 00031 | b0e4... | 0.48 | 0.62 | 完全偏题 |

## Action items
- call_00031 archived to `reports/gemma_shadow_archive/20260415/call_00031.json` for review
- 建议 CEO 检查 prompt template — 偏题率集中在 session_close_yml.py
```

---

## 8. 跨 session 不丢保证

| 数据类型 | 落盘 | 备份 |
|----------|------|------|
| shadow_count | `.ystar_gemma_shadow_count` (文本) | 每 call 写 → git commit weekly |
| shadow raw records | `reports/gemma_shadow_archive/YYYYMMDD/*.json` | git commit daily |
| CIEU quality events | `.ystar_cieu.db` (SQLite) | WAL 模式 + daily backup to `reports/cieu_backups/` |
| daily reports | `reports/gemma_quality_daily/YYYYMMDD.md` | git commit daily |
| thresholds | `scripts/quality_compare.py` 源码常量 | git 永久管 |

**零 RAM 依赖** — 任何时刻 kill Claude Code 进程，重启后所有数据可从 git + SQLite 完整恢复。

---

## 9. Telegram 异常 push 协议

**依赖**: 已有 Telegram bot token (见 `.ystar_session.json` 或 Secretary push notification protocol `agents/Secretary.md`)

**触发**:
1. `pass_rate < 0.70` (日汇总)
2. 单次 call `similarity < 0.50` 或 `retention < 0.60` (实时，超严重)
3. `gemma_error_rate > 5%` (日汇总)

**消息模板**:
```
[Y* Gemma Quality Alert] 2026-04-15
pass_rate 71% (26/37), threshold 70%
Top fail reason: key_info_retention drop
Report: reports/gemma_quality_daily/20260415.md
Action: review + consider rollback
```

---

## 10. Board visibility — Samantha daily 晨报集成

Samantha 每日 08:50 EST Board task reminder (per `agents/Secretary.md`) 新增 top-line:

```
[Gemma Yesterday] 34/37 pass (91.9%), 1 alert pushed. Report: reports/gemma_quality_daily/20260415.md
```

如 pass_rate < 80%，晨报置顶红色警告 + 主动提议 rollback 决策。

---

## 11. 实现 task cards (Leo 派单后续)

| Card | Owner | Est |
|------|-------|-----|
| gemma_client.py shadow + CIEU quality event | Leo | 3h |
| quality_compare.py v1 (difflib + keyword) | Leo | 2h |
| Telegram push integration (复用 Secretary bot) | Leo + Samantha | 1h |
| k9_daily_patrol.sh Step 5 加 | Leo | 30min |
| Samantha 晨报 top-line 模板改 | Samantha | 30min |
| reports/gemma_quality_daily/ 目录 bootstrap (README + schema example) | Samantha | 30min |

**总计 ~7.5h，建议 Leo 2026-04-16 全天 block**。

---

## 12. 本 spec Rt+1 (self-eval)

- ✓ `gemma_client.py` 改动 delta 明确
- ✓ `quality_compare.py` 伪代码完整 + 3 metric 可实现
- ✓ 阈值表 5 条
- ✓ cron 复用 k9_daily_patrol.sh 06:10 slot
- ✓ 目录结构 + front-matter 模板
- ✓ 跨 session 不丢 (git + SQLite 全覆盖)
- ✓ Board visibility 集成 Samantha 晨报
- ✗ 真实现 (待 Leo 派单)
- ✗ 阈值 Board 批准 (初始值写入，等实战调)

**Rt+1 = spec 文字版 + 伪代码 ready for Leo impl，符合 L3 SPEC 成熟度。**

---

## Sources
- Leo Gemma design: `reports/gemma4_api_bridge_exploration_20260415.md` (commit 510ee408)
- CIEU schema: unified_work_protocol_20260415.md (commit 2ab700c5)
- Nightly cron host: `scripts/k9_daily_patrol.sh`
- DMAIC Control/Measure phase inspiration: [ASQ DMAIC](https://asq.org/quality-resources/dmaic)
- PDCA Check-Act cycle: [ASQ PDCA](https://asq.org/quality-resources/pdca-cycle)
- Ollama API: https://github.com/ollama/ollama/blob/main/docs/api.md
