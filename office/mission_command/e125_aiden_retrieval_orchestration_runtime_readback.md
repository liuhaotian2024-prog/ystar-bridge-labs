# E125 Aiden Retrieval Orchestration Runtime

## What Changed
- Merged repo evidence, Aiden 6D brain, E87R code/capability baseline, CIEU history, Y-star memory status, and local vector RAG status into one governed retrieval packet.
- Y-star-gov now validates retrieval before Aiden uses retrieved context in answers/actions.
- Retrieval decisions write formal CIEUStore records.

## Source Coverage
- Satisfied: aiden_6d_brain, code_index_or_capability_map, e123_memory_asset_discovery, repo_evidence_index
- Unavailable declared: cieu_store_history, local_vector_rag
- Evidence items: 28

## Boundaries
- No external action executed.
- No customer/revenue/payment claim.
- Vector RAG may be unavailable; if so the runtime declares the correct build path instead of faking retrieval.