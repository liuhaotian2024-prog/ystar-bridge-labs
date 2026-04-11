"""
Jinjin Integration Examples

Practical examples of using jinjin_client for agent-to-agent coordination.
"""

import logging
from pathlib import Path
from jinjin_client import JinjinClient, ask_jinjin

logging.basicConfig(level=logging.INFO)


def example_1_quick_question():
    """Example 1: Quick one-shot question"""
    print("\n=== Example 1: Quick Question ===")
    response = ask_jinjin("今天的日期是多少？")
    print(f"Response: {response}")


def example_2_full_metadata():
    """Example 2: Get full response with metadata"""
    print("\n=== Example 2: Full Metadata ===")
    client = JinjinClient()
    result = client.ask("请介绍一下Y*gov项目的核心功能")

    print(f"Response: {result['text'][:200]}...")
    print(f"Model: {result['model']}")
    print(f"Latency: {result['duration_ms']}ms")
    print(f"Tokens used: {result['usage']}")
    print(f"Session ID: {result['session_id']}")


def example_3_conversation():
    """Example 3: Multi-turn conversation"""
    print("\n=== Example 3: Conversation ===")
    client = JinjinClient()

    # First question
    q1 = client.ask("Y*gov项目最近有什么更新？")
    print(f"Q1: {q1['text'][:150]}...")
    session_id = q1['session_id']

    # Follow-up question (same session)
    q2 = client.ask("具体说说CIEU审计功能", session_id=session_id)
    print(f"Q2: {q2['text'][:150]}...")


def example_4_delegation():
    """Example 4: Task delegation"""
    print("\n=== Example 4: Task Delegation ===")
    client = JinjinClient()

    task = """
    请帮我检查Mac mini的系统状态：
    1. 磁盘使用率（df -h）
    2. 内存使用（free -m 或 vm_stat）
    3. 当前运行的Python进程（ps aux | grep python）

    汇总结果，突出任何需要注意的问题。
    """

    result = client.ask(task)
    print(f"Delegation result:\n{result['text']}")


def example_5_cieu_analysis():
    """Example 5: CIEU log analysis (if logs exist)"""
    print("\n=== Example 5: CIEU Log Analysis ===")

    cieu_dir = Path.home() / ".k9log" / "cieu"
    if not cieu_dir.exists():
        print("No CIEU logs found, skipping example")
        return

    recent_logs = sorted(cieu_dir.glob("*.json"))[-3:]  # Last 3 logs
    if not recent_logs:
        print("No CIEU logs found")
        return

    log_files = "\n".join([str(p) for p in recent_logs])

    client = JinjinClient()
    result = client.ask(f"""
    请分析最近的CIEU日志文件：

    {log_files}

    识别：
    1. 最常见的操作类型
    2. 是否有scope violations
    3. 是否有未授权的外部操作
    """)

    print(f"CIEU Analysis:\n{result['text']}")


def example_6_health_monitoring():
    """Example 6: Health check and monitoring"""
    print("\n=== Example 6: Health Check ===")
    client = JinjinClient()

    if client.health_check():
        print("✓ Jinjin is online and responsive")

        # Get detailed status
        status = client.ask("请报告你的当前状态：模型版本、工作目录、最近处理的任务")
        print(f"Status: {status['text']}")
    else:
        print("✗ Jinjin is not responding (gateway may be down)")


def example_7_error_handling():
    """Example 7: Error handling"""
    print("\n=== Example 7: Error Handling ===")

    # Test with very short timeout
    try:
        client = JinjinClient(timeout=5)
        result = client.ask("执行一个长时间任务：sleep 10")
        print(f"Result: {result['text']}")
    except Exception as e:
        print(f"Caught expected error: {type(e).__name__}: {e}")


def example_8_workspace_query():
    """Example 8: Query workspace state"""
    print("\n=== Example 8: Workspace Query ===")
    client = JinjinClient()

    result = client.ask("""
    请检查ystar-company工作区的状态：
    1. 有哪些未提交的文件（git status）
    2. 最近3次提交的信息（git log -3 --oneline）
    3. 是否有.claude/tasks/下的待办任务
    """)

    print(f"Workspace state:\n{result['text']}")


def run_all_examples():
    """Run all examples in sequence"""
    examples = [
        example_1_quick_question,
        example_2_full_metadata,
        example_3_conversation,
        example_4_delegation,
        example_5_cieu_analysis,
        example_6_health_monitoring,
        example_7_error_handling,
        example_8_workspace_query,
    ]

    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"✗ {example.__name__} failed: {e}")
        print("\n" + "="*60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Run specific example
        example_name = sys.argv[1]
        example_func = globals().get(f"example_{example_name}")
        if example_func:
            example_func()
        else:
            print(f"Unknown example: {example_name}")
            print("Available examples:")
            for name in globals():
                if name.startswith("example_"):
                    print(f"  - {name.replace('example_', '')}")
    else:
        # Run all examples
        run_all_examples()
