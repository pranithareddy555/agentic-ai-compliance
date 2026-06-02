from __future__ import annotations

import re
from pathlib import Path


def load_text_files(folder_path: str) -> list[tuple[str, str]]:
    folder = Path(folder_path)
    files: list[tuple[str, str]] = []
    for path in sorted(folder.rglob("*")):
        if path.suffix.lower() in {".md", ".txt"} and path.is_file():
            files.append((path.name, path.read_text(encoding="utf-8")))
    return files


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, chunk_size: int = 650, overlap: int = 80) -> list[str]:
    cleaned = normalize_text(text)
    if len(cleaned) <= chunk_size:
        return [cleaned]

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(len(cleaned), start + chunk_size)
        chunks.append(cleaned[start:end])
        if end >= len(cleaned):
            break
        start = max(0, end - overlap)
    return chunks


def extract_candidate_clauses(policy_text: str) -> list[str]:
    policy_text = policy_text.replace("\r", "")
    parts = re.split(r"\n\s*\n|(?<=[.;])\s+(?=[A-Z])", policy_text)
    clauses = [normalize_text(p) for p in parts if normalize_text(p)]
    return clauses[:20]
