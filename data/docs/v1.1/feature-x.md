# Feature X (v1.1)

Feature X is supported starting in v1.1. It enables secondary reranking on top of the base vector similarity score.

How it works:
- The base vector index returns an initial candidate set.
- Feature X applies a lightweight reranker that considers metadata signals.
- The final ordering combines similarity with reranker adjustments.

Enable it by setting:
- `FEATURE_X_ENABLED=true`

Configuration knobs:
- `FEATURE_X_WEIGHT` controls the influence of reranking (default 0.2).
- `FEATURE_X_CANDIDATES` controls candidate set size (default 100).

Constraints:
- Feature X requires `--consistency=strong`.
- Feature X is not available on read-only API keys.
- Feature X adds a small latency overhead per query.

Failure modes:
- Too small candidate sets reduce recall.
- Overweighting reranker signals can distort relevance.
