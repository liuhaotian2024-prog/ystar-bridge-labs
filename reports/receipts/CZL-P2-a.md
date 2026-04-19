# CZL-P2-a Completion Receipt — router_registry Skeleton

**Atomic ID**: CZL-P2-a
**Claimed by**: eng-kernel (Leo)
**Completed + CEO Verified**: 2026-04-18

**Audience**: Board (Phase 2 架构基石启动证据), Ethan-CTO (router API review), Phase 2-b/c/d engineers (依赖此 API skeleton 注册 detector+executor). Purpose: 证明 enforce-as-router 架构底座 API 已建，下游 70% Labs 迁移可以基于此 register 规则。

**Research basis**: Board 2026-04-18 "全部功能写进负责 deny 的模块里做路径导入器" 主张需要底层 API。现有 EnforceDecision 只 3-4 状态不够，需要 INVOKE (调 feature) / INJECT (附上下文) / AUTO_POST (白板) 三种新 decision 承载路由动作。需要 RouterRegistry 单例管理 detector+executor 注册链。

**Synthesis**: router_registry 是 Labs 850 文件 → enforce 70% 迁移的唯一 integration point。API 设计关键：(a) 显式 max_chain_depth=5 防 INVOKE 循环 (b) detector 纯函数 payload→bool，executor 可侧效但需显式 return RouterResult (c) metadata 字段让 Phase 2-b/c/d 迁移时注册来源脚本路径可追溯回源 Labs 文件，便于后续 archive。这是门卫+导游架构的执行底座。

## 5-Tuple
- **Y\***: EnforceDecision 扩 3 值 + RouterRegistry 雏形 + chain_depth 守卫 + singleton API
- **Xt**: EnforceDecision 4 状态 no router, Phase 2-b/c/d 无法 register
- **U**:
  - `Y-star-gov/ystar/domains/openclaw/adapter.py:97-99` — INVOKE / INJECT / AUTO_POST 加入 enum（总 7 值）
  - `Y-star-gov/ystar/governance/router_registry.py` — NEW 300 lines: `RouterResult` dataclass / `RouterRule` dataclass / `RouterRegistry` class (register/unregister/find_matching/execute/stats/describe) + MAX_CHAIN_DEPTH=5 + `get_default_registry() / reset_default_registry()` singleton
  - `Y-star-gov/tests/governance/test_router_registry.py` — 29 tests (registration/matching/execution/pipeline/introspection)
- **Yt+1**: 29 tests PASS + grep 验 4 新 enum 值 + 文件 15458 bytes
- **Rt+1**: 0
