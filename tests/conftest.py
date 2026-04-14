"""
Shared test infrastructure for Y* Bridge Labs
Platform Engineer: Ryan Park (eng-platform)
"""
import os
import sys
from pathlib import Path
import pytest

# Add ystar-company root to Python path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Test constants
TEST_KNOWLEDGE_DIR = REPO_ROOT / "knowledge"
TEST_SCRIPTS_DIR = REPO_ROOT / "scripts"


@pytest.fixture
def repo_root():
    """Fixture providing repository root path."""
    return REPO_ROOT


@pytest.fixture
def knowledge_dir():
    """Fixture providing knowledge directory path."""
    return TEST_KNOWLEDGE_DIR


@pytest.fixture
def scripts_dir():
    """Fixture providing scripts directory path."""
    return TEST_SCRIPTS_DIR


@pytest.fixture
def temp_knowledge_dir(tmp_path):
    """Fixture providing temporary knowledge directory for isolated tests."""
    return tmp_path / "knowledge"


# Marker definitions
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: Integration tests requiring full system"
    )
    config.addinivalue_line(
        "markers", "unit: Unit tests for isolated components"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take more than 5 seconds"
    )
    config.addinivalue_line(
        "markers", "requires_gemma: Tests requiring Gemma 2B model"
    )
