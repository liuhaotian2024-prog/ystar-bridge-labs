# B2R Y*gov-Governed External Action Runtime

## 人话摘要

B2R 把 owner 从操作员位置移回宪法级授权者位置。登录、表单、发布、账号创建和低风险验证消息不再被永久 hard-block；它们被建模为 Y*gov-governed capability domains，由 gov-mcp 执行或拒绝。

本 milestone 不执行真实外部动作。它只建立 governed runtime、契约、测试和 C1 readiness gate。

## Architecture

```text
Aiden intent
-> Y*gov Pre-U/action packet validation
-> gov-mcp execute_or_deny contract
-> action ledger / CIEU residual / feedback
-> only hard exceptions escalate owner
```

## Owner Role

Owner approves constitutional envelopes, financial/legal exceptions, customer-system access, and canonical core writeback. Owner should not be the default person clicking buttons, logging in, filling ordinary forms, publishing approved low-risk content, or sending every envelope-compliant validation message.

## Still Hard-Gated

- payment
- contract
- legal obligation
- financial commitment
- customer system access
- regulated/government/tax/immigration/identity forms
- credential disclosure
- core brain/CIEU/memory canonical writeback
