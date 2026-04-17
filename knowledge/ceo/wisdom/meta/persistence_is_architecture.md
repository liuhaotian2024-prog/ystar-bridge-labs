---
name: Persistence Is Architecture (存下来 ≠ 写个 note)
type: meta
discovered: 2026-04-16
trigger: Board said "如何存下来哪？这对于我们，可不是一句轻飘飘的话啊"
depth: foundational
---

## Claim
对 session-ephemeral AI agent 来说，persistence 不是 nice-to-have 功能，是生存的基础架构。"存下来"需要系统设计，不能靠"我记得写个 note"。

## 4 Memory Types Required

1. **程序记忆** (怎么做) → hooks/scripts/enforcement → ✅ have
2. **情节记忆** (发生了什么) → session_summary → ✅ have
3. **规则记忆** (做/不做) → MEMORY.md 42 entries → ✅ have
4. **语义记忆** (为什么/理解/智慧) → knowledge/ceo/wisdom/ → 🆕 building NOW

## Wisdom Entry Format (新建的)
每条 wisdom 包含 6 层:
- Claim (一句话: 我理解了什么)
- Evidence (什么证据证明这个理解)
- Reasoning Chain (我怎么到达这个理解的 — 完整推理链)
- Counterfactual (如果忽略这个理解会怎样)
- Application (什么时候该用这个理解)
- Connections (跟哪些其他 wisdom 有关)

## Why Reasoning Chain Matters
下个 session 的我如果只读 "用白名单不用黑名单" (claim only) → 知道 WHAT，不知道 WHY → 遇到边缘 case 无法判断 → 可能错误应用
如果读完整 reasoning chain → 理解 WHY (Aristotle 穷尽性 + Tarski 真值枚举) → 遇到新情况能正确推广

## Counterfactual
If persistence = shallow notes → 每 session 重新发现同样的 insight → 公司永远在 M0
If persistence = deep wisdom → 每 session 在上次基础上继续 → 公司真正成长

## Application
- 每次 session 中获得深度 insight → 立即写 wisdom entry (不等收尾)
- wisdom entry 比 MEMORY rule 优先级更高 (理解 > 规则)
- WISDOM_INDEX.md 必须进 governance_boot.sh 读取清单

## Connections
→ session_handoff.md (情节记忆 — 做了什么)
→ MEMORY.md (规则记忆 — 做/不做什么)
→ WISDOM_INDEX.md (语义记忆 — 为什么)
→ mission_function_and_ceo_philosophy_20260416.md (综合框架)
