# Dead Path: 把 MVP 测试绿 = 战略主轴达标

**类型**: dead_path（CTO 专属）
**作废日期**: 2026-04-13
**作废原因**: 2026-04-13 session CTO 报 "Y*Defuse Day 3 MVP 72/72 tests green + pip install e2e OK"，CEO 把此包装成"战略主轴拿下"——被 Board 纠偏：阶段判断错误，测试绿只是工程 checkpoint，不是战略主轴

---

## 1. 禁止复活的表现
- CTO 向 CEO 报告时用 "MVP 达标" / "战略目标完成" 等战略性措辞
- CTO 推 PyPI 发布 / Show HN 时机判断（那是 CSO/CMO + Board 事）
- CTO 以"测试全绿"作为支持对外发布的论据
- CTO 在 DISPATCH.md 写 "Day N 倒计时已拿下"

## 2. 正确做法
- 测试数据报告：数字 + 条件（"在 macOS 14 上 72/72 pass, 0.59s"）
- 不做战略定位，不用"达标""拿下""胜利"等词汇
- 让 CEO 自己决定该工程 checkpoint 对应什么战略含义

## 3. 复活条件
- AMENDMENT-005 (RAPID) 正式生效后，CTO 的 R 范围明确包含"技术可行性"时
- Board 明确把该判断权下放到 CTO 时

## 版本
v0.1 — 2026-04-13
