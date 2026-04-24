#!/usr/bin/env python3
"""
ci_check_imports.py — Static AST scanner for Y*gov import path drift.

Purpose
-------
Prevent the 2026-04-23 class of incident: a file is moved/renamed but some
imports still reference the old path. At runtime this manifests as hook
fail-closed deadlock; at commit time this script catches it and refuses
the commit.

What it does
------------
1. Walks every *.py file under ystar-company/ and Y-star-gov/.
2. For each file, parses the AST and extracts every
       `from ystar.<pkg>.<mod> import ...`
   and
       `import ystar.<pkg>.<mod>`
   reference.
3. For each reference, resolves it against the filesystem:
       - Is there a corresponding .py file or package dir under
         Y-star-gov/ystar/... ?
4. Reports orphan references (imports that do not resolve).
5. Exit 0 if clean, exit 1 if any orphans found (for CI / pre-commit).

Why Y-star-gov specifically
---------------------------
Because ystar-company/ystar/ is a shell (no adapters/ subdir); the real
ystar package lives at /Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar/.
This matches the hard-coded sys.path in hook_wrapper.py line 17.

Usage
-----
    # Standalone:
    python3 scripts/ci_check_imports.py

    # CI / pre-commit:
    python3 scripts/ci_check_imports.py && echo "imports clean"

    # With custom roots:
    python3 scripts/ci_check_imports.py --scan-root /path/to/scan \\
                                         --package-root /path/to/ystar/parent

Output format
-------------
Each orphan prints as:
    <file>:<line>: <module.path.missing>
          expected at: <filesystem path tried>

Limitations
-----------
- Only catches `from ystar.X...` or `import ystar.X...` patterns.
- Dynamic imports via importlib.import_module with f-strings are invisible.
- Does not follow sys.path manipulation in individual files.
"""

import os
import sys
import ast
import argparse
from pathlib import Path


DEFAULT_SCAN_ROOTS = [
    "/Users/haotianliu/.openclaw/workspace/ystar-company",
    "/Users/haotianliu/.openclaw/workspace/Y-star-gov",
]
DEFAULT_PACKAGE_ROOT = "/Users/haotianliu/.openclaw/workspace/Y-star-gov"

SKIP_DIR_NAMES = {"__pycache__", ".git", "node_modules", ".venv", "venv",
                  ".pytest_cache", "build", "dist", ".tox", ".mypy_cache"}


def collect_py_files(roots):
    """Walk roots and yield every .py file (skipping noise dirs)."""
    for root in roots:
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
            for fname in filenames:
                if fname.endswith(".py"):
                    yield os.path.join(dirpath, fname)


def extract_ystar_imports(py_path):
    """
    Parse py_path and return list of (lineno, dotted_name) for every
    `from ystar...` or `import ystar...` reference.

    For `from ystar.a.b import X`, emits ('ystar.a.b', X) by expanding
    into `ystar.a.b.X` only if X is checkable. We conservatively check
    the module portion only ('ystar.a.b'), since X might be a symbol
    (function/class) rather than a submodule.
    """
    try:
        with open(py_path, "r", encoding="utf-8") as f:
            src = f.read()
    except (UnicodeDecodeError, OSError):
        return []

    try:
        tree = ast.parse(src, filename=py_path)
    except SyntaxError:
        # Syntax errors are another problem, not ours. Skip.
        return []

    refs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and node.module.startswith("ystar"):
                refs.append((node.lineno, node.module))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("ystar"):
                    refs.append((node.lineno, alias.name))
    return refs


def resolve_module(dotted_name, package_root):
    """
    Given a dotted module name like 'ystar.adapters.identity_detector' and
    package_root like '/Users/.../Y-star-gov', check whether a matching
    file or package directory exists.

    Returns (exists: bool, tried_path: str).
    """
    parts = dotted_name.split(".")
    # parts[0] is 'ystar' — it sits directly under package_root
    base = Path(package_root)

    # Try as .py file:  ystar/a/b.py
    py_path = base.joinpath(*parts).with_suffix(".py")
    if py_path.is_file():
        return (True, str(py_path))

    # Try as package dir with __init__.py:  ystar/a/b/__init__.py
    pkg_init = base.joinpath(*parts, "__init__.py")
    if pkg_init.is_file():
        return (True, str(pkg_init))

    # Try as namespace package dir (no __init__.py — PEP 420):  ystar/a/b/
    pkg_dir = base.joinpath(*parts)
    if pkg_dir.is_dir():
        return (True, str(pkg_dir) + "/ (namespace package)")

    # Nothing matched — report what we tried
    return (False, str(py_path) + " OR " + str(pkg_init))


def main():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scan-root", action="append", default=None,
        help="Directory to walk for .py files (repeatable). "
             f"Default: {DEFAULT_SCAN_ROOTS}")
    parser.add_argument("--package-root", default=DEFAULT_PACKAGE_ROOT,
        help="Parent directory containing the ystar/ package. "
             f"Default: {DEFAULT_PACKAGE_ROOT}")
    parser.add_argument("--quiet", action="store_true",
        help="Only print orphans, no progress output.")
    args = parser.parse_args()

    scan_roots = args.scan_root if args.scan_root else DEFAULT_SCAN_ROOTS
    package_root = args.package_root

    if not args.quiet:
        print(f"Scanning roots: {scan_roots}")
        print(f"Package root:   {package_root}")
        print(f"Looking for:    ystar.* imports")
        print("")

    if not os.path.isdir(package_root):
        print(f"ERROR: package-root does not exist: {package_root}", file=sys.stderr)
        sys.exit(2)

    ystar_dir = os.path.join(package_root, "ystar")
    if not os.path.isdir(ystar_dir):
        print(f"ERROR: {ystar_dir} is not a directory — wrong package-root?",
              file=sys.stderr)
        sys.exit(2)

    total_files = 0
    total_refs = 0
    orphans = []  # list of (file, lineno, dotted_name, tried_path)

    for py_file in collect_py_files(scan_roots):
        total_files += 1
        refs = extract_ystar_imports(py_file)
        for lineno, dotted in refs:
            total_refs += 1
            exists, tried = resolve_module(dotted, package_root)
            if not exists:
                orphans.append((py_file, lineno, dotted, tried))

    if not args.quiet:
        print(f"Scanned {total_files} .py files, {total_refs} ystar.* references.")
        print("")

    if not orphans:
        if not args.quiet:
            print("✓ All ystar.* imports resolve. Clean.")
        sys.exit(0)

    print(f"✗ Found {len(orphans)} orphan import reference(s):")
    print("")
    # Sort for stable output
    for py_file, lineno, dotted, tried in sorted(orphans):
        # Make paths relative where possible for readability
        try:
            rel = os.path.relpath(py_file)
        except ValueError:
            rel = py_file
        print(f"  {rel}:{lineno}")
        print(f"      import: {dotted}")
        print(f"      expected at: {tried}")
        print("")

    print(f"Commit rejected: {len(orphans)} orphan import(s) must be fixed first.")
    print("Common fix: the file was renamed/moved. Update the import path.")
    sys.exit(1)


if __name__ == "__main__":
    main()
