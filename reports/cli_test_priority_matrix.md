# CLI测试优先级矩阵 - 快速参考

**日期:** 2026-04-03  
**用途:** 快速查看每个命令的测试状态和优先级

---

## 优先级矩阵表

| 命令 | 当前状态 | 测试复杂度 | 预计工作量 | 优先级 | 风险等级 | 开始时间 |
|------|---------|-----------|-----------|--------|---------|---------|
| **setup** | ❌ 无测试 | 🟡 中 | 30-45分钟 | **P0** | 🔴 高 | Week 1 Day 1 |
| **hook-install** | ❌ 无测试 | 🟢 简单 | 15-20分钟 | **P0** | 🔴 高 | Week 1 Day 1 |
| **init** | ❌ 无测试 | 🔴 复杂 | 1-2小时 | **P1** | 🟡 中 | Week 2 Day 1 |
| **baseline** | ❌ 无测试 | 🟡 中 | 30-45分钟 | **P1** | 🟡 中 | Week 2 Day 2 |
| **delta** | ❌ 无测试 | 🟡 中 | 45-60分钟 | **P1** | 🟡 中 | Week 2 Day 2 |
| **audit** | ❌ 无测试 | 🔴 复杂 | 1-2小时 | **P1** | 🟡 中 | Week 2 Day 3 |
| **simulate** | ❌ 无测试 | 🔴 复杂 | 1-2小时 | **P1** | 🟡 中 | Week 2 Day 4 |
| **quality** | ❌ 无测试 | 🔴 复杂 | 1-2小时 | **P1** | 🟡 中 | Week 2 Day 5 |
| **check** | ❌ 无测试 | 🟢 简单 | 20-30分钟 | **P2** | 🟢 低 | Week 3 Day 1 |
| **check-impact** | ❌ 无测试 | 🟡 中 | 45-60分钟 | **P2** | 🟢 低 | Week 3 Day 1 |
| **archive-cieu** | ❌ 无测试 | 🟢 简单 | 20-30分钟 | **P2** | 🟢 低 | Week 3 Day 2 |
| **policy-builder** | ❌ 无测试 | 🟡 中 | 30-45分钟 | **P2** | 🟢 低 | Week 3 Day 2 |
| **demo** | ❌ 无测试 | 🟢 简单 | 15-20分钟 | **P2** | 🟢 低 | Week 3 Day 3 |
| **reset-breaker** | ❌ 无测试 | 🟢 简单 | 10-15分钟 | **P3** | 🟢 低 | Week 4 Day 1 |
| **trend** | ❌ 无测试 | 🟢 简单 | 15-20分钟 | **P3** | 🟢 低 | Week 4 Day 1 |
| **doctor** | ⚠️ 部分测试 | 🔴 复杂 | 1小时 (增强) | **P1** | 🟡 中 | Week 2 Day 1 |
| **verify** | ⚠️ 部分测试 | 🟡 中 | 30分钟 (增强) | **P1** | 🟡 中 | Week 2 Day 2 |
| **seal** | ✅ 有测试 | 🟡 中 | 15分钟 (增强) | **P2** | 🟢 低 | Week 3 Day 2 |
| **report** | ⚠️ 部分测试 | 🔴 复杂 | 45分钟 (增强) | **P1** | 🟡 中 | Week 2 Day 3 |
| **domain list** | ✅ 完整测试 | 🟢 简单 | 0 (已完成) | - | 🟢 低 | ✅ |
| **domain describe** | ✅ 完整测试 | 🟢 简单 | 0 (已完成) | - | 🟢 低 | ✅ |
| **domain init** | ✅ 完整测试 | 🟢 简单 | 0 (已完成) | - | 🟢 低 | ✅ |
| **version** | ✅ 有测试 | 🟢 简单 | 0 (已完成) | - | 🟢 低 | ✅ |

---

## 图例说明

### 测试状态
- ❌ 无测试: 完全没有自动化测试
- ⚠️ 部分测试: 有基础测试但不充分
- ✅ 有测试: 有充分的测试覆盖

