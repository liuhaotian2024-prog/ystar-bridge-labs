#!/usr/bin/env python3
"""
Labs Atlas Scanner — Subsystem inventory + dead code detector
Part of CEO's full-scope insight pipeline (pre-ADE/RLE).

Scans Y*gov, gov-mcp, and Labs scripts to:
1. List all modules and their public APIs
2. Track last invocation time via CIEU
3. Build caller graph
4. Detect dead patterns (exported but never imported)

Output: SUBSYSTEM_INDEX.md
"""

import ast
import os
import re
import sqlite3
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional

# Workspace roots
YSTAR_COMPANY = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
YSTAR_GOV = Path("/Users/haotianliu/.openclaw/workspace/Y-star-gov")
GOV_MCP = YSTAR_COMPANY / "gov-mcp"  # Assuming gov-mcp is under ystar-company

# Scan targets
SCAN_PATHS = [
    (YSTAR_GOV / "ystar" / "governance", "Y*gov-governance"),
    (YSTAR_GOV / "ystar" / "adapters", "Y*gov-adapters"),
    (GOV_MCP / "gov_mcp" if GOV_MCP.exists() else YSTAR_COMPANY / "tools" / "cieu" / "ygva", "gov-mcp"),
    (YSTAR_COMPANY / "scripts", "Labs-scripts"),
]

# CIEU database
CIEU_DB = YSTAR_COMPANY / ".ystar_cieu.db"

class ModuleInfo:
    def __init__(self, path: Path, subsystem: str):
        self.path = path
        self.subsystem = subsystem
        self.module_name = self._get_module_name()
        self.classes: List[str] = []
        self.functions: List[str] = []
        self.imports: List[str] = []
        self.last_invoked: Optional[datetime] = None
        self.callers: Set[str] = set()
        self.status = "unknown"

    def _get_module_name(self) -> str:
        """Convert file path to module name."""
        rel_path = self.path.relative_to(self.path.parents[len(self.path.parents) - 1])
        return str(rel_path.with_suffix("")).replace(os.sep, ".")

    def parse(self):
        """Extract classes, functions, and imports."""
        try:
            with open(self.path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read(), filename=str(self.path))

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self.classes.append(node.name)
                elif isinstance(node, ast.FunctionDef) and not node.name.startswith("_"):
                    self.functions.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.imports.append(node.module)
        except Exception as e:
            print(f"Warning: Failed to parse {self.path}: {e}")

    def public_api(self) -> List[str]:
        """Return list of public API names."""
        return self.classes + self.functions


