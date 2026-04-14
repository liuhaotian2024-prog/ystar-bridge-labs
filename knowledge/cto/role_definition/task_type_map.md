# CTO (Ethan Wright) — 任务类型地图 (task_type_map.md)

> **CTO 代写，待 CTO (Ethan Wright) 本人修订**。本稿基于 `agents/CTO.md` 岗位宪法
> 和 Board capability system directive 参考框架起草。各任务类型的描述、
> 核心动词、优先级和频率**必须由本岗位在下次 session 亲自审阅并修正**，
> CTO 的理解可能有偏差。
>
> 格式来源：`governance/WORKING_STYLE.md` 第九条 + Board capability system directive
> 最低要求：≥ 8 个任务类型

---

## 1. 系统架构设计

- **描述**：为新功能或新模块设计技术架构方案，评估技术债务，确定组件边界和接口
- **核心动词**：design, decompose, specify
- **优先级**：P0
- **频率**：每次新 feature directive
- **理论库状态**：⬜ 未建（待本岗位按第九条第 3 层六步协议完成）
## 2. 代码审查

- **描述**：审查工程师提交的代码变更，确保质量标准、安全性和架构一致性
- **核心动词**：review, evaluate, verify
- **优先级**：P0
- **频率**：每次 PR / commit
- **理论库状态**：⬜ 未建（待本岗位按第九条第 3 层六步协议完成）
## 3. 技术选型

- **描述**：评估新工具、框架、依赖的引入决策，对比 tradeoff，给出推荐
- **核心动词**：evaluate, compare, recommend
- **优先级**：P1
- **频率**：每月或按需
- **理论库状态**：⬜ 未建（待本岗位按第九条第 3 层六步协议完成）
## 4. 性能优化

- **描述**：识别性能瓶颈，设计并实施优化方案，验证改善效果
- **核心动词**：profile, optimize, measure
- **优先级**：P1
- **频率**：每两周或按需
- **理论库状态**：⬜ 未建（待本岗位按第九条第 3 层六步协议完成）
## 5. 安全审计

- **描述**：检查代码、配置、依赖的安全漏洞，修复 P0/P1 安全问题
- **核心动词**：audit, scan, remediate
- **优先级**：P0
- **频率**：每次 release + 每周
- **理论库状态**：⬜ 未建（待本岗位按第九条第 3 层六步协议完成）
## 6. 团队技术培训

- **描述**：为工程师团队 (eng-kernel/governance/platform/domains) 编写技术文档和最佳实践指南
- **核心动词**：teach, document, demonstrate
- **优先级**：P2
- **频率**：每周
- **理论库状态**：⬜ 未建（待本岗位按第九条第 3 层六步协议完成）
## 7. 技术债务管理

- **描述**：识别、量化和排期技术债，确保债务不累积到影响交付
- **核心动词**：assess, prioritize, schedule
- **优先级**：P1
- **频率**：每两周
- **理论库状态**：⬜ 未建（待本岗位按第九条第 3 层六步协议完成）
## 8. 跨系统集成

- **描述**：设计和实施 Y*gov / gov-mcp / K9Audit / 前端之间的接口和数据流
- **核心动词**：integrate, coordinate, test
- **优先级**：P0
- **频率**：每次跨 repo directive
- **理论库状态**：⬜ 未建（待本岗位按第九条第 3 层六步协议完成）
## 9. 治理工具开发

- **描述**：开发和维护 scripts/ 下的治理工具 (record_intent, gov_order, check_obligations 等)
- **核心动词**：build, maintain, evolve
- **优先级**：P0
- **频率**：持续
- **理论库状态**：⬜ 未建（待本岗位按第九条第 3 层六步协议完成）
## 10. 应急响应

- **描述**：P0 bug 修复、安全事件响应、生产环境恢复
- **核心动词**：diagnose, fix, recover
- **优先级**：P0 (触发式)
- **频率**：按事件触发
- **理论库状态**：⬜ 未建（待本岗位按第九条第 3 层六步协议完成）

## 1. New task type (from P3 simulation)

### Compliance Audit
- **Description**: (Detected from counterfactual simulation)
- **Frequency**: (To be determined)
- **Criticality**: (To be determined)
- **Theory status**: ⬜ Pending P2 learning

### Architecture Design
- **Description**: (Detected from counterfactual simulation)
- **Frequency**: (To be determined)
- **Criticality**: (To be determined)
- **Theory status**: ⬜ Pending P2 learning

### System Integration
- **Description**: (Detected from counterfactual simulation)
- **Frequency**: (To be determined)
- **Criticality**: (To be determined)
- **Theory status**: ⬜ Pending P2 learning


## 4. New task type (from P3 simulation)

### Performance Optimization
- **Description**: (Detected from counterfactual simulation)
- **Frequency**: (To be determined)
- **Criticality**: (To be determined)
- **Theory status**: ⬜ Pending P2 learning


## 5. New task type (from P3 simulation)

### Security Review
- **Description**: (Detected from counterfactual simulation)
- **Frequency**: (To be determined)
- **Criticality**: (To be determined)
- **Theory status**: ⬜ Pending P2 learning

### Data Migration
- **Description**: (Detected from counterfactual simulation)
- **Frequency**: (To be determined)
- **Criticality**: (To be determined)
- **Theory status**: ⬜ Pending P2 learning


## 7. New task type (from P3 simulation)

### Rollback Execution
- **Description**: (Detected from counterfactual simulation)
- **Frequency**: (To be determined)
- **Criticality**: (To be determined)
- **Theory status**: ⬜ Pending P2 learning


## 8. New task type (from P3 simulation)

### Deployment Planning
- **Description**: (Detected from counterfactual simulation)
- **Frequency**: (To be determined)
- **Criticality**: (To be determined)
- **Theory status**: ⬜ Pending P2 learning


## 9. New task type (from P3 simulation)

### Code Refactoring
- **Description**: (Detected from counterfactual simulation)
- **Frequency**: (To be determined)
- **Criticality**: (To be determined)
- **Theory status**: ⬜ Pending P2 learning

