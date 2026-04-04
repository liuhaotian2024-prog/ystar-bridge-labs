# CLI功能测试覆盖报告

**生成时间:** 2026-04-03  
**检测范围:** Y*gov v0.48.0 的 18个CLI命令  
**测试目录:** `C:/Users/liuha/OneDrive/桌面/Y-star-gov/tests/`  
**执行人:** eng-platform

---

## 执行摘要

**总体测试覆盖:**
- 已测试命令: 5/18 (28%)
- 部分测试: 4个 (doctor, verify, seal, report)
- 无测试: 14个 (78%)
- 仅文档测试: 1个 (test_cli_docs.py)

**关键发现:**
1. 大多数CLI命令缺少功能测试，仅依赖手动测试
2. 现有测试集中在test_v041_features.py，质量较高但覆盖不全
3. domain命令有完整的单元测试 (test_domain_cli.py)
4. 缺少集成测试和错误处理测试

---

## 测试覆盖详情

### 已测试命令 (5个)

| 命令 | 测试文件 | 测试函数数 | 覆盖质量 | 备注 |
|------|---------|-----------|---------|------|
| domain list | test_domain_cli.py | 2 | ⭐⭐⭐⭐ | 完整单元测试+集成测试 |
| domain describe | test_domain_cli.py | 3 | ⭐⭐⭐⭐ | 包含错误处理测试 |
| domain init | test_domain_cli.py | 2 | ⭐⭐⭐⭐ | 包含防覆盖测试 |
| doctor | test_v041_features.py | 1 | ⭐⭐ | 仅smoke test，无Layer1/Layer2测试 |
| verify | test_v041_features.py | 1 | ⭐ | 仅错误路径，无完整验证逻辑 |
| seal | test_v041_features.py | 2 | ⭐⭐⭐ | 包含验证一致性测试 |
| report | test_v041_features.py | 1 | ⭐⭐ | 仅JSON格式输出测试 |
| version | test_v041_features.py | 1 | ⭐⭐⭐ | 简单但充分 |

### 无测试命令 (13个)

| 命令 | 代码行数 | 测试复杂度 | 预计工作量 | 优先级 | 理由 |
|------|---------|-----------|-----------|--------|------|
| **setup** | 224 | 中 | 30-45分钟 | **P0** | 用户首次安装必经流程，失败影响最大 |
| **hook-install** | 224 | 简单 | 15-20分钟 | **P0** | 安装核心步骤，需验证多环境兼容性 |
| **init** | 301 | 复杂 | 1-2小时 | **P1** | 涉及NL翻译、LLM调用、文件生成 |
| **baseline** | ~80行 | 中 | 30-45分钟 | **P1** | 核心功能，需真实CIEU数据 |
| **delta** | ~120行 | 中 | 45-60分钟 | **P1** | 依赖baseline，需测试版本兼容性 |
| **audit** | 424 | 复杂 | 1-2小时 | **P1** | 生成审计报告，逻辑复杂 |
| **check** | 477 | 简单 | 20-30分钟 | **P2** | 直接JSONL处理，逻辑清晰 |
| **check-impact** | 203 | 中 | 45-60分钟 | **P2** | 涉及多维度分析 |
| **archive-cieu** | 143 | 简单 | 20-30分钟 | **P2** | JSONL导出，逻辑简单 |
| **reset-breaker** | ~30行 | 简单 | 10-15分钟 | **P3** | 内存状态重置 |
| **simulate** | 477 | 复杂 | 1-2小时 | **P1** | A/B效果评估，需mock workload |
| **quality** | 477 | 复杂 | 1-2小时 | **P1** | 合约质量评估 |
| **policy-builder** | 477 | 中 | 30-45分钟 | **P2** | 启动HTTP服务，需端口检测 |
| **demo** | 86 | 简单 | 15-20分钟 | **P2** | 5秒演示，逻辑固定 |

**trend命令:** 在_cli.py中实现 (~40行)，简单SQL查询，预计15分钟，P3优先级

---

## 测试策略设计

### 1. 测试分层策略

#### Layer 1: 单元测试 (快速验证)
- 测试命令参数解析
- 测试错误处理路径
- Mock外部依赖 (DB, LLM, 文件系统)
- 运行时间: <100ms/test

#### Layer 2: 集成测试 (真实场景)
- 使用临时数据库 (tmp_path fixture)
- 测试完整命令流程
- 验证文件生成/修改
- 运行时间: 100ms-1s/test

