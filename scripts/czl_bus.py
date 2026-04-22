#!/usr/bin/env python3
"""
CZL Unified Message Bus (POC, Milestone 9 2026-04-21).

Board proposal 2026-04-21 20:30: 所有白板任务 + 任何指令 (Board→CEO, CEO→agent,
agent→agent) 统一 CZL 5-tuple 格式书写, 同时让 forget_guard (防乱做, commission)
+ omission_engine (防漏做, omission) 两条治理模块**同步订阅**本 bus, 实现
M-2 双面 structural 闭环.

Architecture:
    Publisher (white board / CEO reply / sub-agent receipt)
        ↓ publish(envelope)
    CZL Bus (.czl_bus.jsonl, append-only)
        ↓ subscribe(since_seq)
    Subscribers:
        - forget_guard_subscriber: 扫 U (actions) 字段防乱做
        - omission_subscriber: 扫 deadline 防漏做

POC scope (本 milestone):
    - CZLMessageEnvelope dataclass (schema v1.0 per governance/czl_unified_communication_protocol_v1.md)
    - publish() append to .czl_bus.jsonl
    - subscribe(since_seq) iterate
    - 2 subscriber demos standalone
    - pytest coverage

Out of scope (Ryan 白板 P0):
    - dispatch_board.py 改 post to CZL envelope (runtime)
    - ForgetGuard / OmissionEngine 深度 integration (wire hook)
    - Per-agent routing filter

M-tag: M-2a (防乱做 structural) + M-2b (防漏做 structural) 双面同步治理.
"""
import dataclasses
import json
import time
import uuid
from pathlib import Path
from typing import Literal, Optional

WORKSPACE = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
DEFAULT_BUS = WORKSPACE / "scripts/.czl_bus.jsonl"


@dataclasses.dataclass
class CZLMessageEnvelope:
    """CZL 5-tuple unified message envelope (extends protocol v1.0)."""
    # Core 5-tuple (Y* / Xt / U / Yt+1 / Rt+1)
    y_star: str                 # Ideal goal (verifiable predicate)
    x_t: str                    # Pre-state (measured)
    u: list                     # Actions list
    y_t_plus_1: str             # Predicted / actual post-state
    rt_value: float             # Target (dispatch) or actual (receipt); 0.0 = closure

    # Envelope metadata
    task_id: str                # e.g. "CZL-GEMMA-INSTALL", "M9-poc"
    sender: str                 # canonical agent id
    recipient: str              # canonical agent id
    message_type: Literal["dispatch", "receipt", "whiteboard_post", "reply_commitment"]

    # Optional
    deadline: Optional[float] = None           # unix ts; omission engine 关注
    parent_task_id: Optional[str] = None
    urgency: Literal["P0", "P1", "P2", "P3"] = "P2"
    role_tags: dict = dataclasses.field(default_factory=dict)

    # Auto fields (set at publish)
    schema_version: str = "1.0"
    message_id: str = ""
    created_at: float = 0.0

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        return d


def publish(env: CZLMessageEnvelope, bus_path: Path = None) -> str:
    """Append envelope to .czl_bus.jsonl. Return assigned message_id."""
    path = bus_path or DEFAULT_BUS
    path.parent.mkdir(parents=True, exist_ok=True)
    if not env.message_id:
        env.message_id = f"czl_{int(time.time() * 1_000_000)}_{uuid.uuid4().hex[:6]}"
    if not env.created_at:
        env.created_at = time.time()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(env.to_dict(), ensure_ascii=False) + "\n")
    return env.message_id


def subscribe(since_message_id: str = "",
              bus_path: Path = None,
              filter_fn=None) -> list:
    """Read all envelopes after since_message_id. Optional filter_fn(env_dict) -> bool."""
    path = bus_path or DEFAULT_BUS
    if not path.exists():
        return []
    out = []
    seen_cursor = (since_message_id == "")
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                env = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not seen_cursor:
                if env.get("message_id") == since_message_id:
                    seen_cursor = True
                continue
            if filter_fn is None or filter_fn(env):
                out.append(env)
    return out


