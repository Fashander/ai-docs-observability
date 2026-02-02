# Sample Docs Corpus

This folder contains a small documentation set for a hypothetical vector database. The docs are split by version to simulate breaking changes and incremental feature additions.

- `v1.0/` describes the baseline command set, flags, configuration, and security model.
- `v1.1/` adds Feature X, filter mode, and extended security guidance.
- `troubleshooting.md` contains a common-but-incomplete TLS section.

Run ingestion, then hit the `/ask` endpoint with queries like:
- "Does product support Feature X?"
- "How do I configure TLS?"
- "Is Feature X supported in v1.0?"