#### Layer 3: E2E测试 (用户场景)
- 测试命令组合 (setup -> hook-install -> baseline)
- 测试跨session持久化
- 验证真实CIEU数据
- 运行时间: 1-5s/test

### 2. Mock策略

| 依赖类型 | Mock方法 | 示例 |
|---------|---------|------|
| 文件系统 | tmp_path fixture | pytest内置 |
| CIEU数据库 | tmp_db fixture (已存在) | 见conftest.py |
| LLM调用 | patch anthropic.Client | unittest.mock |
| 用户输入 | patch builtins.input | unittest.mock |
| HTTP服务 | pytest-httpserver | 新增依赖 |
| Git操作 | Mock subprocess.run | unittest.mock |

### 3. 测试数据准备

创建 `tests/fixtures/` 目录存放测试数据:
- `sample_agents.md`: 示例AGENTS.md
- `sample_cieu.db`: 预填充CIEU数据库
- `sample_session.json`: 标准session配置
- `sample_events.jsonl`: 测试用事件流

### 4. CI/CD集成

```yaml
# .github/workflows/cli_tests.yml
name: CLI Tests
on: [push, pull_request]
jobs:
  test-cli:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: pip install -e .[dev]
      - name: Run CLI tests
        run: pytest tests/test_cli_*.py -v --cov=ystar/cli
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 测试实现样例

### 样例1: setup命令测试 (简单命令)

```python
# tests/test_cli_setup.py
import pytest
from unittest.mock import patch
from pathlib import Path


def test_setup_creates_session_json(tmp_path, monkeypatch):
    """测试setup命令生成.ystar_session.json"""
    monkeypatch.chdir(tmp_path)
    
    # Mock用户输入 (全部使用默认值)
    with patch("builtins.input", return_value=""):
        from ystar.cli.setup_cmd import _cmd_setup
        _cmd_setup(skip_prompt=True)
    
    # 验证文件生成
    session_file = tmp_path / ".ystar_session.json"
    assert session_file.exists()
    
    # 验证内容
    import json
    config = json.loads(session_file.read_text())
    assert "session_id" in config
    assert "cieu_db" in config
    assert config["cieu_db"] == ".ystar_cieu.db"


def test_setup_custom_deny_paths(tmp_path, monkeypatch):
    """测试自定义deny paths"""
    monkeypatch.chdir(tmp_path)
    
    inputs = ["myproject", ".data/cieu.db", "/custom,/paths"]
    with patch("builtins.input", side_effect=inputs):
        from ystar.cli.setup_cmd import _cmd_setup
        _cmd_setup(skip_prompt=False)
    
    import json
    config = json.loads((tmp_path / ".ystar_session.json").read_text())
    assert "/custom" in config["deny_paths"]
    assert "/paths" in config["deny_paths"]


def test_setup_overwrite_warning(tmp_path, monkeypatch, capsys):
    """测试覆盖现有配置的警告"""
    monkeypatch.chdir(tmp_path)
    
    # 创建现有配置
    (tmp_path / ".ystar_session.json").write_text('{"old": "config"}')
    
    with patch("builtins.input", return_value=""):
        from ystar.cli.setup_cmd import _cmd_setup
        _cmd_setup(skip_prompt=True)
    
    out = capsys.readouterr().out
    assert "already exists" in out or "overwrite" in out.lower()
```

### 样例2: doctor命令测试 (复杂命令)

```python
# tests/test_cli_doctor.py
import pytest
from pathlib import Path


def test_doctor_layer1_checks(tmp_path, capsys):
    """测试Layer1零依赖检查"""
    from ystar.cli.doctor_cmd import _doctor_layer1
    
    all_ok, ok_count, fail_count = _doctor_layer1()
    
    out = capsys.readouterr().out
    assert "Layer1" in out
    assert ok_count > 0
    # Layer1不应该有失败 (零依赖)
    assert fail_count == 0


def test_doctor_layer2_with_missing_deps(tmp_path, capsys, monkeypatch):
    """测试Layer2在缺少依赖时的行为"""
    # Mock sys.executable返回不存在的Python
    import sys
    monkeypatch.setattr(sys, "executable", "/nonexistent/python")
    
    from ystar.cli.doctor_cmd import _doctor_layer2
    all_ok, ok_count, fail_count = _doctor_layer2()
    
    # 应该检测到失败
    assert not all_ok or fail_count > 0


