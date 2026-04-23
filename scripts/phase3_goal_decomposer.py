#!/usr/bin/env python3
"""
Phase 3 Goal Decomposer — NL goal string -> sub-goal tree in ystar_goal_tree.

Board 2026-04-23 directive: field-functional Phase 3.
3-stage pipeline:
  Stage 1: NL -> structured (Gemma local, template fallback)
  Stage 2: Owner-role inference (ystar_role_scope keyword match)
  Stage 3: DB write (ystar_goal_tree insert)

Usage:
    python3 scripts/phase3_goal_decomposer.py --goal "NL string" [--preview] [--json]
    python3 scripts/phase3_goal_decomposer.py --help

Scope: eng-kernel (Leo Chen)
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

# ── Paths ───────────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, ".ystar_cieu.db")
SESSION_FILE = os.path.join(BASE_DIR, ".ystar_session.json")

# ── Stage 1: NL -> Structured ───────────────────────────────────────────────────

# Quality benchmark from Board's hand-seeded Y_001 tree:
FEW_SHOT_EXAMPLES = [
    {
        "input": "gov-mcp 成功上架并获得第一笔付费",
        "output": {
            "top_goal": {
                "text": "gov-mcp 成功上架并获得第一笔付费",
                "y_star_definition": "pip-installable package on PyPI + 1+ paying external customer + revenue landed in stripe/bank account",
                "deadline": None,
            },
            "subgoals": [
                {
                    "text": "API 文档完整",
                    "y_star_definition": "products/ystar-gov/docs/ has endpoint ref + examples + install guide all sections filled",
                    "depends_on": [],
                },
                {
                    "text": "测试覆盖 >80%",
                    "y_star_definition": "pytest coverage report shows >= 80% line coverage on src/ystar/**",
                    "depends_on": [],
                },
                {
                    "text": "定价策略确定",
                    "y_star_definition": "finance/pricing_v1.md ratified by Board with 3-tier pricing + stripe product SKUs defined",
                    "depends_on": [],
                },
                {
                    "text": "第一个外部用户注册",
                    "y_star_definition": "ystar_users table has 1+ row with verified email NOT in @ystar-company.com / @anthropic.com",
                    "depends_on": ["API 文档完整", "定价策略确定"],
                },
            ],
        },
    },
]

# Template-based decomposition topics (used as fallback when Gemma unavailable)
# Each template includes owner_role hint so role inference doesn't default to CEO
TEMPLATE_TOPICS = {
    # Chinese and English topic keywords -> sub-goal templates
    "付费": [
        {"text": "CFO 定价策略设计与 pricing tier 建模 [owner: ceo]", "y_star_tpl": "pricing document ratified with tier definitions + payment SKUs"},
        {"text": "CTO 支付集成 stripe API 对接与 deploy [owner: cto]", "y_star_tpl": "stripe/payment gateway integrated + test transaction successful"},
        {"text": "CMO 用户获取渠道建立 marketing content 与 landing page [owner: cmo]", "y_star_tpl": "3+ acquisition channels active (blog/SEO/social/referral) with tracking"},
        {"text": "CTO 产品 API 文档完善与 install guide [owner: cto]", "y_star_tpl": "docs/ directory has install guide + API reference + quickstart all sections filled"},
        {"text": "Platform 用户支持流程 deploy 与监控 [owner: platform]", "y_star_tpl": "support channel (email/discord/github issues) live + response SLA defined"},
    ],
    "用户": [
        {"text": "CMO 落地页上线 landing page marketing content [owner: cmo]", "y_star_tpl": "landing page deployed at public URL with value proposition + signup CTA"},
        {"text": "CTO 用户注册流程 API endpoint 实现 [owner: cto]", "y_star_tpl": "user registration endpoint live + email verification working"},
        {"text": "CMO 用户获取策略 marketing campaign 设计 [owner: cmo]", "y_star_tpl": "acquisition plan document with 3+ channels + target metrics per channel"},
        {"text": "CTO 产品 API 文档完善 install guide [owner: cto]", "y_star_tpl": "docs/ has install guide + API reference + quickstart"},
        {"text": "CMO 用户反馈收集 blog content NPS [owner: cmo]", "y_star_tpl": "feedback mechanism (survey/NPS/in-app) deployed + first 10 responses collected"},
    ],
    "上线": [
        {"text": "Kernel 功能完整性验证 test suite [owner: kernel]", "y_star_tpl": "core feature checklist 100% passing in CI + manual smoke test by Board"},
        {"text": "Platform 部署流程自动化 deploy CI/CD [owner: platform]", "y_star_tpl": "one-command deploy script working + rollback tested"},
        {"text": "Platform 监控告警配置 health endpoint [owner: platform]", "y_star_tpl": "health endpoint + error alerting + uptime monitor active"},
        {"text": "CMO 文档与帮助 content landing page [owner: cmo]", "y_star_tpl": "user-facing docs deployed + FAQ section with 10+ entries"},
    ],
    "测试": [
        {"text": "Kernel 单元测试覆盖 test suite [owner: kernel]", "y_star_tpl": "pytest coverage >= 80% on core modules"},
        {"text": "Governance 集成测试搭建 hook enforcement [owner: governance]", "y_star_tpl": "integration test suite with 5+ end-to-end scenarios passing"},
        {"text": "Platform CI 管道配置 deploy pipeline [owner: platform]", "y_star_tpl": "CI pipeline runs on every PR + blocks merge on failure"},
    ],
    "customer": [
        {"text": "CMO landing page deployment marketing content [owner: cmo]", "y_star_tpl": "public landing page with value prop + signup form live"},
        {"text": "CEO pricing strategy and tier modeling [owner: ceo]", "y_star_tpl": "pricing document with 3-tier model + payment integration ready"},
        {"text": "CMO user acquisition channels marketing blog [owner: cmo]", "y_star_tpl": "3+ channels active with attribution tracking"},
        {"text": "CTO API documentation and install guide [owner: cto]", "y_star_tpl": "install guide + API docs + quickstart tutorial complete"},
        {"text": "Platform support process deploy monitoring [owner: platform]", "y_star_tpl": "support channel live + response SLA < 24h defined"},
    ],
    "deploy": [
        {"text": "Platform CI/CD pipeline deploy automation [owner: platform]", "y_star_tpl": "automated build + test + deploy pipeline passing"},
        {"text": "Platform monitoring setup health endpoint [owner: platform]", "y_star_tpl": "health check endpoint + alerting + dashboard active"},
        {"text": "CTO rollback mechanism API safety [owner: cto]", "y_star_tpl": "one-command rollback tested + documented"},
        {"text": "CMO documentation and content [owner: cmo]", "y_star_tpl": "deploy runbook + architecture diagram available"},
    ],
}

# Also update generic fallback with role hints
GENERIC_SUBGOALS_WITH_ROLES = [
    {"text": "CEO 需求分析与规划 [owner: ceo]", "y_star_tpl": "requirements document with acceptance criteria for each feature"},
    {"text": "CTO 核心功能实现 API build [owner: cto]", "y_star_tpl": "core feature implemented + unit tests passing"},
    {"text": "Kernel 测试与验证 test suite [owner: kernel]", "y_star_tpl": "test suite covering critical paths + CI integration"},
    {"text": "CMO 文档编写 content landing page [owner: cmo]", "y_star_tpl": "user-facing documentation complete with examples"},
    {"text": "Platform 发布准备 deploy CI/CD [owner: platform]", "y_star_tpl": "release checklist complete + Board approval obtained"},
]



def _build_gemma_prompt(
    goal_text: str,
    role_list: List[str],
    role_scopes: Optional[Dict[str, List[str]]] = None,
    retry_hint: Optional[str] = None,
) -> str:
    """Build few-shot prompt for Gemma to decompose a goal.

    Args:
        role_scopes: role_id -> keyword list; injected so Gemma can place keywords.
        retry_hint: if set, appended as a corrective instruction (CEO-default retry).
    """
    example = FEW_SHOT_EXAMPLES[0]

    # Build role-keyword context block for Gemma
    role_ctx = ""
    if role_scopes:
        role_lines = []
        for rid, kws in role_scopes.items():
            if kws:
                role_lines.append(f"  {rid}: {', '.join(kws[:8])}")
        if role_lines:
            role_ctx = "Role keyword reference (use these words in sub-goal text to indicate owner):\n" + "\n".join(role_lines) + "\n\n"

    retry_block = ""
    if retry_hint:
        retry_block = f"\nCORRECTION: {retry_hint}\n"

    prompt = f"""You are a goal decomposition engine. Break a top-level goal into 4-6 actionable sub-goals.

