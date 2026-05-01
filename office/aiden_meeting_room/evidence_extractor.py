from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


FORBIDDEN_PATH_MARKERS = (
    ".env",
    "secret",
    ".db",
    ".db-wal",
    ".db-shm",
    ".log",
    "active_agent",
    ".ystar_active_agent",
)


@dataclass(frozen=True)
class EvidenceItem:
    source: str
    line: int
    label: str
    text: str
    classification: str

    @property
    def ref(self) -> str:
        return f"{self.source}:{self.line}"


def safe_read_lines(repo_root: Path, rel_path: str) -> List[str]:
    path = (repo_root / rel_path).resolve()
    lowered = str(path).lower()
    if any(marker in lowered for marker in FORBIDDEN_PATH_MARKERS):
        return []
    if not path.exists() or not path.is_file():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def compact_text(text: str, max_len: int = 220) -> str:
    normalized = " ".join(text.strip().split())
    if len(normalized) <= max_len:
        return normalized
    return normalized[: max_len - 1].rstrip() + "…"


def find_keyword_evidence(
    repo_root: Path,
    rel_path: str,
    keywords: Iterable[str],
    label: str,
    classification: str,
    limit: int = 3,
) -> List[EvidenceItem]:
    lines = safe_read_lines(repo_root, rel_path)
    lowered_keywords = [keyword.lower() for keyword in keywords]
    items: List[EvidenceItem] = []
    for index, line in enumerate(lines, start=1):
        lower = line.lower()
        if any(keyword in lower for keyword in lowered_keywords):
            items.append(
                EvidenceItem(
                    source=rel_path,
                    line=index,
                    label=label,
                    text=compact_text(line),
                    classification=classification,
                )
            )
            if len(items) >= limit:
                break
    return items


def format_evidence(items: Iterable[EvidenceItem], limit: int = 6) -> str:
    selected = list(items)[:limit]
    if not selected:
        return "Evidence: no direct repo evidence found in indexed files."
    return "\n".join(
        f"- Evidence: {item.ref} [{item.classification}] {item.label}: {item.text}"
        for item in selected
    )