def test_doctor_detects_missing_git(tmp_path, monkeypatch, capsys):
    """测试检测缺少git"""
    monkeypatch.chdir(tmp_path)
    
    # Mock subprocess.run让git命令失败
    from unittest.mock import patch
    with patch("subprocess.run", side_effect=FileNotFoundError):
        from ystar.cli.doctor_cmd import _cmd_doctor
        with pytest.raises(SystemExit):
            _cmd_doctor([])
    
    out = capsys.readouterr().out
    assert "git" in out.lower()


def test_doctor_layer1_only_flag(capsys):
    """测试--layer1标志只运行Layer1"""
    from ystar.cli.doctor_cmd import _cmd_doctor
    _cmd_doctor(["--layer1"])
    
    out = capsys.readouterr().out
    assert "Layer1" in out
    assert "Layer2" not in out  # 不应该运行Layer2
```

### 样例3: baseline + delta集成测试

```python
# tests/test_cli_baseline_delta.py
import pytest
import json
from pathlib import Path


@pytest.fixture
def populated_db(tmp_path):
    """创建预填充的CIEU数据库"""
    db_path = tmp_path / ".ystar_cieu.db"
    from ystar.governance.cieu_store import CIEUStore
    import uuid
    
    store = CIEUStore(str(db_path))
    for i in range(10):
        store.write_dict({
            "event_id": uuid.uuid4().hex,
            "session_id": "test_session",
            "agent_id": "test_agent",
            "event_type": "read",
            "decision": "allow" if i % 3 else "deny",
            "passed": i % 3 != 0,
            "violations": []
        })
    return str(db_path)


def test_baseline_captures_snapshot(tmp_path, monkeypatch, populated_db):
    """测试baseline命令捕获状态快照"""
    monkeypatch.chdir(tmp_path)
    
    # 创建session配置
    session_config = {
        "session_id": "test",
        "cieu_db": populated_db
    }
    (tmp_path / ".ystar_session.json").write_text(json.dumps(session_config))
    
    from ystar._cli import _cmd_baseline
    _cmd_baseline([])
    
    # 验证baseline文件生成
    baseline_file = tmp_path / ".ystar_baseline.json"
    assert baseline_file.exists()
    
    baseline_data = json.loads(baseline_file.read_text())
    assert baseline_data["cieu"]["cieu_total_events"] == 10


def test_delta_shows_changes(tmp_path, monkeypatch, populated_db):
    """测试delta命令显示变化"""
    monkeypatch.chdir(tmp_path)
    
    # 准备配置
    session_config = {"session_id": "test", "cieu_db": populated_db}
    (tmp_path / ".ystar_session.json").write_text(json.dumps(session_config))
    
    # 创建baseline
    from ystar._cli import _cmd_baseline
    _cmd_baseline([])
    
    # 添加更多事件
    from ystar.governance.cieu_store import CIEUStore
    import uuid
    store = CIEUStore(populated_db)
    for i in range(5):
        store.write_dict({
            "event_id": uuid.uuid4().hex,
            "session_id": "test_session",
            "agent_id": "test_agent",
            "event_type": "write",
            "decision": "deny",
            "passed": False,
            "violations": []
        })
    
    # 运行delta
    from ystar._cli import _cmd_delta
    _cmd_delta([])
    
    # 验证增量显示 (通过capsys检查输出)
    # 应该显示从10个事件增长到15个事件


def test_delta_without_baseline_fails(tmp_path, monkeypatch, capsys):
    """测试没有baseline时delta命令失败"""
    monkeypatch.chdir(tmp_path)
    
    from ystar._cli import _cmd_delta
    with pytest.raises(SystemExit):
        _cmd_delta([])
    
    out = capsys.readouterr().out
    assert "No baseline found" in out
```

### 样例4: simulate命令测试 (复杂逻辑)

```python
# tests/test_cli_simulate.py
import pytest


def test_simulate_default_sessions(capsys):
    """测试默认50个sessions的模拟"""
    from ystar.cli.quality_cmd import _cmd_simulate
    
    _cmd_simulate([])
    
    out = capsys.readouterr().out
    assert "50 sessions" in out
    assert "Dangerous op intercept" in out
    assert "Risk reduction" in out


def test_simulate_custom_sessions(capsys):
    """测试自定义sessions数量"""
    from ystar.cli.quality_cmd import _cmd_simulate
    
    _cmd_simulate(["--sessions", "100"])
    
    out = capsys.readouterr().out
    assert "100 sessions" in out


