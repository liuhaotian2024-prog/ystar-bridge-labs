# V1.0 Experiment Plan — 八层能力验证 + 自主探索
# Created: 2026-04-05
# Team: Aiden (CEO) + CTO + Platform + Governance Engineers
# Status: IN PROGRESS
# Board Review: 1 week from now

---

## Experiment Design Philosophy

每个实验遵循：
1. 明确假设 → 2. 设计验证 → 3. 执行 → 4. 发现问题 → 5. 修复 → 6. 重新验证
不接受"感觉变好了"。每个结论必须有数据支撑。

---

## 八层实验计划

### Layer 1: 实时拦截 — 50种绕过向量
- [ ] 设计50种危险命令变种（注入、遍历、编码、子进程）
- [ ] Mac + Windows各跑一次
- [ ] 目标：100%拦截，0误报，p99<10ms
- [ ] field_deny和postcondition维度系统验证

### Layer 2: CIEU审计链 — 10000条压力测试
- [ ] 写入10000条记录，验证hash链100%完整
- [ ] 查询任意记录<1秒
- [ ] 伪造攻击模拟（write_dict直接调用）
- [ ] 重启恢复完整性验证

### Layer 3: DelegationChain — 四级权限链
- [ ] CEO→CTO→工程师→实习生完整链
- [ ] 每级尝试权限升级
- [ ] nl_to_contract翻译后子集验证
- [ ] gov_escalate完整审批流

### Layer 4: OmissionEngine — 主动扫描
- [ ] 3分钟deadline义务测试
- [ ] 实现空闲触发主动扫描
- [ ] HARD_OVERDUE阻断验证

### Layer 5: Meta Learning — 100次闭环
- [ ] 跑够100次gov_check
- [ ] 验证tighten()触发和建议
- [ ] 验证contract参数变化
- [ ] Counterfactual→Re-baseline链

### Layer 6: Pearl L3 — 反事实验证
- [ ] 降低触发阈值（连续3次同类violation）
- [ ] 新增gov_counterfactual tool
- [ ] WorkloadSimulation反事实查询
- [ ] 反事实→contract修改闭环

### Layer 7: 用户治理环境 — 500条模拟数据
- [ ] 模拟2周用户数据
- [ ] baseline/delta/trend验证
- [ ] 三种报告格式实现
- [ ] public summary合规性评估

### Layer 8: 安装体验 — 跨平台真实测试
- [ ] Windows完整安装
- [ ] 每步时间记录
- [ ] 第一个DENY出现时间

---

## 自主探索方向（Board额外授权）

### 探索一：CIEU因果追踪能力边界
假设：CIEU记录可以重建完整的决策因果链
验证：从任意DENY事件反向追踪到Board的delegation授权

### 探索二：合约语义覆盖率
假设：8个维度的覆盖率越高，治理质量越好
验证：比较不同覆盖率下的violation拦截率

### 探索三：自动合约优化
假设：GovernanceLoop可以自动发现规则盲区
验证：用500条数据训练后，系统是否能发现人类没注意到的风险

### 探索四：多模型治理一致性
假设：同一合约在不同LLM（Claude/GPT/本地模型）下行为一致
验证：同一组测试用例在不同模型下跑gov_check

### 探索五：治理延迟的真实用户影响
假设：<5ms延迟用户无感知
验证：在100ms、50ms、10ms、5ms、1ms下测量用户体验差异

---

## 进度追踪

每完成一个实验，在这里打勾并记录：
- 日期
- 假设验证结果（通过/失败）
- 发现的问题
- 修复措施
- 重新验证结果

---

## 一周后Board报告内容

1. 八层实验逐层完成率
2. 发现的新问题列表
3. 修复的问题列表
4. 每层的数据证据
5. v1.0准备度评估（百分比）
6. 自主探索的发现
7. 下周计划
