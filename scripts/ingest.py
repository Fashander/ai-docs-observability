from __future__ import annotations

import glob
import hashlib
import os
import re

from app.store import upsert_docs

DOCS_GLOB = os.getenv("DOCS_GLOB", "data/docs/**/*.md")


_VERSION_RE = re.compile(r"v(\d+\.\d+)")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")
_FENCE_RE = re.compile(r"^(```|~~~)")


def split_markdown_sections(md: str):
    lines = md.splitlines()
    sections = []
    stack = []
    current_heading = None
    current_lines = []
    in_code_block = False

    def heading_path() -> str:
        if not stack:
            return "Document"
        return " > ".join([h for _, h in stack])

    def flush_section():
        body = "\n".join(current_lines).strip()
        if not body:
            return
        if current_heading:
            path = heading_path()
            sections.append({"heading": current_heading, "heading_path": path, "text": body})
        else:
            sections.append({"heading": "Preface", "heading_path": "Preface", "text": body})

    for line in lines:
        if _FENCE_RE.match(line.strip()):
            in_code_block = not in_code_block
            current_lines.append(line)
            continue

        if not in_code_block:
            m = _HEADING_RE.match(line)
            if m:
                flush_section()
                level = len(m.group(1))
                title = m.group(2).strip()
                while stack and stack[-1][0] >= level:
                    stack.pop()
                stack.append((level, title))
                current_heading = title
                current_lines = []
                continue

        current_lines.append(line)

    flush_section()

    if not sections:
        return [{"heading": "Document", "heading_path": "Document", "text": md}]
    return sections


def detect_version(path: str, text: str) -> str:
    normalized = path.replace(os.sep, "/").lower()
    m = re.search(r"/v(\d+\.\d+)/", normalized)
    if m:
        return m.group(1)
    for line in text.splitlines()[:10]:
        line = line.strip()
        if line.startswith("#"):
            m = re.search(r"\(v(\d+\.\d+)\)", line.lower())
            if m:
                return m.group(1)
            break
    return "unknown"


def make_doc_id(path: str) -> str:
    rel = os.path.relpath(path)
    return hashlib.sha1(rel.encode("utf-8")).hexdigest()


def make_section_id(doc_id: str, heading_path: str) -> str:
    key = f"{doc_id}:{heading_path}".encode("utf-8")
    return hashlib.sha1(key).hexdigest()


def main() -> None:
    paths = sorted(glob.glob(DOCS_GLOB, recursive=True))
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
            heading_path = section["heading_path"]
            section_id = make_section_id(doc_id, heading_path)
            docs.append(
                {
                    "id": section_id,
                    "text": f"Section: {heading_path}\n\n{section['text']}",
                    "meta": {
                        "source": p,
                        "version": version,
                        "title": os.path.basename(p),
                        "heading": heading,
                        "doc_id": doc_id,
                        "section_id": section_id,
                        "heading_path": heading_path,
                    },
                }
            )

    upsert_docs(docs)
    print(f"Ingested {len(docs)} sections into Chroma.")


if __name__ == "__main__":
    main()
