---
name: Extend > Build (先查已有，再决定造)
type: paradigm
discovered: 2026-04-16
trigger: Board "不对啊，我们又在重复造轮子" — CEO 派 5 个 spec 全 duplicate Y*gov 已有模块; 又 "你的全局观还是太差了"
depth: deep
---

## Claim
任何新组件创建前必须先证明不存在等价物。搜索成本远低于重建成本。优先级: 整合已有 > 扩展已有 > 迁移 K9 > 新造。

## Evidence
CEO 2026-04-16 派 Maya CZL-113 (reply_scan_methodology) + Ethan CZL-114/115 (formal_methods_primer) + Maya CZL-118 (routing_gate) — 全是"新 spec"，但 Y*gov 已有: coordinator_audit.py / metalearning.py / counterfactual_engine.py / adaptive.py / causal_feedback.py / enforcement_observer.py 等 9+ 模块。precheck_existing.py 只扫 1 repo 导致全报 "build_new" (false negative)。Board 两次 catch (2026-04-15 + 2026-04-16)。

## Reasoning Chain
1. CEO 想到一个 idea → 直觉 "需要新东西" → 派 sub-agent 写 spec
2. 但 Y*gov 已有等价物 → 新 spec = duplicate → 两套不同步 → 混乱
3. 正确: 想到 idea → precheck 4 repo → matches? → YES → extend existing → NO → justify + build
4. Precheck = O(1 minute) 搜索 vs O(1 hour) 新建 → 搜索 ROI 60x

## Counterfactual
If skip precheck: 每个 idea 都造新 → 组件数爆炸 → 维护不可能 → governance theater
If always precheck: 组件数受控 → 每个真有价值 → 维护成本 O(n) not O(n²)

## Application
CEO dispatch prompt 必含 BOOT step 2: `python3 scripts/precheck_existing.py <component_name>`
If matches > 0: dispatch 必须是 EXTEND atomic (编辑已有 file), NOT BUILD atomic (写新 file)
If matches = 0: dispatch 需 explicit justification "为什么不存在等价物"

## Connections
→ pre_build_routing_gate_v1.md (formal spec)
→ precheck_existing.py (implementation, CZL-151 修到 4-repo)
→ FG rule new_artifact_without_precheck (CZL-154 promoting to warn)
→ Board feedback_god_view_before_build (MEMORY rule)
