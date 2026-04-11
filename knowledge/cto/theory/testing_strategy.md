# CTO Theory: 测试策略 (Testing Strategy)
# Priority 2 理论库 · 2026-04-11 · CEO代CTO自主学习

---

## 核心原则

### 1. 测试是信任资产
807+测试不是技术债务，是信任基础设施。每个测试 = 一个"这件事不会出错"的承诺。
Y*gov作为治理框架，自己的测试必须是行业标杆——治理别人的系统如果自己不可靠，谁会信？

### 2. 测试门控（Test Gate）
CTO.md明确：86测试（现807+）必须全过才能commit。
不是建议，是Iron Rule级别的要求。跳过测试=跳过信任。

### 3. 测试金字塔

| 层级 | 数量 | 速度 | 覆盖 | Y*gov实例 |
|------|------|------|------|----------|
| 单元测试 | 多 | 快 | 函数级 | test_memory_store(14), test_precheck(9) |
| 集成测试 | 中 | 中 | 模块间 | test_health_omission_integration(8) |
| 端到端测试 | 少 | 慢 | 全链路 | BOARD-2026-04-09-E2E |

### 4. 今天的测试成果
本session新增79个测试，全过：
- 14 YML memory
- 26 gov_health
- 8 health-omission integration
- 9 precheck
- 12 identity
- 10 dispatch

### 5. 测试即文档
好的测试名就是功能说明：
- `test_board_mandate_initial_score_immutable` → Board规定initial_score不可变
- `test_dispatch_without_authority` → CEO越权dispatch会被DENY
- `test_cto_wrong_dimension_deny` → CTO用CMO维度预检会被拒

### 6. 环境陷阱
今天踩的坑：系统Python 3.9 vs Homebrew Python 3.11的包路径不同，导致import失败。
教训：测试必须在**产品实际运行的Python版本**下跑，不是随便哪个python3。

---

*Werner Vogels: "如果你没测试过故障模式，它就不工作。"*
