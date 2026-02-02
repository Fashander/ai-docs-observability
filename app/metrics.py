from __future__ import annotations

from prometheus_client import Counter, Histogram

NAMESPACE = "ai_docs"

queries_total = Counter(
    f"{NAMESPACE}_queries_total",
    "Total queries received by the docs assistant",
)

unanswered_total = Counter(
    f"{NAMESPACE}_unanswered_total",
    "Queries where the assistant could not answer confidently from docs",
)

refusals_total = Counter(
    f"{NAMESPACE}_refusals_total",
    "Queries explicitly refused",
    labelnames=("reason",),
)

citation_gaps_total = Counter(
    f"{NAMESPACE}_citation_gaps_total",
    "Answers returned without citations",
)

version_conflicts_total = Counter(
    f"{NAMESPACE}_version_conflicts_total",
    "Answers where citations disagree on version (multi-version evidence)",
)

unsupported_feature_questions_total = Counter(
    f"{NAMESPACE}_unsupported_feature_questions_total",
    "Queries asking about features that are not supported (based on doc evidence / rules)",
)

request_latency_seconds = Histogram(
    f"{NAMESPACE}_request_latency_seconds",
    "Latency for /ask requests",
    buckets=(0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4),
)
