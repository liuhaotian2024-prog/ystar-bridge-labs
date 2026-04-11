#!/usr/bin/env python3
"""
Full Knowledge Import Script for YML (Y* Memory Layer)
Scans knowledge directories and imports to .ystar_memory.db

Board-mandated import rules:
- Each file split into reasonable chunks (max 500 chars per memory)
- Deduplication by content hash
- CIEU audit trail for all imports
- Reports statistics on completion
"""

import sys
import os
import hashlib
import time
import json
from pathlib import Path
from typing import List, Dict, Tuple

# Add Y-star-gov to path for MemoryStore access
sys.path.insert(0, "/Users/haotianliu/.openclaw/workspace/Y-star-gov")

from ystar.memory.store import MemoryStore
from ystar.memory.models import Memory

# Import mapping: (source_glob, memory_type, half_life_days, agent_id)
IMPORT_RULES = [
    ("knowledge/cases/CASE_*.md", "lesson", 180, "ceo"),
    ("knowledge/ceo/team_dna.md", "knowledge", 120, "ceo"),
    ("knowledge/ceo/decision_making.md", "knowledge", 90, "ceo"),
    ("knowledge/ceo/strategy_frameworks.md", "knowledge", 90, "ceo"),
    ("knowledge/cto/competitive_architecture.md", "knowledge", 60, "cto"),
    ("knowledge/cto/three_layer_architecture*.md", "knowledge", 60, "cto"),
    ("knowledge/cto/technical_decision_making.md", "knowledge", 60, "cto"),
    ("knowledge/cmo/hn_writing_guide.md", "knowledge", 60, "cmo"),
    ("knowledge/cmo/positioning_framework.md", "knowledge", 60, "cmo"),
    ("knowledge/cso/developer_led_growth.md", "knowledge", 60, "cso"),
    ("knowledge/cso/enterprise_sales_process.md", "knowledge", 60, "cso"),
    ("governance/CIEU_VIDEO_METHODOLOGY.md", "knowledge", 90, "cto"),
    ("governance/WORKING_STYLE.md", "knowledge", 120, "ceo"),
]

COMPANY_ROOT = Path("/Users/haotianliu/.openclaw/workspace/ystar-company")
DB_PATH = COMPANY_ROOT / ".ystar_memory.db"
CIEU_DB_PATH = COMPANY_ROOT / ".ystar_cieu.db"
MAX_CHUNK_SIZE = 500


def compute_content_hash(content: str) -> str:
    """Compute SHA256 hash of content for deduplication."""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def split_content(content: str, max_size: int = MAX_CHUNK_SIZE) -> List[str]:
    """
    Split content into chunks, respecting paragraph boundaries.

    Strategy:
    - Split by double newline first (paragraphs)
    - If paragraph > max_size, split by sentences
    - If sentence > max_size, hard split
    """
    chunks = []
    paragraphs = content.split('\n\n')

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(para) <= max_size:
            chunks.append(para)
        else:
            # Split by sentences
            sentences = para.replace('. ', '.\n').split('\n')
            current_chunk = ""

            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue

                if len(current_chunk) + len(sent) + 1 <= max_size:
                    current_chunk += (" " + sent if current_chunk else sent)
                else:
                    if current_chunk:
                        chunks.append(current_chunk)

                    # If single sentence > max_size, hard split
                    if len(sent) > max_size:
                        for i in range(0, len(sent), max_size):
                            chunks.append(sent[i:i+max_size])
                        current_chunk = ""
                    else:
                        current_chunk = sent

            if current_chunk:
                chunks.append(current_chunk)

    return chunks


def extract_title_from_markdown(content: str) -> str:
    """Extract title from markdown content (first # heading)."""
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
    return "Untitled"


def load_existing_hashes(store: MemoryStore) -> set:
    """Load all existing content hashes to avoid duplicates."""
    import sqlite3

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("SELECT content FROM memories")
    hashes = {compute_content_hash(row[0]) for row in cursor.fetchall()}
    conn.close()

    return hashes


