# Feature List (v1.1)

This release adds Feature X and expands filtering. The goal is better retrieval precision without forcing schema changes.

Supported:
- Collections
- Vector search with filters
- Basic indexes (HNSW)
- Metadata filtering (equality + range)
- Feature X (new)

Not supported:
- Sharding
- Multi-region replication

Operational notes:
- Range filters require numeric metadata values.
- Compaction is recommended after large deletes.
- Feature X increases CPU usage during query reranking.

Failure modes:
- Range filters on string values return 400.
- Compaction can delay writes if disk I/O is saturated.
- Misconfigured Feature X can reduce relevance if reranker weights are wrong.
