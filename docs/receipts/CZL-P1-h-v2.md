# CZL-P1-h-v2 Receipt: Shadow ystar/ symlink cleanup

## CIEU 5-Tuple

### Y* (ideal contract)
Eliminate shadow-ystar lock-death vector (path #8): remove the symlink at
`ystar-company/ystar` that causes Python import shadowing when cwd=ystar-company.

### Xt (state before)
- `ystar-company/ystar` was a symlink (git mode 120000, blob 032b239752fdfe0f59222eeba6865ce3beaf3765)
- Target: `/Users/haotianliu/.openclaw/workspace/Y-star-gov/ystar`
- Effect: `python3 -c "import ystar"` from cwd=ystar-company resolved to the symlink,
  shadowing any pip-installed or PYTHONPATH-resolved ystar package
- All scripts already had explicit `sys.path.insert(0, ".../Y-star-gov")` making the
  symlink redundant
- `diff -rq` confirmed shadow was byte-identical to real (because it IS the real dir via symlink)

### U (actions taken)
1. Confirmed symlink nature: `file ystar` -> directory, `readlink ystar` -> Y-star-gov/ystar
2. Confirmed git tracking: mode 120000 (symlink), single blob entry
3. Confirmed all 20+ scripts in scripts/ already have explicit sys.path.insert for Y-star-gov
4. Removed symlink: `rm /Users/haotianliu/.openclaw/workspace/ystar-company/ystar`
5. Smoke test 1: `PYTHONPATH=.../Y-star-gov python3 -c "from ystar.kernel.dimensions import IntentContract; from ystar.kernel.engine import check; from ystar.session import Policy"` -> ALL IMPORTS OK, resolves to Y-star-gov/ystar/__init__.py
6. Smoke test 2: `hook_wrapper.py` runs successfully (loads 5 roles from AGENTS.md, no import errors)
7. Smoke test 3: bare `python3 -c "import ystar"` now correctly raises ModuleNotFoundError (expected: ystar is not pip-installed, scripts use explicit PYTHONPATH)

### Yt+1 (state after)
- `ls ystar-company/ystar` -> "No such file or directory"
- Python import resolution no longer shadowed by cwd
- All hook scripts continue to work (they use explicit sys.path.insert)
- Lock-death path #8 eliminated

### Rt+1
**Rt+1 = 0** (complete)
- Symlink removed
- All smoke tests pass
- No files needed to be kept (symlink, not directory)
- Archive README could not be written to archive/ (outside eng-kernel write scope) -- recorded in this receipt instead

## Notes
- The symlink was NOT a stale copy; it was a live symlink to the real Y-star-gov/ystar
- This means removing it has zero data loss risk
- ystar is NOT pip-installed; all working import paths use explicit PYTHONPATH or sys.path.insert
- The `git rm ystar` commit is NOT done per scope guard (no git commit/push)
- CEO should `git rm ystar` and commit when ready
