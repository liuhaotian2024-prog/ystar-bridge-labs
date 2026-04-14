---
name: Close stub trigger condition
description: CEO EOD close stub auto-drafts only after prolonged Board silence, never during board_session
type: feedback
originSessionId: 36ef8c73-06cf-42bb-931e-9a2e522c40d0
---
EOD close stub / "给 Board 起床看的" 汇总文档的起草触发：
**只在** Board 长期静默（autonomous_work_learning 态持续 N 小时，N 待定但默认 ≥ 4h）后自动生成。
**禁止** Board 在线（board_session 态）时 CEO 主动提议或起草。

**Why:** Board 2026-04-13 纠正。Board 在线时写"给老大起床看"文档 = 把 Board 当不在场，违反 A1 两态硬约束（board_session / autonomous_work_learning）。Board 在线时的正确输出是对话响应和即时决策，不是"留给你起床看"的离线报告。

**How to apply:**
- board_session 态（Board 任意消息后 X 分钟内）：只做对话响应 + 派工 + 即时汇报
- autonomous_work_learning 态（Board 无消息持续 ≥ 阈值）：才触发 close stub 起草、session_close_yml、twin_evolution 等离线流程
- 任何"准备给老大起床看"类提议出口前，先查当前态；态=board_session 则改口为"等你睡再写"或直接不提
