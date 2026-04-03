# Platform Engineer — 8层架构北极星蓝图专业看法

**工程师:** eng-platform  
**日期:** 2026-04-02  
**负责层:** L5 Runtime Orchestration / L7 Product Value  
**代码审查范围:** adapters/, cli/, products/, _hook_server.py (6896行)

---

## 一、当前状态评估（基于代码事实）

### L5 Runtime Orchestration Layer

**hook.py 现状（674行）:**
- 已经不是"薄adapter"，而是事实上的 runtime ingress controller
- 承担职责：
  1. 身份检测（_detect_agent_id，5个数据源优先级）
  2. 策略路径选择（session有无自动切换enforce/check）
  3. 边界执行（immutable/write_boundary/tool_restriction 三层检查）
  4. Session 派发（从payload/env/file多源加载）
  5. Omission 设置（调用omission_adapter注入事件）
  6. CIEU 写入（7处 _write_cieu 调用）
  7. Orchestrator 喂数据（on_hook_call）

**问题诊断:**
- `_write_cieu()` (行625-646) 用 `except Exception: pass` 静默吞所有CIEU写入失败
- `orchestrator.py` (行100) 初始化失败也用 `except: pass`
- hook.py 是 single point of failure — 任何一层出错都可能破坏整个治理路径
- Windows/bash跨平台问题刚修复（FIX-6/FIX-7），但长期方案未定

**orchestrator.py 现状（384行）:**
- 设计合理：batched invocation降低hook延迟
- 4个子系统wiring：InterventionEngine / GovernanceLoop / PathA / CausalEngine
- fail-safe设计：orchestrator失败不阻塞hook
- 问题：初始化失败静默（行99-100 except: pass）

**omission_adapter.py 现状（302行）:**
- 职责清晰：OpenClaw/Y* event → TrackedEntity + GovernanceEvent
- 支持实时适配和批量回放
- 设计符合分层原则（adapter知道场景，engine保持通用）

### L7 Product Value Layer

