#!/usr/bin/env python3
"""
Tech Radar Engine — Y* Bridge Labs autonomous tech scouting system

Scans internal gaps against external tech catalog, generates integration proposals.
MVP: static catalog + basic keyword matching + extendable architecture.

Usage:
  python3 scripts/tech_radar.py scan                               # scan all gaps from SUBSYSTEM_INDEX + priority_brief
  python3 scripts/tech_radar.py for "agent peer collaboration"     # query specific gap
  python3 scripts/tech_radar.py update "AutoGen" mature_score=0.95 # update catalog entry
  python3 scripts/tech_radar.py list --category multi_agent_orchestration # list category
  python3 scripts/tech_radar.py match "need cross-agent memory coordination for 4 engineers" # free-text query
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import re

CATALOG_PATH = Path(__file__).parent.parent / "data" / "tech_radar_catalog.json"
REPORTS_DIR = Path(__file__).parent.parent / "reports" / "tech_radar_briefs"
WORKSPACE = Path(__file__).parent.parent


class TechRadar:
    def __init__(self, catalog_path: Path = CATALOG_PATH):
        self.catalog_path = catalog_path
        self.catalog = self._load_catalog()

    def _load_catalog(self) -> Dict:
        if not self.catalog_path.exists():
            raise FileNotFoundError(f"Catalog not found: {self.catalog_path}")
        with open(self.catalog_path) as f:
            return json.load(f)

    def _save_catalog(self):
        self.catalog["last_updated"] = datetime.now().strftime("%Y-%m-%d")
        with open(self.catalog_path, "w") as f:
            json.dump(self.catalog, f, indent=2)

    def search_by_keywords(self, query: str, top_k: int = 5) -> List[Tuple[str, Dict, float]]:
        """
        Match query against catalog entries using keyword overlap + relevance score.
        Returns: [(tech_name, tech_data, score), ...]
        """
        query_tokens = set(re.findall(r'\w+', query.lower()))
        results = []

        for category, techs in self.catalog["categories"].items():
            for tech in techs:
                # Match against: name, relevance_areas, notes, category
                tech_text = " ".join([
                    tech["name"].lower(),
                    " ".join(tech["labs_relevance_areas"]),
                    tech.get("notes", "").lower(),
                    category.replace("_", " ")  # multi_agent_orchestration → multi agent orchestration
                ])
                tech_tokens = set(re.findall(r'\w+', tech_text))

                # Score: keyword overlap + mature_score weighting + category bonus
                overlap = len(query_tokens & tech_tokens)
                if overlap > 0:
                    # Higher weight for relevance_areas match
                    relevance_match = any(token in " ".join(tech["labs_relevance_areas"]).lower() for token in query_tokens)
                    score = overlap * 10 + tech["mature_score"] * 5
                    if relevance_match:
                        score += 15  # Boost if relevance_areas match
                    results.append((tech["name"], tech, score))

        results.sort(key=lambda x: x[2], reverse=True)
        return results[:top_k]

    def match_gap_pattern(self, gap_description: str) -> List[str]:
        """Match gap description to predefined gap patterns."""
        gap_patterns = self.catalog.get("gap_patterns", {})
        matched = []

        for pattern_name, tech_list in gap_patterns.items():
            # Simple keyword matching (MVP - can be upgraded to semantic later)
            # Split pattern_name by underscore to separate words
            pattern_words = pattern_name.replace("_", " ").lower()
            gap_lower = gap_description.lower()

            # Check if any pattern word appears in gap description
            pattern_tokens = set(re.findall(r'\w+', pattern_words))
            gap_tokens = set(re.findall(r'\w+', gap_lower))

            # Fuzzy match: at least 2 overlapping tokens OR exact substring match
            overlap = pattern_tokens & gap_tokens
            if len(overlap) >= 2 or pattern_words in gap_lower:
                matched.extend(tech_list)

        return list(set(matched))  # deduplicate

    def generate_brief(self, gap_id: str, gap_description: str, top_k: int = 3) -> str:
        """Generate integration brief for a specific gap."""
        # Match by pattern first, then keyword search
        pattern_matches = self.match_gap_pattern(gap_description)
        keyword_matches = self.search_by_keywords(gap_description, top_k=top_k + 3)

        # Combine and deduplicate
        candidate_names = pattern_matches + [m[0] for m in keyword_matches]
        seen = set()
        candidates = []
        for name in candidate_names:
            if name not in seen:
                seen.add(name)
                # Fetch full data
                tech_data = self._get_tech_by_name(name)
                if tech_data:
                    candidates.append(tech_data)
            if len(candidates) >= top_k:
                break

        # Generate markdown brief
        brief = f"""# Tech Radar Brief — {gap_id}
