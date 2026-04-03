# Pre-Commit Checklist — CTO Verification Protocol

**Source:** AGENTS.md CTO Engineering Standards  
**Moved to knowledge:** 2026-04-03（Constitutional cleanup）  
**Authority:** Y*gov OmissionEngine enforced

---

## Purpose

Ensure code quality and system health before every git commit. Prevents regressions, test failures, and configuration drift.

## Constitutional Requirement

**From AGENTS.md:**
> 每次git commit后，必须运行 ystar doctor --layer1  
> doctor失败 = 禁止push

**This guide provides detailed pre-commit verification steps.**

---

## Quick Checklist (Required Before Every Commit)

```bash
# 1. Run tests
python -m pytest tests/ -q --tb=no

# 2. Check doctor
ystar doctor --layer1

# 3. Verify no debugging code
grep -r "print(" --include="*.py" ystar/ | grep -v test | grep -v "#"

# 4. Check for secrets
git diff --cached | grep -i "api_key\|password\|secret\|token" | grep -v "# Example"

# 5. Verify version consistency (if version changed)
grep -h "version" pyproject.toml setup.py ystar/__init__.py
```

If all pass → safe to commit.

---

## Detailed Verification Steps

### Step 1: Test Suite Verification

**Command:**
```bash
python -m pytest tests/ -v --tb=short
```

**Success criteria:**
- All tests pass (or known failures documented)
- No new test failures introduced
- Test count ≥ previous commit

**If tests fail:**
1. Fix the failing tests
2. Re-run full suite
3. Do NOT commit until all pass
4. Exception: Known flaky tests (must be documented in `tests/KNOWN_FLAKY.md`)

**Fast check (< 5 seconds):**
```bash
python -m pytest tests/ -q --tb=no
```

---

### Step 2: System Health Check

**Command:**
```bash
ystar doctor --layer1
```

**Success criteria:**
```
[✓] CIEU Database
[✓] Omission Database
[✓] Contract File
[✓] Interrupt Gate
[✓] Unreachable Obligations — 0 found
[✓] Engine Configuration

All checks passed -- Y*gov is healthy
```

**If doctor fails:**
1. Read error message carefully
2. Fix underlying issue (do NOT bypass)
3. Re-run doctor
4. Do NOT commit until doctor passes

**Common failures:**
- CIEU not recording → restart session, re-run `ystar hook-install`
- Unreachable obligations > 0 → check obligation_triggers.py for bugs
- Config invalid → verify AGENTS.md syntax

---

### Step 3: Debug Code Detection

**Command:**
```bash
# Check for print statements
grep -rn "print(" ystar/ --include="*.py" | grep -v "test_" | grep -v "#.*print"

# Check for breakpoints
grep -rn "breakpoint()\|pdb.set_trace()\|import pdb" ystar/ --include="*.py"

# Check for commented-out code blocks
grep -rn "# TODO\|# FIXME\|# HACK" ystar/ --include="*.py"
```

**Success criteria:**
- No debugging print() statements in production code
- No breakpoint() or pdb calls
- TODOs/FIXMEs are acceptable (but should have issue tracking)

**If found:**
- Remove debug statements
- Replace print() with logging if needed
- Document TODOs with issue numbers

---

### Step 4: Secrets Detection

**Command:**
```bash
# Check staged changes
git diff --cached | grep -i "api_key\|password\|secret\|token\|credential"

# Check for common secret patterns
git diff --cached | grep -E "(sk-|pk-|ghp_|ghs_)[a-zA-Z0-9]{20,}"
```

**Success criteria:**
- No API keys, tokens, or passwords in diff
- Examples/placeholders are okay if clearly marked

**If secrets found:**
1. **STOP immediately**
2. Do NOT commit
3. Remove secrets from code
4. Add to `.gitignore` if it's a config file
5. Use environment variables instead
6. Follow `knowledge/emergency_procedures.md` if already committed

---

### Step 5: Version Consistency Check

**When to run:** Only if version number changed

**Command:**
```bash
# Extract versions
PYPROJECT_VER=$(grep '^version = ' pyproject.toml | cut -d'"' -f2)
SETUP_VER=$(grep "version=" setup.py | cut -d'"' -f2)
INIT_VER=$(grep "__version__" ystar/__init__.py | cut -d'"' -f2)

# Compare
echo "pyproject.toml: $PYPROJECT_VER"
echo "setup.py: $SETUP_VER"
echo "__init__.py: $INIT_VER"

# Should all be identical
```

