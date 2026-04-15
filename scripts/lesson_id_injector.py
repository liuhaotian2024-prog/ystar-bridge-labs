#!/usr/bin/env python3
"""
Inject lesson_id UUID front-matter into all knowledge/{role}/lessons/*.md files.
Idempotent: skips files that already have lesson_id.
Phase 1 of Lesson Usage Tracking (CEO 8f049222 design, Samantha A030 merge).

Usage:
    python3 scripts/lesson_id_injector.py [--dry-run]
"""
import argparse
import re
import uuid
from pathlib import Path


def has_lesson_id(content: str) -> bool:
    """Check if front-matter already contains lesson_id."""
    # Match YAML front-matter block
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return False
    fm_block = fm_match.group(1)
    return bool(re.search(r'^lesson_id:\s*\S', fm_block, re.MULTILINE))


def inject_lesson_id(content: str, lesson_id: str) -> str:
    """Inject lesson_id into front-matter. Create front-matter if missing."""
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)

    if fm_match:
        # Front-matter exists, append lesson_id at end of block
        fm_block = fm_match.group(1)
        new_fm = f"---\n{fm_block}\nlesson_id: {lesson_id}\n---"
        return content.replace(fm_match.group(0), new_fm, 1)
    else:
        # No front-matter, create minimal one
        new_fm = f"---\nlesson_id: {lesson_id}\n---\n\n"
        return new_fm + content


def main():
    parser = argparse.ArgumentParser(description="Inject lesson_id into lesson files")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    args = parser.parse_args()

    workspace = Path(__file__).resolve().parent.parent
    knowledge_dir = workspace / "knowledge"

    if not knowledge_dir.exists():
        print(f"ERROR: knowledge/ directory not found at {knowledge_dir}")
        return 1

    # Find all lesson .md files
    lesson_files = list(knowledge_dir.glob("*/lessons/*.md"))

    if not lesson_files:
        print(f"No lesson files found in {knowledge_dir}/*/lessons/")
        return 0

    processed = 0
    skipped = 0
    errors = 0

    for lesson_path in sorted(lesson_files):
        try:
            content = lesson_path.read_text(encoding="utf-8")

            if has_lesson_id(content):
                skipped += 1
                continue

            lesson_id = str(uuid.uuid4())
            new_content = inject_lesson_id(content, lesson_id)

            if args.dry_run:
                print(f"[DRY-RUN] Would inject {lesson_id} into {lesson_path.relative_to(workspace)}")
            else:
                lesson_path.write_text(new_content, encoding="utf-8")
                print(f"✓ Injected {lesson_id} into {lesson_path.relative_to(workspace)}")

            processed += 1

        except Exception as e:
            print(f"✗ ERROR processing {lesson_path.relative_to(workspace)}: {e}")
            errors += 1

    print(f"\n{'[DRY-RUN] ' if args.dry_run else ''}Summary:")
    print(f"  Processed: {processed}")
    print(f"  Skipped (already have lesson_id): {skipped}")
    print(f"  Errors: {errors}")

    return 1 if errors > 0 else 0


if __name__ == "__main__":
    exit(main())
