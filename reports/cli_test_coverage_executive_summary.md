# CLI测试覆盖检测 - 执行摘要

**日期:** 2026-04-03  
**执行人:** eng-platform  
**任务:** 检测Y*gov 18个CLI命令的功能测试覆盖情况

---

## 核心发现 (TL;DR)

| 指标 | 当前状态 | 目标 | 差距 |
|------|---------|------|------|
| **命令测试覆盖率** | 28% (5/18) | 100% | 需要补13个命令 |
| **P0命令覆盖** | 0% (0/2) | 100% | setup、hook-install无测试 |
| **代码覆盖率** | 未测量 | 80% | 待测量 |
| **集成测试** | 0个 | 5+ | 需要建立E2E测试 |

**风险等级:** 🔴 **高风险** - P0安装命令无自动化测试，用户安装失败无法自动检测

---

## 关键问题

### 1. P0命令无测试 (最高风险)
- `ystar setup`: 用户首次安装必经流程，**无任何测试**
- `ystar hook-install`: 安装核心步骤，**无任何测试**
- **影响:** 安装失败只能通过用户反馈发现，无法提前捕获

### 2. 复杂命令依赖手动测试
- `simulate`, `quality`, `audit`, `init`: 逻辑复杂，无自动化验证
- **影响:** 回归问题无法及时发现，维护成本高

### 3. 缺少集成测试
- 现有测试仅覆盖单个命令
- 无跨命令工作流测试 (如 setup -> baseline -> delta)
- **影响:** 命令间协作问题无法发现

---

## 已有测试质量评估

### ⭐⭐⭐⭐ 高质量 (可作为标准)
- **domain命令** (test_domain_cli.py): 9个测试，覆盖正常+错误路径

### ⭐⭐⭐ 良好
- **seal命令** (test_v041_features.py): 包含验证一致性测试

### ⭐⭐ 基础
- **doctor/report命令**: 仅smoke test，无深度测试

### ⭐ 不充分
- **verify命令**: 仅测试错误路径

---

## 工作量评估

### 快速修复 (1-2周) - 降低P0风险
| 阶段 | 工作量 | 产出 |
|------|--------|------|
| **Week 1** | 1-1.5小时 | P0命令测试 (setup, hook-install) |
| **Week 2** | 5-8小时 | P1命令测试 (baseline, delta, audit, simulate, quality, init) |

### 完整覆盖 (3-4周)
| 阶段 | 工作量 | 产出 |
|------|--------|------|
| Week 1 | 1-2天 | P0命令测试 ✅ |
| Week 2 | 1周 | P1命令测试 ✅ |
| Week 3 | 3-4天 | P2命令测试 (check, impact, archive, demo, policy-builder) |
| Week 4 | 2-3天 | P3命令测试 + 集成测试 |

**总工作量:** 15-23小时 (包含调试+文档)

---

## 推荐方案

### 立即执行 (本周)
1. ✅ **P0测试** (1-1.5小时)
   - test_cli_setup.py
   - test_cli_hook_install.py
   - 立即降低安装失败风险

2. ✅ **CI集成** (30分钟)
   - 在GitHub Actions中启用CLI测试
   - 设置覆盖率门禁 (80%)

### 短期执行 (2周内)
3. ✅ **P1测试** (5-8小时)
   - baseline, delta, audit, simulate, quality, init
   - 覆盖核心业务逻辑

4. ✅ **测试基础设施** (1小时)
   - 创建tests/fixtures/目录
   - 建立标准测试模板

### 中期执行 (1个月内)
5. ✅ **完整覆盖** (7-10小时)
   - P2/P3命令测试
   - E2E集成测试

---

## 预期收益

| 收益 | 量化指标 | 时间线 |
|------|---------|--------|
| **降低安装失败率** | P0测试覆盖 → 提前发现环境问题 | Week 1后生效 |
| **提升代码质量** | 覆盖率 28% → 80%+ | Week 4后达成 |
| **加速开发迭代** | CI自动化验证 → 减少手动测试 | Week 1后生效 |
| **减少回归问题** | 自动化捕获 → 发布前发现 | Week 2后生效 |

---

## 测试策略亮点

### 分层测试架构
```
Layer 3: E2E测试 (1-5s/test)
         ↓ 测试用户场景
Layer 2: 集成测试 (100ms-1s/test)
         ↓ 测试真实数据
Layer 1: 单元测试 (<100ms/test)
         ↓ 测试逻辑正确性
```

### Mock策略
- 文件系统: pytest tmp_path
- 数据库: tmp_db fixture
- LLM调用: unittest.mock
- 用户输入: patch builtins.input

### CI门禁
- 所有CLI测试通过
- 覆盖率 ≥80%
- 无新增pylint警告
- 平均测试时间 <5s

---

## 交付物

### 已完成
✅ CLI测试覆盖报告 (详细版)  
✅ 测试实现样例代码 (7个样例)  
✅ 工作量评估表  
✅ 测试策略设计  

### 待执行
⏳ 创建测试文件 (13个新文件)  
⏳ 建立测试fixtures  
⏳ CI集成配置  
⏳ 覆盖率报告生成  

---

## 下一步行动

### 需要决策
1. **优先级确认**: 是否同意P0/P1/P2/P3分级？
2. **时间分配**: 分配1周 or 4周完成？
3. **资源分配**: eng-platform独立完成 or 需要CTO支持？

### 待批准
1. 创建13个新测试文件到Y-star-gov/tests/
2. 修改tests/conftest.py增加fixtures
3. 在CI中启用CLI测试门禁

---

## 附录: 文件清单

### 生成的报告文件
- `cli_test_coverage_2026-04-03.md` - 详细报告 (40页)
- `cli_test_samples_2026-04-03.py` - 测试样例代码 (400行)
- `cli_test_coverage_executive_summary.md` - 本文件

### 位置
```
ystar-company/reports/
├── cli_test_coverage_2026-04-03.md
├── cli_test_samples_2026-04-03.py
└── cli_test_coverage_executive_summary.md
```

---

**报告生成:** eng-platform  
**审核待定:** CTO  
**决策待定:** CEO (Aiden/承远)

**建议:** 立即批准P0测试实施，本周内完成setup/hook-install测试，降低用户安装失败风险。