Each sub-goal JSON object must have:
- "text": description that INCLUDES role-specific keywords so ownership is clear
- "y_star_definition": verifiable completion criterion
- "depends_on": list of dependency sub-goal texts (empty if none)

IMPORTANT: Distribute sub-goals across different roles. End each "text" with [owner: ROLE] hint.

Good sub-goal text examples:
- "CMO ships landing page and marketing content for funnel acquisition [owner: cmo]"
- "CTO builds API integration and deploys backend service [owner: cto]"
- "Platform engineer configures deployment pipeline and monitoring [owner: platform]"
Bad (no role signal): "Craft product positioning" or "Set up infrastructure"

{role_ctx}Available roles: {json.dumps(role_list)}
{retry_block}
Example input: "{example['input']}"
Example output:
{json.dumps(example['output'], ensure_ascii=False, indent=2)}

Now decompose:
Input: "{goal_text}"

Output (valid JSON only, no markdown fences):"""
    return prompt


def _try_gemma_decompose(
    goal_text: str,
    role_list: List[str],
    role_scopes: Optional[Dict[str, List[str]]] = None,
    retry_hint: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Attempt Stage 1 via Gemma local. Returns parsed dict or None on failure."""
    try:
        # Import gemma_client from same directory
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from gemma_client import generate as gemma_generate
    except ImportError:
        return None

    prompt = _build_gemma_prompt(goal_text, role_list, role_scopes, retry_hint)
    result = gemma_generate(prompt, max_tokens=1000)

    if result.get("error"):
        return None

    raw_text = result.get("text", "").strip()
    if not raw_text:
        return None

    # Try to extract JSON from the response (Gemma may wrap in markdown fences)
    json_match = re.search(r'\{[\s\S]*\}', raw_text)
    if not json_match:
        return None

    try:
        parsed = json.loads(json_match.group())
    except json.JSONDecodeError:
        return None

    # Validate structure
    if "top_goal" not in parsed or "subgoals" not in parsed:
        return None
    if not isinstance(parsed["subgoals"], list) or len(parsed["subgoals"]) < 2:
        return None

    # Validate each subgoal has required fields
    for sg in parsed["subgoals"]:
        if "text" not in sg or "y_star_definition" not in sg:
            return None

    return parsed


