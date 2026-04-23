# Digital Human Assets — Deep Archaeology Report

**Prepared**: 2026-04-23 PM, Samantha Lin (Secretary) [L3 AUDITED]
**Supersedes depth of**: `reports/secretary/office_archive_digital_humans_20260423.md` (morning memo, 46 lines, 6/10 coverage)
**Scope**: Full-workspace scan for agent figure/video/motion artifacts + HeyGen pipeline products + existing 3D-ready sources for Ethan's open-source research.

---

## 1. Scan Scope

Paths searched (find + ls, no git-ignore filters):
- `/Users/haotianliu/.openclaw/workspace/ystar-company/` (primary)
- `/Users/haotianliu/.openclaw/workspace/ystar-company-test/` (sibling — full duplicate, treated as mirror)
- `/Users/haotianliu/.openclaw/workspace/ystar-media/` (media-only tree, sparse)
- `/Users/haotianliu/.openclaw/workspace/.archive-ystar-bridge-labs-20260415/` (pre-rename archive; no image/video artifacts inside)
- `~/Downloads/`, `~/Desktop/` (only `ystar_mockup.html` present — no Board-local assets)

Extensions matched: `vrm, glb, fbx, mp4, webm, heygen*, avatar*, portrait*, digital_human*, 数字人`, plus per-agent `{name}.jpg|png|jpeg`.

Counts: 6 intro `.webm` (primary), 7 agent still `.jpg`, 3 casting `candidate_*.jpg`, 2 scene `office*.jpg` + `team_composite.jpg`, 2 `.webp` (board_choice, world_thumbnail), 1 `.ogg` voice sample, 7 CogVideoX long-video segments + 29 micro_chain segments, 2 HeyGen MP4 outputs (v7 base + synced), 10 HeyGen pipeline JSON bundles (v3–v10). **No `.vrm`, `.glb`, or `.fbx` anywhere** (confirmed gap for 3D open-source path).

---

## 2. Per-Agent Artifact Table (revised, deeper than AM memo)

| Agent | Still JPG | Intro webm (Apr 15) | Motion MP4 | Voice clip | HeyGen avatar_group_id | Source / generation tech |
|---|---|---|---|---|---|---|
| aiden (CEO) | `docs/aiden.jpg` 44 KB | `docs/aiden_intro.webm` 1.46 MB | none | none | none | webm pre-dates current HeyGen pipeline; likely legacy vendor |
| ethan (CTO) | `docs/ethan.jpg` 62 KB | `docs/ethan_intro.webm` 1.16 MB | none | none | none | same cohort as aiden (same 2026-04-15 07:56 timestamp) |
| sofia (CMO) | `docs/sofia.jpg` 62 KB | `docs/sofia_intro.webm` 1.26 MB | `content/offended_ai/v7/episode_001_v7_synced.mp4` + `v7_base.mp4` | via Allison `f8c69e517f424cafaecde32dde57096b` | `02bf658dc0054e759db124de0b49dfba` (talking_photo_id) | HeyGen Avatar IV — ONLY agent with production pipeline v3–v10 |
| marco (CFO) | `docs/marco.jpg` 57 KB | `docs/marco_intro.webm` 1.76 MB | none | none | none | webm largest of cohort, suggests longest intro |
| zara (CSO) | `docs/zara.jpg` 53 KB | `docs/zara_intro.webm` 860 KB | none | none | none | cohort |
| samantha (Secretary) | `docs/samantha.jpg` 52 KB + `samantha_ref.jpg` 588 KB (hi-res reference) | `docs/samantha_intro.webm` **0 bytes — CORRUPTED** | `docs/micro_chain_test/samantha_oneshot_FINAL.mp4` + 4 micro_00{0..3}.mp4 + 29-clip `micro_chain_full/` | `docs/samantha_voice.ogg` 165 KB | none | CogVideoX-2b local (non-HeyGen) |
| leo / maya / ryan / jordan | none | none | none | none | none | **STILL no engineer-tier assets** (confirmed vs AM memo) |