Generated: {datetime.now().isoformat()}
Gap: {gap_description}

## Matched Technologies (Top {len(candidates)})

"""
        for i, tech in enumerate(candidates, 1):
            brief += f"""### {i}. {tech['name']}
- **Maturity**: {tech['mature_score']:.2f}/1.00
- **License**: {tech['license']}
- **GitHub**: {tech['github_url']}
- **Paper**: {tech.get('paper_url', 'N/A')}
- **Relevance**: {', '.join(tech['labs_relevance_areas'])}
- **Integration Complexity**: {tech['integration_complexity']}
- **Notes**: {tech.get('notes', 'N/A')}

**Integration Recommendation**:
"""
            # Generate recommendation based on complexity + maturity
            if tech['integration_complexity'] == 'low' and tech['mature_score'] > 0.75:
                brief += "✅ **High Priority** — Low complexity, high maturity. Recommend POC within 1 sprint.\n"
            elif tech['mature_score'] > 0.80:
                brief += "🔍 **Evaluate** — High maturity but complex integration. Needs architecture design.\n"
            elif tech['mature_score'] < 0.65:
                brief += "⚠️ **Monitor** — Early stage. Consider for research, not immediate integration.\n"
            else:
                brief += "📋 **Consider** — Moderate maturity. Evaluate against internal build cost.\n"

            brief += "\n"

        # Add action items
        brief += f"""## Next Steps
1. Review GitHub repos and papers for selected candidates
2. Create proof-of-concept branch for top-1 candidate
3. Update gap status in SUBSYSTEM_INDEX or priority_brief
4. Record decision in knowledge/{{role}}/decisions/

