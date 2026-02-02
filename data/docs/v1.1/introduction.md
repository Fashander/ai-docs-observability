# Introduction (v1.1)

VectorDB is a document database with vector search capabilities. It stores JSON documents with embeddings, supports hybrid filters, and provides a simple HTTP API for indexing and retrieval.

In v1.1, Feature X and storage compaction add scale and stability for long-lived collections. Filter semantics are richer, and consistency controls are more explicit to reduce surprise under load.

Collections remain the primary unit of isolation. Each collection has its own index and statistics, allowing you to reason about latency and recall per workload.

Key additions:
- Feature X for secondary reranking.
- Compaction to reclaim space after large deletes.
- Filter mode to control strictness when metadata is incomplete.
