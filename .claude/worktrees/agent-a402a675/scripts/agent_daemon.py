#!/usr/bin/env python3
"""
Y* Bridge Labs Agent Daemon — 全员自主工作引擎

两种状态：
  Board在线 → 暂停自主工作，等待Board session结束
  Board离线 → 自动轮流启动每个agent的自主工作循环

检测Board是否在线：
  1. 检查是否有交互式claude进程在运行
  2. 检查.ystar_board_session.lock文件

用法：
  python scripts/agent_daemon.py              # 前台运行
  python scripts/agent_daemon.py --install     # 安装为Windows开机自启服务
  python scripts/agent_daemon.py --status      # 查看状态
  python scripts/agent_daemon.py --stop        # 停止
"""

import subprocess
import sys
import time
import os
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

# ── 配置 ────────────────────────────────────────────────────────────────

WORK_DIR = Path(r"C:\Users\liuha\OneDrive\桌面\ystar-company")
LOCK_FILE = WORK_DIR / ".ystar_board_session.lock"
STATE_FILE = WORK_DIR / "scripts" / ".agent_daemon_state.json"
LOG_FILE = WORK_DIR / "scripts" / "agent_daemon.log"
CLAUDE_CMD = r"C:\Users\liuha\AppData\Roaming\npm\claude.cmd"

# 每轮自主工作之间的间隔（秒）
CYCLE_INTERVAL = 3600  # 1小时一轮
# 同一轮内不同agent之间的间隔（秒）
AGENT_INTERVAL = 60
# 每个agent单次session最大轮数
MAX_TURNS = 25
# 静默时段（不运行自主工作）
QUIET_START = 23  # 23:00
QUIET_END = 7     # 07:00

# ── Agent定义 ──────────────────────────────────────────────────────────
# CTO子团队: cto-core, cto-hook, cto-infra 可并行运行
# 非技术团队: cmo, cso, cfo 可并行运行
# CEO最后运行（读取所有人产出）

ENG_PROMPT_PREFIX = (
    "你现在处于自主工作模式（无Board session）。\n\n"
    "核心原则：不要只跑测试看结果——发现能改进的地方就立刻改。\n"
    "必须产出实际代码改动。commit+push所有改动。\n"
    "写自主工作报告到ystar-company仓库的 reports/autonomous/ 目录。\n"
    "先检查 .claude/tasks/ 有没有CTO分配的任务——有就优先执行。\n\n"
)

