#!/usr/bin/env python3
"""Labs Smart Dispatch Router — Task → Owner matching

Architecture:
- Layer 3: Smart Routing (THIS) — task description → recommended owner
- Layer 2: Semantic (labs_rag_query) — find similar tasks, context, lessons
- Layer 1: Structure (labs_atlas) — subsystem inventory, dependency graph

Routing algorithm (deterministic, no LLM):
1. Query Labs RAG for top-5 similar tasks/lessons/skills
2. Extract historical owner patterns from RAG results
3. Match task keywords against role triggers (from .claude/agents/*.md)
4. Score each role based on:
   - Keyword match strength (TF-IDF style)
   - Historical owner frequency
   - Subsystem overlap (if task mentions subsystem names)
5. Return ranked recommendations with confidence + reasoning

Design constraints (Iron Rule 1):
- NO LLM inference
- Pure rule-based scoring (keywords × history × subsystems)
- Deterministic output (same task → same recommendation)
- Fast (<100ms for typical query)

Usage:
    from scripts.labs_router import LabsRouter

    router = LabsRouter()
    rec = router.route("fix circuit breaker bug")
    print(rec)  # {"owner": "Maya-Governance", "confidence": 0.82, ...}

CLI:
    python3 scripts/labs_router.py "fix circuit breaker bug"
    python3 scripts/labs_router.py "design pricing model" --verbose

Author: Ryan Park (eng-platform)
Date: 2026-04-13
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import subprocess


@dataclass
class RoutingRecommendation:
    """Routing decision with evidence."""
    owner: str  # "Ryan-Platform" format
    confidence: float  # 0.0-1.0
    reason: str  # human-readable explanation
    related_skills: List[str]  # from RAG
    related_lessons: List[str]  # from RAG
    related_subsystems: List[str]  # from Atlas
    score_breakdown: Dict[str, float]  # {"keyword": 0.4, "history": 0.3, ...}


# Role trigger patterns extracted from .claude/agents/*.md
# (These would normally be loaded dynamically, but hook blocks .claude/agents/ reads)
# Updated 2026-04-13 based on current role definitions
ROLE_TRIGGERS = {
    "ceo": {
        "keywords": ["coordination", "strategy", "board", "delegation", "cross-department",
                    "integration", "alignment", "roadmap", "priority", "decision"],
        "subsystems": [],
        "typical_tasks": ["coordinate", "delegate", "integrate", "report", "align"]
    },
    "cto": {
        "keywords": ["architecture", "technical", "code", "test", "build", "infrastructure",
                    "system", "deployment", "ci/cd", "pipeline"],
        "subsystems": ["ystar", "governance", "kernel", "adapters"],
        "typical_tasks": ["architect", "review", "approve", "design"]
    },
    "eng-kernel": {  # Leo Chen
        "keywords": ["core", "runtime", "engine", "memory", "yml", "cieu", "persistence",
                    "session", "state", "identity", "detector"],
        "subsystems": ["ystar/kernel", "ystar/memory", "identity_detector"],
        "typical_tasks": ["implement", "fix", "test", "optimize"]
    },
    "eng-governance": {  # Maya Patel
        "keywords": ["governance", "policy", "compliance", "circuit", "breaker", "health",
                    "precheck", "obligation", "omission", "enforcement", "audit"],
        "subsystems": ["ystar/governance", "gov-mcp", "health.py", "precheck.py"],
        "typical_tasks": ["implement", "fix", "test", "enforce", "audit"]
    },
    "eng-platform": {  # Ryan Park
        "keywords": ["adapter", "hook", "orchestrator", "connector", "scanner", "cli",
                    "doctor", "setup", "install", "integration", "mcp", "dispatch"],
        "subsystems": ["ystar/adapters", "ystar/cli", "gov-mcp", "hook_server"],
        "typical_tasks": ["implement", "fix", "test", "integrate", "wrap"]
    },
    "eng-domains": {  # Jordan Lee
        "keywords": ["domain", "specialized", "tool", "wrapper", "integration", "external",
                    "api", "rag", "semantic", "atlas", "routing"],
        "subsystems": ["ystar/domains", "ystar/integrations", "labs_rag", "labs_atlas"],
        "typical_tasks": ["implement", "research", "integrate", "build"]
    },
    "cmo": {
        "keywords": ["content", "marketing", "blog", "article", "hn", "linkedin", "video",
                    "narrative", "launch", "messaging"],
        "subsystems": [],
        "typical_tasks": ["write", "publish", "promote", "create"]
    },
    "cso": {
        "keywords": ["sales", "customer", "lead", "crm", "patent", "growth", "user",
                    "pricing", "deal"],
        "subsystems": [],
        "typical_tasks": ["contact", "follow-up", "qualify", "close"]
    },
    "cfo": {
        "keywords": ["finance", "cost", "pricing", "budget", "revenue", "cash", "model",
                    "token", "expense"],
        "subsystems": [],
        "typical_tasks": ["analyze", "model", "forecast", "track"]
    }
}


class LabsRouter:
    """Smart task routing engine."""

    def __init__(self, company_root: Optional[Path] = None):
        self.company_root = company_root or Path(__file__).parent.parent
        self.rag_script = self.company_root / "scripts" / "labs_rag_query.py"

        # Validate RAG script exists
        if not self.rag_script.exists():
            raise FileNotFoundError(f"Labs RAG script not found: {self.rag_script}")

    def _query_rag(self, task: str, top_k: int = 5) -> List[Dict]:
        """Query Labs RAG for similar tasks/lessons."""
        try:
            result = subprocess.run(
                ["python3", str(self.rag_script), task, "--top-k", str(top_k)],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return []

            # Parse RAG output (format: numbered list with Score/Snippet)
            hits = []
            current_hit = {}

            for line in result.stdout.split('\n'):
                # Match numbered entries: "1. path/to/file.md"
                match_entry = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
                if match_entry:
                    if current_hit:
                        hits.append(current_hit)
                    current_hit = {"path": match_entry.group(2).strip()}
                    continue

                # Match score line: "Score: 162.662 | Age: 0.0 days | bm25=19.38"
                if line.strip().startswith("Score:"):
                    parts = line.strip().split('|')
                    score_match = re.search(r'Score:\s+([\d.]+)', parts[0])
                    if score_match:
                        current_hit["score"] = float(score_match.group(1))
                    continue

                # Match snippet line
                if line.strip().startswith("Snippet:"):
                    current_hit["snippet"] = line.strip().replace("Snippet:", "").strip()
                    continue

            if current_hit:
                hits.append(current_hit)

            return hits

        except Exception as e:
            print(f"[LabsRouter] RAG query failed: {e}", file=sys.stderr)
            return []

    def _extract_historical_owners(self, rag_hits: List[Dict]) -> Dict[str, int]:
        """Extract owner frequency from RAG results."""
        owner_count = defaultdict(int)

        for hit in rag_hits:
            path = hit.get("path", "")

            # Pattern 1: knowledge/{role}/... → role
            match = re.search(r'knowledge/([^/]+)/', path)
            if match:
                owner_count[match.group(1)] += 1
                continue

            # Pattern 2: reports/..._author_role.md or role-specific filenames
            for role in ROLE_TRIGGERS.keys():
                if role in path.lower():
                    owner_count[role] += 1
                    break

        return dict(owner_count)

    def _extract_subsystems(self, task: str) -> List[str]:
        """Extract subsystem mentions from task description."""
        subsystems = []
        task_lower = task.lower()

        # Common subsystem patterns
        patterns = [
            r'ystar[/.](\w+)',  # ystar/kernel, ystar.governance
            r'(hook|orchestrator|adapter|connector|scanner)',
            r'(health|precheck|omission|circuit)',
            r'(rag|atlas|routing)',
            r'gov-mcp',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, task_lower)
            subsystems.extend(matches)

        return list(set(subsystems))

    def _score_role(
        self,
        role: str,
        task: str,
        historical_owners: Dict[str, int],
        subsystems: List[str]
    ) -> Tuple[float, Dict[str, float]]:
        """Score a single role for this task.

        Returns: (total_score, breakdown)
        """
        breakdown = {}
        task_lower = task.lower()

        # Component 1: Keyword match (TF-IDF style)
        trigger_config = ROLE_TRIGGERS[role]
        keyword_hits = sum(1 for kw in trigger_config["keywords"] if kw in task_lower)
        keyword_score = keyword_hits / max(len(trigger_config["keywords"]), 1)
        breakdown["keyword"] = keyword_score

        # Component 2: Historical owner frequency
        total_history = sum(historical_owners.values())
        if total_history > 0:
            history_score = historical_owners.get(role, 0) / total_history
        else:
            history_score = 0.0
        breakdown["history"] = history_score

        # Component 3: Subsystem overlap
        role_subsystems = set(trigger_config["subsystems"])
        task_subsystems = set(subsystems)
        if role_subsystems and task_subsystems:
            subsystem_score = len(role_subsystems & task_subsystems) / len(role_subsystems)
        else:
            subsystem_score = 0.0
        breakdown["subsystem"] = subsystem_score

        # Component 4: Typical task verb match
        task_verbs = re.findall(r'\b(implement|fix|build|design|write|analyze|test|deploy|integrate)\b', task_lower)
        verb_score = 0.0
        if task_verbs:
            matched_verbs = [v for v in task_verbs if v in trigger_config["typical_tasks"]]
            verb_score = len(matched_verbs) / len(task_verbs) if task_verbs else 0.0
        breakdown["verb"] = verb_score

        # Weighted combination
        # Favor keyword match over history to prefer specialists
        weights = {
            "keyword": 0.5,
            "history": 0.2,
            "subsystem": 0.2,
            "verb": 0.1
        }

        total_score = sum(breakdown[k] * weights[k] for k in weights)

        # Penalty for CEO on specialist tasks (encourage delegation)
        if role == "ceo" and keyword_score < 0.3:
            total_score *= 0.5  # halve CEO score if low keyword match

        return total_score, breakdown

    def route(self, task: str, verbose: bool = False) -> RoutingRecommendation:
        """Route a task to recommended owner.

        Args:
            task: Task description string
            verbose: Print debug info

        Returns:
            RoutingRecommendation with owner, confidence, evidence
        """
        # Step 1: Query RAG
        rag_hits = self._query_rag(task, top_k=5)

        if verbose:
            print(f"[LabsRouter] RAG hits: {len(rag_hits)}", file=sys.stderr)

        # Step 2: Extract context
        historical_owners = self._extract_historical_owners(rag_hits)
        subsystems = self._extract_subsystems(task)

        if verbose:
            print(f"[LabsRouter] Historical owners: {historical_owners}", file=sys.stderr)
            print(f"[LabsRouter] Subsystems: {subsystems}", file=sys.stderr)

        # Step 3: Score all roles
        role_scores = {}
        role_breakdowns = {}

        for role in ROLE_TRIGGERS.keys():
            score, breakdown = self._score_role(role, task, historical_owners, subsystems)
            role_scores[role] = score
            role_breakdowns[role] = breakdown

        # Step 4: Select best role
        best_role = max(role_scores, key=role_scores.get)
        best_score = role_scores[best_role]

        if verbose:
            print(f"[LabsRouter] Role scores:", file=sys.stderr)
            for role, score in sorted(role_scores.items(), key=lambda x: x[1], reverse=True):
                print(f"  {role}: {score:.3f} {role_breakdowns[role]}", file=sys.stderr)

        # Step 5: Generate recommendation
        # Map role to Name-Role format
        role_name_map = {
            "ceo": "Aiden-CEO",
            "cto": "Ethan-CTO",
            "eng-kernel": "Leo-Kernel",
            "eng-governance": "Maya-Governance",
            "eng-platform": "Ryan-Platform",
            "eng-domains": "Jordan-Domains",
            "cmo": "Sofia-CMO",
            "cso": "Zara-CSO",
            "cfo": "Marco-CFO"
        }

        owner = role_name_map.get(best_role, best_role)
        confidence = min(best_score, 1.0)  # Cap at 1.0

        # Generate reason
        reason_parts = []
        breakdown = role_breakdowns[best_role]

        if breakdown["keyword"] > 0.3:
            reason_parts.append(f"strong keyword match ({breakdown['keyword']:.2f})")
        if breakdown["history"] > 0.3:
            reason_parts.append(f"historical owner pattern ({breakdown['history']:.2f})")
        if breakdown["subsystem"] > 0.3:
            reason_parts.append(f"subsystem overlap ({breakdown['subsystem']:.2f})")

        reason = "; ".join(reason_parts) if reason_parts else "default routing"

        # Extract related items from RAG
        related_skills = []
        related_lessons = []
        for hit in rag_hits:
            path = hit.get("path", "")
            if "/skills/" in path:
                related_skills.append(path)
            elif "/lessons/" in path:
                related_lessons.append(path)

        return RoutingRecommendation(
            owner=owner,
            confidence=confidence,
            reason=reason,
            related_skills=related_skills[:3],
            related_lessons=related_lessons[:3],
            related_subsystems=subsystems,
            score_breakdown=breakdown
        )


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Labs Smart Dispatch Router")
    parser.add_argument("task", help="Task description")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show debug info")
    parser.add_argument("--json", action="store_true", help="Output JSON")

    args = parser.parse_args()

    router = LabsRouter()
    rec = router.route(args.task, verbose=args.verbose)

    if args.json:
        print(json.dumps(asdict(rec), indent=2))
    else:
        print(f"Recommended Owner: {rec.owner}")
        print(f"Confidence: {rec.confidence:.2f}")
        print(f"Reason: {rec.reason}")

        if rec.related_skills:
            print(f"Related Skills: {', '.join(rec.related_skills)}")
        if rec.related_lessons:
            print(f"Related Lessons: {', '.join(rec.related_lessons)}")
        if rec.related_subsystems:
            print(f"Related Subsystems: {', '.join(rec.related_subsystems)}")

        print(f"Score Breakdown: {rec.score_breakdown}")


if __name__ == "__main__":
    main()
