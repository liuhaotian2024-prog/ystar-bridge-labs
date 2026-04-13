#!/usr/bin/env python3
"""
Whitelist Matcher — A018 Phase 1 Sync Mechanism A
Matches hook event payloads to whitelist entries using fuzzy matching.
Author: Ryan Park (eng-platform)
Date: 2026-04-13
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

try:
    from rapidfuzz import fuzz
except ImportError:
    print("ERROR: rapidfuzz not installed. Run: pip install rapidfuzz", file=sys.stderr)
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


@dataclass
class WhitelistEntry:
    """Structured whitelist entry."""
    id: str
    who: str
    what: str
    task_type: str
    core_verbs: List[str]
    when_trigger: str
    when_complete: str
    prerequisites: List[str]
    observable_signal: str
    source_file: str  # role_mandate.yaml or event_workflow.yaml


@dataclass
class MatchResult:
    """Match result with score and metadata."""
    entry_id: str
    score: float
    matched_fields: Dict[str, float]
    entry: WhitelistEntry


class WhitelistMatcher:
    """Fuzzy matcher for hook events → whitelist entries."""

    THRESHOLD = 70  # Match threshold (0-100 scale)
    FIELD_WEIGHTS = {
        "who": 2.0,      # Agent identity is critical
        "what": 1.5,     # Action description is important
        "task_type": 1.2,
        "core_verbs": 1.0,
        "when_trigger": 0.8,
        "observable_signal": 1.0,
    }

    def __init__(self, whitelist_dir: Path):
        """Load whitelist entries from YAML files."""
        self.whitelist_dir = Path(whitelist_dir)
        self.entries: List[WhitelistEntry] = []
        self._load_entries()

    def _load_entries(self):
        """Load all whitelist entries from role_mandate.yaml and event_workflow.yaml."""
        for yaml_file in ["role_mandate.yaml", "event_workflow.yaml"]:
            yaml_path = self.whitelist_dir / yaml_file
            if not yaml_path.exists():
                print(f"WARNING: {yaml_path} not found, skipping", file=sys.stderr)
                continue

            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            for entry_dict in data.get("entries", []):
                entry = WhitelistEntry(
                    id=entry_dict["id"],
                    who=entry_dict["who"],
                    what=entry_dict["what"],
                    task_type=entry_dict["task_type"],
                    core_verbs=entry_dict.get("core_verbs", []),
                    when_trigger=entry_dict["when_trigger"],
                    when_complete=entry_dict["when_complete"],
                    prerequisites=entry_dict.get("prerequisites", []),
                    observable_signal=entry_dict["observable_signal"],
                    source_file=yaml_file,
                )
                self.entries.append(entry)

        print(f"Loaded {len(self.entries)} whitelist entries from {self.whitelist_dir}", file=sys.stderr)

    def match_event(self, event_payload: Dict) -> Optional[MatchResult]:
        """
        Match a hook event payload to the best whitelist entry.
        Returns MatchResult if score >= THRESHOLD, else None.
        """
        if not self.entries:
            print("WARNING: No whitelist entries loaded", file=sys.stderr)
            return None

        # Extract searchable fields from event payload
        search_text = self._extract_search_text(event_payload)
        agent_id = event_payload.get("agent_id", "unknown")

        # Score all entries
        scored_entries: List[Tuple[float, WhitelistEntry]] = []
        for entry in self.entries:
            score, matched_fields = self._score_entry(entry, search_text, agent_id)
            scored_entries.append((score, entry, matched_fields))

        # Sort by score descending
        scored_entries.sort(key=lambda x: x[0], reverse=True)

        # Return best match if above threshold
        best_score, best_entry, matched_fields = scored_entries[0]
        if best_score >= self.THRESHOLD:
            return MatchResult(
                entry_id=best_entry.id,
                score=best_score,
                matched_fields=matched_fields,
                entry=best_entry,
            )
        else:
            return None

    def get_top_k_similar(self, event_payload: Dict, k: int = 3) -> List[MatchResult]:
        """Get top-k most similar entries (even if below threshold)."""
        if not self.entries:
            return []

        search_text = self._extract_search_text(event_payload)
        agent_id = event_payload.get("agent_id", "unknown")

        scored_entries: List[Tuple[float, WhitelistEntry, Dict]] = []
        for entry in self.entries:
            score, matched_fields = self._score_entry(entry, search_text, agent_id)
            scored_entries.append((score, entry, matched_fields))

        scored_entries.sort(key=lambda x: x[0], reverse=True)

        return [
            MatchResult(
                entry_id=entry.id,
                score=score,
                matched_fields=matched_fields,
                entry=entry,
            )
            for score, entry, matched_fields in scored_entries[:k]
        ]

    def _extract_search_text(self, event_payload: Dict) -> str:
        """Extract searchable text from event payload."""
        parts = []

        # Tool call context
        if "tool" in event_payload:
            parts.append(event_payload["tool"])
        if "command" in event_payload:
            parts.append(event_payload["command"])
        if "file_path" in event_payload:
            parts.append(event_payload["file_path"])

        # Intent context
        context = event_payload.get("context", {})
        if "intent" in context:
            parts.append(context["intent"])
        if "purpose" in context:
            parts.append(context["purpose"])

        # Event type
        if "event_type" in event_payload:
            parts.append(event_payload["event_type"])

        return " ".join(parts)

    def _score_entry(self, entry: WhitelistEntry, search_text: str, agent_id: str) -> Tuple[float, Dict[str, float]]:
        """
        Score a whitelist entry against search context.
        Returns (weighted_score, field_scores_dict).
        """
        field_scores = {}

        # WHO: exact match on agent_id gets bonus, fuzzy match otherwise
        if entry.who == agent_id:
            field_scores["who"] = 100.0
        elif entry.who == "all_agents":
            field_scores["who"] = 80.0
        else:
            field_scores["who"] = fuzz.token_set_ratio(entry.who, agent_id)

        # WHAT: fuzzy match action description
        field_scores["what"] = fuzz.token_set_ratio(entry.what, search_text)

        # TASK_TYPE: fuzzy match
        field_scores["task_type"] = fuzz.token_set_ratio(entry.task_type, search_text)

        # CORE_VERBS: match any verb in search text
        verb_scores = [fuzz.partial_ratio(verb, search_text) for verb in entry.core_verbs]
        field_scores["core_verbs"] = max(verb_scores) if verb_scores else 0.0

        # WHEN_TRIGGER: fuzzy match
        field_scores["when_trigger"] = fuzz.token_set_ratio(entry.when_trigger, search_text)

        # OBSERVABLE_SIGNAL: fuzzy match
        field_scores["observable_signal"] = fuzz.token_set_ratio(entry.observable_signal, search_text)

        # Compute weighted score
        weighted_score = 0.0
        total_weight = sum(self.FIELD_WEIGHTS.values())

        for field, score in field_scores.items():
            weight = self.FIELD_WEIGHTS.get(field, 1.0)
            weighted_score += score * weight

        # Normalize to 0-100 scale
        normalized_score = weighted_score / total_weight

        return normalized_score, field_scores


def main():
    """CLI interface for whitelist matcher."""
    import argparse

    parser = argparse.ArgumentParser(description="Match hook event to whitelist entry")
    parser.add_argument("--whitelist-dir", default="governance/whitelist", help="Path to whitelist YAML directory")
    parser.add_argument("--event-json", help="JSON file with event payload (or stdin if omitted)")
    parser.add_argument("--top-k", type=int, default=3, help="Show top-k similar entries if no match")

    args = parser.parse_args()

    # Load event payload
    if args.event_json:
        with open(args.event_json, "r") as f:
            event_payload = json.load(f)
    else:
        event_payload = json.load(sys.stdin)

    # Initialize matcher
    whitelist_dir = Path(args.whitelist_dir)
    matcher = WhitelistMatcher(whitelist_dir)

    # Try to match
    result = matcher.match_event(event_payload)

    if result:
        print(f"✓ MATCH: {result.entry_id} (score: {result.score:.1f})")
        print(f"  Source: {result.entry.source_file}")
        print(f"  Who: {result.entry.who}")
        print(f"  What: {result.entry.what}")
        print(f"  Task Type: {result.entry.task_type}")
        print(f"  Field Scores: {json.dumps(result.matched_fields, indent=2)}")
        sys.exit(0)
    else:
        print(f"✗ NO MATCH (threshold {matcher.THRESHOLD})")
        print(f"\nTop-{args.top_k} most similar:")
        top_k = matcher.get_top_k_similar(event_payload, k=args.top_k)
        for i, match in enumerate(top_k, 1):
            print(f"\n  {i}. {match.entry_id} (score: {match.score:.1f})")
            print(f"     Who: {match.entry.who}")
            print(f"     What: {match.entry.what}")
            print(f"     Diff: score {match.score:.1f} < threshold {matcher.THRESHOLD}")
        sys.exit(1)


if __name__ == "__main__":
    main()