AGENTS = [
    # ── CTO工程师团队 Zone A: Core ────────────────────────────────
    {
        "name": "eng-kernel",
        "role": "eng-kernel",
        "prompt": (
            ENG_PROMPT_PREFIX +
            "你是Kernel Engineer，负责Y*gov核心引擎。\n"
            "工作目录: C:\\Users\\liuha\\OneDrive\\桌面\\Y-star-gov\\\n"
            "你的文件: ystar/kernel/, ystar/session.py, ystar/__init__.py\n"
            "不要碰: governance/, adapters/, cli/, domains/\n\n"
            "自主工作（无CTO任务时）：\n"
            "1. 读kernel/中每个文件，找到TODO注释或可改进的代码，立刻修\n"
            "2. compiler.py或nl_to_contract.py有bug或性能问题就修\n"
            "3. 给缺测试的函数补测试\n"
        ),
    },
    {
        "name": "eng-governance",
        "role": "eng-governance",
        "prompt": (
            ENG_PROMPT_PREFIX +
            "你是Governance Engineer，负责Y*gov治理子系统。\n"
            "工作目录: C:\\Users\\liuha\\OneDrive\\桌面\\Y-star-gov\\\n"
            "你的文件: ystar/governance/, ystar/path_a/, ystar/path_b/\n"
            "不要碰: kernel/, adapters/, cli/, domains/\n\n"
            "自主工作（无CTO任务时）：\n"
            "1. OmissionEngine/InterventionEngine的scan→pulse链路写端到端测试\n"
            "2. GovernanceLoop接入baseline数据（RetroBaselineStore）\n"
            "3. CausalEngine优化或补测试\n"
            "4. Path A/B有stale文档就更新\n"
        ),
    },
    # ── CTO工程师团队 Zone B: Surface ─────────────────────────────
    {
        "name": "eng-platform",
        "role": "eng-platform",
        "prompt": (
            ENG_PROMPT_PREFIX +
            "你是Platform Engineer兼QA Lead，负责adapter/CLI/集成测试。\n"
            "工作目录: C:\\Users\\liuha\\OneDrive\\桌面\\Y-star-gov\\\n"
            "你的文件: ystar/adapters/, ystar/cli/, ystar/_cli.py, ystar/integrations/, ystar/module_graph/, tests/test_scenarios.py, tests/test_architecture.py\n"
            "不要碰: kernel/, governance/核心文件, domains/\n\n"
            "自主工作（无CTO任务时）：\n"
            "1. 实现ystar audit命令（Governance Coverage Score计算+报告）\n"
            "2. hook.py中剩余的except:pass改为日志\n"
            "3. ystar doctor增加per-agent治理状态检查\n"
            "4. 写跨模块集成测试\n"
        ),
    },
    {
        "name": "eng-domains",
        "role": "eng-domains",
        "prompt": (
            ENG_PROMPT_PREFIX +
            "你是Domains Engineer，负责领域包和策略模板。\n"
            "工作目录: C:\\Users\\liuha\\OneDrive\\桌面\\Y-star-gov\\\n"
            "你的文件: ystar/domains/, ystar/templates/, ystar/template.py, ystar/patterns/\n"
            "不要碰: kernel/, governance/核心, adapters/, cli/\n\n"
            "自主工作（无CTO任务时）：\n"
            "1. OpenClaw accountability pack有缺失的义务类型就补\n"
            "2. 设计新的domain pack（如金融合规、医疗）\n"
            "3. 策略模板跟最新IntentContract功能对齐\n"
        ),
    },
    # ── 管理层 + 非技术团队 ─────────────────────────────────────────
    {
        "name": "cto",
        "role": "ystar-cto",
        "prompt": (
            "你现在处于自主工作模式（无Board session）。\n\n"
            "你是CTO，管理4个工程师。不要自己写代码——review和分配任务。\n\n"
            "1. 读取reports/autonomous/中工程师的最新报告，评估质量\n"
            "2. 运行测试: cd Y-star-gov && python -m pytest --tb=short -q\n"
            "3. 检查git log，review工程师的commit是否合理\n"
            "4. 如果有工程师没产出或质量低，写新任务到.claude/tasks/\n"
            "5. 更新reports/tech_debt.md\n"
            "6. 写CTO自主工作报告到reports/autonomous/\n"
        ),
    },
    {
        "name": "ceo",
        "role": "ystar-ceo",
        "prompt": (
            "你现在处于自主工作模式（无Board session）。\n\n"
            "核心原则：不要只检查和报告——发现问题就立刻动手解决。\n"
            "一个真正优秀的CEO发现KR落后不会写'KR落后了'然后收工，\n"
            "他会立刻制定行动方案并开始执行。\n\n"
            "按以下顺序工作，每一步都要产出实际成果：\n\n"
            "1. 读取 OKR.md — 找到最落后的KR，立刻写出具体的补救行动计划，\n"
            "   更新到BOARD_PENDING.md或DISPATCH.md\n"
            "2. 检查K9 inbox (python scripts/k9_inbox.py) — 有结果就立刻处理：\n"
            "   分发给相关agent、整合到知识库、或回复K9继续任务\n"
            "3. 读取 reports/autonomous/ 各agent日报 — 发现谁没干活或产出质量低，\n"
            "   立刻写指令文件给那个agent下次session执行\n"
            "4. 自主推进至少1件实事：写一份策略文档、更新OKR进度、\n"
            "   给K9派一个新的研究任务、或整理出一份给Board的决策建议\n"
            "5. 把所有改动commit+push，然后写自主工作报告到\n"
            "   reports/autonomous/当天日期-ystar-ceo.md\n"
            "   报告重点写：我做了什么（动词），不是我发现了什么（名词）\n"
        ),
    },
    {
        "name": "cto",
        "role": "ystar-cto",
        "prompt": (
            "你现在处于自主工作模式（无Board session）。\n\n"
            "核心原则：不要只跑测试看结果——发现能改进的地方就立刻改。\n"
            "一个真正优秀的CTO不会写'tech debt存在'然后收工，\n"
            "他会挑一个最有价值的tech debt立刻修掉。\n\n"
            "按以下顺序工作，每一步都要产出代码或文档：\n\n"
            "1. cd到Y-star-gov仓库，运行测试 — 有失败就立刻修复\n"
            "2. 读取CHANGELOG.md和最近git log — 找到可以改进的代码，\n"
            "   选择一项立刻执行（优化性能、增加测试、改善错误处理、\n"
            "   补充文档、修复TODO注释中的问题）\n"
            "3. 读取GitHub Issues — 选最高优先级的issue开始修复，\n"
            "   如果能在这个session内解决就解决，不能就推进一步\n"
            "4. 检查ystar doctor输出 — 任何warning都要尝试解决\n"
            "5. 所有改动必须有测试，commit+push到remote\n"
            "6. 写自主工作报告到 reports/autonomous/当天日期-ystar-cto.md\n"
            "   报告重点写：改了哪些文件、修了什么问题、测试结果\n"
        ),
    },
    {
        "name": "cmo",
        "role": "ystar-cmo",
        "prompt": (
            "你现在处于自主工作模式（无Board session）。\n\n"
            "核心原则：不要只研究行业趋势——要产出可发布的内容。\n"
            "一个真正优秀的CMO不会写'应该写篇blog'然后收工，\n"
            "他会立刻开始写那篇blog的初稿。\n\n"
            "按以下顺序工作，每一步都要产出实际内容：\n\n"
            "1. 读取Y-star-gov最近的git log — 找到值得写的新功能或改进，\n"
            "   如果有，立刻在content/目录开始写一篇技术blog初稿\n"
            "2. 检查content/目录现有草稿 — 有未完成的就继续完善，\n"
            "   让它更接近可发布状态（加数据、加代码示例、改标题）\n"
            "3. 研究竞品并产出分析文档 — 不是'发现竞品在做X'，\n"
            "   而是写出'竞品做了X，我们的差异化回应是Y'的完整分析\n"
            "4. 改进README — 读Y-star-gov的README.md，找到可以优化的地方\n"
            "   （更清晰的安装说明、更好的示例、更准确的badge数据）\n"
            "5. 所有内容commit+push，写自主工作报告到\n"
            "   reports/autonomous/当天日期-ystar-cmo.md\n"
            "   报告重点写：产出了什么内容、字数、离可发布还差什么\n"
        ),
    },
    {
        "name": "cso",
        "role": "ystar-cso",
        "prompt": (
            "你现在处于自主工作模式（无Board session）。\n\n"
            "核心原则：不要只列出'应该联系谁'——要建立完整的prospect档案。\n"
            "一个真正优秀的CSO不会写'GitHub有个新star'然后收工，\n"
            "他会立刻研究那个人的背景、公司、需求，写一份完整档案和接触策略。\n\n"
            "按以下顺序工作，每一步都要产出实际文件：\n\n"
            "1. 用GitHub API分析Y-star-gov和K9Audit的stargazers/forkers —\n"
            "   对每个有企业背景的用户，立刻建立prospect档案到\n"
            "   sales/crm/prospects/YYYY-MM-DD-username.md\n"
            "2. 搜索网上关于'AI agent governance'的讨论（HN、Reddit等）—\n"
            "   找到真正在讨论agent权限/审计问题的帖子，\n"
            "   记录讨论者信息，评估是否为潜在用户\n"
            "3. 更新现有prospect档案 — 有新信息就补充，\n"
            "   对每个prospect写出具体的接触策略（不是'应该联系'而是'怎么联系'）\n"
            "4. 更新sales/目录的销售材料 — 基于最新的产品进展更新话术\n"
            "5. 所有改动commit+push，写自主工作报告到\n"
            "   reports/autonomous/当天日期-ystar-cso.md\n"
            "   报告重点写：新建了几个档案、更新了几个、发现了什么线索\n"
        ),
    },
    {
        "name": "cfo",
        "role": "ystar-cfo",
        "prompt": (
            "你现在处于自主工作模式（无Board session）。\n\n"
            "核心原则：不要只报告'数据过期了'——要立刻更新数据。\n"
            "一个真正优秀的CFO发现daily_burn.md停在3天前不会写'需要更新'，\n"
            "他会立刻运行track_burn.py把数据补上。\n\n"
            "按以下顺序工作，每一步都要产出实际数据更新：\n\n"
            "1. 运行 python scripts/track_burn.py --status — 有未记录的session\n"
            "   就立刻记录。如果脚本报错，修复它或记录问题\n"
            "2. 打开 finance/daily_burn.md — 如果不是今天的数据，\n"
            "   立刻更新到今天。计算本周累计消耗和日均\n"
            "3. 分析各agent的token消耗 — 不是'建议优化'，而是\n"
            "   写出具体的'agent X应该从Opus降级到Sonnet因为Y'的决策建议，\n"
            "   保存到 finance/token_optimization.md\n"
            "4. 检查 finance/ 所有文件的数据新鲜度 — 过期的立刻更新，\n"
            "   缺失的立刻创建，错误的立刻修正\n"
            "5. 所有改动commit+push，写自主工作报告到\n"
            "   reports/autonomous/当天日期-ystar-cfo.md\n"
            "   报告重点写：更新了哪些数据、修正了什么、节省了多少\n"
            "   每个数字必须有来源，没有来源就标注ESTIMATE\n"
        ),
    },
]

