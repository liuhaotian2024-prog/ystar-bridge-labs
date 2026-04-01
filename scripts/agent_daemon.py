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

AGENTS = [
    {
        "name": "ceo",
        "role": "ystar-ceo",
        "prompt": (
            "你现在处于自主工作模式（无Board session）。执行以下循环：\n"
            "1. 读取 OKR.md，检查哪些KR落后，制定推进行动\n"
            "2. 检查K9 inbox: python scripts/k9_inbox.py\n"
            "3. 检查Team Health: 各agent最近一次产出是什么时候\n"
            "4. 读取 reports/autonomous/ 最新日报，发现需要跟进的事项\n"
            "5. 执行至少1项自主工作（研究、策略、协调）\n"
            "6. 写入今日自主工作报告到 reports/autonomous/ 目录\n"
            "7. 如果有commit，push到remote\n"
            "完成后退出。"
        ),
    },
    {
        "name": "cto",
        "role": "ystar-cto",
        "prompt": (
            "你现在处于自主工作模式（无Board session）。执行以下循环：\n"
            "1. 检查Y-star-gov仓库的GitHub Issues\n"
            "2. 运行测试: python -m pytest --tb=short -q\n"
            "3. 检查tech_debt.md，选择一项改进执行\n"
            "4. 执行至少1项自主工作（代码优化、测试补充、文档更新）\n"
            "5. 写入今日自主工作报告到 reports/autonomous/ 目录\n"
            "6. 如果有commit，push到remote\n"
            "完成后退出。"
        ),
    },
    {
        "name": "cmo",
        "role": "ystar-cmo",
        "prompt": (
            "你现在处于自主工作模式（无Board session）。执行以下循环：\n"
            "1. 读取Y-star-gov最近的git log，了解产品最新进展\n"
            "2. 检查content/目录，评估内容pipeline\n"
            "3. 研究竞品内容策略（搜索MOSAIC, AutoHarness最新文章）\n"
            "4. 执行至少1项自主工作（草拟内容、研究行业趋势、优化现有内容）\n"
            "5. 写入今日自主工作报告到 reports/autonomous/ 目录\n"
            "6. 如果有commit，push到remote\n"
            "完成后退出。"
        ),
    },
    {
        "name": "cso",
        "role": "ystar-cso",
        "prompt": (
            "你现在处于自主工作模式（无Board session）。执行以下循环：\n"
            "1. 检查GitHub stargazers/forks，分析新用户profile\n"
            "2. 搜索HN/Reddit/LinkedIn上关于AI agent governance的讨论\n"
            "3. 建立或更新prospect档案到 sales/crm/prospects/\n"
            "4. 执行至少1项自主工作（用户发现、渠道研究、销售材料更新）\n"
            "5. 写入今日自主工作报告到 reports/autonomous/ 目录\n"
            "6. 如果有commit，push到remote\n"
            "完成后退出。"
        ),
    },
    {
        "name": "cfo",
        "role": "ystar-cfo",
        "prompt": (
            "你现在处于自主工作模式（无Board session）。执行以下循环：\n"
            "1. 运行 python scripts/track_burn.py --status 检查token记录\n"
            "2. 更新 finance/daily_burn.md\n"
            "3. 分析今日各agent token消耗，提出优化建议\n"
            "4. 执行至少1项自主工作（财务数据整理、定价研究、成本分析）\n"
            "5. 写入今日自主工作报告到 reports/autonomous/ 目录\n"
            "6. 如果有commit，push到remote\n"
            "完成后退出。"
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
            "claude",
            "-p", agent["prompt"],
            "--max-turns", str(MAX_TURNS),
            "--no-session-persistence",
        ]

        # 如果有agent-name参数支持
        # cmd.extend(["--agent-name", name])

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


# ── 主循环 ──────────────────────────────────────────────────────────────

def run_cycle(state: dict):
    """运行一轮完整的自主工作循环（所有agent各一次）。"""
    log.info("=" * 60)
    log.info("Starting autonomous work cycle #%d", state["total_cycles"] + 1)

    for agent in AGENTS:
        # 每个agent之前检查Board是否上线
        if is_board_active():
            log.info("Board session detected, pausing autonomous work")
            return

        if is_quiet_hours():
            log.info("Quiet hours, skipping remaining agents")
            return

        success = run_agent(agent)

        # 记录运行状态
        state["agent_runs"].setdefault(agent["name"], []).append({
            "time": datetime.now().isoformat(),
            "success": success,
        })
        # 只保留最近10次记录
        state["agent_runs"][agent["name"]] = state["agent_runs"][agent["name"]][-10:]

        save_state(state)

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
