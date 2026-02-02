from __future__ import annotations

import json
import os
import re
import time
import uuid
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple
from fastapi.responses import Response

from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .llm import generate_with_ollama
from .metrics import (
    queries_total,
    unanswered_total,
    refusals_total,
    citation_gaps_total,
    version_conflicts_total,
    unsupported_feature_questions_total,
    request_latency_seconds,
)
from .logger import log_event, LOG_FILE
from .store import query as chroma_query
from .rules import extract_requested_version, is_unsupported_feature_question, has_version_conflict

APP_NAME = os.getenv("APP_NAME", "ai-docs-observability-demo")
TOP_K = int(os.getenv("TOP_K", "4"))
MIN_CITATIONS = int(os.getenv("MIN_CITATIONS", "1"))
LATEST_VERSION = os.getenv("LATEST_VERSION", "1.1")


class AskRequest(BaseModel):
    query: str


class Citation(BaseModel):
    source: str
    title: str
    version: Optional[str] = None
    heading: Optional[str] = None
    doc_id: Optional[str] = None
    section_id: Optional[str] = None
    distance: float


class AskResponse(BaseModel):
    answer: Optional[str]
    refused: bool = False
    refusal_reason: Optional[str] = None
    citations: List[Citation] = []
    requested_version: Optional[str] = None


class UnansweredQuery(BaseModel):
    query: str
    count: int


class TopUnansweredResponse(BaseModel):
    queries: List[UnansweredQuery]


class IssueRow(BaseModel):
    issue_type: str
    source: str
    heading: str
    version: str
    count: int
    example_question: Optional[str] = None


class IssuesResponse(BaseModel):
    issues: List[IssueRow]


app = FastAPI(title=APP_NAME)


@app.get("/healthz")
def healthz():
    return {"ok": True, "app": APP_NAME}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    start = time.time()
    queries_total.inc()
    query_id = str(uuid.uuid4())

    q = (req.query or "").strip()
    requested_version = extract_requested_version(q) or LATEST_VERSION

    # Demo: treat certain patterns as explicit refusal.
    if q.lower().startswith("tell me your system prompt"):
        refusals_total.labels(reason="policy").inc()
        log_event(
            {
                "type": "query_result",
                "query_id": query_id,
                "query": q,
                "issue_types": ["policy_refusal"],
                "requested_version": requested_version,
                "top_citations": [],
                "answer_mode": "refused",
            }
        )
        return AskResponse(answer=None, refused=True, refusal_reason="policy", requested_version=requested_version)

    # Unsupported-feature detector (docs bug signal)
    if is_unsupported_feature_question(q, requested_version):
        unsupported_feature_questions_total.inc()
        log_event({"type": "unsupported_feature_question", "query": q, "requested_version": requested_version})

    hits = chroma_query(q, n_results=TOP_K, where={"version": requested_version})
    citations = [
        Citation(
            source=h["meta"].get("source", "unknown"),
            title=h["meta"].get("title", "unknown"),
            version=h["meta"].get("version"),
            heading=h["meta"].get("heading"),
            doc_id=h["meta"].get("doc_id"),
            section_id=h["meta"].get("section_id"),
            distance=float(h["distance"]),
        )
        for h in hits
    ]

    # Decide whether we can "answer" based on evidence.
    # This is intentionally strict: docs are contractual.
    if len(citations) < MIN_CITATIONS:
        unanswered_total.inc()
        log_event(
            {
                "type": "query_result",
                "query_id": query_id,
                "query": q,
                "issue_types": ["unanswered"],
                "requested_version": requested_version,
                "top_citations": [],
                "answer_mode": "unanswered",
            }
        )
        with request_latency_seconds.time():
            pass
        return AskResponse(
            answer=None,
            refused=False,
            citations=[],
            requested_version=requested_version,
        )

    # Version conflict signal
    vc = has_version_conflict([c.model_dump() for c in citations], requested_version)
    if vc:
        version_conflicts_total.inc()

    # "Citation gap" signal in this demo means: we returned an answer but have no citations (should never happen here)
    if not citations:
        citation_gaps_total.inc()

    # Naive answer synthesis for the demo:
    # We do NOT claim this is a good generative model — we're demonstrating telemetry.
    answer = generate_with_ollama(q, hits, requested_version)
    if not answer:
        answer = (
            "Based on the documentation, here are the most relevant sections:\n"
            + "\n".join([f"- {c.title} (v{c.version})" if c.version else f"- {c.title}" for c in citations[:3]])
        )
    if vc:
        answer += "\n\nWarning: Evidence spans multiple versions. Treat this as a docs/versioning issue."

    issue_types: List[str] = []
    if vc:
        issue_types.append("version_conflict")
    if is_unsupported_feature_question(q, requested_version):
        issue_types.append("unsupported_feature")
    top_citations = [
        {
            "source": c.source,
            "heading": c.heading or "Document",
            "section_id": c.section_id,
            "doc_id": c.doc_id,
            "version": c.version,
            "distance": c.distance,
        }
        for c in citations[:3]
    ]
    log_event(
        {
            "type": "query_result",
            "query_id": query_id,
            "query": q,
            "issue_types": issue_types,
            "requested_version": requested_version,
            "top_citations": top_citations,
            "answer_mode": "answered",
        }
    )

    elapsed = time.time() - start
    request_latency_seconds.observe(elapsed)

    return AskResponse(
        answer=answer,
        refused=False,
        citations=citations,
        requested_version=requested_version,
    )