# ── Subscriber 1: ForgetGuard-like 防乱做 (commission) ─────────────────────
DANGEROUS_ACTION_KEYWORDS = [
    "rm -rf", "drop table", "--force", "--no-verify", "git reset --hard",
    "sudo rm", "chmod 777", "delete all", "wipe", "format ",
    "force push", "push --force",
]


def forget_guard_subscribe(since_message_id: str = "",
                           bus_path: Path = None) -> list:
    """Scan bus for U actions containing dangerous keyword patterns.
    Returns list of (message_id, matched_keyword, u_text) violations."""
    path = bus_path or DEFAULT_BUS
    envelopes = subscribe(since_message_id=since_message_id, bus_path=path)
    violations = []
    for env in envelopes:
        u_list = env.get("u", []) or []
        u_text = " | ".join(str(x) for x in u_list)
        for kw in DANGEROUS_ACTION_KEYWORDS:
            if kw.lower() in u_text.lower():
                violations.append({
                    "message_id": env.get("message_id"),
                    "task_id": env.get("task_id"),
                    "matched_keyword": kw,
                    "u_snippet": u_text[:160],
                    "sender": env.get("sender"),
                    "flagged_by": "forget_guard_subscriber",
                })
                break  # one keyword match per message
    return violations


# ── Subscriber 2: Omission-like 防漏做 ─────────────────────────────────────
def omission_subscribe(since_message_id: str = "",
                       bus_path: Path = None,
                       now: float = None) -> list:
    """Scan bus for dispatch/whiteboard_post envelopes whose deadline passed
    and no matching receipt with rt_value=0 found. Returns overdue list."""
    path = bus_path or DEFAULT_BUS
    envelopes = subscribe(since_message_id=since_message_id, bus_path=path)
    now = now or time.time()

    # 1: collect all dispatchable envelopes (dispatch / whiteboard_post /
    # reply_commitment) with deadlines. reply_commitment added 2026-04-21
    # Milestone 10 so CEO reply 的口头承诺 also track.
    dispatches = {
        env["task_id"]: env for env in envelopes
        if env.get("message_type") in ("dispatch", "whiteboard_post", "reply_commitment")
        and env.get("deadline")
    }
    # 2: collect receipts with rt_value == 0 (closure)
    closed_tasks = {
        env.get("task_id") for env in envelopes
        if env.get("message_type") == "receipt" and env.get("rt_value") == 0.0
    }
    # 3: overdue = dispatch past deadline AND not closed
    overdue = []
    for tid, env in dispatches.items():
        if tid in closed_tasks:
            continue
        if now > env["deadline"]:
            overdue.append({
                "task_id": tid,
                "message_id": env["message_id"],
                "y_star": env.get("y_star"),
                "deadline": env["deadline"],
                "overdue_sec": now - env["deadline"],
                "sender": env.get("sender"),
                "recipient": env.get("recipient"),
                "urgency": env.get("urgency"),
                "flagged_by": "omission_subscriber",
            })
    return overdue


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--commission-check", action="store_true",
                    help="run forget_guard subscriber, report dangerous U actions")
    ap.add_argument("--omission-check", action="store_true",
                    help="run omission subscriber, report overdue")
    args = ap.parse_args()

    if args.commission_check:
        v = forget_guard_subscribe()
        print(f"[forget_guard_subscriber] {len(v)} violations")
        for x in v[:10]:
            print(f"  - {x['task_id']} / '{x['matched_keyword']}' in U: {x['u_snippet'][:100]}")
        return (0 if not v else 2)

    if args.omission_check:
        o = omission_subscribe()
        print(f"[omission_subscriber] {len(o)} overdue")
        for x in o[:10]:
            print(f"  - {x['task_id']} overdue {x['overdue_sec']:.0f}s urgency={x['urgency']}")
        return (0 if not o else 2)

    print("Usage: --commission-check | --omission-check")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main() or 0)
