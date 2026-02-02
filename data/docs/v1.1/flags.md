# Flags Reference (v1.1)

Flags apply to the CLI client and are resolved in the following order: command line, config file, environment variables. v1.1 introduces filter mode to control strictness when metadata is incomplete.

| Flag | Type | Default | Description |
| --- | --- | --- | --- |
| `--endpoint` | string | `http://localhost:8000` | API base URL |
| `--api-key` | string | none | API key for auth |
| `--namespace` | string | `default` | Logical tenant |
| `--consistency` | string | `eventual` | `eventual` or `strong` |
| `--timeout` | int | `30` | Request timeout (seconds) |
| `--top-k` | int | `10` | Max results for `query` |
| `--filter-mode` | string | `auto` | `auto`, `strict`, `relaxed` |

Details:
- `auto` selects strictness based on filter completeness.
- `strict` requires every result to match every filter clause.
- `relaxed` allows partial matches when metadata is missing.

Examples:
```bash
vectordb query --filter-mode strict --top-k 20
```

Failure modes:
- `strict` mode with sparse metadata can return zero results.
- `relaxed` mode can increase false positives.
