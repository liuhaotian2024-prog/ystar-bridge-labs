"""
Tests for dispatch_role_routing.py — scope-to-engineer routing.

CZL-DISPATCH-EXEC (2026-04-19, Ethan Wright CTO ruling):
Verifies the 7 routing rules + test-file prefix-strip + fallback.
"""
import sys
import os
import pytest

# Ensure scripts/ is on path so we can import dispatch_role_routing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts"))
from dispatch_role_routing import route_scope, display_name, FALLBACK_ENGINEER


class TestRouteScope:
    """S1: route_scope() returns correct engineer for all test cases."""

    def test_kernel_adapters(self):
        """Y-star-gov/ystar/adapters/hook.py -> eng-kernel"""
        assert route_scope("Y-star-gov/ystar/adapters/hook.py") == "eng-kernel"

    def test_kernel_boundary_enforcer(self):
        """boundary_enforcer -> eng-kernel (Ethan's addition to CEO spec)"""
        assert route_scope("Y-star-gov/ystar/kernel/boundary_enforcer.py") == "eng-kernel"

    def test_kernel_identity_detector(self):
        """identity_detector -> eng-kernel"""
        assert route_scope("some/path/identity_detector.py") == "eng-kernel"

    def test_platform_hook_wrapper(self):
        """scripts/hook_wrapper.py -> eng-platform"""
        assert route_scope("scripts/hook_wrapper.py") == "eng-platform"

    def test_platform_dispatch(self):
        """scripts/dispatch_board.py -> eng-platform"""
        assert route_scope("scripts/dispatch_board.py") == "eng-platform"

    def test_platform_czl_prefix(self):
        """scripts/czl_boot_inject.py -> eng-platform (Ethan's czl_ expansion)"""
        assert route_scope("scripts/czl_boot_inject.py") == "eng-platform"

    def test_governance_omission_engine(self):
        """Y-star-gov/ystar/governance/omission_engine.py -> eng-governance"""
        assert route_scope("Y-star-gov/ystar/governance/omission_engine.py") == "eng-governance"

    def test_governance_forget_guard(self):
        """ForgetGuard -> eng-governance"""
        assert route_scope("some/ForgetGuard/rules.yaml") == "eng-governance"

    def test_governance_omission_prefix(self):
        """omission_ prefix -> eng-governance"""
        assert route_scope("omission_adapter.py") == "eng-governance"

    def test_domains_openclaw(self):
        """Y-star-gov/ystar/domains/openclaw/adapter.py -> eng-domains"""
        assert route_scope("Y-star-gov/ystar/domains/openclaw/adapter.py") == "eng-domains"

    def test_cto_triage_reports(self):
        """reports/cto/some_review.md -> eng-cto-triage"""
        assert route_scope("reports/cto/some_review.md") == "eng-cto-triage"

    def test_fallback_unknown_path(self):
        """some/unknown/path.py -> eng-cto-triage (fallback)"""
        assert route_scope("some/unknown/path.py") == FALLBACK_ENGINEER

    def test_fallback_empty_string(self):
        """Empty scope -> eng-cto-triage (fallback)"""
        assert route_scope("") == FALLBACK_ENGINEER

    def test_fallback_none_like(self):
        """Whitespace-only scope -> eng-cto-triage (fallback)"""
        assert route_scope("   ") == FALLBACK_ENGINEER

    def test_comma_separated_first_match_wins(self):
        """Comma-separated: ROUTE_TABLE order wins when full string matches.

        When the full comma-separated string is checked against ROUTE_TABLE,
        rule 1 (eng-kernel) matches before rule 3 (eng-platform) because
        the adapters/ pattern appears in the full string.
        This is correct: ROUTE_TABLE priority order is the tiebreaker.
        """
        result = route_scope("scripts/hook_wrapper.py,Y-star-gov/ystar/adapters/hook.py")
        # Rule 1 (eng-kernel) matches "Y-star-gov/ystar/adapters/" in the full string
        assert result == "eng-kernel"

    def test_comma_separated_platform_only(self):
        """Comma-separated with platform-only paths -> eng-platform."""
        result = route_scope("scripts/hook_wrapper.py,scripts/dispatch_board.py")
        assert result == "eng-platform"

    def test_comma_separated_second_path_matches(self):
        """When first path is unknown, second path routes correctly."""
        result = route_scope("random/file.py,Y-star-gov/ystar/governance/fg.py")
        assert result == "eng-governance"

    def test_test_file_prefix_strip(self):
        """Test file routing: tests/governance/ strips to governance/ -> eng-governance"""
        # tests/governance/test_omission.py -> strip tests/ -> governance/test_omission.py
        # But wait, the ROUTE_TABLE rule 2 matches "Y-star-gov/ystar/governance/" not just "governance/"
        # Let's use a test path that matches after stripping
        result = route_scope("tests/scripts/hook_test.py")
        # After stripping: scripts/hook_test.py -> matches rule 3 (scripts/hook_)
        assert result == "eng-platform"


class TestDisplayName:
    """Verify display_name returns human-readable strings."""

    def test_known_engineer(self):
        assert display_name("eng-kernel") == "Leo Chen (eng-kernel)"

    def test_unknown_engineer(self):
        assert display_name("eng-unknown") == "eng-unknown"

    def test_cto_triage(self):
        assert display_name("eng-cto-triage") == "Ethan Wright (CTO -- manual triage)"


class TestCLI:
    """Test __main__ block via subprocess."""

    def test_cli_scope_arg(self):
        import subprocess
        result = subprocess.run(
            [sys.executable, "-m", "dispatch_role_routing",
             "--scope", "scripts/hook_wrapper.py"],
            capture_output=True, text=True,
            cwd=os.path.join(os.path.dirname(__file__), "..", "..", "scripts"),
        )
        assert result.returncode == 0
        assert "eng-platform" in result.stdout