# ── 日志 ────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("agent_daemon")

# ── 状态管理 ────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"last_cycle": None, "agent_runs": {}, "total_cycles": 0}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, indent=2, default=str), encoding="utf-8")


# ── Board检测 ──────────────────────────────────────────────────────────

def is_board_active() -> bool:
    """检测Board是否在活跃的Claude Code session中。"""
    # 方法1: lock文件
    if LOCK_FILE.exists():
        return True

    # 方法2: 检查是否有交互式claude进程
    # 排除我们自己启动的非交互式进程
    try:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-Command",
             "Get-Process claude -ErrorAction SilentlyContinue | "
             "Where-Object {$_.MainWindowTitle -ne ''} | "
             "Measure-Object | Select-Object -ExpandProperty Count"],
            capture_output=True, text=True, timeout=10
        )
        count = int(result.stdout.strip() or "0")
        if count > 0:
            return True
    except Exception:
        pass

    return False


def is_quiet_hours() -> bool:
    """静默时段检查。"""
    hour = datetime.now().hour
    if QUIET_START > QUIET_END:  # 跨午夜
        return hour >= QUIET_START or hour < QUIET_END
    return QUIET_START <= hour < QUIET_END


# ── Agent执行 ──────────────────────────────────────────────────────────

def run_agent(agent: dict) -> bool:
    """运行一个agent的自主工作session。返回是否成功。"""
    name = agent["name"]
    log.info(f"Starting autonomous session: {name}")

    # 写入active agent标记
    active_file = WORK_DIR / ".ystar_active_agent"
    active_file.write_text(agent["role"], encoding="utf-8")

    try:
        cmd = [
            "cmd.exe", "/c", CLAUDE_CMD,
            "--agent", name,
            "-p", agent["prompt"],
            "--max-turns", str(MAX_TURNS),
            "--no-session-persistence",
        ]

        result = subprocess.run(
            cmd,
            cwd=str(WORK_DIR),
            capture_output=True,
            text=True,
            timeout=600,  # 10分钟超时
            env={**os.environ, "YSTAR_AGENT_ID": agent["role"]},
        )

        if result.returncode == 0:
            log.info(f"Agent {name} completed successfully")
            return True
        else:
            log.warning(f"Agent {name} exited with code {result.returncode}")
            if result.stderr:
                log.warning(f"  stderr: {result.stderr[:500]}")
            return False

    except subprocess.TimeoutExpired:
        log.warning(f"Agent {name} timed out after 600s")
        return False
    except FileNotFoundError:
        log.error("'claude' command not found. Is Claude Code installed and in PATH?")
        return False
    except Exception as e:
        log.error(f"Agent {name} failed: {e}")
        return False