### 测试复杂度
- 🟢 简单: 5-30分钟，逻辑简单，少量mock
- 🟡 中等: 30-60分钟，中等逻辑复杂度
- 🔴 复杂: 1-2小时，复杂逻辑，多重依赖

### 风险等级
- 🔴 高: P0命令，用户首次接触，失败影响大
- 🟡 中: P1命令，核心业务逻辑，失败影响中等
- 🟢 低: P2/P3命令，非核心功能，失败影响小

---

## 分阶段执行计划

### Phase 1: 紧急修复 (Week 1) - 1-1.5小时
**目标:** 降低P0风险，确保用户安装流程可测试

| 任务 | 工作量 | 交付物 |
|------|--------|--------|
| test_cli_setup.py | 30-45分钟 | setup命令测试 (4-5个test) |
| test_cli_hook_install.py | 15-20分钟 | hook-install测试 (3个test) |
| CI集成 | 15分钟 | GitHub Actions配置 |

**里程碑:** P0命令有自动化测试，CI集成完成

---

### Phase 2: 核心覆盖 (Week 2) - 5-8小时
**目标:** 覆盖P1核心命令，建立测试基础设施

| 任务 | 工作量 | 交付物 |
|------|--------|--------|
| test_cli_doctor.py (增强) | 1小时 | Layer1/Layer2完整测试 |
| test_cli_baseline_delta.py | 1.5小时 | baseline+delta集成测试 |
| test_cli_audit.py | 1-2小时 | audit完整测试 |
| test_cli_report.py (增强) | 45分钟 | report多格式测试 |
| test_cli_verify_seal.py (增强) | 30分钟 | verify完整测试 |
| test_cli_init.py | 1-2小时 | init + NL翻译测试 |
| test_cli_simulate.py | 1-2小时 | simulate测试 |
| test_cli_quality.py | 1-2小时 | quality测试 |
| conftest.py增强 | 30分钟 | fixtures: sample_agents_md等 |

**里程碑:** 所有P1命令有测试，测试基础设施完善

---

### Phase 3: 全面覆盖 (Week 3) - 3-4.5小时
**目标:** 覆盖P2命令，建立完整测试套件

| 任务 | 工作量 | 交付物 |
|------|--------|--------|
| test_cli_check.py | 20-30分钟 | check命令测试 |
| test_cli_impact.py | 45-60分钟 | check-impact测试 |
| test_cli_archive.py | 20-30分钟 | archive-cieu测试 |
| test_cli_policy_builder.py | 30-45分钟 | policy-builder测试 |
| test_cli_demo.py | 15-20分钟 | demo测试 |
| test_cli_seal.py (增强) | 15分钟 | seal增强测试 |

**里程碑:** 所有P2命令有测试

---

### Phase 4: 完善收尾 (Week 4) - 2-3小时
**目标:** P3命令 + E2E测试 + 覆盖率优化

| 任务 | 工作量 | 交付物 |
|------|--------|--------|
| test_cli_reset_breaker.py | 10-15分钟 | reset-breaker测试 |
| test_cli_trend.py | 15-20分钟 | trend测试 |
| test_cli_e2e.py | 1-1.5小时 | 端到端集成测试 (5-10个场景) |
| 覆盖率优化 | 30-60分钟 | 补充遗漏的错误路径 |
| 文档更新 | 30分钟 | 更新README测试章节 |

**里程碑:** 100%命令覆盖，覆盖率≥80%

---

## 测试文件大小估算

