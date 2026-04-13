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

# Y*gov Core Innovations — Preservation Guard (from knowledge/ceo/lessons/innovation_preservation_guard_2026_04_13.md)
PRESERVED_INNOVATIONS = {
    "iron_rule_1": ["hook", "zero llm", "deterministic", "constitutional ai", "llm critique"],
    "cieu_5tuple": ["cieu", "5-tuple", "5tuple", "xt u y* yt+1 rt+1", "mathematical form"],
    "omission_engine": ["omission", "未发生", "missing detection", "what didn't happen", "reverse detection"],
    "12_layer_construction": ["第十一条", "12层", "12 layer", "l0-l12", "cognitive construction"],
    "capability_delegation": ["capability", "gov_delegate", "monotonicity", "delegation chain", "rbac", "acl"],
    "name_role_binding": ["name-role", "aiden-ceo", "behavior rules", "c-suite identity", "agent role placeholder"],
    "boot_contract": ["193 constraints", "11 category", "boot contract", "code-enforced", "hard constraints"],
    "dogfooding_product": ["dogfooding", "company as product", "self-governance", "product validation"],
    "autonomy_engine": ["autonomyengine", "ade", "prescriptive dual", "detector driver", "omission autonomy"],
    "memory_classification": ["4类记忆", "4 memory types", "relevance scoring", "memory classification"],
    "amendment_evolution": ["amendment", "dasc", "governance evolution", "self-evolution protocol"],
    "three_modes": ["break-glass", "autonomous", "standard", "mode switching", "human-ai collaboration mode"]
}

# Red Line Innovations — Conflicts require adapter-only approach
RED_LINE = ["iron_rule_1", "cieu_5tuple", "omission_engine", "12_layer_construction", "capability_delegation", "name_role_binding"]


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

    def _detect_innovation_conflicts(self, tech_name: str, tech_data: Dict) -> Tuple[List[str], bool, bool]:
        """
        Detect potential conflicts with Y*gov core innovations.
        Returns: (preserved_innovations, is_red_line_conflict, borrowed_pattern_only)
        """
        # Build search text from tech data
        search_text = " ".join([
            tech_name.lower(),
            " ".join(tech_data.get("labs_relevance_areas", [])),
            tech_data.get("notes", "").lower(),
            tech_data.get("category", "")
        ])

        detected_conflicts = []
        red_line_hit = False

        # Scan for keyword matches
        for innovation_key, keywords in PRESERVED_INNOVATIONS.items():
            for keyword in keywords:
                if keyword.lower() in search_text:
                    detected_conflicts.append(innovation_key)
                    if innovation_key in RED_LINE:
                        red_line_hit = True
                    break  # One hit per innovation is enough

        # Determine borrowed_pattern_only
        # High complexity OR framework-level = likely SDK replacement (bad)
        # Low complexity OR mentions "pattern"/"idea"/"approach" = likely pattern borrow (good)
        borrowed_pattern_only = (
            tech_data.get("integration_complexity") == "low"
            or "pattern" in search_text
            or "idea" in search_text
            or "approach" in search_text
        )

        # Override: if it's a framework/orchestration tool with high maturity, likely SDK replacement
        if tech_data.get("category") == "multi_agent_orchestration" and tech_data.get("mature_score", 0) > 0.8:
            borrowed_pattern_only = False

        return list(set(detected_conflicts)), red_line_hit, borrowed_pattern_only

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

        # Detect preservation conflicts for all candidates
        any_red_line = False
        for tech in candidates:
            conflicts, red_line_hit, borrowed_pattern = self._detect_innovation_conflicts(tech["name"], tech)
            tech["preserved_innovations"] = conflicts
            tech["red_line_conflict"] = red_line_hit
            tech["borrowed_pattern_only"] = borrowed_pattern
            if red_line_hit:
                any_red_line = True

        # Generate markdown brief
        brief = f"""# Tech Radar Brief — {gap_id}
Generated: {datetime.now().isoformat()}
Gap: {gap_description}

"""

        # Add RED LINE warning if any tech has red line conflict
        if any_red_line:
            brief += """## ⚠️ RED LINE — Adapt-Only Required

**CRITICAL**: One or more candidates conflict with Y*gov core innovations that define our product differentiation.

**Rules**:
1. Borrow IDEA/pattern only — DO NOT import SDK or allow framework replacement
2. Build Y*gov-native adapter wrapping the borrowed concept
3. Preserve mathematical form, enforcement mechanisms, and cognitive architecture

**Why**: Y* Bridge Labs' value is "governance-as-dogfooding" — if core innovations are replaced by external frameworks, we become another LangGraph/AutoGen demo. External tech is training equipment, not organ replacement.

Conflicting innovations flagged below with 🔴.

---

"""

        brief += f"""## Matched Technologies (Top {len(candidates)})

"""
        for i, tech in enumerate(candidates, 1):
            red_flag = "🔴 " if tech["red_line_conflict"] else ""
            brief += f"""### {i}. {red_flag}{tech['name']}
- **Maturity**: {tech['mature_score']:.2f}/1.00
- **License**: {tech['license']}
- **GitHub**: {tech['github_url']}
- **Paper**: {tech.get('paper_url', 'N/A')}
- **Relevance**: {', '.join(tech['labs_relevance_areas'])}
- **Integration Complexity**: {tech['integration_complexity']}
- **Notes**: {tech.get('notes', 'N/A')}

**Preservation Analysis**:
- **Preserved Innovations**: {', '.join(tech['preserved_innovations']) if tech['preserved_innovations'] else 'None detected'}
- **Red Line Conflict**: {'YES — Adapter-only integration' if tech['red_line_conflict'] else 'No'}
- **Borrowed Pattern Only**: {'YES — Extract idea/pattern' if tech['borrowed_pattern_only'] else 'NO — Requires SDK/framework integration'}

**Integration Recommendation**:
"""
            # Generate recommendation based on preservation + complexity + maturity
            if tech['red_line_conflict']:
                brief += "🔴 **ADAPT ONLY** — Core innovation conflict detected. Borrow the concept/pattern, build Y*gov-native implementation. DO NOT import SDK.\n"
                brief += f"   - Conflicts: {', '.join([c for c in tech['preserved_innovations'] if c in RED_LINE])}\n"
                brief += "   - Recommended: Create adapter in ystar/adapters/ that wraps external idea into Y*gov primitives\n"
            elif tech['integration_complexity'] == 'low' and tech['mature_score'] > 0.75:
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
2. For RED LINE conflicts: Design adapter architecture before any implementation
3. For non-conflicts: Create proof-of-concept branch for top-1 candidate
4. Update gap status in SUBSYSTEM_INDEX or priority_brief
5. Record decision in knowledge/{{role}}/decisions/ with preservation rationale

---
**Generated by**: Tech Radar Engine MVP + Preservation Guard
**Catalog version**: {self.catalog.get("version", "1.0")}
**Preservation Guard**: Active — 12 core innovations, 6 red lines
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