---
**Generated by**: Tech Radar Engine MVP
**Catalog version**: {self.catalog.get("version", "1.0")}
"""

        return brief

    def _get_tech_by_name(self, name: str) -> Optional[Dict]:
        """Get full tech data by name."""
        for category, techs in self.catalog["categories"].items():
            for tech in techs:
                if tech["name"] == name:
                    return {**tech, "category": category}
        return None

    def scan_gaps(self) -> List[str]:
        """
        Scan internal gaps from multiple sources:
        - SUBSYSTEM_INDEX dead modules
        - priority_brief today_targets
        - Y* Charter §2 gaps (if available)

        Returns list of (gap_id, gap_description) tuples.
        """
        gaps = []

        # Source 1: SUBSYSTEM_INDEX dead modules (from boot output)
        # For MVP, we'll scan priority_brief which references key gaps
        priority_brief = WORKSPACE / "reports" / "priority_brief.md"
        if priority_brief.exists():
            with open(priority_brief) as f:
                content = f.read()
                # Extract P0/P1/P2 items as gaps
                for line in content.split('\n'):
                    if '**CIEU persistence' in line:
                        gaps.append(("CIEU_persistence_断裂", "CIEU events not persisted, in-memory only, data loss on restart"))
                    if 'wisdom_extractor' in line:
                        gaps.append(("wisdom_extractor_扩读", "Expand wisdom extractor to cover experiments/ + git diff + proposals/"))
                    if 'gov_dispatch' in line or 'delegation chain' in line.lower():
                        gaps.append(("delegation_chain_invalid", "MCP grant plane vs Hook enforcement plane not aligned, chain unauthorized expansion"))

        # Hardcoded MVP gaps from Y* Charter (dogfooding known gaps)
        gaps.extend([
            ("agent_peer_collaboration", "4 engineers need cross-agent memory + task handoff without CEO mediation"),
            ("causal_chain_visualization", "CIEU events stored but no visual trace of causal chains for audit"),
            ("proactive_omission_scan", "OmissionEngine needs idle-triggered autonomous scanning"),
            ("constitutional_learning", "No mechanism for agent to learn from constitutional violations"),
            ("multi_agent_rag", "Knowledge silos per agent, no shared knowledge graph"),
        ])

        return gaps

    def update_tech(self, tech_name: str, updates: Dict[str, str]):
        """Update a tech entry in catalog."""
        for category, techs in self.catalog["categories"].items():
            for tech in techs:
                if tech["name"] == tech_name:
                    for key, value in updates.items():
                        if key in tech:
                            # Type casting
                            if key == "mature_score":
                                tech[key] = float(value)
                            else:
                                tech[key] = value
                    self._save_catalog()
                    print(f"Updated {tech_name}: {updates}")
                    return
        print(f"Tech not found: {tech_name}")

    def list_category(self, category: str):
        """List all techs in a category."""
        if category in self.catalog["categories"]:
            techs = self.catalog["categories"][category]
            print(f"=== {category} ({len(techs)} entries) ===\n")
            for tech in techs:
                print(f"- {tech['name']} (maturity: {tech['mature_score']}, complexity: {tech['integration_complexity']})")
                print(f"  {tech['github_url']}")
                print()
        else:
            print(f"Category not found: {category}")
            print(f"Available: {', '.join(self.catalog['categories'].keys())}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    radar = TechRadar()

    if command == "scan":
        # Scan all gaps and generate briefs
        gaps = radar.scan_gaps()
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        print(f"Scanning {len(gaps)} gaps...")
        for gap_id, gap_desc in gaps:
            brief = radar.generate_brief(gap_id, gap_desc, top_k=3)
            brief_path = REPORTS_DIR / f"{gap_id}_{datetime.now().strftime('%Y%m%d')}.md"
            with open(brief_path, "w") as f:
                f.write(brief)
            print(f"✓ {gap_id} → {brief_path}")

        print(f"\nGenerated {len(gaps)} briefs in {REPORTS_DIR}")

    elif command == "for":
        # Query specific gap
        if len(sys.argv) < 3:
            print("Usage: tech_radar.py for <gap_description>")
            sys.exit(1)

        gap_desc = " ".join(sys.argv[2:])
        brief = radar.generate_brief("custom_query", gap_desc, top_k=3)
        print(brief)

    elif command == "match":
        # Free-text query
        if len(sys.argv) < 3:
            print("Usage: tech_radar.py match <query>")
            sys.exit(1)

        query = " ".join(sys.argv[2:])
        results = radar.search_by_keywords(query, top_k=5)
        print(f"Top matches for: {query}\n")
        for name, tech, score in results:
            print(f"- {name} (score: {score:.1f}, maturity: {tech['mature_score']})")
            print(f"  {tech['github_url']}")
            print()

    elif command == "update":
        # Update tech entry
        if len(sys.argv) < 4:
            print("Usage: tech_radar.py update <tech_name> <field>=<value> [<field>=<value> ...]")
            sys.exit(1)

        tech_name = sys.argv[2]
        updates = {}
        for arg in sys.argv[3:]:
            if "=" in arg:
                key, value = arg.split("=", 1)
                updates[key] = value

        radar.update_tech(tech_name, updates)

    elif command == "list":
        # List category
        if "--category" in sys.argv:
            idx = sys.argv.index("--category")
            if idx + 1 < len(sys.argv):
                radar.list_category(sys.argv[idx + 1])
            else:
                print("Usage: tech_radar.py list --category <category_name>")
        else:
            # List all categories
            print("Available categories:")
            for cat in radar.catalog["categories"].keys():
                count = len(radar.catalog["categories"][cat])
                print(f"  - {cat} ({count} entries)")

    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