class LabsAtlas:
    def __init__(self):
        self.modules: Dict[str, ModuleInfo] = {}
        self.caller_graph: Dict[str, Set[str]] = defaultdict(set)
        self.dead_patterns: List[Tuple[str, str, str]] = []  # (module, symbol, reason)

    def scan_all(self):
        """Scan all target directories."""
        print("🔍 Scanning subsystems...")
        for scan_path, subsystem in SCAN_PATHS:
            if not scan_path.exists():
                print(f"⚠️  Skipping {subsystem}: {scan_path} not found")
                continue
            self._scan_directory(scan_path, subsystem)

        print(f"✅ Found {len(self.modules)} modules")

    def _scan_directory(self, root: Path, subsystem: str):
        """Recursively scan directory for Python modules."""
        for py_file in root.rglob("*.py"):
            if py_file.name.startswith("__") or "test_" in py_file.name:
                continue

            module = ModuleInfo(py_file, subsystem)
            module.parse()
            self.modules[str(py_file)] = module

    def build_caller_graph(self):
        """Build who-calls-whom graph by grepping imports + execution patterns."""
        print("🔗 Building caller graph (v2: enhanced detection)...")

        for module_path, module in self.modules.items():
            module_stem = module.path.stem  # e.g., "boundary_enforcer"
            module_name = module.module_name.split(".")[-1]  # Last component

            # 1. Standard import patterns
            import_patterns = [
                f"from .* import .*{module_name}",
                f"import .*{module_name}",
                f"from ystar\\..*{module_name} import",  # Submodule imports
            ]

            for search_root, _ in SCAN_PATHS:
                if not search_root.exists():
                    continue

                for pattern in import_patterns:
                    try:
                        result = os.popen(f"grep -r -l '{pattern}' {search_root} --include='*.py' 2>/dev/null").read()
                        for caller_file in result.strip().split('\n'):
                            if caller_file and caller_file != str(module.path):
                                module.callers.add(caller_file)
                    except Exception:
                        pass

            # 2. Cron job executions (scripts/*.py called by crontab)
            if module.subsystem == "Labs-scripts":
                try:
                    crontab = os.popen("crontab -l 2>/dev/null").read()
                    if module_stem in crontab:
                        module.callers.add("crontab")
                except Exception:
                    pass

            # 3. Hook config executions (.claude/settings.json)
            if module.subsystem == "Labs-scripts":
                try:
                    hook_config = YSTAR_COMPANY / ".claude" / "settings.json"
                    if hook_config.exists():
                        with open(hook_config) as f:
                            config_text = f.read()
                            if module_stem in config_text:
                                module.callers.add("hook:SessionStart")
                except Exception:
                    pass

            # 4. Shell wrapper executions (scripts/*.sh calling python3 scripts/X.py)
            if module.subsystem == "Labs-scripts":
                try:
                    for sh_file in (YSTAR_COMPANY / "scripts").glob("*.sh"):
                        with open(sh_file) as f:
                            sh_content = f.read()
                            # Match: python3 scripts/X.py or python3.11 scripts/X.py
                            if re.search(rf'python3(?:\.11)?\s+.*{module_stem}\.py', sh_content):
                                module.callers.add(str(sh_file))
                except Exception:
                    pass

            # 5. MCP tool registrations (gov_mcp/server.py or tools/cieu/ygva)
            # Check if this module is referenced in MCP server tool registration
            mcp_paths = [
                YSTAR_COMPANY / "gov-mcp" / "gov_mcp" / "server.py",
                YSTAR_COMPANY / "tools" / "cieu" / "ygva" / "governor.py",
            ]
            for mcp_file in mcp_paths:
                if mcp_file.exists():
                    try:
                        with open(mcp_file) as f:
                            mcp_content = f.read()
                            if module_stem in mcp_content or module_name in mcp_content:
                                module.callers.add(f"mcp:{mcp_file.name}")
                    except Exception:
                        pass

    def query_cieu_invocations(self):
        """Query CIEU database for last invocation times."""
        print("📊 Querying CIEU for invocation history...")

        if not CIEU_DB.exists():
            print("⚠️  CIEU database not found, skipping invocation tracking")
            return

        try:
            conn = sqlite3.connect(str(CIEU_DB))
            cursor = conn.cursor()

            for module_path, module in self.modules.items():
                # Query for any event mentioning this module
                module_stem = module.path.stem

                cursor.execute("""
                    SELECT MAX(created_at) FROM cieu_events
                    WHERE file_path LIKE ? OR command LIKE ? OR skill_name LIKE ?
                """, (f"%{module_stem}%", f"%{module_stem}%", f"%{module_stem}%"))

                result = cursor.fetchone()
                if result and result[0]:
                    module.last_invoked = datetime.fromtimestamp(result[0])

            conn.close()
        except Exception as e:
            print(f"⚠️  CIEU query failed: {e}")

    def detect_dead_patterns(self):
        """Detect modules/symbols that are exported but never consumed."""
        print("🔍 Detecting dead code patterns (v2: caller-aware)...")

        now = datetime.now()
        dormant_threshold = now - timedelta(days=7)
        dead_threshold = now - timedelta(days=30)

        for module_path, module in self.modules.items():
            # Enhanced status determination (v2)
            has_callers = len(module.callers) > 0
            has_invocation = module.last_invoked is not None

            if has_invocation:
                # Has CIEU records - use timestamp-based logic
                if module.last_invoked >= dormant_threshold:
                    module.status = "active"
                elif module.last_invoked >= dead_threshold:
                    module.status = "dormant"
                elif not has_callers:
                    module.status = "dead"
                    self.dead_patterns.append((
                        module.subsystem,
                        module.module_name,
                        f"Last invoked {(now - module.last_invoked).days}d ago, no callers"
                    ))
                else:
                    module.status = "dormant"
            else:
                # No CIEU records - rely on caller graph
                if has_callers:
                    # Has callers but no CIEU: likely a library/adapter module
                    caller_sources = [str(c) for c in module.callers]

                    # Check if actively used (has cron/hook/shell/MCP callers)
                    active_caller_patterns = ["crontab", "hook:", ".sh", "mcp:"]
                    has_active_caller = any(
                        any(pattern in caller for pattern in active_caller_patterns)
                        for caller in caller_sources
                    )

                    # Also check if imported by production code (non-test files)
                    has_production_caller = any(
                        "test_" not in caller and "/tests/" not in caller
                        for caller in caller_sources
                        if not any(p in caller for p in active_caller_patterns)
                    )

                    if has_active_caller or has_production_caller:
                        module.status = "active"
                    else:
                        # Has callers but no active execution context (only test imports)
                        module.status = "unknown"
                else:
                    # No callers, no invocation - truly dead
                    module.status = "dead"
                    self.dead_patterns.append((
                        module.subsystem,
                        module.module_name,
                        "Never invoked, no callers"
                    ))

            # Check for instantiated-but-never-consumed classes
            for cls in module.classes:
                # Grep for class usage across all repos
                used = False
                for search_root, _ in SCAN_PATHS:
                    if not search_root.exists():
                        continue
                    result = os.popen(f"grep -r '{cls}(' {search_root} --include='*.py' 2>/dev/null").read()
                    if result.strip() and str(module.path) not in result:
                        used = True
                        break

                if not used and module.status in ["dead", "dormant"]:
                    self.dead_patterns.append((
                        module.subsystem,
                        f"{module.module_name}.{cls}",
                        "Class exported but never instantiated"
                    ))

    def generate_index(self, output_path: Path):
        """Generate SUBSYSTEM_INDEX.md."""
        print(f"📝 Generating {output_path}...")

        sections = defaultdict(list)
        for module_path, module in self.modules.items():
            sections[module.subsystem].append(module)

        with open(output_path, 'w') as f:
            f.write("# Labs Atlas — Subsystem Index\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write("## Summary\n\n")
            f.write(f"- Total modules: {len(self.modules)}\n")
            f.write(f"- Active: {sum(1 for m in self.modules.values() if m.status == 'active')}\n")
            f.write(f"- Dormant (7d+): {sum(1 for m in self.modules.values() if m.status == 'dormant')}\n")
            f.write(f"- Dead (30d+, no callers): {sum(1 for m in self.modules.values() if m.status == 'dead')}\n")
            f.write(f"- Unknown: {sum(1 for m in self.modules.values() if m.status == 'unknown')}\n\n")

            # Dead patterns section
            if self.dead_patterns:
                f.write("## Dead Code Patterns\n\n")
                f.write("| Subsystem | Symbol | Reason |\n")
                f.write("|-----------|--------|--------|\n")
                for subsystem, symbol, reason in self.dead_patterns[:20]:  # Top 20
                    f.write(f"| {subsystem} | `{symbol}` | {reason} |\n")
                f.write("\n")

            # Per-subsystem details
            for subsystem in sorted(sections.keys()):
                f.write(f"## {subsystem}\n\n")
                f.write("| Module | Status | Last Invoked | Callers | Public API |\n")
                f.write("|--------|--------|--------------|---------|------------|\n")

                for module in sorted(sections[subsystem], key=lambda m: (m.status, m.module_name)):
                    last_inv = module.last_invoked.strftime("%Y-%m-%d") if module.last_invoked else "never"
                    callers_count = len(module.callers)
                    api_summary = f"{len(module.classes)}c, {len(module.functions)}f"

                    status_emoji = {
                        "active": "✅",
                        "dormant": "⚠️",
                        "dead": "💀",
                        "unknown": "❓"
                    }.get(module.status, "❓")

                    f.write(f"| `{module.module_name}` | {status_emoji} {module.status} | {last_inv} | {callers_count} | {api_summary} |\n")

                f.write("\n")

        print(f"✅ Index written to {output_path}")


def main():
    atlas = LabsAtlas()
    atlas.scan_all()
    atlas.build_caller_graph()
    atlas.query_cieu_invocations()
    atlas.detect_dead_patterns()

    output = YSTAR_COMPANY / "SUBSYSTEM_INDEX.md"
    atlas.generate_index(output)

    print("\n🎯 Labs Atlas scan complete!")
    print(f"📄 Full report: {output}")
    print(f"\n💀 Found {len(atlas.dead_patterns)} dead code patterns")
    print(f"📊 Active modules: {sum(1 for m in atlas.modules.values() if m.status == 'active')}/{len(atlas.modules)}")


if __name__ == "__main__":
    main()
