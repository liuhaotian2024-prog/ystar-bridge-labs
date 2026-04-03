#!/usr/bin/env python3
"""
Hook performance benchmark.

Measures latency of hook_wrapper.py for different tool types.
"""
import json
import subprocess
import time
import sys
import os

def benchmark_hook(tool_name, tool_input, iterations=10):
    """Measure hook invocation latency."""
    payload = json.dumps({
        "tool_name": tool_name,
        "tool_input": tool_input,
        "session_id": "bench_session",
    })

    latencies = []
    for i in range(iterations):
        start = time.time()
        proc = subprocess.run(
            [sys.executable, "hook_wrapper.py"],
            input=payload,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__),
        )
        elapsed = time.time() - start
        latencies.append(elapsed * 1000)  # Convert to ms

        if proc.returncode != 0:
            print(f"  ERROR on iteration {i}: {proc.stderr[:200]}")
            return None

    avg = sum(latencies) / len(latencies)
    min_lat = min(latencies)
    max_lat = max(latencies)

    return {
        "avg_ms": round(avg, 1),
        "min_ms": round(min_lat, 1),
        "max_ms": round(max_lat, 1),
    }

if __name__ == "__main__":
    print("Hook Performance Benchmark")
    print("=" * 60)

    # Test Read (fast path)
    print("\n[1] Read tool (fast path - should skip governance):")
    result = benchmark_hook("Read", {"file_path": "test.txt"}, iterations=10)
    if result:
        print(f"  Avg: {result['avg_ms']}ms  Min: {result['min_ms']}ms  Max: {result['max_ms']}ms")

    # Test Write (full governance path)
    print("\n[2] Write tool (full governance path):")
    result = benchmark_hook("Write", {"file_path": "test.txt", "content": "test"}, iterations=5)
    if result:
        print(f"  Avg: {result['avg_ms']}ms  Min: {result['min_ms']}ms  Max: {result['max_ms']}ms")

    # Test Bash (full governance path)
    print("\n[3] Bash tool (full governance path):")
    result = benchmark_hook("Bash", {"command": "echo hello"}, iterations=5)
    if result:
        print(f"  Avg: {result['avg_ms']}ms  Min: {result['min_ms']}ms  Max: {result['max_ms']}ms")

    print("\n" + "=" * 60)
    print("DONE. Check scripts/hook_debug.log for detailed timing.")
