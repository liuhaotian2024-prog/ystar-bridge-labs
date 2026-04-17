---
name: Whitelist > Blacklist
type: paradigm
discovered: 2026-04-16
trigger: Board said "这是黑名单思路，应该是白名单思路" when CEO described reply scan violation detection
depth: foundational
---

## Claim
有限枚举合法形式（whitelist）永远优于无限排除非法形式（blacklist），因为前者的 P(correct) → 1.0 而后者的 P(correct) 受 detector 准确度上界约束。

## Evidence
Reply scan detector (blacklist): scan every reply → detect dispatch → check 5-tuple → 90% accuracy (10% miss/false-fire)
Reply taxonomy (whitelist): 5 templates [DISPATCH|RECEIPT|NOTIFICATION|QUERY|ACK] → match template → 100% compliance by construction

## Reasoning Chain
1. CEO built coordinator_audit as blacklist detector (scan → identify → fire)
2. Board catches: "你这还是黑名单思路"
3. Whitelist = enumerate ALL valid forms (finite set, formally provable complete)
4. Blacklist = enumerate ALL invalid forms (infinite set, can never be complete)
5. Aristotelian mutual exclusion + collective exhaustion = whitelist's formal foundation
6. Tarski truth conditions: enumerate true statements is tractable; enumerate all false is not

## Counterfactual
If I kept blacklist: every new reply format would need new detector → infinite detector-building → never catches everything.
If I use whitelist: new format = add 1 template → coverage remains 100%.

## Application
Apply WHENEVER designing enforcement/validation/detection:
- "What patterns should I catch?" → WRONG QUESTION (blacklist)
- "What patterns are allowed?" → RIGHT QUESTION (whitelist)
- ForgetGuard rules, CROBA scope, reply format, dispatch format, commit classification — ALL should be whitelist

## Connections
→ formal_methods_primer §2 Aristotelian categories
→ reply_taxonomy_whitelist_v1.md implementation
→ action_model_v2 §3 sized variants (3 valid types = whitelist of atomic classes)