| 测试文件 | 预计测试数 | 预计行数 | 复杂度 |
|---------|-----------|---------|--------|
| test_cli_setup.py | 6-8个 | 150-200 | 🟡 中 |
| test_cli_hook_install.py | 4-5个 | 80-120 | 🟢 简单 |
| test_cli_init.py | 8-10个 | 250-300 | 🔴 复杂 |
| test_cli_baseline_delta.py | 6-8个 | 180-220 | 🟡 中 |
| test_cli_audit.py | 8-10个 | 220-280 | 🔴 复杂 |
| test_cli_doctor.py | 8-12个 | 200-250 | 🔴 复杂 |
| test_cli_simulate.py | 6-8个 | 150-200 | 🔴 复杂 |
| test_cli_quality.py | 6-8个 | 150-200 | 🔴 复杂 |
| test_cli_check.py | 4-5个 | 80-100 | 🟢 简单 |
| test_cli_impact.py | 6-8个 | 150-180 | 🟡 中 |
| test_cli_archive.py | 4-5个 | 80-100 | 🟢 简单 |
| test_cli_demo.py | 4-5个 | 80-100 | 🟢 简单 |
| test_cli_e2e.py | 8-12个 | 300-400 | 🔴 复杂 |
| **总计** | **78-108个** | **2,070-2,650行** | - |

---

## 依赖关系图

```
E2E测试
    ↓
baseline → delta
    ↓
setup → hook-install → doctor
    ↓
audit → seal → verify
    ↓
report
    ↓
simulate → quality
    ↓
check → check-impact
```

**关键依赖:**
- delta依赖baseline
- seal/verify依赖audit
- 所有测试依赖setup生成的配置

---

## 测试覆盖率目标

| 模块 | 当前覆盖率 | 目标覆盖率 | 差距 |
|------|-----------|-----------|------|
| ystar/cli/setup_cmd.py | 未测量 | 85% | - |
| ystar/cli/doctor_cmd.py | ~30% | 80% | +50% |
| ystar/cli/report_cmd.py | ~20% | 80% | +60% |
| ystar/cli/init_cmd.py | 0% | 75% | +75% |
| ystar/cli/quality_cmd.py | 0% | 75% | +75% |
| ystar/cli/domain_cmd.py | ~90% | 90% | 维持 |
| ystar/cli/archive_cmd.py | 0% | 80% | +80% |
| ystar/cli/impact_cmd.py | 0% | 80% | +80% |
| ystar/cli/demo_cmd.py | 0% | 85% | +85% |
| **ystar/cli/ 平均** | **~15%** | **≥80%** | **+65%** |

---

## 风险缓解清单

| 风险 | 缓解措施 | 责任人 | 状态 |
|------|---------|--------|------|
| P0命令无测试 | Week 1完成setup/hook-install测试 | eng-platform | ⏳ 待执行 |
| LLM调用不稳定 | Mock所有anthropic.Client调用 | eng-platform | ⏳ 待执行 |
| 数据库锁冲突 | 每个测试独立tmp_path | eng-platform | ⏳ 待执行 |
| CI运行时间过长 | 并行执行+pytest-xdist | eng-platform | ⏳ 待执行 |
| Windows/Linux差异 | 跨平台测试矩阵 | eng-platform | ⏳ 待执行 |

---

## 成功标准

### Week 1后
- ✅ P0命令有测试 (setup, hook-install)
- ✅ CI集成完成
- ✅ 至少1个P0测试失败被捕获

### Week 2后
- ✅ 所有P1命令有测试
- ✅ 测试覆盖率 ≥50%
- ✅ 至少1个P1回归问题被捕获

### Week 4后
- ✅ 所有18个命令有测试 (100%覆盖)
- ✅ 测试覆盖率 ≥80%
- ✅ CI平均运行时间 <5分钟
- ✅ 0个flaky测试

---

## 快速决策表

**如果只有1周时间:**  
→ 只做Phase 1 (P0命令) + Phase 2部分 (baseline/delta/doctor)

**如果只有2周时间:**  
→ 完成Phase 1 + Phase 2 (所有P1命令)

**如果有4周时间:**  
→ 完成所有Phases (完整覆盖)

**如果资源紧张:**  
→ 优先P0+P1，P2/P3延后或外包

---

**更新频率:** 每周更新一次执行状态  
**负责人:** eng-platform  
**审核:** CTO  
**批准:** CEO
