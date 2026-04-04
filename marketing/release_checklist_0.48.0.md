# Release Checklist — Y*gov 0.48.0

**Date:** 2026-04-03  
**Status:** Ready for Board approval  
**Test Status:** ✅ 559/559 passing

## Pre-Release Verification

### Code Quality
- [x] All tests passing (559/559)
- [x] CHANGELOG.md updated with all fixes
- [x] README.md badges updated (559 tests)
- [x] Version number in pyproject.toml: 0.48.0
- [x] Version number in setup.py: 0.48.0
- [x] Wheel built: dist/ystar-0.48.0-py3-none-any.whl (643KB)

### Documentation
- [x] README.md first screen clarity
- [x] CLI Reference complete
- [x] Installation instructions tested
- [x] `ystar demo` command works
- [x] `ystar doctor` diagnostic works

### Security
- [x] No credentials in source code
- [x] No CIEU logs with sensitive data in examples
- [x] MIT license file present
- [x] No external dependencies (except Python stdlib)

## Release Commands (Board Approval Required)

### 1. Build Fresh Wheel
```bash
cd "C:/Users/liuha/OneDrive/桌面/Y-star-gov"
rm -rf dist/ build/ *.egg-info
python -m build
```

### 2. Test Installation Locally
```bash
pip uninstall ystar -y
pip install dist/ystar-0.48.0-py3-none-any.whl
ystar --version  # Should show: ystar 0.48.0
ystar doctor
```

### 3. Upload to PyPI (REQUIRES BOARD APPROVAL)
```bash
# TestPyPI first (optional safety check)
python -m twine upload --repository testpypi dist/ystar-0.48.0-py3-none-any.whl

# Production PyPI
python -m twine upload dist/ystar-0.48.0-py3-none-any.whl
```

### 4. Create GitHub Release
```bash
cd "C:/Users/liuha/OneDrive/桌面/Y-star-gov"
git tag -a v0.48.0 -m "Y*gov 0.48.0 - Foundation Sovereignty + 559 tests passing"
git push origin v0.48.0
gh release create v0.48.0 \
  --title "Y*gov 0.48.0 — Foundation Sovereignty" \
  --notes-file CHANGELOG.md \
  dist/ystar-0.48.0-py3-none-any.whl
```

### 5. Verify Installation from PyPI
```bash
pip uninstall ystar -y
pip install ystar
ystar --version  # Should show: ystar 0.48.0
ystar hook-install
ystar doctor
```

## Post-Release Actions

### Immediate (Within 1 hour)
- [ ] Post to Show HN (use marketing/show_hn_draft.md)
- [ ] Monitor HN comments for first 2 hours
- [ ] Watch PyPI download stats
- [ ] Monitor GitHub issues for installation problems

### Day 1-3
- [ ] Respond to all HN comments within 4 hours
- [ ] Fix any critical installation bugs as hotfix 0.48.1
- [ ] Track first external user success metric

### Week 1
- [ ] Write launch retrospective
- [ ] Analyze download/install success rate
- [ ] Collect user feedback for 0.49.0 roadmap

## Rollback Plan

If critical bug discovered post-release:
```bash
# Yank from PyPI (keeps version, shows warning)
twine yank ystar 0.48.0 --reason "Critical bug - use 0.47.0"

# Users can still install 0.47.0
pip install ystar==0.47.0
```

## Key Metrics to Track

- PyPI downloads (Day 1, Day 7, Day 30)
- GitHub stars
- Installation success rate (via `ystar doctor` telemetry opt-in)
- Show HN engagement (upvotes, comments, click-through)
- First external contributor
- First external GitHub issue
- First enterprise inquiry

## Risk Assessment

**Low Risk:**
- Code has 559 passing tests
- No external dependencies = no supply chain risk
- Installation tested on Windows + macOS

**Medium Risk:**
- First major public launch (user volume unknown)
- Hook installation may fail on exotic environments

**Mitigation:**
- `ystar doctor` provides diagnostic info
- README has troubleshooting section
- CEO monitoring HN/GitHub for first 48 hours

## Board Approval Required For

- ⚠️ PyPI upload (external release)
- ⚠️ GitHub release tag
- ⚠️ Show HN post

All preparation work (wheel build, local testing, docs) can proceed autonomously.
