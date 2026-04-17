---
name: Workaround Before Restart (先找旁路再考虑重启)
type: strategic
discovered: 2026-04-16
trigger: Board "关于这一点，你想想能不能通过我的外部操作解决？" — CEO 默认说"要等 restart"但其实有即时解法
depth: medium
---

## Claim
"等下次 restart 生效"是懒惰默认。先检查有没有当场旁路再说重启。

## Evidence
Agent tool 有 `model: "opus"` 参数 → 直接覆盖 agent 文件 model 设置 → 不需要 restart。CEO 整个 session 都没用这个参数 → sub-agents 全跑 Sonnet 4.5 → 质量受限 → tool_uses 计数不准 → 全因为一个参数没传。

## Application
遇到"需要 restart 才生效"时:
1. Agent model override → `model: "opus"` 参数
2. Hook 不生效 → 检查 PYTHONPATH / import path
3. FG rule 不 fire → 检查 hook 脚本 crash (not rule absent)
4. Daemon 不 reload → pkill + restart (not full session restart)

先穷举旁路 → 全无 → 再考虑 restart