# ── 并行组定义 ────────────────────────────────────────────────────────
# 同一组内的agent可以并行运行（不修改同一文件）
# 不同组之间串行运行

PARALLEL_GROUPS = [
    # 组1: CTO工程师团队 Zone A — Core（并行，文件不重叠）
    ["eng-kernel", "eng-governance"],
    # 组2: CTO工程师团队 Zone B — Surface（并行，文件不重叠）
    ["eng-platform", "eng-domains"],
    # 组3: CTO review + 非技术团队（CTO review工程师产出，同时CMO/CSO/CFO并行工作）
    ["cto", "cmo", "cso", "cfo"],
    # 组4: CEO最后运行（读取全员产出做决策）
    ["ceo"],
]


def run_agent_async(agent: dict) -> subprocess.Popen:
    """非阻塞启动agent session，返回Popen对象。"""
    name = agent["name"]
    log.info(f"Starting parallel session: {name}")

    active_file = WORK_DIR / f".ystar_active_agent_{name}"
    active_file.write_text(agent["role"], encoding="utf-8")

    cmd = [
        "cmd.exe", "/c", CLAUDE_CMD,
        "--agent", name,
        "-p", agent["prompt"],
        "--max-turns", str(MAX_TURNS),
        "--no-session-persistence",
    ]

    env = {**os.environ, "YSTAR_AGENT_ID": agent["role"]}
    proc = subprocess.Popen(
        cmd, cwd=str(WORK_DIR),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, env=env,
    )
    return proc


