# Sample Docs Corpus

This folder intentionally contains a tiny, imperfect “documentation set” so the observability signals are easy to reproduce.

- `product-v1.0.md` says Feature X is **not supported**.
- `product-v1.1.md` introduces Feature X and adds a few config flags.
- `troubleshooting.md` contains a common-but-incomplete TLS section.

Run ingestion, then hit the `/ask` endpoint with queries like:
- “Does product support Feature X?”
- “How do I configure TLS?”
- “Is Feature X supported in v1.0?”
