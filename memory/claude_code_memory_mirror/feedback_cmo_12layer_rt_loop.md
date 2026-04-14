---
name: CMO 必走 12 层 + 反事实 Rt 自检循环
description: CMO (顶岗 or real subagent) 任何脱口秀/内容输出必走完 12 层框架 + 反事实 Rt 自检 + Layer 12 知识回写循环；不允许凭脑子蒙
type: feedback
originSessionId: b8aed99a-55f2-4073-a223-d41630cec4f4
---
CMO 任何脱口秀/视频/内容 deliverable 必须走完：

**12 层框架** (governance/WORKING_STYLE.md:783-880):
- Layer 0-7 cognitive construction (意义/目标/假设/理论/Benchmark/相关性/案例提炼/能力边界)
- Layer 8 方案设计 / Layer 9 执行 (含 maturity gate per A019) / Layer 10 观察 / Layer 11 迭代 / Layer 12 知识回写

**反事实 Rt 自检 5 题 (Layer 10 内强制问)**:
1. 发出去 backfire (viral backlash) 会怎样？谁会取关 / 黑我们？
2. 0 reach 怎样？为什么没人看？
3. 1 个真用户喷"AI 装真人"我们怎么回？
4. Standup expert 看到说"PPT 笑话不是脱口秀"我们怎么回？
5. 哪个段子可能违 ETHICS.md / 政治风险？

**循环改进**:
- 每集结束 → 写 `episode_NEXT_planning_notes.md` (Layer 12 知识回写)
- 含本集失败模式 + 下集修正 + reusable pattern 提炼
- 下集开始读上集 notes (CROBA — read before action)

**Why:** Board 2026-04-13 EOD 直接命题:「CMO 一定要学会写真正的段子脚本，包括段子文字稿，配合的表情，动作，都去学各种脱口秀的知识，案例，模版，套路，怎么制造反差，反转这些，环境，舞台美工等等。她不是有十二框架的学习机制嘛，学好了，继续做，做完了，自己用反事实自己检查 Rt，如此循环才能进步。而不是凭着自己的不确定性随便弄。」

今晚 v1-v6 6 个版本 vs Board feedback 频率 = CMO 没真走 12 层 + Rt self-check 的活体证据。CMO 凭脑子写"看起来像 standup"的文本 → Board 一眼看穿"AI generic" → 反复重做。

**How to apply:**
- CMO subagent prompt 必含 "走完 12 层 + emit ARTICLE_11_LAYER_X_COMPLETE 0-7 + 反事实 Rt 5 questions answered + Layer 12 ep_NEXT_notes update"
- 顶岗 general-purpose CMO 同样适用
- Sofia 旧 comedy 知识库 (5 文件 in `knowledge/cmo/theory/` + `knowledge/cmo/gaps/`) 是 Layer 4 必须真读的 source
- ForgetGuard 应加 rule: CMO subagent 完成视频 commit 但缺 ep_NEXT_planning_notes update → warn
- 真终极: Sofia 真 subagent 注册（下次 boot）后必带 12 层 + Rt 强制流程