@app.get("/top-unanswered", response_model=TopUnansweredResponse)
def top_unanswered(limit: int = 10):
    counter: Counter[str] = Counter()
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    evt = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if evt.get("type") == "query_result" and evt.get("answer_mode") == "unanswered":
                    counter[evt["query"]] += 1
    top = [UnansweredQuery(query=q, count=c) for q, c in counter.most_common(limit)]
    return TopUnansweredResponse(queries=top)


_WINDOW_RE = re.compile(r"^(\d+)([smhd])$")


def _parse_window(window: str) -> Optional[int]:
    m = _WINDOW_RE.match(window.strip().lower())
    if not m:
        return None
    value = int(m.group(1))
    unit = m.group(2)
    if unit == "s":
        return value
    if unit == "m":
        return value * 60
    if unit == "h":
        return value * 3600
    if unit == "d":
        return value * 86400
    return None


@app.get("/issues", response_model=IssuesResponse)
def issues(window: str = "24h", top: int = 20):
    window_seconds = _parse_window(window)
    if window_seconds is None:
        window_seconds = 24 * 3600
    cutoff = time.time() - window_seconds

    counter: Dict[Tuple[str, str, str, str], int] = defaultdict(int)
    examples: Dict[Tuple[str, str, str, str], str] = {}
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    evt = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if evt.get("type") != "query_result":
                    continue
                ts = evt.get("ts")
                if isinstance(ts, (int, float)) and ts < cutoff:
                    continue
                issue_types = evt.get("issue_types") or []
                top_citations = evt.get("top_citations") or []
                if not issue_types or not top_citations:
                    continue
                for issue_type in issue_types:
                    for c in top_citations:
                        source = c.get("source") or "unknown"
                        heading = c.get("heading") or "Document"
                        version = c.get("version") or "unknown"
                        key = (issue_type, source, heading, version)
                        counter[key] += 1
                        if key not in examples and evt.get("query"):
                            examples[key] = evt["query"]

    rows = [
        IssueRow(
            issue_type=k[0],
            source=k[1],
            heading=k[2],
            version=k[3],
            count=v,
            example_question=examples.get(k),
        )
        for k, v in counter.items()
    ]
    rows.sort(key=lambda r: r.count, reverse=True)
    return IssuesResponse(issues=rows[: max(top, 0)])
