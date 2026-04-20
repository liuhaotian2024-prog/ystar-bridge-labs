#!/usr/bin/env python3
"""
Aiden Neural Network — Import wisdom files as nodes + cross-references as edges.

Reads all .md files under knowledge/ceo/wisdom/,
extracts frontmatter metadata, assigns 6D coordinates,
discovers cross-references, and populates aiden_brain.db.
"""

import os
import re
import hashlib
import json
import sys

sys.path.insert(0, os.path.dirname(__file__))
from aiden_brain import init_db, add_node, add_edge, stats, DB_PATH

WISDOM_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "knowledge", "ceo", "wisdom"
)

# ── 6D Coordinate Assignment ───────────────────────────────────────

DEPTH_MAP = {"kernel": 1.0, "existential": 1.0, "architectural": 0.85,
             "foundational": 0.7, "operational": 0.5, "tactical": 0.3}

TYPE_DIMS = {
    "self_knowledge": {"y": 0.9, "x": 0.3, "phi": 0.8, "c": 0.7},
    "meta":           {"y": 0.8, "x": 0.6, "phi": 0.9, "c": 0.5},
    "paradigm":       {"y": 0.7, "x": 0.5, "phi": 0.6, "c": 0.6},
    "ceo_learning":   {"y": 0.4, "x": 0.9, "phi": 0.4, "c": 0.3},
    "strategic":      {"y": 0.5, "x": 0.7, "z": 0.7, "phi": 0.5, "c": 0.5},
    "hub":            {"y": 1.0, "x": 0.8, "z": 0.6, "phi": 0.7, "c": 0.8},
}

COURAGE_KEYWORDS = [
    "courage", "勇气", "质疑", "challenge", "question consensus",
    "independent", "独立", "dare", "fear", "恐惧", "blind spot",
    "deformation", "变形", "honest", "诚实"
]
Z_KEYWORDS = [
    "external", "外部", "user", "用户", "publish", "发布",
    "case study", "audience", "受众", "world", "世界", "impact"
]
PHI_KEYWORDS = [
    "counterfactual", "反事实", "metacognition", "元", "reflection",
    "反思", "四象限", "self-check", "sandbox", "replay"
]


def classify_type(rel_path: str) -> str:
    parts = rel_path.split(os.sep)
    if len(parts) > 1:
        folder = parts[0]
        if folder == "ceo_learning":
            return "ceo_learning"
        elif folder == "paradigms":
            return "paradigm"
        elif folder == "self_knowledge":
            return "self_knowledge"
        elif folder == "strategic":
            return "strategic"
        elif folder == "meta":
            return "meta"
    if "WHO_I_AM" in rel_path:
        return "hub"
    return "meta"


def parse_frontmatter(content: str) -> dict:
    fm = {}
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if m:
        for line in m.group(1).split("\n"):
            if ":" in line:
                key, val = line.split(":", 1)
                fm[key.strip()] = val.strip()
    return fm


def compute_6d(node_type: str, depth_label: str, content: str) -> dict:
    base = TYPE_DIMS.get(node_type, {})
    dims = {
        "y": base.get("y", 0.5),
        "x": base.get("x", 0.5),
        "z": base.get("z", 0.3),
        "t": 0.5,
        "phi": base.get("phi", 0.5),
        "c": base.get("c", 0.5),
    }
    # Adjust Y based on depth label
    if depth_label:
        for label, val in DEPTH_MAP.items():
            if label in depth_label.lower():
                dims["y"] = max(dims["y"], val)
                break
    # Adjust C (courage) based on content keywords
    content_lower = content.lower()
    c_hits = sum(1 for kw in COURAGE_KEYWORDS if kw in content_lower)
    dims["c"] = min(1.0, dims["c"] + c_hits * 0.05)
    # Adjust Z (impact) based on content keywords
    z_hits = sum(1 for kw in Z_KEYWORDS if kw in content_lower)
    dims["z"] = min(1.0, dims["z"] + z_hits * 0.05)
    # Adjust Φ (metacognition) based on content keywords
    phi_hits = sum(1 for kw in PHI_KEYWORDS if kw in content_lower)
    dims["phi"] = min(1.0, dims["phi"] + phi_hits * 0.05)
    return dims


def make_node_id(rel_path: str) -> str:
    return rel_path.replace(os.sep, "/").replace(".md", "").replace(" ", "_")