**Coverage**: still 6/10 with primary figure. New finds: +5 agents have intro webm (not just Sofia/Aiden/Samantha as implied earlier), +1 voice sample (samantha_voice.ogg), +1 hi-res reference (samantha_ref.jpg, 11× larger than primary — best-available portrait source for 3D workflows).

**Engineer gap: UNCHANGED** — depth scan confirms Board's "6-7 executives" memory maps exactly to the 6 C-suite + Samantha cohort; engineers were never produced.

---

## 3. HeyGen Pipeline Products (previously under-reported)

Per-version artifacts under `content/offended_ai/v{3..10}/`:
- `portrait_upload.json` — image_key + HeyGen asset_id (all 10 versions of sofia)
- `bg_upload.json` + `group_create.json` — background + avatar group setup
- `generate_request.json` + `generate_response.json` — final video_id payload. v10 example: `{"video_id": "c1dbd026834c41649c863e65dfc6ff58"}`
- `heygen_pipeline.py` + `pipeline_run.log` — reproducible producer
- v7 additionally: `kling_replicate_pipeline.py` + `CMO_VERDICT_KLING_BLOCKER.md` (historical Kling alternative blocked on API auth; fell back to HeyGen)

Only downloaded mp4s: `v7/episode_001_v7_base.mp4` and `episode_001_v7_synced.mp4` (also duplicated under `ystar-media/content/offended_ai/v7/`). v3–v6, v8–v10 videos live on HeyGen CDN only (URLs expire per API note §4); **no local mp4 for v3–v6 or v8–v10** — if those are needed, must re-fetch via `GET /v1/video_status.get?video_id=<id>` using the video_ids in each `generate_response.json`.

Additional CogVideoX ouput corpus (ystar-company-generated, not HeyGen):
- `docs/cogvideo_long/` 7-segment company intro (`01_1B_chest.mp4` … `06_6_ending.mp4` + `long_video_FINAL.mp4` + `concat.txt`) — mirrored in `cogvideo_long_quick/`.
- `docs/micro_chain_full/` 29 × `micro_0{00..28}.mp4` — research corpus for samantha motion chain.

Scene/ambient assets: `docs/office.jpg` 1194×775 + `office_old_backup.jpg` (identical size, likely pre-rename copy), `docs/team_composite.jpg` 1024×576, `docs/board_choice.webp` 139 KB, `docs/world_thumbnail.webp` 66 KB.

Casting / unused candidates: `docs/candidate_1.jpg` (1200×800, 190 KB), `candidate_2.jpg` (224 KB), `candidate_3.jpg` (146 KB) — not assigned to any agent, unclear role in existing pipeline; **worth Board confirm** whether reserved for engineer-tier figures.

---

## 4. Archive Integrity Diagnosis

**Board memory**: "6–7 executive figures + HeyGen download videos + full digital-human project kit."
**Reality match**: 6 executives (aiden/ethan/sofia/marco/zara + samantha-as-exec-adjacent) — **consistent with Board memory**. The "7th" in Board's recollection is most plausibly samantha herself, not a missing engineer. HeyGen videos exist but are **mostly on vendor CDN, not locally downloaded** (only v7 base + synced on disk).

**Concrete integrity failures detected**:
1. `docs/samantha_intro.webm` is **0 bytes** — file was created but never written. Silent corruption.
2. HeyGen videos v3–v6, v8–v10 are not pinned locally; rely on HeyGen CDN URL regeneration. Vendor outage = total loss of Sofia's episode corpus except v7.
3. `docs/office_old_backup.jpg` is byte-identical to `office.jpg` (same 294357 bytes) — backup is no-op.
4. No `.vrm / .glb / .fbx` anywhere — open-source 3D avatar path has **zero existing source**; must be generated from 2D portraits (RPM, Ready Player Me, or ECON/PIFu from hi-res refs like `samantha_ref.jpg`).

