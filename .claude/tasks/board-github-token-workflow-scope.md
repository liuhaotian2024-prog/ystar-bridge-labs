## Task: GitHub Token Workflow Scope Issue
**Priority:** P2  
**Owner:** Board (Haotian Liu)  
**Created:** 2026-04-02  
**Blocker for:** Y-star-gov repo push

### Problem
Cannot push to Y-star-gov repository:

```
! [remote rejected] main -> main (refusing to allow a Personal Access Token 
to create or update workflow `.github/workflows/test.yml` without `workflow` scope)
```

### Root Cause
GitHub Personal Access Token used for authentication lacks `workflow` scope.

### Commits Blocked
- `9c859f0` fix(platform): Windows hook installation — use .bat wrapper
- `24c77af` docs: Add CHANGELOG.md + fix test for moved development docs
- `3f7fda0` platform: Windows hook command fix + cleanup + CI (this added the workflow)

### Solution Required
Board must update GitHub PAT with `workflow` scope:
1. Go to https://github.com/settings/tokens
2. Find the token used by this machine
3. Add `workflow` scope (allows editing .github/workflows/*)
4. Save and update local credential

### Workaround (if urgent)
Temporarily remove workflow file from commit history:
```bash
git reset --soft HEAD~3
git restore --staged .github/workflows/test.yml
git commit (recommit other changes)
```

**Not recommended** — better to fix token permissions.

### Impact
- Low: Local work continues normally
- Medium: Cannot share Windows hook fix with other developers yet
- None: Does not block development or testing

### Status
Documented. Awaiting Board action on token permissions.
