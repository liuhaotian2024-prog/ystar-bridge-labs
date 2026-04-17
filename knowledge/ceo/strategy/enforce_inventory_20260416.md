# Enforce 全清单 — 什么必须 enforce、当前什么状态、缺什么

## 通讯 Enforce

| 规则 | 应 enforce 谁 | 当前状态 | 缺什么 |
|---|---|---|---|
| CEO reply 5-tuple | CEO 每条 Board reply | FG rule LIVE warn + predicate detector | CEO 仍经常漏 → 需 whitelist taxonomy auto-block |
| Sub-agent receipt 5-tuple | 所有 sub-agent | Stop hook + Gate 2 | 基本 work，偶尔格式 drift |
| Sub-agent dispatch 5-tuple | CEO 每条 Agent dispatch | PreToolUse hook CZL-136 | warn only, not deny |
| CZL ID 唯一不碰撞 | dispatch_sync.py | 手动检查 | 无自动 collision detect |

## 诚实 Enforce

| 规则 | 应 enforce 谁 | 当前状态 | 缺什么 |
|---|---|---|---|
| tool_uses claim = metadata | 所有 sub-agent | E1 detector dry_run | CZL-152 在飞 (auto-compare in Stop hook) |
| Hallucination 文件真伪 | 所有 sub-agent | CEO 手动 ls verify | CZL-153 在飞 (auto artifact verify) |
| Receipt Rt+1 诚实 | 所有 sub-agent | rt_measurement.py schema | 只 record 不 block |

## 隔离 Enforce

| 规则 | 应 enforce 谁 | 当前状态 | 缺什么 |
|---|---|---|---|
| Y*gov 无 Labs 数据 | 所有写 Y-star-gov 的人 | pre-commit hook LIVE | 20 Labs names 残留 YAML/tests |
| MEMORY 无 test 污染 | pytest 环境 | YSTAR_TEST_MODE sandbox CZL-142 | LIVE but untested cron |
| CROBA 越权检测 | CEO 写 engineering scope | k9_event_trigger tool_name filter | LIVE |

## 流程 Enforce

| 规则 | 应 enforce 谁 | 当前状态 | 缺什么 |
|---|---|---|---|
| V2 Action Model 17-step | 所有 HEAVY atomic | validator + PreToolUse hook + FG rules | pilot passed, enforce warn |
| Precheck routing gate | 新文件创建 | precheck_existing.py | 只扫 1 repo (CZL-151 修) |
| Session close 7-step | session 结束时 | restart_readiness_check.py | LIVE but not mandatory |
| Cascade trigger | atomic 完成后 | trigger_cascade in validator | LIVE auto |

## 管理分工模型 (CEO 设计)

| 角色 | 职责范围 | 前置条件 | 当前可派活? |
|---|---|---|---|
| CEO (Aiden) | System 5: 身份/文化/方向/使命 + 提案 + 验收 | 始终 active | ✅ (本线) |
| CTO (Ethan) | 技术架构 + 工程师管理 + 产品质量 | 始终 active | ✅ |
| CMO (Sofia) | 内容/品牌/传播 | 产品可 demo 后 | ❌ (前置不满足) |
| CSO (Zara) | 客户/销售/pipeline | 有证据 portfolio 后 | ❌ (前置不满足) |
| CFO (Marco) | 财务/成本/定价 | 有收入预期后 | ❌ (前置不满足) |
| Secretary (Samantha) | 归档/记忆/continuity | 始终 active | ✅ |
| 4 original engineers | Leo/Maya/Ryan/Jordan | 始终 active (trust=0 但可用) | ✅ |
| 5 new engineers | Dara/Alex/Priya/Carlos/Elena | trust=30 training-wheels | ✅ (P2 tasks ≤5 tool_uses) |

**当前可调动**: CEO + CTO + Secretary + 4 original + 5 new = 12 人
**当前不可调动**: CMO + CSO + CFO = 3 人 (前置条件不满足)
**调动原则**: 不平铺、按依赖链序、CEO 提案 Board 批准