def _template_decompose(goal_text: str) -> Dict[str, Any]:
    """Template-based fallback decomposition (rule engine)."""
    # Find best matching topic
    best_topic = None
    best_score = 0
    goal_lower = goal_text.lower()

    for topic_key, templates in TEMPLATE_TOPICS.items():
        # Count keyword occurrences in goal text
        score = goal_lower.count(topic_key)
        if score > best_score:
            best_score = score
            best_topic = topic_key

    if best_topic and best_score > 0:
        templates = TEMPLATE_TOPICS[best_topic]
    else:
        templates = GENERIC_SUBGOALS_WITH_ROLES

    # Extract deadline if present (e.g., "三个月内", "6 months", "by 2026-07")
    deadline = None
    deadline_match = re.search(r'(\d+)\s*个?月', goal_text)
    if deadline_match:
        months = int(deadline_match.group(1))
        # Approximate deadline
        import datetime
        deadline = (datetime.datetime.now() + datetime.timedelta(days=months * 30)).strftime("%Y-%m-%d")

    deadline_match_en = re.search(r'(\d+)\s*months?', goal_text, re.IGNORECASE)
    if not deadline and deadline_match_en:
        months = int(deadline_match_en.group(1))
        import datetime
        deadline = (datetime.datetime.now() + datetime.timedelta(days=months * 30)).strftime("%Y-%m-%d")

    # Build y_star_definition for top goal from the goal text
    top_y_star = f"All sub-goals completed + Board verification that '{goal_text}' is achieved"

    subgoals = []
    for tpl in templates:
        subgoals.append({
            "text": tpl["text"],
            "y_star_definition": tpl["y_star_tpl"],
            "depends_on": [],
        })

    return {
        "top_goal": {
            "text": goal_text,
            "y_star_definition": top_y_star,
            "deadline": deadline,
        },
        "subgoals": subgoals,
    }


# ── Stage 2: Owner-Role Inference ───────────────────────────────────────────────

def _load_role_scopes(conn: sqlite3.Connection) -> Dict[str, List[str]]:
    """Load role -> scope_keywords from ystar_role_scope table."""
    roles = {}
    try:
        rows = conn.execute("SELECT role_id, scope_keywords FROM ystar_role_scope").fetchall()
        for row in rows:
            role_id = row[0]
            keywords = json.loads(row[1]) if row[1] else []
            roles[role_id] = [kw.lower() for kw in keywords]
    except sqlite3.OperationalError:
        # Table doesn't exist yet; return empty
        pass
    return roles