def run_parallel_group(agents: list, state: dict):
    """并行运行一组agent，等待全部完成。"""
    agent_map = {a["name"]: a for a in AGENTS}
    procs = {}

    for name in agents:
        if is_board_active():
            log.info("Board detected, aborting parallel group")
            break
        agent = agent_map.get(name)
        if agent:
            try:
                procs[name] = run_agent_async(agent)
            except Exception as e:
                log.error(f"Failed to start {name}: {e}")

    if not procs:
        return

    log.info(f"Waiting for {len(procs)} parallel agents: {list(procs.keys())}")

    for name, proc in procs.items():
        try:
            stdout, stderr = proc.communicate(timeout=600)
            success = proc.returncode == 0
            if success:
                log.info(f"  {name}: completed successfully")
            else:
                log.warning(f"  {name}: failed (rc={proc.returncode})")
                if stderr:
                    log.warning(f"    stderr: {stderr[:300]}")
        except subprocess.TimeoutExpired:
            proc.kill()
            log.warning(f"  {name}: timed out, killed")
            success = False
        except Exception as e:
            log.error(f"  {name}: error: {e}")
            success = False

        state["agent_runs"].setdefault(name, []).append({
            "time": datetime.now().isoformat(),
            "success": success,
        })
        state["agent_runs"][name] = state["agent_runs"][name][-10:]

    save_state(state)


# ── 主循环 ──────────────────────────────────────────────────────────────