def extract_summary(content: str, name: str) -> str:
    """Extract first meaningful line after frontmatter as summary."""
    body = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
    for line in body.split("\n"):
        line = line.strip().lstrip("#").strip()
        if line and not line.startswith("---") and len(line) > 10:
            return line[:120]
    return name


def extract_cross_refs(content: str) -> list:
    """Extract markdown links to .md files."""
    refs = re.findall(r'\]\(([^)]+\.md)\)', content)
    return refs


def resolve_ref_to_id(ref_path: str, source_dir: str) -> str:
    """Resolve a relative reference to a node ID."""
    if ref_path.startswith("../"):
        return None
    full = os.path.normpath(os.path.join(source_dir, ref_path))
    try:
        rel = os.path.relpath(full, WISDOM_ROOT)
        if rel.startswith(".."):
            return None
        return make_node_id(rel)
    except ValueError:
        return None


# ── Main Import ─────────────────────────────────────────────────────

def import_all(db_path: str = DB_PATH):
    init_db(db_path)

    # Phase 1: Discover and create all nodes
    nodes = {}
    for root, dirs, files in os.walk(WISDOM_ROOT):
        for f in files:
            if not f.endswith(".md"):
                continue
            fpath = os.path.join(root, f)
            rel = os.path.relpath(fpath, WISDOM_ROOT)
            node_id = make_node_id(rel)

            with open(fpath, "r", encoding="utf-8") as fh:
                content = fh.read()

            fm = parse_frontmatter(content)
            node_type = classify_type(rel)
            depth_label = fm.get("depth", "")
            name = fm.get("name", f.replace(".md", "").replace("_", " ").title())
            dims = compute_6d(node_type, depth_label, content)
            summary = extract_summary(content, name)
            principles = []
            if "principles" in fm:
                try:
                    principles = json.loads(fm["principles"].replace("'", '"'))
                except (json.JSONDecodeError, TypeError):
                    principles = [p.strip() for p in fm["principles"].split(",")]

            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

            add_node(node_id, name, file_path=rel, node_type=node_type,
                     depth_label=depth_label, dims=dims,
                     principles=principles, summary=summary,
                     content_hash=content_hash,
                     db_path=db_path)

            nodes[node_id] = {
                "content": content, "dir": os.path.dirname(rel),
                "principles": principles
            }

    print(f"Imported {len(nodes)} nodes")

    # Phase 2: Create edges from cross-references
    edge_count = 0
    for node_id, info in nodes.items():
        refs = extract_cross_refs(info["content"])
        source_dir = info["dir"]
        for ref in refs:
            target_id = resolve_ref_to_id(ref, os.path.join(WISDOM_ROOT, source_dir))
            if target_id and target_id in nodes and target_id != node_id:
                add_edge(node_id, target_id, weight=0.7,
                         edge_type="explicit", db_path=db_path)
                edge_count += 1

    # Phase 3: Create edges from shared principles
    principle_map = {}
    for node_id, info in nodes.items():
        for p in info["principles"]:
            principle_map.setdefault(p, []).append(node_id)
    for p, ids in principle_map.items():
        for i, a in enumerate(ids):
            for b in ids[i+1:]:
                add_edge(a, b, weight=0.5, edge_type="principle_shared",
                         db_path=db_path)
                edge_count += 1

    # Phase 4: Create edges from same-directory proximity
    dir_map = {}
    for node_id, info in nodes.items():
        d = info["dir"]
        dir_map.setdefault(d, []).append(node_id)
    for d, ids in dir_map.items():
        if len(ids) <= 1:
            continue
        for i, a in enumerate(ids):
            for b in ids[i+1:]:
                add_edge(a, b, weight=0.3, edge_type="proximity",
                         db_path=db_path)
                edge_count += 1

    print(f"Created {edge_count} edges (explicit + principle + proximity)")

    # Stats
    s = stats(db_path)
    print(f"\nBrain stats: {json.dumps(s, indent=2)}")


def _verify_add_node_is_safe():
    """Guard: refuse to run if add_node() still uses INSERT OR REPLACE.
    This prevents the self-destruct pattern from destroying access_count
    on every import. See CZL-BRAIN-ADD-NODE-PRESERVE."""
    import inspect
    source = inspect.getsource(add_node)
    if "INSERT OR REPLACE" in source:
        print("FATAL: add_node() still uses INSERT OR REPLACE which destroys "
              "access_count on every re-import. Fix aiden_brain.py first.",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    _verify_add_node_is_safe()
    import_all()
