# RFC: NonceLedger接入DelegationChain
**RFC编号:** RFC-2026-004
**标题:** NonceLedger防重放攻击接入DelegationChain验证
**提出者:** CTO (eng-kernel)
**日期:** 2026-04-03
**状态:** 待Board审批
**优先级:** P2

## 1. 动机
NonceLedger已在dimensions.py完整实现，
但没有任何调用点。每个DelegationContract
的授权grant可以被无限重放，
同一个授权可以在不同session里反复使用。

## 2. 设计方案
在hook.py的register_session()里初始化session级NonceLedger。
每次HANDOFF/SUBAGENT_SPAWN时调用ledger.consume(dc)，
失败则DENY并写入CIEU。
每个授权grant只能使用一次。

## 3. 向后兼容性
NonceLedger是session级的，每次session重新初始化。
不影响跨session的DelegationChain复用。
旧版session.json无nonce字段时降级为不验证。

## 4. 不硬编码原则
nonce验证开关作为session.json可配置参数：
{ "delegation_chain": { "nonce_enabled": true } }
默认true，用户可关闭。

## 5. 测试计划
新增tests/test_nonce_ledger_hook.py，8个测试用例。
现有669测试必须全部通过。

## 6. 风险
LOW-MEDIUM — 修改register_session()，
需要确认session级NonceLedger不影响
正常的HANDOFF流程。

## 7. Board决策点
1. 批准接入？
2. 默认nonce_enabled=true是否合适？

**状态:** ⏸️ 等待Board审批

---

## Board批复 (2026-04-03)

**批准人:** Board（刘浩天）
**状态:** ✅ 已批准，可以执行

### 批准内容
1. ✅ NonceLedger接入DelegationChain验证
2. ✅ session级NonceLedger，每次session重新初始化
3. ✅ 旧session.json无nonce字段时降级为不验证

### 强制性设计要求
nonce_enabled不得硬编码，必须作为
session.json可配置参数：

  nonce_enabled = session_cfg.get(
      "delegation_chain", {}
  ).get("nonce_enabled", True)

**执行优先级:** P2
