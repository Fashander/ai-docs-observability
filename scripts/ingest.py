from __future__ import annotations

import glob
import hashlib
import os
import re

from app.store import upsert_docs

DOCS_GLOB = os.getenv("DOCS_GLOB", "data/docs/*.md")


_VERSION_RE = re.compile(r"v(\d+\.\d+)")
_HEADING_RE = re.compile(r"(?m)^#{1,6}\s+(.+)$")


def split_markdown_sections(md: str):
    parts = re.split(r"(?m)^#{1,6}\s+", md)
    if len(parts) == 1:
        return [{"heading": "Document", "text": md}]
    preface = parts[0].strip()
    rest = parts[1:]
    sections = []
    if preface:
        sections.append({"heading": "Preface", "text": preface})
    headings = _HEADING_RE.findall(md)
    for h, body in zip(headings, rest):
        body = body.strip()
        if body:
            sections.append({"heading": h.strip(), "text": body})
    return sections


def detect_version(path: str, text: str) -> str:
    base = os.path.basename(path).lower()
    m = _VERSION_RE.search(base)
    if m:
        return m.group(1)
    head = text[:500].lower()
    m = _VERSION_RE.search(head)
    if m:
        return m.group(1)
    return "unknown"


def make_doc_id(path: str) -> str:
    rel = os.path.relpath(path)
    return hashlib.sha1(rel.encode("utf-8")).hexdigest()


def make_section_id(doc_id: str, heading: str) -> str:
    key = f"{doc_id}:{heading}".encode("utf-8")
    return hashlib.sha1(key).hexdigest()


def main() -> None:
    paths = sorted(glob.glob(DOCS_GLOB))
    if not paths:
        raise SystemExit(f"No docs found for glob: {DOCS_GLOB}")

    docs = []
    for p in paths:
        with open(p, "r", encoding="utf-8") as f:
            text = f.read().strip()

        doc_id = make_doc_id(p)
        version = detect_version(p, text)
        for section in split_markdown_sections(text):
            heading = section["heading"]
            docs.append(
                {
                    "id": make_section_id(doc_id, heading),
                    "text": section["text"],
                    "meta": {
                        "source": p,
                        "version": version,
                        "title": os.path.basename(p),
                        "heading": heading,
                        "doc_id": doc_id,
                        "section_id": make_section_id(doc_id, heading),
                    },
                }
            )

    upsert_docs(docs)
    print(f"Ingested {len(docs)} sections into Chroma.")


if __name__ == "__main__":
    main()