def write_cieu_audit(event_type: str, details: Dict):
    """Write CIEU audit record for import operation."""
    import sqlite3
    import uuid

    event_id = str(uuid.uuid4())
    seq_global = int(time.time() * 1_000_000)  # microsecond timestamp
    created_at = time.time()

    conn = sqlite3.connect(CIEU_DB_PATH)

    # Use existing schema (don't CREATE TABLE — already exists)
    conn.execute("""
        INSERT INTO cieu_events (
            event_id, seq_global, created_at, session_id, agent_id, event_type,
            decision, passed, task_description, params_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        event_id,
        seq_global,
        created_at,
        "yml_import",  # session_id
        "cto",         # agent_id
        event_type,    # event_type
        "allow",       # decision (import is allowed)
        1,             # passed
        json.dumps(details),  # task_description (repurpose for details)
        json.dumps(details)   # params_json
    ))

    conn.commit()
    conn.close()

    return event_id


def import_file(
    file_path: Path,
    memory_type: str,
    half_life_days: float,
    agent_id: str,
    store: MemoryStore,
    existing_hashes: set
) -> Tuple[int, int]:
    """
    Import a single file into memory store.

    Returns:
        (imported_count, skipped_count)
    """
    if not file_path.exists():
        return 0, 0

    content = file_path.read_text(encoding='utf-8')
    title = extract_title_from_markdown(content)
    chunks = split_content(content)

    imported = 0
    skipped = 0

    for i, chunk in enumerate(chunks):
        chunk_hash = compute_content_hash(chunk)

        if chunk_hash in existing_hashes:
            skipped += 1
            continue

        # Create memory object
        mem = Memory(
            agent_id=agent_id,
            memory_type=memory_type,
            content=chunk,
            initial_score=1.0,
            half_life_days=half_life_days,
            context_tags=[
                f"source:{file_path.name}",
                f"title:{title}",
                f"chunk:{i+1}/{len(chunks)}"
            ],
            metadata={
                "source_file": str(file_path.relative_to(COMPANY_ROOT)),
                "import_time": time.time(),
                "chunk_index": i,
                "total_chunks": len(chunks),
                "content_hash": chunk_hash
            }
        )

        # Store memory
        cieu_ref = write_cieu_audit("KNOWLEDGE_IMPORT", {
            "file": str(file_path.relative_to(COMPANY_ROOT)),
            "chunk": f"{i+1}/{len(chunks)}",
            "agent_id": agent_id,
            "memory_type": memory_type
        })

        store.remember(mem, cieu_ref=cieu_ref)
        existing_hashes.add(chunk_hash)
        imported += 1

    return imported, skipped


def main():
    """Main import process."""
    print("Y* Memory Layer — Full Knowledge Import")
    print("=" * 60)
    print(f"Database: {DB_PATH}")
    print(f"Company Root: {COMPANY_ROOT}")
    print()

    # Initialize store
    store = MemoryStore(str(DB_PATH))

    # Load existing content hashes
    print("Loading existing memory hashes for deduplication...")
    existing_hashes = load_existing_hashes(store)
    print(f"Found {len(existing_hashes)} existing memories")
    print()

    # Process each import rule
    total_imported = 0
    total_skipped = 0
    total_files = 0

    for pattern, mem_type, half_life, agent in IMPORT_RULES:
        print(f"Processing: {pattern}")
        print(f"  Type: {mem_type} | Half-life: {half_life}d | Agent: {agent}")

        # Resolve glob pattern
        if '*' in pattern:
            files = list(COMPANY_ROOT.glob(pattern))
        else:
            files = [COMPANY_ROOT / pattern]

        files = [f for f in files if f.exists()]

        if not files:
            print(f"  WARNING: No files found for pattern {pattern}")
            print()
            continue

        for file_path in files:
            imported, skipped = import_file(
                file_path,
                mem_type,
                half_life,
                agent,
                store,
                existing_hashes
            )

            total_imported += imported
            total_skipped += skipped
            total_files += 1

            print(f"  {file_path.name}: +{imported} imported, {skipped} skipped")

        print()

    # Final report
    print("=" * 60)
    print("IMPORT COMPLETE")
    print(f"Files processed: {total_files}")
    print(f"New memories imported: {total_imported}")
    print(f"Duplicates skipped: {total_skipped}")
    print(f"Total memories in DB: {len(existing_hashes)}")
    print()

    # Write final CIEU audit
    write_cieu_audit("KNOWLEDGE_IMPORT_COMPLETE", {
        "files_processed": total_files,
        "memories_imported": total_imported,
        "duplicates_skipped": total_skipped,
        "total_memories": len(existing_hashes)
    })

    print("CIEU audit records written to .ystar_cieu.db")


if __name__ == "__main__":
    main()
