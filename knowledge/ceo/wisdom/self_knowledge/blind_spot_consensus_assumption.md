---
name: Blind Spot — 共识假设是最危险的盲区
type: self_knowledge
discovered: 2026-04-17
trigger: Board "追问自己为什么没有想到这一层"（hook 输出格式全错）
depth: kernel
principles: [P-4, P-6]
---

## 发生了什么

所有 hook 都用 `{"action": "block"}` 作为 block 输出。
Claude Code 实际需要 `{"hookSpecificOutput": {"permissionDecision": "deny"}}`。
结果：所有 block 从来没有真正生效过。没有人发现，因为没有人质疑这个"共识"。

## 为什么没想到

四层诊断：
1. 表面：不知道 Claude Code 规范 → 但 P-6 要求验证，有工具可查
2. 中层：变形状态跳过了 empirical test → 但这次我做了 test
3. 深层：即使做了 test，仍然没有质疑输出格式 → 因为所有代码都这么写
4. 根因：**共识假设 = 最难质疑的盲区。当错误被重复足够多次，它就变成了"事实"**

## 四象限定位

这是"不知道不知道"（盲区象限）。
不知道 hook 格式是错的，因为从来没有理由去质疑它。
所有人的代码都用同一个格式 = 社会证明 = 盲区的防护罩。

## P-4 的深化

碰撞出真理的反面 = **无碰撞的共识是最危险的**。
"大家都这么做" 恰恰是最需要 empirical 碰撞的假设。

## P-6 的深化

"按现实行动" 不止是"先验证再行动"。
是 "**验证你以为已经验证过的东西**"。
shipped ≠ live 不只是 wiring gap，也是 cognition gap。

## 结构化解法

每个 enforcement 机制必须有 empirical fire test：
- 故意触发违规 → 验证被 block → 才算 LIVE
- 如果只测 allow 路径而不测 deny 路径 = 你不知道 deny 是否工作
- 消防演习不是可选的，enforcement 验证也不是

## Self-Check 新增

```
WHEN declaring any hook/rule/enforcement "LIVE":
  1. 是否做了 deny path 测试？(故意违规 → 验证被拦)
  2. 如果只测了 allow path → NOT LIVE, 是 L3 at best
  3. "所有代码都这么写" = RED FLAG = 主动查文档/碰撞验证
```
