#!/usr/bin/env python3
"""
Test suite for Tech Radar Engine MVP

Coverage:
- Catalog loading
- Keyword search
- Gap pattern matching
- Brief generation
- Update operations
- Dogfooding critical queries
"""

import pytest
import json
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from tech_radar import TechRadar, CATALOG_PATH, REPORTS_DIR


@pytest.fixture
def radar():
    """Initialize TechRadar instance."""
    return TechRadar()


def test_catalog_loads(radar):
    """Test catalog loads successfully with expected structure."""
    assert "categories" in radar.catalog
    assert "gap_patterns" in radar.catalog
    assert "version" in radar.catalog

    # Check all categories exist
    expected_categories = [
        "long_term_memory",
        "rag_variants",
        "multi_agent_orchestration",
        "reasoning",
        "tool_use",
        "self_improvement",
        "agent_dev_frameworks",
        "hermes_skill_system"
    ]
    for cat in expected_categories:
        assert cat in radar.catalog["categories"], f"Missing category: {cat}"


def test_catalog_entry_schema(radar):
    """Test each catalog entry has required fields."""
    required_fields = ["name", "github_url", "mature_score", "labs_relevance_areas", "integration_complexity", "license"]

    for category, techs in radar.catalog["categories"].items():
        for tech in techs:
            for field in required_fields:
                assert field in tech, f"{tech.get('name', 'UNKNOWN')} missing field: {field}"

            # Type checks
            assert isinstance(tech["mature_score"], (int, float)), f"{tech['name']} mature_score not numeric"
            assert 0 <= tech["mature_score"] <= 1.0, f"{tech['name']} mature_score out of range"
            assert isinstance(tech["labs_relevance_areas"], list), f"{tech['name']} relevance_areas not list"
            assert tech["integration_complexity"] in ["low", "medium", "high"], f"{tech['name']} invalid complexity"


def test_keyword_search_basic(radar):
    """Test basic keyword search returns results."""
    results = radar.search_by_keywords("multi-agent collaboration", top_k=3)

    assert len(results) > 0, "No results for basic query"
    assert len(results) <= 3, "Returned more than top_k"

    # Each result is (name, data, score)
    for name, data, score in results:
        assert isinstance(name, str)
        assert isinstance(data, dict)
        assert isinstance(score, (int, float))
        assert score > 0


def test_dogfood_agent_peer_collaboration(radar):
    """
    DOGFOOD: Query 'agent peer collaboration' MUST return AutoGen/CrewAI/LangGraph.
    This is the critical use case from Board spec.
    """
    results = radar.search_by_keywords("agent peer collaboration", top_k=5)

    result_names = [name for name, _, _ in results]

    # Must include at least 2 of the 3 key frameworks
    key_frameworks = ["AutoGen", "CrewAI", "LangGraph"]
    matched = [fw for fw in key_frameworks if fw in result_names]

    assert len(matched) >= 2, f"Expected AutoGen/CrewAI/LangGraph in top-5, got: {result_names}"


def test_gap_pattern_matching(radar):
    """Test gap pattern matching returns expected techs."""
    # Pattern: "agent_peer_collaboration"
    results = radar.match_gap_pattern("agent peer collaboration system")

    assert len(results) > 0, "No pattern match for known gap"
    assert "AutoGen" in results or "CrewAI" in results, "Expected multi-agent frameworks in pattern match"


def test_generate_brief_structure(radar):
    """Test brief generation produces valid markdown with expected sections."""
    brief = radar.generate_brief("test_gap", "agent memory and reasoning", top_k=2)

    # Check structure
    assert "# Tech Radar Brief" in brief
    assert "## Matched Technologies" in brief
    assert "## Next Steps" in brief
    assert "Tech Radar Engine MVP" in brief

    # Check contains at least 1 tech
    assert "**Maturity**:" in brief
    assert "**Integration Recommendation**:" in brief


def test_scan_gaps_returns_list(radar):
    """Test scan_gaps returns valid gap list."""
    gaps = radar.scan_gaps()

    assert isinstance(gaps, list), "scan_gaps should return list"
    assert len(gaps) > 0, "Should detect at least some gaps"

    # Each gap is (gap_id, gap_description)
    for gap in gaps:
        assert isinstance(gap, tuple), f"Gap should be tuple, got {type(gap)}"
        assert len(gap) == 2, f"Gap tuple should have 2 elements, got {len(gap)}"
        gap_id, gap_desc = gap
        assert isinstance(gap_id, str) and len(gap_id) > 0
        assert isinstance(gap_desc, str) and len(gap_desc) > 0


def test_update_tech(radar, tmp_path):
    """Test tech entry update (using tmp catalog to avoid modifying real one)."""
    # Create temp catalog copy
    tmp_catalog = tmp_path / "test_catalog.json"
    with open(CATALOG_PATH) as f:
        catalog_data = json.load(f)
    with open(tmp_catalog, "w") as f:
        json.dump(catalog_data, f)

    # Init radar with temp catalog
    temp_radar = TechRadar(catalog_path=tmp_catalog)

    # Update entry
    temp_radar.update_tech("AutoGen", {"mature_score": "0.95"})

    # Reload and verify
    with open(tmp_catalog) as f:
        updated = json.load(f)

    # Find AutoGen
    autogen = None
    for category, techs in updated["categories"].items():
        for tech in techs:
            if tech["name"] == "AutoGen":
                autogen = tech
                break

    assert autogen is not None, "AutoGen not found in catalog"
    assert autogen["mature_score"] == 0.95, "Update did not persist"


def test_catalog_urls_are_real(radar):
    """
    CRITICAL: Ensure all GitHub URLs and papers are real (not fabricated).
    We check basic URL format, not liveness (would require network).
    """
    for category, techs in radar.catalog["categories"].items():
        for tech in techs:
            github_url = tech.get("github_url", "")
            if github_url:  # Empty string is allowed for paper-only entries
                assert github_url.startswith("http"), f"{tech['name']} github_url not valid: {github_url}"
                # Known real domains
                assert any(domain in github_url for domain in ["github.com", "huggingface.co", "arxiv.org"]), \
                    f"{tech['name']} github_url suspicious: {github_url}"

            paper_url = tech.get("paper_url", "")
            if paper_url:
                assert paper_url.startswith("http"), f"{tech['name']} paper_url not valid: {paper_url}"


def test_all_licenses_non_empty(radar):
    """Ensure all entries have license field populated."""
    for category, techs in radar.catalog["categories"].items():
        for tech in techs:
            license_field = tech.get("license", "")
            # Empty string allowed if no public implementation (e.g., Toolformer)
            if tech.get("github_url"):  # If GitHub exists, license must exist
                assert license_field, f"{tech['name']} has GitHub but no license"


def test_integration_with_priority_brief(radar):
    """
    Test that scan_gaps can parse priority_brief.md and extract real gaps.
    """
    gaps = radar.scan_gaps()
    gap_ids = [gid for gid, _ in gaps]

    # Should detect at least one gap from priority_brief
    priority_gaps = ["CIEU_persistence_断裂", "delegation_chain_invalid", "wisdom_extractor_扩读"]
    detected = [g for g in priority_gaps if g in gap_ids]

    assert len(detected) > 0, f"Should detect at least 1 priority_brief gap, found: {gap_ids}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
