#!/usr/bin/env python3
"""
Aiden Recall — CLI interface to the neural network.

Usage:
    aiden_recall.py "concept"           — activate and show related knowledge
    aiden_recall.py --boot              — session boot activation (context-aware)
    aiden_recall.py --learn a b c       — record co-activation (Hebbian)
    aiden_recall.py --stats             — brain statistics
    aiden_recall.py --6d node_id        — show 6D coordinates of a node
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))
from aiden_brain import (activate, record_co_activation, stats,
                         get_db, apply_decay, DB_PATH)


def boot_activation():
    """Session boot: activate from current context (recent git, active goals)."""
    context_terms = []

    # Read session handoff for context
    handoff = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                           "memory", "session_handoff.md")
    if os.path.exists(handoff):
        with open(handoff, "r", encoding="utf-8") as f:
            content = f.read()
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#") and len(line) > 5:
                context_terms.append(line[:100])

    query = " ".join(context_terms[:5]) if context_terms else "CEO Aiden wisdom"
    results = activate(query, top_n=8)

    print("=== Aiden Brain Boot Activation ===")
    print(f"Context: {query[:80]}...")
    print()
    for nid, name, level, fpath, hop in results:
        marker = " (spread)" if hop > 0 else ""
        print(f"  [{level:.2f}] {name[:60]}{marker}")
        if fpath:
            print(f"         → {fpath}")
    print()
    s = stats()
    print(f"Brain: {s['nodes']} nodes, {s['edges']} edges, "
          f"{s['hebbian_edges']} learned, avg_w={s['avg_weight']}")


def show_6d(node_id: str):
    conn = get_db()
    node = conn.execute(
        "SELECT * FROM nodes WHERE id=?", (node_id,)).fetchone()
    conn.close()
    if not node:
        print(f"Node '{node_id}' not found")
        return
    print(f"=== {node['name']} ===")
    print(f"  Y (depth/identity):        {node['dim_y']:.2f}")
    print(f"  X (breadth/knowledge):     {node['dim_x']:.2f}")
    print(f"  Z (impact/transcendence):  {node['dim_z']:.2f}")
    print(f"  T (evolution/direction):   {node['dim_t']:.2f}")
    print(f"  Φ (metacognition):         {node['dim_phi']:.2f}")
    print(f"  C (courage/action):        {node['dim_c']:.2f}")
    print(f"  Base activation:           {node['base_activation']:.3f}")
    print(f"  Access count:              {node['access_count']}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    if sys.argv[1] == "--boot":
        boot_activation()
    elif sys.argv[1] == "--stats":
        s = stats()
        print(json.dumps(s, indent=2))
    elif sys.argv[1] == "--learn":
        node_ids = sys.argv[2:]
        if len(node_ids) < 2:
            print("Need at least 2 node IDs")
            return
        record_co_activation(node_ids)
        print(f"Hebbian update: {' + '.join(node_ids)}")
    elif sys.argv[1] == "--6d":
        if len(sys.argv) < 3:
            print("Need node_id")
            return
        show_6d(sys.argv[2])
    elif sys.argv[1] == "--decay":
        apply_decay()
        print("Decay applied")
    else:
        query = " ".join(sys.argv[1:])
        results = activate(query, top_n=10)
        if not results:
            print("No activations. Try different terms.")
            return
        print(f"=== Aiden Recall: '{query}' ===")
        for nid, name, level, fpath, hop in results:
            marker = " ★" if hop > 0 else ""
            print(f"  [{level:.2f}] {name[:60]}{marker}")


if __name__ == "__main__":
    main()
