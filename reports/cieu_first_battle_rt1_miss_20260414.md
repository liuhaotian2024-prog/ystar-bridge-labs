# CIEU 首战 Rt+1 miss 基线 (2026-04-14)
Trigger Ethan-CTO 一派 prose-claim Ethan 宣称 install CIEU 到 9 agents done, CEO grep 实测 0 match → actual Rt+1=1.0 vs claimed 0.3.
## 发现
- Ethan prose-claim 无 tool_result evidence
- .claude/agents/*.md immutable 对 CTO 也 deny, 需 Samantha override
- sub-agent "说 done 就信" pattern 彻底打掉
## Rt+1 真测 mechanism
CEO grep/ls 复核, 不信 prose
## 教训
每 claim 必 tool_result 块. 参考本基线.
