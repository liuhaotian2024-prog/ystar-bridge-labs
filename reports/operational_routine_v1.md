# Y* Bridge Labs — Operational Weekly Routine v1

**Author**: CEO Aiden
**Created**: 2026-04-13
**Trigger**: Board 直接质询 "CEO 是否能像真人 CEO 自驱"——routine scheduler 是 4 项缺失 capability 之一
**Status**: ACTIVE（cron 入注后即生效，无延迟激活）

---

## 设计原则

- **Predictable rhythm** — 团队每周知道几点会发生什么，不靠当时心情
- **Each ritual = atomic CIEU event** — 跑没跑可审计
- **Time = EDT**（Board 默认时区）
- **Rituals are scripts, not policy docs** — code-enforced，不是 README 摆设

---

## 周节奏

| 时间 | Ritual | Owner | Output | CIEU event |
|---|---|---|---|---|
| **周一 09:00** | 战略复盘 — 上周交付 review + 本周 priority_brief.today_targets 重写 | CEO | 更新 priority_brief.md + 产 weekly_strategy_$DATE.md | `WEEKLY_STRATEGY_REVIEW` |
| **周二 09:00** | 产品 review — Y\*gov + 三层洞察 + 闭环 system 状态 | CTO | 产 product_status_$DATE.md | `PRODUCT_REVIEW` |
| **周三 09:00** | Tech radar scan — Maya tech_radar 全 gap 自动扫，CEO review brief | CEO + Maya | tech_radar_briefs/ 更新 | `TECH_RADAR_WEEKLY` |
| **周四 09:00** | 1:1 round — CEO 给每个 active engineer 跑一次 retrospective（你这周做了啥 / 卡在哪 / 下周计划）| CEO | reports/1on1s/$DATE_$role.md | `ONE_ON_ONE` |
| **周五 09:00** | 对外 update + Board 周报 — Y\*gov GitHub stars/issues 摘要 + Labs 本周交付 + risks | CEO | BOARD_PENDING.md 加 weekly digest 段 | `BOARD_WEEKLY_DIGEST` |
| **周日 21:00** | 周末 self-eval — 12 层框架自审本周决策 + 反事实 | CEO | knowledge/ceo/lessons/weekly_$DATE.md | `WEEKLY_SELF_EVAL` |

---

## 日节奏

| 时间 | Ritual | Owner |
|---|---|---|
| **每日 06:00** | README 滚动晨报（Jordan 已 cron `6689c91`） | publish_morning_to_readme.py |
| **每日 07:00** | External signals 拉取（Leo MVP 跑后） | external_signals.py |
| **每日 08:47** | morning_report 学习 dashboard | ystar_wakeup.sh morning_report |
| **每日 21:57** | mission_report 当日交付汇总 | ystar_wakeup.sh twin |
| **每 5 min** | CEO heartbeat（Ryan MVP 跑后） | ceo_heartbeat.py |
| **每 15 min** | Goal progress dashboard 重算（Maya MVP 跑后） | goal_progress.py |
| **每 60 min** | Atlas + RAG 增量索引重建 | （留待 v2） |

---

## Crontab 入清单（Board 手动装一次）

```cron
# Y* Bridge Labs Operational Routine v1
# CEO weekly rhythm
0 9 * * 1   /usr/bin/python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/ritual_weekly_strategy.py >> /tmp/ritual.log 2>&1
0 9 * * 2   /usr/bin/python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/ritual_product_review.py >> /tmp/ritual.log 2>&1
0 9 * * 3   /usr/bin/python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/tech_radar.py scan >> /tmp/ritual.log 2>&1
0 9 * * 4   /usr/bin/python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/ritual_one_on_one_round.py >> /tmp/ritual.log 2>&1
0 9 * * 5   /usr/bin/python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/ritual_board_weekly_digest.py >> /tmp/ritual.log 2>&1
0 21 * * 0  /usr/bin/python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/ritual_weekly_self_eval.py >> /tmp/ritual.log 2>&1

# Daily (Ryan/Maya/Leo MVPs after they ship)
*/5 * * * * /usr/bin/python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/ceo_heartbeat.py >> /tmp/ceo_heartbeat.log 2>&1
*/15 * * * * /usr/bin/python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/goal_progress.py >> /tmp/goal_progress.log 2>&1
0 7 * * *   /usr/bin/python3 /Users/haotianliu/.openclaw/workspace/ystar-company/scripts/external_signals.py >> /tmp/external_signals.log 2>&1
```

---

## 6 个 ritual 脚本（待实装，每个 atomic 单活）

| 脚本 | 内容 | 工期 | Owner |
|---|---|---|---|
| `ritual_weekly_strategy.py` | 跑 wisdom_extractor 上周回顾 + 提示 CEO 重写 priority_brief | 30min | CEO 自己（reports/）+ Ryan（cron） |
| `ritual_product_review.py` | gov_doctor + Atlas + Tech Radar 综合产品状态 | 30min | CTO 派 Leo |
| `ritual_one_on_one_round.py` | 对每 engineer agent 跑 retrospective prompt → 收集到 reports/1on1s/ | 60min | CEO + Jordan |
| `ritual_board_weekly_digest.py` | 拉本周 commits + GitHub stars 变化 + 主要 ship → BOARD_PENDING.md 加段 | 30min | CEO 自己 |
| `ritual_weekly_self_eval.py` | 12 层自审 + 反事实 + lesson 回写 | 60min | CEO 自己 |

---

## 节奏自检

每月最后一个周日，CEO 运行 `ritual_audit.py`（待实装）核对：
- 6 个 weekly ritual 这个月触发了几次？应=4
- 每日 ritual 触发率 ≥ 95%？
- 某 ritual 漏跑 → emit `RITUAL_MISSED` CIEU + 调整时间或废止

---

## v1 限制（诚实交代）

- 实际 ritual 脚本（6 个）还没写——本文是规范 + cron 入清单，**Board 装 cron 后会失败**直到脚本 ship
- 1:1 retrospective 现在没真实 transcript 数据可挖（agents 是 sub-agent 不持久）
- 自我节奏审计（`ritual_audit.py`）属 v2

**先发布规范，让团队对齐预期；脚本 ship 后逐步激活。**
