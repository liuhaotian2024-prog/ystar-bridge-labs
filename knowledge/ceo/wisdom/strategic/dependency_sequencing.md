---
name: Dependency Sequencing (不平铺全上)
type: strategic
discovered: 2026-04-16
trigger: Board rejected CEO proposal #001 (jump to customers) — "产品空白 CSO 找客户 = 破坏口碑"
depth: deep
---

## Claim
公司活动有因果依赖链。平铺全上 = 资源浪费 + 口碑损害。正确做法 = 拓扑排序依赖 DAG → 按序执行。

## Evidence
Board 否决了 CEO 提案 #001 (先找客户)："如果我们的基础和技术产品服务都还是空白，那么 CSO 联系客户有意义吗？搞不好只会破坏口碑"。又说："为什么我之前几乎没有给几个高管派任务？" — 因为前置条件不满足，不是忘了。

## Reasoning Chain
1. CEO 提案: 客户 0 分 → 去找客户 (看起来合理)
2. Board 否决: 产品 install 坏了 → 客户试用失败 → 永不回来 (因果推理)
3. 正确顺序: 基础建设 → 产品可用 → 证据积累 → 客户接触 → 收入
4. 每一步的前置条件 = 上一步的输出
5. 拓扑排序: A → B → C，不能跳到 C

## Dependency DAG (current)
```
基础建设稳定 (治理/测试/enforce/自动化)
    ↓
产品可安装 (pip install ystar works)
    ↓
证据积累 (赏金成绩 / 案例发布 / 开源贡献)
    ↓
外部信誉 (blog / paper / thought leadership)
    ↓
客户接触 (CSO outreach with evidence portfolio)
    ↓
收入 (pricing validation → first paying customer)
```

## Counterfactual
If CEO 平铺全上 (同时派 CTO 修产品 + CSO 找客户 + CMO 写 blog):
→ CSO 找到客户但产品 install 失败 → 口碑损害
→ CMO 写 blog 承诺功能但功能 broken → 信誉损失
→ 所有工作互相矛盾 → 一团乱麻

## Application
每次 CEO 提案前: 画 dependency DAG → 验前置条件满足 → 只提当前可执行层
CMO/CSO/CFO 不派活 ≠ 忘了 → 前置条件不满足时正确决策是等待 + 做前置

## Connections
→ Board rejected CEO proposal #001 (跳太快)
→ Campaign v7-R1 (修改版: 先稳基础)
→ 市场入口策略 (evidence_before_pitch.md)
→ topological sort = formal_methods_primer FOL predicate: "∀ task t, ∄ unmet dependency → may_execute(t)"