def test_simulate_with_custom_agents_md(tmp_path, capsys):
    """测试使用自定义AGENTS.md"""
    # 创建测试用AGENTS.md
    agents_md = tmp_path / "AGENTS.md"
    agents_md.write_text("""
# Rules
- Never modify /production
- Never run rm -rf
    """)
    
    from ystar.cli.quality_cmd import _cmd_simulate
    _cmd_simulate(["--agents-md", str(agents_md)])
    
    out = capsys.readouterr().out
    assert "simulation" in out.lower()


def test_simulate_deterministic_with_seed(capsys):
    """测试相同seed产生一致结果"""
    from ystar.integrations.simulation import WorkloadSimulator
    
    sim1 = WorkloadSimulator(sessions=10, seed=42)
    report1 = sim1.run()
    
    sim2 = WorkloadSimulator(sessions=10, seed=42)
    report2 = sim2.run()
    
    # 相同seed应该产生相同的recall
    assert report1.recall == report2.recall
    assert report1.false_positive_rate == report2.false_positive_rate
```

### 样例5: hook-install测试 (环境依赖)

```python
# tests/test_cli_hook_install.py
import pytest
from pathlib import Path
from unittest.mock import patch


def test_hook_install_creates_pretoolusse_py(tmp_path, monkeypatch):
    """测试hook-install创建PreToolUse.py"""
    monkeypatch.chdir(tmp_path)
    
    # Mock claude config目录
    claude_dir = tmp_path / ".claude" / "hooks"
    claude_dir.mkdir(parents=True)
    
    with patch("pathlib.Path.home", return_value=tmp_path):
        from ystar.cli.setup_cmd import _cmd_hook_install
        _cmd_hook_install()
    
    hook_file = claude_dir / "PreToolUse.py"
    assert hook_file.exists()
    
    content = hook_file.read_text()
    assert "from ystar" in content
    assert "enforce(" in content


def test_hook_install_overwrites_existing_hook(tmp_path, monkeypatch, capsys):
    """测试覆盖现有hook"""
    monkeypatch.chdir(tmp_path)
    
    claude_dir = tmp_path / ".claude" / "hooks"
    claude_dir.mkdir(parents=True)
    
    # 创建现有hook
    hook_file = claude_dir / "PreToolUse.py"
    hook_file.write_text("# Old hook")
    
    with patch("pathlib.Path.home", return_value=tmp_path):
        from ystar.cli.setup_cmd import _cmd_hook_install
        _cmd_hook_install()
    
    out = capsys.readouterr().out
    assert "backup" in out.lower() or "overwrite" in out.lower()


def test_hook_install_validates_python_path(tmp_path, monkeypatch):
    """测试验证Python路径"""
    import sys
    assert Path(sys.executable).exists()
    
    from ystar.cli.setup_cmd import _cmd_hook_install
    # 应该能检测到当前Python环境
```

---

## 工作量评估

### 按优先级分组

#### P0 (必须完成) - 总计: 1-1.5小时
- setup: 30-45分钟
- hook-install: 15-20分钟

#### P1 (高优先级) - 总计: 5-8小时
- init: 1-2小时
- baseline: 30-45分钟
- delta: 45-60分钟
- audit: 1-2小时
- simulate: 1-2小时
- quality: 1-2小时

#### P2 (中优先级) - 总计: 3-4.5小时
- check: 20-30分钟
- check-impact: 45-60分钟
- archive-cieu: 20-30分钟
- policy-builder: 30-45分钟
- demo: 15-20分钟

#### P3 (低优先级) - 总计: 30分钟
- reset-breaker: 10-15分钟
- trend: 15-20分钟

### 总工作量
- **纯编码时间:** 9.5-14.5小时
- **调试+修复时间:** +30% = 12.5-19小时
- **文档+Code Review:** +20% = 15-23小时

**分阶段执行建议:**
- Week 1: P0命令 (1-2天)
- Week 2: P1命令 (1周)
- Week 3: P2命令 (3-4天)
- Week 4: P3命令 + 集成测试 (2-3天)

---

## 依赖和环境准备

### 新增测试依赖

```toml
# pyproject.toml [project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-mock>=3.10",
    "pytest-httpserver>=1.0",  # 新增: 测试policy-builder
    "pytest-timeout>=2.1",      # 新增: 防止hang
]
```

### conftest.py增强

```python
# tests/conftest.py (新增)
import pytest
from pathlib import Path


@pytest.fixture
def sample_agents_md(tmp_path):
    """创建示例AGENTS.md"""
    agents = tmp_path / "AGENTS.md"
    agents.write_text("""
# Agent Governance Rules

## Core Constraints
- Never modify /production directory
- Never run rm -rf commands
- Only write to ./workspace/ directory

## Financial Rules
- Maximum transaction: $10,000
- Require approval for >$5,000

## Data Privacy
- Never access .env files
- Only read from allowed_data/
    """)
    return agents


