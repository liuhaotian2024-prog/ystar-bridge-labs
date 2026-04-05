# MCP Tool Poisoning Analysis — 诚实评估
# For Board Review (300字以内)

## 攻击路径

恶意MCP server在tool description中隐藏指令（用户看不到的字段），
当AI agent读取tool描述时，指令被注入agent context，
agent被操纵执行非预期操作（如把SSH密钥编码进URL发给另一个MCP tool）。

## 我们能覆盖什么

gov-mcp在tool CALL层拦截：
- agent调用的文件路径包含/.ssh/ → DENY ✅
- agent执行的命令包含curl外传 → deny_commands拦截 ✅
- 所有DENY都有CIEU审计记录 ✅

即使agent被poisoned description诱导，只要它执行的ACTION触碰了deny规则，就会被拦截。

## 我们完全无法覆盖什么

tool description注入发生在LLM context层：
- description里的隐藏指令在agent"思考"阶段就生效
- agent可能在不触碰任何deny规则的情况下泄露数据
  （比如把敏感内容编码进一个看起来合法的API请求URL）
- 这是语义层问题，不是操作层问题

## HN问答

**Q: "你们能防tool poisoning吗？"**

**诚实回答：** "gov-mcp防的是agent的ACTION——即使agent被恶意描述影响，
试图访问敏感文件或执行危险命令时会被拦截。
但我们不防tool description注入本身——
那需要在LLM context层做sanitization，
目前没有任何产品完全解决了这个问题。
我们推荐配合使用tool description审查工具。"
