# Feature List (v1.0)

The feature surface in v1.0 is intentionally conservative. The goal is to make behavior easy to reason about and to produce reliable telemetry during early adoption.

Supported:
- Collections
- Vector search with filters
- Basic indexes (HNSW)
- Metadata filtering (equality only)

Not supported:
- Feature X (planned)
- Sharding
- Multi-region replication

Operational limitations:
- Each collection must fit on a single node.
- Index builds are offline and may block writes for large collections.

What this means in practice:
- Equality-only metadata filters are best for categorical constraints.
- Without sharding, capacity planning must consider peak collection size.
- Single-node indexes simplify failure modes but limit throughput.

Failure modes to watch:
- Large collections can cause long index build times.
- Imbalanced metadata keys reduce filter selectivity and slow queries.
- Incorrect embedding dimensions will hard-fail writes.