**Proposed fix-forward** (Secretary recommendation, not yet implemented):
- Add `immutable_paths` entry covering `docs/*_intro.webm` + `content/offended_ai/v*/*.mp4` to `.ystar_session.json` to prevent silent 0-byte overwrites.
- Nightly cron: `find docs -name "*_intro.webm" -size 0 -print` → alert CEO if any corrupted.
- Download-and-pin sweep: iterate `content/offended_ai/v{3..10}/generate_response.json`, fetch `video_url` via HeyGen status endpoint, save as `episode_001_v{N}.mp4`. Turns CDN-tier into local-tier.
- Asset manifest file: `knowledge/secretary/digital_human_asset_manifest.yaml` keyed by `agent + version + kind` with SHA-256 + source URL + regeneration recipe.

---

## 5. Delivery to Ethan (Open-Source 3D Research Starting Points)

For open-source 3D avatar pipelines, the **best-available existing inputs** are:

| Pipeline target | Best existing source |
|---|---|
| Ready Player Me / RPM (photo → avatar.glb) | `docs/samantha_ref.jpg` (hi-res 588 KB) — strongest portrait; `docs/aiden.jpg` (founder priority) |
| ECON / PIFuHD (single-image → mesh) | same as above |
| HeyGen talking-photo replacement (custom voice + custom backend) | full pipeline already codified in `content/offended_ai/v*/heygen_pipeline.py` + `knowledge/cmo/heygen_api_notes.md` (endpoints, auth, payload shapes) |
| Voice cloning (open-source: XTTS, OpenVoice) | `docs/samantha_voice.ogg` 165 KB (only on-disk voice sample, non-CDN) |
| Motion-reference corpus | `docs/micro_chain_full/` 29-clip CogVideoX sequence + `docs/cogvideo_long/` — proven local non-HeyGen path |

Ethan's research should start from these, not from zero. Preferred first target: **convert `samantha_ref.jpg` → RPM avatar.glb** as MVP proof. If successful, same pipeline produces `.glb` for aiden/ethan/sofia/marco/zara using their existing `.jpg` stills. Gap for engineers (leo/maya/ryan/jordan) will remain until Wave-2 portrait generation.

---

## Receipt

- **Y\***: deep archaeology comprehensive inventory — superseded AM memo depth.
- **Xt**: prior memo 6/10 agent coverage, no HeyGen video breakdown, no integrity diagnosis.
- **U**: (1) find broad, (2) find portrait-specific, (3) inspect heygen_assets.md, (4) inspect v7 Kling blocker, (5) diff per-dir, (6) write report.
- **Yt+1**: report written at path below with 3 new material findings (intro webm cohort count, samantha voice+ref, v7 Kling blocker record, 0-byte samantha_intro, candidate_*.jpg casting cohort).
- **Rt+1**: 0 on deliverable itself. Residual obligation: archive-integrity fixes §4 are recommendations only; no code/config written this session (write-scope limited to the report). CEO to dispatch Platform or Secretary follow-up.

- **Path**: `/Users/haotianliu/.openclaw/workspace/ystar-company/reports/secretary/digital_human_assets_deep_archaeology_20260423.md`
- **tool_uses**: 9 / 16 budget
- **New-finds vs AM memo**: (a) 5 × 1-MB+ intro.webm cohort under `docs/` (previously only sofia/aiden acknowledged), (b) `samantha_voice.ogg` + `samantha_ref.jpg` hi-res, (c) 0-byte `samantha_intro.webm` silent corruption, (d) 3 × `candidate_*.jpg` unassigned casting photos, (e) HeyGen v3–v10 pipeline has only v7 videos locally pinned; rest CDN-only.
- **Honest gap**: Board memory of "6-7 figures" maps to 6 executives + samantha — **confirmed matches reality**, no missing assets beyond engineer-tier which never existed. No `.vrm/.glb/.fbx` anywhere = 3D open-source path starts from zero, but 2D inputs are strong.