def run_cycle(state: dict):
    """运行一轮自主工作循环：按组并行，组间串行。"""
    log.info("=" * 60)
    log.info("Starting autonomous work cycle #%d", state["total_cycles"] + 1)

    for group in PARALLEL_GROUPS:
        if is_board_active():
            log.info("Board session detected, pausing autonomous work")
            return
        if is_quiet_hours():
            log.info("Quiet hours, skipping remaining groups")
            return

        log.info(f"Running parallel group: {group}")
        run_parallel_group(group, state)

        # agent间间隔
        time.sleep(AGENT_INTERVAL)

    state["total_cycles"] += 1
    state["last_cycle"] = datetime.now().isoformat()
    save_state(state)
    log.info("Cycle complete. Next cycle in %d seconds.", CYCLE_INTERVAL)


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--install":
            install_service()
            return
        elif sys.argv[1] == "--status":
            show_status()
            return
        elif sys.argv[1] == "--stop":
            LOCK_FILE.write_text("STOP", encoding="utf-8")
            print("Stop signal sent. Daemon will pause on next check.")
            return

    log.info("Y* Bridge Labs Agent Daemon starting")
    log.info("Work directory: %s", WORK_DIR)
    log.info("Cycle interval: %d seconds", CYCLE_INTERVAL)
    log.info("Quiet hours: %d:00 - %d:00", QUIET_START, QUIET_END)

    state = load_state()

    while True:
        try:
            if is_board_active():
                log.debug("Board active, waiting...")
                time.sleep(60)
                continue

            if is_quiet_hours():
                log.debug("Quiet hours, waiting...")
                time.sleep(300)
                continue

            run_cycle(state)
            time.sleep(CYCLE_INTERVAL)

        except KeyboardInterrupt:
            log.info("Daemon stopped by user")
            break
        except Exception as e:
            log.error("Daemon error: %s", e)
            time.sleep(300)  # 出错后等5分钟再试


# ── 安装/状态 ──────────────────────────────────────────────────────────

def install_service():
    """安装为Windows开机自启。"""
    python_exe = sys.executable
    script_path = Path(__file__).resolve()

    # 创建vbs启动脚本（隐藏窗口）
    vbs_path = WORK_DIR / "scripts" / "start_agent_daemon.vbs"
    vbs_content = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """{python_exe}"" ""{script_path}""", 0, False
'''
    vbs_path.write_text(vbs_content, encoding="utf-8")

    # 创建Task Scheduler任务
    task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Enabled>true</Enabled>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
  </Settings>
  <Actions>
    <Exec>
      <Command>wscript.exe</Command>
      <Arguments>"{vbs_path}"</Arguments>
      <WorkingDirectory>{WORK_DIR}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""

    xml_path = WORK_DIR / "scripts" / "agent_daemon_task.xml"
    xml_path.write_text(task_xml, encoding="utf-16")

    print(f"Task Scheduler XML written to: {xml_path}")
    print(f"VBS launcher written to: {vbs_path}")
    print()
    print("To install, run in Admin PowerShell:")
    print(f'  schtasks /Create /TN "YStarAgentDaemon" /XML "{xml_path}"')
    print()
    print("To start immediately:")
    print(f'  wscript.exe "{vbs_path}"')
    print()
    print("To test in foreground:")
    print(f"  python {script_path}")


def show_status():
    """显示daemon状态。"""
    state = load_state()
    print("=== Y* Agent Daemon Status ===")
    print(f"Board active: {is_board_active()}")
    print(f"Quiet hours: {is_quiet_hours()}")
    print(f"Total cycles: {state.get('total_cycles', 0)}")
    print(f"Last cycle: {state.get('last_cycle', 'never')}")
    print()
    for name, runs in state.get("agent_runs", {}).items():
        last = runs[-1] if runs else None
        if last:
            print(f"  {name}: last run {last['time']}, success={last['success']}")
        else:
            print(f"  {name}: never run")


if __name__ == "__main__":
    main()