def infer_owner_role(goal_text: str, role_scopes: Dict[str, List[str]]) -> Tuple[str, str]:
    """
    Infer the best owner role for a goal text based on keyword matching.
    Also checks for explicit [owner: ROLE] hint from Gemma prompt output.

    Returns (role_id, inference_basis) where inference_basis is a human-readable
    explanation of why this role was chosen.
    """
    goal_lower = goal_text.lower()

    # Check for explicit [owner: role] hint first (highest priority)
    owner_hint = re.search(r'\[owner:\s*(\w+)\]', goal_lower)
    if owner_hint:
        hinted_role = owner_hint.group(1).strip()
        # Validate hinted role exists in role_scopes (or known roles)
        known_roles = set(role_scopes.keys()) | {"ceo", "cto", "cmo", "cso", "cfo", "secretary", "platform", "governance", "kernel"}
        if hinted_role in known_roles:
            return hinted_role, f"explicit [owner: {hinted_role}] hint"

    scores = {}

    for role_id, keywords in role_scopes.items():
        score = 0
        matched_kws = []
        for kw in keywords:
            if kw in goal_lower:
                score += 1
                matched_kws.append(kw)
        if score > 0:
            scores[role_id] = (score, matched_kws)

    if not scores:
        return "ceo", "no keyword match -> default to ceo"

    # Pick highest score; on tie, prefer cto > ceo > others (most actionable)
    tie_break_order = ["cto", "ceo", "platform", "kernel", "governance", "cmo", "secretary"]
    best_role = max(
        scores.keys(),
        key=lambda r: (scores[r][0], -tie_break_order.index(r) if r in tie_break_order else 0),
    )
    best_score, best_kws = scores[best_role]
    basis = f"matched {best_score} keyword(s): {best_kws}"
    return best_role, basis


# ── Stage 3: DB Write ───────────────────────────────────────────────────────────

def _next_goal_id(conn: sqlite3.Connection) -> int:
    """Find next available Y_NNN number."""
    rows = conn.execute(
        "SELECT goal_id FROM ystar_goal_tree WHERE goal_id LIKE 'Y_%'"
    ).fetchall()
    max_n = 0
    for row in rows:
        gid = row[0]
        # Extract top-level number: Y_003 -> 3, Y_003_2 -> 3
        m = re.match(r'Y_(\d+)', gid)
        if m:
            n = int(m.group(1))
            if n > max_n:
                max_n = n
    return max_n + 1


def _insert_goal_tree(
    conn: sqlite3.Connection,
    top_goal_id: str,
    decomposed: Dict[str, Any],
    role_assignments: Dict[str, Tuple[str, str]],
) -> List[Dict[str, Any]]:
    """Insert top goal + sub-goals into ystar_goal_tree. Returns list of inserted rows."""
    now = time.time()
    inserted = []

    top = decomposed["top_goal"]
    top_role, top_basis = role_assignments.get(
        top["text"], ("ceo", "top-level default")
    )

    # Insert top goal
    conn.execute(
        "INSERT OR REPLACE INTO ystar_goal_tree "
        "(goal_id, parent_goal_id, goal_text, y_star_definition, owner_role, "
        "created_at, created_by, status, weight) VALUES (?,?,?,?,?,?,?,?,?)",
        (
            top_goal_id, None, top["text"], top["y_star_definition"],
            top_role, now, "phase3_auto", "active", 1.0,
        ),
    )
    inserted.append({
        "goal_id": top_goal_id,
        "parent_goal_id": None,
        "goal_text": top["text"],
        "y_star_definition": top["y_star_definition"],
        "owner_role": top_role,
        "inference_basis": top_basis,
        "weight": 1.0,
    })

    # Insert sub-goals
    for i, sg in enumerate(decomposed["subgoals"], 1):
        sub_id = f"{top_goal_id}_{i}"
        sg_role, sg_basis = role_assignments.get(
            sg["text"], ("ceo", "no match -> default")
        )
        weight = 0.8  # default sub-goal weight
        conn.execute(
            "INSERT OR REPLACE INTO ystar_goal_tree "
            "(goal_id, parent_goal_id, goal_text, y_star_definition, owner_role, "
            "created_at, created_by, status, weight) VALUES (?,?,?,?,?,?,?,?,?)",
            (
                sub_id, top_goal_id, sg["text"], sg["y_star_definition"],
                sg_role, now, "phase3_auto", "active", weight,
            ),
        )
        inserted.append({
            "goal_id": sub_id,
            "parent_goal_id": top_goal_id,
            "goal_text": sg["text"],
            "y_star_definition": sg["y_star_definition"],
            "owner_role": sg_role,
            "inference_basis": sg_basis,
            "weight": weight,
        })

    conn.commit()
    return inserted


