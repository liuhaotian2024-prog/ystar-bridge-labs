## Task: W7.3 sentence-transformer embedding for narrative_coherence_detector

Engineer: eng-governance (Maya Patel)
Priority: P0
Assigned: 2026-04-15 20:50 UTC
Deadline: ≤3h wall clock

## Context

`scripts/narrative_coherence_detector.py` 当前用纯 keyword match，语义飘移漏抓。
需要升级为 sentence-transformer embedding + cosine similarity，降低误报/漏报。

## Acceptance Criteria

- [ ] `narrative_coherence_detector.py` 新增 `sentence-transformers` 依赖
- [ ] `check_ceo_output_vs_subgoal` 函数支持 embedding similarity
- [ ] 策略：max(keyword_score, embedding_score)，fail-open 到 TF-IDF
- [ ] 3 梯度阈值：perfect < 0.3 / partial 0.3-0.6 / off > 0.7
- [ ] E2E test: 3 对照 (perfect/partial/off) 验证 embedding 生效
- [ ] 三层 evidence：grep / production call / E2E verify
- [ ] Commit + push

## Files in Scope

- `scripts/narrative_coherence_detector.py`
- `tests/test_w7_3_embedding.py` (new)
- `.ystar_session.json` (add sentence-transformers to dependencies if needed)

## Technical Notes

Model: `sentence-transformers/all-MiniLM-L6-v2` (384 维, 快速, 适合 Y*gov 场景)

Import:
```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
emb1 = model.encode("CEO output text")
emb2 = model.encode("Sub-goal description")
cosine = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
```

Thresholds:
- cosine > 0.7 → perfect match
- 0.4 < cosine ≤ 0.7 → partial match
- cosine ≤ 0.4 → off-track (逆转 metric: 0.3/0.6/0.7 实际对应 1-cosine = drift)

## Evidence Format

Commit message 必须包含：
- CIEU 5-tuple (Y*/Xt/U/Yt+1/Rt+1)
- Evidence Layer 1: grep embedding 相关代码行数
- Evidence Layer 2: production call 产出 cosine similarity 值
- Evidence Layer 3: E2E test 3 对照通过

## Execution Notes

- 先 `pip install sentence-transformers` (Y*gov 源码 repo 如果需要也 add to requirements.txt)
- Model 会自动下载到 `~/.cache/torch/sentence_transformers/`，首次运行需联网
- 如遇 daemon 锁死，自救：`pkill -9 -f hook_daemon; rm -f /tmp/ystar_hook*.sock`

## Report Back

完成后立刻 commit + push，不等 CEO 确认。遇 blocker 先自救，Board 绝不介入权限。