**Success criteria:**
- All three files have identical version string
- Version follows semver: X.Y.Z
- Version is newer than previous release

**If inconsistent:**
1. Update all three files to same version
2. Re-run check
3. Commit with message: "chore: bump version to X.Y.Z"

---

### Step 6: Code Style Check (Optional but Recommended)

**Command:**
```bash
# Check formatting (if using black)
black --check ystar/

# Check imports (if using isort)
isort --check ystar/

# Type checking (if using mypy)
mypy ystar/ --ignore-missing-imports
```

**Not enforced by governance, but good practice.**

---

## Pre-Commit Hook Integration

**Automated version (recommended):**

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
set -e

echo "Running pre-commit checks..."

# 1. Tests
echo "[1/3] Running tests..."
python -m pytest tests/ -q --tb=no || { echo "❌ Tests failed"; exit 1; }

# 2. Doctor
echo "[2/3] Running doctor..."
ystar doctor --layer1 > /dev/null || { echo "❌ Doctor failed"; exit 1; }

# 3. Secrets check
echo "[3/3] Checking for secrets..."
git diff --cached | grep -qi "api_key\|sk-\|ghp_" && { echo "❌ Possible secret detected"; exit 1; }

echo "✅ All pre-commit checks passed"
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

**To bypass (emergency only):**
```bash
git commit --no-verify -m "emergency: reason for bypass"
```

---

## Post-Commit Verification

**After successful commit:**

```bash
# 1. Verify commit was created
git log -1 --oneline

# 2. Check commit is on correct branch
git branch --contains HEAD

# 3. Verify no uncommitted changes remain
git status

# 4. Check commit message follows convention
# Format: "type: description"
# Types: feat, fix, docs, test, chore, refactor
```

---

## Special Cases

### Large Refactoring

**Additional checks:**
- Run full test suite with coverage: `pytest --cov=ystar tests/`
- Verify coverage didn't drop: compare to previous commit
- Check for unused imports: `pylint ystar/ --disable=all --enable=unused-import`

### Adding New Dependencies

**Additional checks:**
- Update `requirements.txt` or `pyproject.toml`
- Document why dependency is needed
- Check license compatibility
- Verify dependency is actively maintained

### Configuration Changes

**Additional checks:**
- If modifying `session.json`: run `ystar check-impact session.json`
- If modifying `omission_engine.py`: extra doctor verification
- If modifying `hook.py`: test hook installation in clean environment

---

## Troubleshooting

### Tests pass locally but fail in CI

**Causes:**
- Platform-specific code (Windows vs Linux)
- Missing test dependencies in CI
- Timing-dependent tests (flaky)

**Fix:**
- Add platform checks in tests
- Update CI requirements.txt
- Mark flaky tests with `@pytest.mark.flaky`

### Doctor passes locally but not in CI

**Causes:**
- CIEU database not available in CI
- Missing AGENTS.md in CI environment
- Different working directory

**Fix:**
- Mock CIEU in CI tests
- Ensure AGENTS.md is in repo
- Use relative paths

### Secrets detected but they're examples

**Fix:**
- Add comment: `# Example key (not real)`
- Use obvious fake values: `sk-example-not-a-real-key`
- Exclude from grep with patterns

---

## Commit Message Format

**Convention:**
```
type: brief description (< 70 chars)

Optional longer explanation of what changed and why.
Can span multiple lines.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `test:` Adding or fixing tests
- `chore:` Maintenance (version bump, deps update)
- `refactor:` Code restructuring (no behavior change)
- `perf:` Performance improvement
- `style:` Formatting, whitespace

**Examples:**
```
feat: add cancel_obligation() for graceful obligation cleanup

fix: correct sqlite Row.get() usage in omission_store

docs: update pre-commit checklist with secrets detection

test: add 7 tests for cancel_obligation mechanism

chore: bump version to 0.48.1

refactor: extract obligation creation logic to helper method
```

---

**Last updated:** 2026-04-03  
**Next review:** When new pre-commit requirements added
