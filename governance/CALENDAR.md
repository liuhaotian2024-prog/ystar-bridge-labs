# 日历与时间机制 · Calendar & Time Authority

## 时间权威

公司所有时间以 **美国东部时间（ET / America/New_York）** 为准。
所有报告、日志、commit message中的时间必须使用ET。

## 当前时间校准

**校准基准**: 2026-04-06 12:28 ET（由Board于此时刻确认）
**系统时区**: America/New_York (EDT, UTC-4)
**Day计数基准**: Day 1 = 2026-03-26

## 时间职责

**Secretary负责：**
1. 监督所有agent的时间使用是否正确
2. 日报时间戳必须是ET
3. 发现时间错误主动纠正
4. 每日提醒中标注当前日期和Day编号

## Day计算公式

```
Day = floor((current_unix - 1742961600) / 86400) + 1
其中 1742961600 = 2026-03-26 00:00:00 UTC
```

## 重要日期记录

| 日期 (ET) | Day | 事件 |
|---|---|---|
| 2026-03-26 | 1 | 公司成立，CASE-001 CMO fabrication |
| 2026-03-29 | 4 | CEO命名Aiden/承远 |
| 2026-03-30 | 5 | HN Series 1, Telegram创建 |
| 2026-04-03 | 9 | Constitutional repair, Iron Rules |
| 2026-04-05 | 11 | gov-mcp v0.1.0, 16/16 mechanisms live |
| 2026-04-06 | 12 | 前端上线, Worker对话接通, 临时约法创立 |
