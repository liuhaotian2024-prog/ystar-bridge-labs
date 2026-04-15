# Video Binary Storage Migration Report
**Date**: 2026-04-14  
**Engineer**: Ryan Park (Platform)  
**Trigger**: Board caught 20+ mp4 binaries in git repo during push signal-9 debug (顾问 P1 catch)

---

## Problem Statement

**Observed**:
- 20+ tracked mp4 files in git history (`docs/cogvideo_long*/`, `docs/micro_chain_full/`)
- 7 new untracked video/audio binaries in working directory (`content/offended_ai/`, `docs/`)
- No policy preventing future binary pollution
- Push size bloat + collaboration friction

**Root Cause**: No binary storage policy; content creators directly committing media assets to git.

---

## Solution: Path C (Incremental Defense) — SELECTED

### Evaluated Paths

| Path | Description | Pros | Cons | Verdict |
|------|-------------|------|------|---------|
| **A: git-lfs** | Migrate all binaries to Git LFS | Clean separation, versioning | Payment dependency, requires re-clone, quota limits | ❌ Rejected: adds external dependency |
| **B: History Rewrite** | Use git-filter-repo/BFG to purge mp4 from history | Clean repo size | Destructive, breaks existing clones, data loss risk | ❌ Rejected: too risky without Board approval |
| **C: Incremental** | .gitignore blocks future binaries; old files stay in history; external storage for new assets | Zero破坏性, immediate defense, backward compatible | Old binaries bloat full clones | ✅ **SELECTED** |

### Recommendation Reasoning

**Path C chosen** because:
1. **Zero破坏性**: No history rewrite → no clone breakage, no data loss risk
2. **Immediate forward防御**: .gitignore blocks all future `*.mp4/*.mov/*.wav` from entering staging
3. **Backward compatible**: Existing 20 mp4 files remain in history (flagged deprecated); shallow clone mitigates size impact
4. **External storage ready**: New binaries → `~/.openclaw/workspace/ystar-media/` with registry at `content/video_registry.yml`

**Trade-off accepted**: Old binaries (est. 50-200MB) remain in full clone history. Mitigation: new contributors use `git clone --depth 1`.

---

## Implementation (Completed)

### 1. .gitignore Update

**Added comprehensive binary block rules**:
```gitignore
# Video/audio binaries → external storage
*.mp4
*.mov
*.avi
*.mkv
*.flv
*.wmv
*.webm
*.wav
*.mp3
*.aac
*.flac
*.ogg
*.m4a
```

**Result**: All video/audio formats now blocked from `git add`.

### 2. External Storage Setup

**Created**: `~/.openclaw/workspace/ystar-media/`

**Migrated 7 untracked binaries**:
- `content/offended_ai/build/full_audio.wav` → `ystar-media/content/offended_ai/build/`
- `content/offended_ai/v6/sofia_clean_despill.mov` → `ystar-media/content/offended_ai/v6/`
- `content/offended_ai/v7/episode_001_v7_base.mp4` → `ystar-media/content/offended_ai/v7/`
- `content/offended_ai/v7/episode_001_v7_synced.mp4` → `ystar-media/content/offended_ai/v7/`
- `docs/micro_chain_full/samantha_oneshot_FINAL.mp4` → `ystar-media/docs/micro_chain_full/`
- `docs/segA_lipsync_FINAL.mov` → `ystar-media/docs/`
- `docs/segA_mov.mov` → `ystar-media/docs/`

### 3. Asset Registry

**Created**: `content/video_registry.yml`

Maps logical content paths → physical storage paths. Example:
```yaml
offended_ai:
  v7:
    episode_001_synced: ~/.openclaw/workspace/ystar-media/content/offended_ai/v7/episode_001_v7_synced.mp4
```

**Purpose**: Single source of truth for video asset locations; supports automation (e.g., build scripts).

---

## Verification (Rt+1=0 proof)

### Test 1: .gitignore blocks new binaries
```bash
$ git check-ignore content/offended_ai/v7/episode_001_v7_base.mp4
content/offended_ai/v7/episode_001_v7_base.mp4  # ✅ Matched
```

### Test 2: git status clean after touch test.mp4
```bash
$ touch test.mp4 && git status --short
# (no output — test.mp4 not staged) ✅
```

### Test 3: Migration report delivered
- **Path**: `reports/video_storage_migration_20260414.md` ✅

---

## Legacy Binaries Status

**20 tracked mp4 files remain in git history** (flagged deprecated):
- `docs/cogvideo_long/*.mp4` (7 files)
- `docs/cogvideo_long_quick/*.mp4` (7 files)
- `docs/micro_chain_full/micro_*.mp4` (6 files)

**Decision**: NO history rewrite without Board approval. These files:
- Remain accessible via git history (backward compat)
- Are documented in `content/video_registry.yml` as `legacy_tracked`
- Will not be fetched by shallow clones (`git clone --depth 1`)

**Future cleanup**: If Board approves history rewrite, CTO can use `git-filter-repo` to purge old binaries. Not required for Rt+1=0.

---

## Forward Policy

1. **All new video/audio assets** → `~/.openclaw/workspace/ystar-media/`
2. **Update registry**: Add entry to `content/video_registry.yml` when creating new asset
3. **Content creators**: Reference external paths in scripts/docs; never commit binaries to repo
4. **New contributors**: Use `git clone --depth 1` for size-optimized checkout

---

## CIEU Impact

**Constraint**: `[GOV_NO_BINARY_PUSH]` (implicit Y*gov hygiene rule)  
**Violation**: 20+ mp4 files in git history  
**Resolution**: Forward防御 via .gitignore; legacy binaries flagged deprecated  
**Outcome**: Rt+1=0 achieved (future binaries blocked); existing violations documented not escalated

---

## Board Decision Space

**Recommendations for Board review** (NO selection required for current task):

1. **Accept Path C as-is**: Forward防御 in place, legacy binaries remain (default recommendation)
2. **Optional future cleanup**: Approve CTO to run `git-filter-repo` to purge history (requires team coordination + backup)
3. **External storage tier upgrade**: If `ystar-media/` grows >10GB, migrate to Google Drive with URL registry (not urgent)

**Current action**: None required from Board. Migration complete, policy enforced.

---

## Appendix: Verification Commands

**Check .gitignore coverage**:
```bash
git check-ignore -v *.mp4 *.mov *.wav
```

**List legacy tracked binaries**:
```bash
git ls-files '*.mp4' '*.mov' '*.wav'
```

**Verify clean staging**:
```bash
touch test_video.mp4 && git status --short | grep test_video.mp4
# (should return empty)
rm test_video.mp4
```

---

**Status**: ✅ Rt+1=0 achieved  
**Next action**: Monitor `git status` during next content creation cycle; verify creators use external storage  
**Owner**: Ryan Park (Platform) — ongoing policy enforcement
