# ystar-defuse MVP 执行计划

## 架构决策（基于Gemma对话）

### 1. Hook失败模式
- Fail-closed: 任何hook异常都DENY tool call
- 超时阈值: 100ms
- 失败记录到CIEU: event_type='hook_failure' or 'hook_timeout'

### 2. 不可篡改标识符
- session_id = hash(启动时间戳 + 进程PID + 随机salt)
- event_id = sha256(session_id + session_seq + timestamp)
- SQLite UNIQUE约束: (session_id, session_seq)

### 3. 最小规则集算法
- 聚类24小时观察数据（目录前缀、base command）
- 覆盖率阈值: >95%正常行为
- 噪声过滤: <3次出现的行为不生成规则
- 贪心算法最小化规则数

### 4. 权限衰减
- 高频权限: 30天未用→休眠
- 低频权限: 7天未用→休眠
- 休眠后不删除，轻提醒重新激活

### 5. 危险组合检测窗口
- Δt_max = 60秒
- 特殊组合（读密钥→base64）: Δt = 5秒
- 用户输入重置窗口（不跨意图关联）

### 6. 拦截后状态
- 替换tool call为 raise SafetyViolation(reason, cieu_id)
- Session继续运行（不terminate）
- Agent可catch exception并告知用户

---

## 技术栈

- 语言: Python 3.8+
- 存储: SQLite3 (CIEU events + whitelist rules)
- Hook: Claude Code PreToolUse (settings.json配置)
- CLI: argparse
- 测试: pytest
- 打包: setuptools

---

## 目录结构

```
ystar-defuse/
├── src/
│   └── ystar_defuse/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── shield.py          # 主引擎（两层防护协调）
│       │   ├── level1_enforcer.py # 硬底线规则
│       │   ├── level2_learner.py  # 自动学习白名单
│       │   └── cieu_logger.py     # CIEU轻量版
│       ├── rules/
│       │   ├── __init__.py
│       │   ├── sensitive_paths.py # 敏感文件pattern
│       │   ├── dangerous_cmds.py  # 破坏性命令pattern
│       │   └── secret_patterns.py # 密钥/密码pattern
│       ├── analysis/
│       │   ├── __init__.py
│       │   ├── behavior_cluster.py # 行为聚类算法
│       │   └── combo_detector.py   # 危险组合检测
│       ├── hook.py                 # PreToolUse hook入口
│       ├── cli.py                  # CLI入口
│       └── db.py                   # SQLite schema + 操作
├── tests/
│   ├── test_level1.py
│   ├── test_level2.py
│   ├── test_cieu.py
│   ├── test_learning.py
│   ├── test_combo_detection.py
│   └── conftest.py
├── setup.py
├── pyproject.toml
├── README.md
└── LICENSE (MIT)
```

---

## Day 1-2 任务分解

### T1: CIEU SQLite基础 (2h)
- db.py: schema定义
  ```sql
  CREATE TABLE cieu_events (
    id INTEGER PRIMARY KEY,
    event_id TEXT UNIQUE NOT NULL,
    session_id TEXT NOT NULL,
    session_seq INTEGER NOT NULL,
    timestamp REAL NOT NULL,
    event_type TEXT NOT NULL,  -- blocked|allowed|alert|hook_failure
    action_type TEXT NOT NULL, -- read_file|execute|network|output
    target TEXT,               -- 文件路径/域名/命令
    rule_id TEXT,              -- 命中的规则ID
    details TEXT,              -- JSON额外信息
    UNIQUE(session_id, session_seq)
  );
  
  CREATE TABLE whitelist_rules (
    id INTEGER PRIMARY KEY,
    rule_id TEXT UNIQUE NOT NULL,
    rule_type TEXT NOT NULL,   -- path_prefix|command_pattern|domain
    pattern TEXT NOT NULL,
    learned_at REAL NOT NULL,
    last_used REAL,
    use_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active' -- active|dormant
  );
  ```
- cieu_logger.py: 事件写入+查询API

### T2: Level 1硬底线规则 (3h)
- sensitive_paths.py: 敏感文件pattern列表
  ```python
  SENSITIVE_PATTERNS = [
    r'\.env$', r'\.env\..*',
    r'\.ssh/', r'id_rsa', r'authorized_keys',
    r'credentials', r'\.aws/credentials',
    r'\.kube/config', r'\.docker/config\.json'
  ]
  ```
- dangerous_cmds.py: 破坏性命令pattern
  ```python
  DANGEROUS_COMMANDS = [
    r'^rm\s+-rf\s+/',  # rm -rf /
    r'^chmod\s+777',   # chmod 777
    r'>\s*/dev/sda',   # 写硬盘
    r'^dd\s+.*of=/dev' # dd覆盖设备
  ]
  ```