**CLI 当前状态（_cli.py 100行 + cli/*.py）:**
- 15个命令已实现（setup/init/doctor/audit/report/verify/seal等）
- **缺口1：** 无 installation baseline 概念 — 用户不知道"治理前后对比"
- **缺口2：** 无 daily delta 自动输出 — 用户需手动运行 `ystar report`
- **缺口3：** 无 trend/maturity/ROI 可视化 — report_render.py 只有markdown/json输出
- **缺口4：** 无 operator/manager/auditor 分角色报告

**report_render.py 现状（200行）:**
- 已拆分完成：governance/report_metrics.py（指标）+ products/report_render.py（渲染）
- 支持 markdown / json / HN summary
- 问题：HN summary 硬编码emoji（行68-73），违反"no emoji unless requested"原则
- 缺少 delta() 实现（声明在docstring行17，但未实现）

---

## 二、专业看法

### 1. hook.py 是否需要拆分？

**判断：需要拆分。**

**建议拆分方案（4个文件）:**

```
ystar/adapters/
  hook.py              ← 保留：格式翻译 + 路径分发（<100行）
  identity_detector.py ← 新建：_detect_agent_id + session加载
  boundary_enforcer.py ← 新建：immutable/write/tool三层检查
  cieu_writer.py       ← 新建：_write_cieu + 错误恢复策略
```

**理由:**
- hook.py 当前674行，违反"薄adapter"原则
- 身份检测、边界检查、CIEU写入是三个独立关注点
- 拆分后每个文件<200行，符合单一职责
- 测试隔离性更好（boundary可以独立mock）

**蓝图修正建议:**
- L5定义改为："runtime_ingress（hook.py）+ identity_service + boundary_enforcer + audit_writer"
- 明确 orchestrator.py 是"subsystem wiring coordinator"，不是执行者

---

### 2. "except Exception: pass" 是否需要改？

**判断：必须改。违反工程纪律。**

**当前问题:**
- hook.py行646：CIEU写入失败静默 → 审计链断裂，用户无感知
- orchestrator.py行100：初始化失败静默 → governance loop永远不运行
- 违反 Proactive Trigger："hook has silent except:pass → replace with logging"

**改成什么:**

```python
# 替换所有 except Exception: pass 为：
except Exception as e:
    _log.error("CIEU write failed: %s (session=%s, tool=%s)", 
               e, session_id, tool_name, exc_info=True)
    # 可选：写入 fallback audit log（.ystar_cieu_errors.jsonl）
    _write_fallback_audit(who, tool_name, params, error=str(e))
```

**工程原则:**
- 失败必须可观测（log.error）
- 审计数据有fallback机制（jsonl备份）
- 让 `ystar doctor` 能检测到"CIEU写入成功率<100%"并告警

---

### 3. L7产品价值层最大的缺口

**P0缺口：Installation Baseline 不存在**

**问题现状:**
- 用户运行 `ystar setup` 后，不知道治理是否生效
- 无法回答："Y*gov changed my system" — 改了什么？怎么验证？
- 缺少"治理前→治理后"对比视图

**解决方案（新命令）:**

```bash
ystar baseline         # 安装后第一次运行，生成baseline快照
ystar delta            # 每天运行，输出与baseline的diff
ystar trend --days 7   # 显示7天趋势（fulfillment_rate/expiry_rate等）
```

**实现路径:**
- baseline: 保存首次 CIEU snapshot（allow_rate, tool_distribution, agent_activity）
- delta: 对比当前 CIEU 与 baseline，输出 +/- 变化表格
- trend: 读取多天 CIEU，生成 ASCII sparkline 或 JSON for 前端

**产品价值:**
- "安装→baseline→delta→trend" 形成完整用户旅程
- 每天自动输出delta → 持续价值感知
- 符合蓝图L7定义："daily delta, trend/maturity/ROI"

---

### 4. 跨平台（Windows bash/cmd）长期方案

**当前状态:**
- FIX-6/FIX-7 修复了MSYS路径转换问题
- 但依赖 bash环境检测（os.environ["MSYSTEM"]）
- hook_install 仍然写入 `.bashrc` — 对cmd/PowerShell用户无效

**长期方案（3个选择）:**

**方案A: Platform-Agnostic Hook Loader（推荐）**
```
ystar hook-install → 生成 .ystar_hook_loader.py
OpenClaw配置改为：preToolUse: "python .ystar_hook_loader.py"
loader自动检测平台，调用对应hook实现
```

**方案B: Native Binary Hook**
```
用Rust编译成 ystar-hook.exe / ystar-hook（无Python依赖）
速度更快，跨平台自然支持
```

**方案C: 保持现状，文档明确bash依赖**
```
README增加："Windows用户需安装Git Bash"
doctor命令检测bash可用性
```

**建议：P2优先级实施方案A。** 理由：
- 不增加新依赖（Python已存在）
- 保持hook.py纯Python可测试性
- 解决cmd/PowerShell用户痛点

---

### 5. 蓝图不合理/需要修正的地方

**问题1: L5定义过于抽象**
- "wire subsystems into the real execution path without becoming the law"
- 实际上hook.py已经在执行law（immutable/boundary检查）
- 建议改为："runtime ingress + execution boundary enforcement + subsystem coordination"

**问题2: L7缺少"baseline"概念**
- 蓝图提到"daily delta"，但delta相对什么？
- 建议明确："installation baseline → daily delta → trend analysis → maturity score"

**问题3: 跨层依赖未定义**
- hook.py（L5）直接调用 CIEUStore（应该是哪层？）
- orchestrator.py（L5）调用 GovernanceLoop（应该是哪层？）
- 建议增加："L5 may call L3 Governance Services via defined interfaces"

---

## 三、优先级排序（P0/P1/P2）

### P0 — 必须立即修复（阻塞用户价值）
1. **除except:pass静默吞错** — FIX-8，预计2小时
   - 替换 hook.py + orchestrator.py 所有静默异常
   - 增加 fallback audit log
   - doctor 命令检测 CIEU 写入成功率

2. **实现 ystar baseline/delta** — 新特性，预计4小时
   - baseline: 保存首次快照到 .ystar_baseline.json
   - delta: 输出与baseline对比表格
   - 让"Y*gov changed my system"可验证

### P1 — 重要但不紧急（改善体验）
3. **hook.py 拆分** — 重构，预计6小时
   - 拆成 hook/identity/boundary/cieu_writer 4个文件
   - 保持向后兼容
   - 增加单元测试覆盖每个模块

4. **report_render delta() 实现** — 预计2小时
   - 实现docstring承诺的delta()方法
   - 输出"Baseline vs Current"对比表格

### P2 — 可以延后（优化改善）
5. **跨平台hook loader** — 新架构，预计8小时
   - 实施方案A（Platform-Agnostic Hook Loader）
   - 替换当前 .bashrc hook

6. **分角色报告** — 新特性，预计4小时
   - operator report: 关注daily delta + alerts
   - manager report: 关注team fulfillment_rate + trends
   - auditor report: 关注CIEU integrity + violations

---

## 四、立即执行决定

基于Constitutional Thinking Discipline：

**系统性问题发现:**
- 静默异常模式在adapters/遍布，不止hook.py
- 用户无法验证"治理是否生效"（缺baseline）
- 蓝图L5定义与实际代码职责不匹配

**谁应该早发现:**
- 代码审查应该拦截 except:pass（需要pre-commit hook）
- QA应该测试"CIEU写入失败场景"（缺失）
- 文档应该明确"安装后如何验证"（README未提及）

**预防措施（立即行动）:**
1. 创建 FIX-8 issue：清除所有静默异常
2. 增加 pytest fixture：mock CIEU写入失败，验证降级行为
3. 更新 README：增加"Verify Installation"章节（运行baseline）

**我现在开始执行 P0-1（FIX-8）。**

---

## 附录：关键文件路径

- C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/adapters/hook.py (674行)
- C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/adapters/orchestrator.py (384行)
- C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/adapters/omission_adapter.py (302行)
- C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/_cli.py (100行)
- C:/Users/liuha/OneDrive/桌面/Y-star-gov/ystar/products/report_render.py (200行)
- C:/Users/liuha/OneDrive/桌面/Y-star-gov/tests/test_hook.py (待创建)
- C:/Users/liuha/OneDrive/桌面/Y-star-gov/tests/test_orchestrator.py (待创建)

**Platform Engineer报告完成。等待董事长审阅。**
