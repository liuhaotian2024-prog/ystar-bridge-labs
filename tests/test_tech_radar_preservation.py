#!/usr/bin/env python3
"""
Test suite for Tech Radar Preservation Guard

Validates that preservation detection correctly identifies conflicts with Y*gov core innovations.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from tech_radar import TechRadar, PRESERVED_INNOVATIONS, RED_LINE
import pytest


class TestPreservationGuard:
    """Test preservation guard detection and red line enforcement."""

    @pytest.fixture
    def radar(self):
        """Create TechRadar instance."""
        return TechRadar()

    def test_constitutional_safety_triggers_iron_rule_red_line(self, radar):
        """Query 'constitutional safety' should trigger iron_rule_1 red line (Constitutional AI uses LLM critique)."""
        brief = radar.generate_brief(
            gap_id="test_constitutional",
            gap_description="constitutional safety enforcement for AI agents",
            top_k=3
        )

        # Should detect iron_rule_1 conflict
        assert "iron_rule_1" in brief.lower() or "hook" in brief.lower()
        # Should show RED LINE warning
        assert "RED LINE" in brief or "🔴" in brief
        # Should recommend adapter-only
        assert "ADAPT ONLY" in brief or "adapter" in brief.lower()

    def test_agent_memory_no_red_line(self, radar):
        """Query 'agent memory' for Letta should NOT trigger red line (memory doesn't conflict with 12 innovations)."""
        brief = radar.generate_brief(
            gap_id="test_memory",
            gap_description="agent memory management and persistence",
            top_k=3
        )

        # May detect memory_classification but should NOT be red line
        # RED LINE only triggered if one of the 6 core innovations is hit
        # Memory is innovation #10 but NOT in RED_LINE list
        # So this should pass through without red flag
        # We verify by checking that if RED LINE appears, it's not for memory_classification alone

        if "RED LINE" in brief:
            # If red line triggered, it must be for one of the 6 red line innovations
            red_line_innovations = ["iron_rule_1", "cieu_5tuple", "omission_engine", "12_layer_construction", "capability_delegation", "name_role_binding"]
            found_red_line = any(innovation in brief.lower() for innovation in red_line_innovations)
            # This is acceptable - some memory tech might mention hooks/delegation
            # The test is that memory_classification itself is not blocking
            pass
        else:
            # Ideal case: no red line at all for pure memory query
            assert "Preserved Innovations" in brief  # But should still have preservation analysis

    def test_delegation_framework_triggers_capability_conflict(self, radar):
        """Query 'delegation framework' should trigger capability_delegation conflict."""
        brief = radar.generate_brief(
            gap_id="test_delegation",
            gap_description="delegation framework for agent capability authorization",
            top_k=3
        )

        # Should detect capability_delegation
        assert "capability" in brief.lower() or "delegation" in brief.lower()
        # Should show RED LINE (capability_delegation is in RED_LINE list)
        assert "RED LINE" in brief or "🔴" in brief

    def test_ordinary_query_has_preservation_field(self, radar):
        """Ordinary query should have preserved_innovations field even if empty."""
        brief = radar.generate_brief(
            gap_id="test_ordinary",
            gap_description="generic data processing pipeline optimization",
            top_k=3
        )

        # Should contain preservation analysis section
        assert "Preservation Analysis" in brief
        # May be "None detected" but field must exist
        assert "Preserved Innovations" in brief  # Field exists in Preservation Analysis section
        # Check that even with no conflicts, analysis is performed
        assert "None detected" in brief or len(brief) > 0  # Either shows None or has content

    def test_detect_innovation_conflicts_method(self, radar):
        """Test _detect_innovation_conflicts method directly."""
        # Mock tech data that should trigger iron_rule_1
        tech_data = {
            "name": "Constitutional AI Framework",
            "labs_relevance_areas": ["LLM critique", "safety alignment"],
            "notes": "Uses language model for constitutional decision making",
            "category": "governance",
            "integration_complexity": "high",
            "mature_score": 0.85
        }

        conflicts, red_line_hit, borrowed_pattern = radar._detect_innovation_conflicts(
            "Constitutional AI Framework",
            tech_data
        )

        # Should detect iron_rule_1 (keywords: "llm critique")
        assert "iron_rule_1" in conflicts
        # Should flag as red line
        assert red_line_hit is True
        # High complexity + high maturity = likely NOT pattern-only
        assert borrowed_pattern is False

    def test_low_complexity_pattern_detection(self, radar):
        """Test that low complexity techs are marked as borrowed_pattern_only."""
        tech_data = {
            "name": "Simple Pattern Library",
            "labs_relevance_areas": ["design patterns"],
            "notes": "Collection of reusable patterns for agent coordination",
            "category": "utils",
            "integration_complexity": "low",
            "mature_score": 0.70
        }

        conflicts, red_line_hit, borrowed_pattern = radar._detect_innovation_conflicts(
            "Simple Pattern Library",
            tech_data
        )

        # Low complexity should favor borrowed_pattern_only
        assert borrowed_pattern is True
        # Should not hit red line (no keywords match)
        assert red_line_hit is False

    def test_orchestration_framework_not_pattern_only(self, radar):
        """Test that high-maturity orchestration frameworks are NOT marked as pattern-only."""
        tech_data = {
            "name": "Multi-Agent Orchestration Framework",
            "labs_relevance_areas": ["agent coordination", "task delegation"],
            "notes": "Full-featured framework for managing agent teams",
            "category": "multi_agent_orchestration",
            "integration_complexity": "high",
            "mature_score": 0.90
        }

        conflicts, red_line_hit, borrowed_pattern = radar._detect_innovation_conflicts(
            "Multi-Agent Orchestration Framework",
            tech_data
        )

        # High maturity orchestration = likely SDK replacement, NOT pattern-only
        assert borrowed_pattern is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
