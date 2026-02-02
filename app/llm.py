from __future__ import annotations

import json
import os
import urllib.request
from typing import Any, Dict, List, Optional

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
OLLAMA_TIMEOUT_SEC = float(os.getenv("OLLAMA_TIMEOUT_SEC", "15"))


def _build_prompt(query: str, hits: List[Dict[str, Any]], requested_version: Optional[str]) -> str:
    header = "Answer the user question using only the provided documentation context."
    if requested_version:
        header += f" The user asked about version v{requested_version}."
    parts = [header, "\nQuestion:\n" + query, "\nContext:"]
    for idx, hit in enumerate(hits, start=1):
        meta = hit.get("meta", {})
        title = meta.get("title", "unknown")
        version = meta.get("version") or "unknown"
        parts.append(f"\n[{idx}] {title} (v{version})\n{hit.get('text', '')}")
    parts.append("\nIf the answer is not in the context, say you do not know.")
    return "\n".join(parts)


def generate_with_ollama(
    query: str, hits: List[Dict[str, Any]], requested_version: Optional[str]
) -> Optional[str]:
    if not OLLAMA_MODEL:
        return None
    prompt = _build_prompt(query, hits, requested_version)
    payload = json.dumps(
        {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT_SEC) as resp:
            body = resp.read().decode("utf-8")
    except Exception:
        return None

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return None
    answer = data.get("response")
    if isinstance(answer, str) and answer.strip():
        return answer.strip()
    return None
