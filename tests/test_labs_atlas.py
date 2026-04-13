"""
Tests for Labs Atlas — Subsystem inventory + dead code detector
"""

import os
import sys
import tempfile
from pathlib import Path
import pytest

# Add scripts to path for import
YSTAR_DIR = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
sys.path.insert(0, str(YSTAR_DIR / "scripts"))

from labs_atlas_scan import ModuleInfo, LabsAtlas
from labs_atlas_query import parse_index


class TestModuleInfo:
    def test_module_name_extraction(self):
        """Test module name extraction from file path."""
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(b"# test module\n")
            f.flush()

            module = ModuleInfo(Path(f.name), "test-subsystem")
            assert module.module_name
            assert module.subsystem == "test-subsystem"

            os.unlink(f.name)

    def test_parse_classes_and_functions(self):
        """Test extraction of classes and functions."""
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False, mode='w') as f:
            f.write("""
class TestClass:
    def method(self):
        pass

def public_function():
    pass

def _private_function():
    pass
""")
            f.flush()

            module = ModuleInfo(Path(f.name), "test")
            module.parse()

            assert "TestClass" in module.classes
            assert "public_function" in module.functions
            assert "_private_function" not in module.functions
            assert len(module.public_api()) >= 2

            os.unlink(f.name)


class TestLabsAtlas:
    def test_scan_initialization(self):
        """Test Labs Atlas initialization."""
        atlas = LabsAtlas()
        assert isinstance(atlas.modules, dict)
        assert isinstance(atlas.dead_patterns, list)

    def test_scan_finds_modules(self):
        """Test that scanner finds Python modules."""
        atlas = LabsAtlas()

        # Create temp directory with a module (NOT starting with test_)
        with tempfile.TemporaryDirectory() as tmpdir:
            module_file = Path(tmpdir) / "scanner_module.py"
            module_file.write_text("def example_func(): pass\n")

            # Temporarily modify SCAN_PATHS
            import labs_atlas_scan
            original_paths = labs_atlas_scan.SCAN_PATHS
            labs_atlas_scan.SCAN_PATHS = [(Path(tmpdir), "test-subsystem")]

            atlas.scan_all()

            # Should find at least the module
            assert len(atlas.modules) >= 1

            # Restore original paths
            labs_atlas_scan.SCAN_PATHS = original_paths

    def test_dead_pattern_detection(self):
        """Test detection of dead code patterns."""
        atlas = LabsAtlas()

        # Create a mock module with no callers and no invocation
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(b"class UnusedClass:\n    pass\n")
            f.flush()

            module = ModuleInfo(Path(f.name), "test")
            module.parse()
            module.status = "dead"
            atlas.modules[str(Path(f.name))] = module

            atlas.detect_dead_patterns()

            # Should detect dead patterns
            assert len(atlas.dead_patterns) > 0

            os.unlink(f.name)

    def test_generate_index(self):
        """Test index generation."""
        atlas = LabsAtlas()

        # Create a simple module
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as f:
            f.write(b"def test(): pass\n")
            f.flush()

            module = ModuleInfo(Path(f.name), "test-subsystem")
            module.parse()
            module.status = "active"
            atlas.modules[str(Path(f.name))] = module

            with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as out:
                atlas.generate_index(Path(out.name))

                # Check index was created
                assert Path(out.name).exists()
                content = Path(out.name).read_text()
                assert "Labs Atlas" in content
                assert "Summary" in content

                os.unlink(out.name)

            os.unlink(f.name)


class TestLabsAtlasQuery:
    def test_parse_index(self):
        """Test parsing of SUBSYSTEM_INDEX.md."""
        # Create a minimal index file
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False, mode='w') as f:
            f.write("""# Labs Atlas — Subsystem Index
Generated: 2026-04-13

## Summary
- Total modules: 1

## test-subsystem

| Module | Status | Last Invoked | Callers | Public API |
|--------|--------|--------------|---------|------------|
| `test.module` | ✅ active | 2026-04-13 | 0 | 1c, 2f |
""")
            f.flush()

            # Temporarily replace INDEX_PATH
            import labs_atlas_query
            original_path = labs_atlas_query.INDEX_PATH
            labs_atlas_query.INDEX_PATH = Path(f.name)

            data = parse_index()

            assert "test-subsystem" in data
            assert len(data["test-subsystem"]) == 1
            assert data["test-subsystem"][0]["name"] == "test.module"
            assert data["test-subsystem"][0]["callers"] == 0

            # Restore original path
            labs_atlas_query.INDEX_PATH = original_path
            os.unlink(f.name)


def test_integration_scan_and_query():
    """Integration test: scan -> generate -> query."""
    atlas = LabsAtlas()

    # Minimal scan
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test modules
        (Path(tmpdir) / "active_module.py").write_text("def func(): pass\n")
        (Path(tmpdir) / "dead_module.py").write_text("class DeadClass: pass\n")

        # Scan
        import labs_atlas_scan
        original_paths = labs_atlas_scan.SCAN_PATHS
        labs_atlas_scan.SCAN_PATHS = [(Path(tmpdir), "test-subsystem")]

        atlas.scan_all()
        atlas.detect_dead_patterns()

        # Generate index
        with tempfile.NamedTemporaryFile(suffix='.md', delete=False) as idx:
            atlas.generate_index(Path(idx.name))

            # Verify index exists
            assert Path(idx.name).exists()
            content = Path(idx.name).read_text()
            assert "test-subsystem" in content

            os.unlink(idx.name)

        # Restore
        labs_atlas_scan.SCAN_PATHS = original_paths


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