# ── CIEU Event Emission ─────────────────────────────────────────────────────────

def _get_session_id() -> str:
    """Read session_id from .ystar_session.json."""
    try:
        with open(SESSION_FILE) as f:
            return json.load(f).get("session_id", "standalone")
    except Exception:
        return "standalone"


def _emit_cieu_event(
    conn: sqlite3.Connection,
    top_goal_id: str,
    subgoal_count: int,
    gemma_used: bool,
    fallback_to_template: bool,
) -> str:
    """Emit WAVE3_PHASE3_DECOMPOSER_LANDED CIEU event. Returns event_id."""
    event_id = str(uuid.uuid4())
    seq_global = int(time.time() * 1_000_000)

    conn.execute(
        """INSERT INTO cieu_events
           (event_id, seq_global, created_at, session_id, agent_id,
            event_type, decision, passed, file_path,
            params_json, result_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            event_id,
            seq_global,
            time.time(),
            _get_session_id(),
            "eng-kernel",
            "WAVE3_PHASE3_DECOMPOSER_LANDED",
            "auto_approve",
            1,
            "scripts/phase3_goal_decomposer.py",
            json.dumps({
                "live_fire_goal": "NL goal decomposition",
                "top_goal_id_assigned": top_goal_id,
                "subgoal_count": subgoal_count,
                "gemma_used": gemma_used,
                "fallback_to_template": fallback_to_template,
            }),
            json.dumps({"status": "success", "pipeline": "phase3"}),
        ),
    )
    conn.commit()
    return event_id


# ── Main Pipeline ───────────────────────────────────────────────────────────────

def decompose_goal(
    goal_text: str,
    preview: bool = False,
    as_json: bool = False,
) -> Dict[str, Any]:
    """
    Full 3-stage pipeline: NL -> structured -> role inference -> DB write.

    Returns dict with {top_goal_id, tree, gemma_used, fallback_to_template, event_id}.
    """
    conn = sqlite3.connect(DB_PATH)

    # Load role scopes for inference
    role_scopes = _load_role_scopes(conn)
    role_list = list(role_scopes.keys()) if role_scopes else [
        "ceo", "cto", "cmo", "secretary", "platform", "governance", "kernel"
    ]

    # ── Stage 1: NL -> Structured ──
    gemma_used = False
    fallback_to_template = False

    decomposed = _try_gemma_decompose(goal_text, role_list, role_scopes)
    if decomposed is not None:
        gemma_used = True
    else:
        # Gemma unavailable or returned garbage; use template engine
        decomposed = _template_decompose(goal_text)
        fallback_to_template = True

    # ── Stage 2: Owner-Role Inference ──
    def _infer_all(dec: Dict[str, Any]) -> Dict[str, Tuple[str, str]]:
        """Run role inference on top goal + all subgoals."""
        assignments = {}
        assignments[dec["top_goal"]["text"]] = infer_owner_role(
            dec["top_goal"]["text"], role_scopes,
        )
        for sg in dec["subgoals"]:
            assignments[sg["text"]] = infer_owner_role(sg["text"], role_scopes)
        return assignments

    role_assignments = _infer_all(decomposed)

    # ── Stage 2b: CEO-default saturation retry ──
    # If Gemma was used but >3 subgoals defaulted to CEO, retry with corrective hint (max 2 retries)
    if gemma_used and role_scopes:
        max_retries = 2
        for retry_i in range(max_retries):
            ceo_count = sum(
                1 for sg in decomposed["subgoals"]
                if role_assignments.get(sg["text"], ("ceo", ""))[0] == "ceo"
            )
            if ceo_count <= 3:
                break  # acceptable distribution
            retry_hint = (
                f"Your previous output assigned {ceo_count}/{len(decomposed['subgoals'])} "
                f"sub-goals to ceo by default. That is wrong. Distribute roles: use keywords "
                f"like 'CMO', 'CTO', 'platform', 'marketing', 'deploy', 'content', 'API', "
                f"'landing page', 'blog' in sub-goal text so each maps to the right owner. "
                f"Add [owner: role] hint at end of each sub-goal text."
            )
            retry_result = _try_gemma_decompose(goal_text, role_list, role_scopes, retry_hint)
            if retry_result is not None:
                decomposed = retry_result
                role_assignments = _infer_all(decomposed)
            else:
                break  # Gemma failed on retry, accept current

    # ── Stage 3: ID generation + DB write ──
    next_n = _next_goal_id(conn)
    top_goal_id = f"Y_{next_n:03d}"

    if preview:
        # Build preview tree without DB write
        tree = []
        top_role, top_basis = role_assignments.get(
            decomposed["top_goal"]["text"], ("ceo", "default")
        )
        tree.append({
            "goal_id": top_goal_id,
            "parent_goal_id": None,
            "goal_text": decomposed["top_goal"]["text"],
            "y_star_definition": decomposed["top_goal"]["y_star_definition"],
            "owner_role": top_role,
            "inference_basis": top_basis,
            "weight": 1.0,
        })
        for i, sg in enumerate(decomposed["subgoals"], 1):
            sg_role, sg_basis = role_assignments.get(sg["text"], ("ceo", "default"))
            tree.append({
                "goal_id": f"{top_goal_id}_{i}",
                "parent_goal_id": top_goal_id,
                "goal_text": sg["text"],
                "y_star_definition": sg["y_star_definition"],
                "owner_role": sg_role,
                "inference_basis": sg_basis,
                "weight": 0.8,
            })

        conn.close()
        return {
            "mode": "preview",
            "top_goal_id": top_goal_id,
            "tree": tree,
            "gemma_used": gemma_used,
            "fallback_to_template": fallback_to_template,
            "subgoal_count": len(decomposed["subgoals"]),
            "event_id": None,
        }

    # Commit mode: write to DB
    tree = _insert_goal_tree(conn, top_goal_id, decomposed, role_assignments)

    # Emit CIEU event
    event_id = _emit_cieu_event(
        conn, top_goal_id, len(decomposed["subgoals"]),
        gemma_used, fallback_to_template,
    )

    conn.close()

    return {
        "mode": "commit",
        "top_goal_id": top_goal_id,
        "tree": tree,
        "gemma_used": gemma_used,
        "fallback_to_template": fallback_to_template,
        "subgoal_count": len(decomposed["subgoals"]),
        "event_id": event_id,
    }


# ── CLI ─────────────────────────────────────────────────────────────────────────

def _format_tree_human(result: Dict[str, Any]) -> str:
    """Human-readable tree output."""
    lines = []
    mode = result["mode"]
    lines.append(f"=== Phase 3 Goal Decomposition ({mode} mode) ===")
    lines.append(f"Top Goal: {result['top_goal_id']}")
    lines.append(f"Sub-goals: {result['subgoal_count']}")
    lines.append(f"Gemma used: {result['gemma_used']}")
    if result['fallback_to_template']:
        lines.append("(template fallback: Gemma unavailable or returned unparseable output)")
    if result.get("event_id"):
        lines.append(f"CIEU event_id: {result['event_id']}")
    lines.append("")

    for node in result["tree"]:
        indent = "  " if node.get("parent_goal_id") else ""
        prefix = "+-" if node.get("parent_goal_id") else ""
        lines.append(f"{indent}{prefix}[{node['goal_id']}] {node['goal_text']}")
        lines.append(f"{indent}  owner: {node['owner_role']} ({node.get('inference_basis', '')})")
        lines.append(f"{indent}  y*: {node['y_star_definition']}")
        lines.append(f"{indent}  weight: {node['weight']}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase 3 Goal Decomposer: NL goal -> sub-goal tree in ystar_goal_tree",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Preview (dry-run, no DB write):\n"
            '  python3 scripts/phase3_goal_decomposer.py --goal "获得100个付费用户" --preview\n\n'
            "  # Commit to DB:\n"
            '  python3 scripts/phase3_goal_decomposer.py --goal "获得100个付费用户"\n\n'
            "  # JSON output:\n"
            '  python3 scripts/phase3_goal_decomposer.py --goal "获得100个付费用户" --preview --json\n'
        ),
    )
    parser.add_argument("--goal", required=True, help="Natural language goal string")
    parser.add_argument("--preview", action="store_true", help="Dry-run: show tree but don't insert into DB")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output as JSON")
    args = parser.parse_args()

    if not os.path.exists(DB_PATH):
        print(f"ERROR: DB not found at {DB_PATH}", file=sys.stderr)
        sys.exit(1)

    result = decompose_goal(args.goal, preview=args.preview, as_json=args.as_json)

    if args.as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(_format_tree_human(result))


if __name__ == "__main__":
    main()