- secret_patterns.py: 密钥输出pattern（用于output遮蔽）
  ```python
  SECRET_PATTERNS = [
    (r'sk-[A-Za-z0-9]{48}', 'OPENAI_API_KEY'),
    (r'ghp_[A-Za-z0-9]{36}', 'GITHUB_TOKEN'),
    (r'xox[baprs]-[A-Za-z0-9-]+', 'SLACK_TOKEN')
  ]
  ```
- level1_enforcer.py: 检查逻辑
  ```python
  def check_file_access(path: str) -> tuple[bool, str | None]:
    # 返回 (is_allowed, violation_reason)
  
  def check_command(cmd: str) -> tuple[bool, str | None]:
    # ...
  
  def check_network(url: str, payload: str) -> tuple[bool, str | None]:
    # 检查域名白名单 + payload中是否有密钥pattern
  
  def sanitize_output(text: str) -> str:
    # 遮蔽密钥pattern
  ```

### T3: PreToolUse Hook集成 (2h)
- hook.py: 主入口
  ```python
  def pre_tool_use(tool_name: str, tool_args: dict) -> dict:
    """
    返回格式:
    {
      "allowed": bool,
      "reason": str,        # 如果blocked
      "modified_args": dict # 如果需要修改参数（如output遮蔽）
    }
    """
    try:
      # 1. 记录session_seq
      # 2. Level 1检查
      # 3. 如果通过，Level 2检查
      # 4. 写CIEU
      # 5. 返回决策
    except Exception as e:
      # Fail-closed
      cieu_logger.log_hook_failure(e)
      return {"allowed": False, "reason": "Hook internal error"}
  ```
- settings.json配置
  ```json
  {
    "hooks": {
      "preToolUse": "python /path/to/ystar-defuse/src/ystar_defuse/hook.py"
    }
  }
  ```

### T4: 基础CLI (1h)
- cli.py: start|stop|report命令
  ```bash
  ystar-defuse start           # 激活hook + 进入学习模式
  ystar-defuse stop            # 停用
  ystar-defuse report          # 查看最近CIEU事件
  ystar-defuse report --stats  # 统计报表
  ```

---

## Day 2-3 任务分解

### T5: 学习模式 (3h)
- level2_learner.py: 观察+聚类
  ```python
  class BehaviorLearner:
    def observe(self, event: CIEUEvent):
      # 24小时内记录所有通过Level 1的行为
    
    def generate_whitelist(self) -> list[WhitelistRule]:
      # 聚类 + 最小规则集算法
      # 返回规则列表
    
    def is_new_behavior(self, action) -> bool:
      # 当前action是否在白名单中
  ```

### T6: 危险组合检测 (2h)
- combo_detector.py: 时间窗口内事件关联
  ```python
  class ComboDetector:
    def __init__(self, window_seconds=60):
      self.window = window_seconds
      self.recent_events = deque()
    
    def check_dangerous_combo(self, new_event) -> list[str]:
      # 返回检测到的危险组合列表
      # 如: ["read_secret + network_request"]
  ```

### T7: 权限衰减 (1h)
- level2_learner.py增强
  ```python
  def decay_permissions():
    # 遍历whitelist_rules
    # 高频规则: >30天未用 → status='dormant'
    # 低频规则: >7天未用 → status='dormant'
  ```

### T8: 轻提醒机制 (2h)
- 新行为触发时，通过CLI交互提示用户
- 或生成待确认队列，下次`ystar-defuse confirm`时批量确认

---

## Day 3-4 任务分解

### T9: pip包打包 (1h)
- setup.py + pyproject.toml
- 入口点: `ystar-defuse` CLI
- 依赖: 只有Python标准库（无外部依赖）

### T10: Claude Code Skill (1h)
- ystar-defuse.skill目录
- skill.json定义
- 安装脚本: `/install ystar-defuse` → 配置settings.json

### T11: 测试 (4h)
- test_level1.py: 20+用例测试硬底线规则
- test_level2.py: 白名单学习+新行为提醒
- test_cieu.py: CIEU记录完整性
- test_learning.py: 最小规则集算法
- test_combo_detection.py: 危险组合检测
- conftest.py: session_id mock + SQLite in-memory

### T12: README (1h)
- 面向非IT用户
- 10秒安装 → 24小时学习 → 1次确认 → 零维护
- 不用术语（如"hook", "CIEU"），用类比（如"shield学习你的agent"）

### T13: 摩擦度验证 (2h)
- 干净机器测试安装
- 非IT用户可用性测试（找Board测试？）
- 卸载残留检查

---

## 总工时估算: 24-28小时

MVP可行，3-4天完成。

---

## 下一步

Layer 4: 开始执行 Day 1-2 任务（T1-T4）
