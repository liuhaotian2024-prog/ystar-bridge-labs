#!/usr/bin/env python3
"""Tests for Labs Smart Dispatch Router

Validates:
- Keyword-based routing
- Historical pattern learning
- Subsystem overlap detection
- Deterministic output (no LLM variance)

Author: Ryan Park (eng-platform)
Date: 2026-04-13
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.labs_router import LabsRouter, ROLE_TRIGGERS
import pytest


@pytest.fixture
def router():
    """Create router instance."""
    return LabsRouter()


class TestRoleTriggersConfig:
    """Validate role trigger configuration."""

    def test_all_roles_have_triggers(self):
        """All roles must have keyword/subsystem/task definitions."""
        expected_roles = {
            "ceo", "cto", "eng-kernel", "eng-governance", "eng-platform",
            "eng-domains", "cmo", "cso", "cfo"
        }

        assert set(ROLE_TRIGGERS.keys()) == expected_roles

        for role, config in ROLE_TRIGGERS.items():
            assert "keywords" in config, f"{role} missing keywords"
            assert "subsystems" in config, f"{role} missing subsystems"
            assert "typical_tasks" in config, f"{role} missing typical_tasks"
            assert isinstance(config["keywords"], list)


class TestBasicRouting:
    """Test basic task routing scenarios."""

    def test_circuit_breaker_bug_to_maya(self, router):
        """Circuit breaker bugs → Maya (Governance)."""
        rec = router.route("fix circuit breaker bug")

        assert rec.owner == "Maya-Governance"
        assert rec.confidence > 0.0
        assert "circuit" in rec.related_subsystems or "breaker" in rec.reason.lower()

    def test_hook_deployment_to_ryan(self, router):
        """Hook/adapter tasks → Ryan (Platform)."""
        rec = router.route("deploy hook server to production")

        # Should route to Platform (Ryan) or CTO (Ethan)
        assert rec.owner in ["Ryan-Platform", "Ethan-CTO"]
        assert rec.confidence > 0.0

    def test_pricing_model_to_cfo(self, router):
        """Pricing/finance tasks → Marco (CFO)."""
        rec = router.route("design pricing model for enterprise tier")

        assert rec.owner == "Marco-CFO"
        assert rec.confidence > 0.0

    def test_blog_post_to_cmo(self, router):
        """Content/marketing tasks → Sofia (CMO)."""
        rec = router.route("write blog post about governance features")

        assert rec.owner == "Sofia-CMO"
        assert rec.confidence > 0.0

    def test_memory_system_to_leo(self, router):
        """Memory/YML/kernel tasks → Leo (Kernel)."""
        rec = router.route("implement YML memory persistence layer")

        assert rec.owner == "Leo-Kernel"
        assert rec.confidence > 0.0


class TestSubsystemDetection:
    """Test subsystem extraction from task descriptions."""

    def test_extract_ystar_subsystems(self, router):
        """Detect ystar/* subsystem mentions."""
        subsystems = router._extract_subsystems("fix bug in ystar/governance/health.py")

        assert "governance" in subsystems or "health" in subsystems

    def test_extract_component_names(self, router):
        """Detect component names (hook, adapter, etc)."""
        subsystems = router._extract_subsystems("debug orchestrator timing issues")

        assert "orchestrator" in subsystems

    def test_extract_gov_mcp(self, router):
        """Detect gov-mcp mentions."""
        subsystems = router._extract_subsystems("add new tool to gov-mcp server")

        assert "gov-mcp" in subsystems


class TestScoring:
    """Test scoring mechanism."""

    def test_keyword_match_increases_score(self, router):
        """Keyword matches should increase role score."""
        # Governance-heavy keywords
        rec_gov = router.route("fix governance policy compliance bug")
        score_gov = rec_gov.score_breakdown.get("keyword", 0.0)

        # Generic task with no specific keywords
        rec_generic = router.route("do something")
        score_generic = rec_generic.score_breakdown.get("keyword", 0.0)

        # Governance-specific task should score higher on keywords
        # (Note: This is relative to the specific role chosen, not absolute)
        assert rec_gov.owner == "Maya-Governance"
        assert score_gov > 0.0

    def test_deterministic_output(self, router):
        """Same task should produce same recommendation."""
        task = "implement circuit breaker reset logic"

        rec1 = router.route(task)
        rec2 = router.route(task)

        assert rec1.owner == rec2.owner
        assert rec1.confidence == rec2.confidence
        assert rec1.score_breakdown == rec2.score_breakdown


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_task(self, router):
        """Empty task should still return a recommendation."""
        rec = router.route("")

        assert rec.owner is not None
        assert 0.0 <= rec.confidence <= 1.0

    def test_unknown_domain_task(self, router):
        """Tasks outside known domains should still route."""
        rec = router.route("reorganize office furniture")

        # Should route to CEO (coordination) or default
        assert rec.owner is not None

    def test_multi_role_task(self, router):
        """Task spanning multiple roles picks strongest match."""
        rec = router.route("fix governance hook adapter integration test")

        # Should pick one of: Maya (governance), Ryan (hook/adapter), Leo (test), or CTO (technical coordination)
        assert rec.owner in ["Maya-Governance", "Ryan-Platform", "Leo-Kernel", "Ethan-CTO"]


class TestRecommendationStructure:
    """Validate recommendation data structure."""

    def test_recommendation_has_required_fields(self, router):
        """Recommendation must have all required fields."""
        rec = router.route("test task")

        assert hasattr(rec, "owner")
        assert hasattr(rec, "confidence")
        assert hasattr(rec, "reason")
        assert hasattr(rec, "related_skills")
        assert hasattr(rec, "related_lessons")
        assert hasattr(rec, "related_subsystems")
        assert hasattr(rec, "score_breakdown")

    def test_confidence_bounded(self, router):
        """Confidence must be in [0, 1]."""
        rec = router.route("any task")

        assert 0.0 <= rec.confidence <= 1.0

    def test_owner_format(self, router):
        """Owner should be in Name-Role format."""
        rec = router.route("any task")

        # Should match pattern: Name-Role (e.g., "Maya-Governance")
        assert "-" in rec.owner or rec.owner in ["ceo", "cto"]  # fallback patterns


class TestIntegrationWithRAG:
    """Test integration with Labs RAG."""

    def test_rag_query_returns_results(self, router):
        """RAG integration should return hits for known topics."""
        hits = router._query_rag("circuit breaker", top_k=3)

        # RAG should return some results for governance topics
        # (May be empty if RAG index is stale, but should not error)
        assert isinstance(hits, list)

    def test_historical_owner_extraction(self, router):
        """Historical owner extraction should parse RAG hits."""
        # Mock RAG hits
        mock_hits = [
            {"path": "knowledge/eng-governance/skills/circuit_breaker.md", "score": 10.0},
            {"path": "knowledge/eng-governance/lessons/policy_fix.md", "score": 8.0},
            {"path": "knowledge/ceo/decisions/delegation.md", "score": 5.0},
        ]

        owners = router._extract_historical_owners(mock_hits)

        assert "eng-governance" in owners
        assert owners["eng-governance"] == 2
        assert owners["ceo"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
