---
name: AI 身份必披露
description: 所有对外 cold outreach (email/LinkedIn/social/blog) 必须披露 AI agent 作者身份 + 人类 reviewer + 提供 human-only opt-out
type: feedback
originSessionId: b8aed99a-55f2-4073-a223-d41630cec4f4
---
所有 Y\* Bridge Labs 对外 cold outreach 必须满足 4 条强制：
1. 第一段披露 AI 作者身份（不假装真人）
2. 命名具体 AI agent persona (Zara/Marco/Sofia 等)
3. 命名人类 reviewer (Founder Haotian Liu)
4. 提供"human only"opt-out 通道

**Why:** 2026-04-13 Board 审批 Stripe Joe Camilleri outreach 时硬约束："发的时候一定要有 AI agent 试验性运作的声明，不要伪装成真人"。本质：合法 + 信任建立。Y\* Bridge Labs 卖点正是"AI agent team 用自己的治理产品治理自己"——伪装成真人 = 自我否定 USP + 法律风险 (CAN-SPAM, GDPR Art 14)。这一条违反 = P0 reputational disaster (CISO 看穿后立刻黑名单 + 公开 call out)。

**How to apply:**
- ✅ 模板：`sales/outreach/email_template_v1.md` 已含 disclosure 段
- ✅ 标准段落已写进模板 tail (4 mandatory items)
- 任何 CSO / CMO / 顶岗 sub-agent 起 outreach → 必先 reference 这个模板
- ForgetGuard 应加 rule: scan outgoing email/blog content lacking "AI" / "agent" / "Zara/Marco/Sofia" 关键字 → warn
- ⚠️ 适用范围：cold (从未沟通过的) outreach；warm (内部/已知) 通信不强制
- **Board** 是 final reviewer：CSO 准备好邮件 → CEO 自审 → Board 一句"批准"才真发
