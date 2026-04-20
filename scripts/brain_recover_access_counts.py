#!/usr/bin/env python3
"""
CZL-BRAIN-ADD-NODE-PRESERVE: One-time recovery script.

Derives access_count from activation_log entries and backfills
nodes.access_count where the derived count exceeds the current value.

This compensates for the INSERT OR REPLACE bug that zeroed access_count
on every aiden_import run.

Safe to run multiple times (idempotent: only increases, never decreases).
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "aiden_brain.db")


def recover(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Derive per-node activation counts from activation_log JSON
    rows = conn.execute(
        'SELECT json_extract(value, "$.node_id") AS nid, COUNT(*) AS derived_count '
        'FROM activation_log, json_each(activated_nodes) '
        'GROUP BY nid'
    ).fetchall()

    derived = {r["nid"]: r["derived_count"] for r in rows}

    updated = 0
    for nid, count in derived.items():
        current = conn.execute(
            "SELECT access_count FROM nodes WHERE id=?", (nid,)
        ).fetchone()
        if current and count > current["access_count"]:
            conn.execute(
                "UPDATE nodes SET access_count = ? WHERE id = ?", (count, nid)
            )
            updated += 1
            print("  RECOVERED: {} -> {}".format(nid, count))

    conn.commit()

    # Verify
    total_nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
    nonzero = conn.execute(
        "SELECT COUNT(*) FROM nodes WHERE access_count > 0"
    ).fetchone()[0]
    conn.close()

    print("Recovery complete: {} nodes backfilled from activation_log".format(updated))
    print("Nodes with access_count > 0: {} / {}".format(nonzero, total_nodes))
    return updated


if __name__ == "__main__":
    recover()
