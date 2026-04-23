#!/usr/bin/env python3
"""
Tests for Y* Field Validator — F1 Goodhart failure mode detection.

4 atomic tests covering:
- Valid m_functor (keyword match)
- Wishful m_functor (no keyword match — F1 Goodhart)
- Missing m_functor (None)
- Unknown axis (not in whitelist)
"""
import os
import sys

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from ystar.governance.y_star_field_validator import validate_m_functor


def test_valid_m_functor():
    """M-3 + task with 'customer demo' keywords -> VALID (1)."""
    result = validate_m_functor("M-3", "build customer demo for enterprise pipeline")
    assert result == 1, f"Expected 1 (VALID), got {result}"


def test_wishful_m_functor():
    """M-3 + task with zero M-3 keywords -> WISHFUL (-1, F1 Goodhart)."""
    result = validate_m_functor("M-3", "routine maintenance cleanup")
    assert result == -1, f"Expected -1 (WISHFUL), got {result}"


def test_missing_m_functor():
    """None m_functor -> SKIP (0)."""
    result = validate_m_functor(None, "any task description here")
    assert result == 0, f"Expected 0 (SKIP), got {result}"


def test_unknown_axis():
    """M-99 (not in whitelist) -> SKIP (0)."""
    result = validate_m_functor("M-99", "any task description here")
    assert result == 0, f"Expected 0 (SKIP), got {result}"
