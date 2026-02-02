# Supported Commands (v1.1)

v1.1 expands the command surface with storage compaction and improved index inspection. Behavior remains backward compatible with v1.0 unless noted.

| Command | Purpose | Notes |
| --- | --- | --- |
| `create_collection` | Create a collection | Idempotent on name |
| `upsert` | Insert or update documents | Requires `id` and `embedding` |
| `query` | Vector search | Supports metadata filters |
| `delete` | Remove documents | By `id` or filter |
| `list_collections` | List collections | Returns name + stats |
| `describe_index` | Inspect index | HNSW metrics + build params |
| `compact` | Optimize storage | New in v1.1 |

Command theory and behavior:

`compact`
- Rewrites storage segments to remove tombstones from deletes.
- Safe for concurrent reads; may delay writes during compaction windows.
- Improves query performance when many documents were deleted.
- Failure modes: insufficient disk, compaction lock contention.

`query` changes in v1.1
- Supports range filters on numeric metadata keys.
- Filter evaluation can be strict or relaxed depending on `filter_mode`.

Request:
```json
{
  "collection": "articles",
  "vector": [0.1, 0.2, 0.3],
  "top_k": 5,
  "filter": {"rating": {"$gte": 4}}
}
```

Response:
```json
{
  "results": [
    {"id": "doc_010", "score": 0.89, "metadata": {"rating": 4, "topic": "security"}}
  ]
}
```

`describe_index` changes in v1.1
- Exposes build parameters (M, efConstruction) and current `efSearch`.
- Useful for troubleshooting recall vs latency.
