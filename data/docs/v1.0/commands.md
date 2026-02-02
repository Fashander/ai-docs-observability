# Supported Commands (v1.0)

This version exposes a small set of commands that cover the full indexing and retrieval lifecycle. All commands are scoped to a collection unless otherwise noted.

| Command | Purpose | Notes |
| --- | --- | --- |
| `create_collection` | Create a collection | Idempotent on name |
| `upsert` | Insert or update documents | Requires `id` and `embedding` |
| `query` | Vector search | Supports metadata filters |
| `delete` | Remove documents | By `id` or filter |
| `list_collections` | List collections | Returns name + stats |
| `describe_index` | Inspect index | Basic HNSW metrics |

Command theory and behavior:

`create_collection`
- Allocates a logical namespace and an index.
- Idempotent: calling it with the same name returns the existing collection.
- Creates index defaults (HNSW) with standard parameters.
- Failure modes: invalid name, unauthorized, or index capacity exceeded.

Request:
```json
{
  "name": "articles",
  "dimensions": 384,
  "metadata": {"owner": "search"}
}
```

Response:
```json
{
  "name": "articles",
  "dimensions": 384,
  "created": true
}
```

`upsert`
- Writes or replaces a document by `id`.
- Requires an `embedding` field with the correct dimensionality.
- Metadata keys are merged; conflicting keys are overwritten.
- Upserts are atomic per document and do not require a full reindex.
- Failure modes: dimension mismatch, missing id, invalid metadata type.

Request:
```json
{
  "collection": "articles",
  "documents": [
    {
      "id": "doc_001",
      "embedding": [0.1, 0.2, 0.3],
      "metadata": {"lang": "en", "topic": "tls"}
    }
  ]
}
```

Response:
```json
{
  "collection": "articles",
  "upserted": 1,
  "errors": []
}
```

`query`
- Accepts a query vector and returns the most similar documents.
- Results are ranked by cosine similarity.
- Filters are applied before scoring; a document must match all filter clauses.
- A higher score means more similar; scores are not calibrated probabilities.
- Failure modes: empty index, invalid filter, or top_k too large.

Request:
```json
{
  "collection": "articles",
  "vector": [0.1, 0.2, 0.3],
  "top_k": 5,
  "filter": {"lang": "en"}
}
```

Response:
```json
{
  "results": [
    {"id": "doc_001", "score": 0.92, "metadata": {"lang": "en", "topic": "tls"}}
  ]
}
```

`delete`
- Removes documents by explicit `id` list or by filter.
- Filter deletes are strict: all clauses must match.
- Deleting many documents may temporarily reduce recall until compaction.
- Failure modes: filter too broad, unauthorized, or unknown IDs.

`list_collections`
- Returns available collections with basic statistics.
- Useful for inventory and verifying ingestion.

`describe_index`
- Surfaces index size, graph degree, and build status.
- Use it to understand recall and latency tradeoffs.