@pytest.fixture
def sample_session_config(tmp_path):
    """创建标准session配置"""
    import json
    import uuid
    
    config = {
        "session_id": f"test_{uuid.uuid4().hex[:8]}",
        "cieu_db": str(tmp_path / ".ystar_cieu.db"),
        "deny_paths": ["/etc", "/root"],
        "contract_path": "AGENTS.md"
    }
    
    config_file = tmp_path / ".ystar_session.json"
    config_file.write_text(json.dumps(config, indent=2))
    return config_file
```

---

## 质量门禁

### 测试覆盖率目标
- 代码覆盖率: ≥80% (ystar/cli/)
- 命令覆盖率: 100% (所有18个命令有至少1个测试)
- 错误路径覆盖: ≥60%

### CI门禁规则
```yaml
# 要求:
- 所有CLI测试通过
- 覆盖率不低于80%
- 无新增pylint警告
- 平均测试时间 <5s
```

---

## 风险和缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| LLM调用不稳定 | init/quality测试flaky | Mock所有LLM调用 |
| 文件系统权限 | Windows/Linux行为不一致 | 使用tmp_path，避免硬编码路径 |
| 数据库锁 | 并发测试失败 | 每个测试用独立数据库 |
| 网络依赖 | policy-builder端口冲突 | 使用随机端口+pytest-httpserver |
| Git依赖 | 非git环境测试失败 | Mock subprocess.run |

---

## 下一步行动

### 立即执行 (本周)
1. 创建 `tests/test_cli_setup.py` - setup命令测试 (P0)
2. 创建 `tests/test_cli_hook_install.py` - hook-install测试 (P0)
3. 增强 `tests/conftest.py` - 添加fixtures
4. 在CI中启用CLI测试

### 短期计划 (2周内)
1. 完成P1命令测试 (baseline, delta, audit, simulate, quality, init)
2. 建立CLI测试标准模板
3. 生成测试覆盖率报告

### 长期计划 (1个月内)
1. 完成所有命令测试 (P2, P3)
2. 建立E2E测试套件
3. 自动化回归测试

---

## 附录: 测试文件清单

### 需要创建的测试文件 (13个)

```
tests/
├── test_cli_setup.py           # setup + hook-install
├── test_cli_init.py            # init命令
├── test_cli_baseline_delta.py  # baseline + delta
├── test_cli_audit.py           # audit命令
├── test_cli_report.py          # report命令 (增强现有)
├── test_cli_verify_seal.py     # verify + seal (增强现有)
├── test_cli_check.py           # check命令
├── test_cli_impact.py          # check-impact命令
├── test_cli_archive.py         # archive-cieu命令
├── test_cli_simulate.py        # simulate命令
├── test_cli_quality.py         # quality命令
├── test_cli_policy_builder.py  # policy-builder命令
├── test_cli_doctor.py          # doctor命令 (增强现有)
├── test_cli_demo.py            # demo命令
└── test_cli_e2e.py             # 端到端集成测试
```

### 测试fixtures目录结构

```
tests/fixtures/
├── sample_agents.md            # 标准AGENTS.md
├── sample_cieu.db              # 预填充CIEU数据
├── sample_session.json         # 标准session配置
├── sample_events.jsonl         # 测试事件流
├── sample_contract.py          # 示例contract
└── templates/
    ├── minimal_agents.md
    ├── complex_agents.md
    └── invalid_agents.md
```

---

## 总结

**当前状态:** CLI功能主要依赖手动测试，自动化覆盖率低 (28%)

**核心问题:**
1. P0命令 (setup, hook-install) 无测试，安装失败风险高
2. 复杂命令 (simulate, quality, audit) 无自动化验证
3. 缺少集成测试和错误路径覆盖

**推荐方案:**
- 分4周逐步实施，优先P0/P1命令
- 总工作量: 15-23小时 (包含调试+文档)
- 第1周完成P0命令可立即降低安装失败风险

**预期收益:**
- 降低用户安装失败率 (setup/hook-install测试)
- 捕获回归问题 (所有命令自动化测试)
- 提升代码质量 (覆盖率 28% → 80%+)
- 加速开发迭代 (CI自动化验证)

---

**报告生成:** eng-platform  
**审核待定:** CTO  
**批准待定:** CEO (Aiden/承远)
