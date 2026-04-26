# Safe Mining Policy

## Level 0: Path-Only Inventory

Allowed now.

Records filename, extension, size, git status, and artifact class. Does not read
file contents.

## Level 1: Metadata-Only Inspection

Future possible.

May include file size, modified time, and checksum if safe. Still no content
read for DB/log/runtime artifacts.

## Level 2: Bounded Text Sampling

Future only.

Allowed only for curated text reports through explicit adapters. Never for
DB/WAL/SHM. Requires size/time bounds and review.

## Level 3: Structured Adapter Extraction

Future only.

Examples: DB read via safe readonly adapter, bounded log parser, CIEU schema
mapping. Not implemented here.

## Level 4: Curated Memory Ingestion

Future only.

Requires human/reviewer approval, CIEU-backed evidence, and guarded brain
writeback. No artifact becomes canonical memory without review.

Current milestone implements only Level 0 path-only inventory.
