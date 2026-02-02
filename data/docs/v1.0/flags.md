# Flags Reference (v1.0)

Flags apply to the CLI client and are resolved in the following order: command line, config file, environment variables. Use the CLI flags for quick experiments and move persistent values into config for production.

| Flag | Type | Default | Description |
| --- | --- | --- | --- |
| `--endpoint` | string | `http://localhost:8000` | API base URL |
| `--api-key` | string | none | API key for auth |
| `--namespace` | string | `default` | Logical tenant |
| `--consistency` | string | `eventual` | `eventual` or `strong` |
| `--timeout` | int | `30` | Request timeout (seconds) |
| `--top-k` | int | `10` | Max results for `query` |

Details:
- `--endpoint` should include the protocol; TLS requires `https`.
- `--api-key` is required for any write command such as `upsert` or `delete`.
- `--namespace` scopes all requests; changing it is equivalent to changing tenants.
- `--consistency=strong` trades latency for stronger read-after-write behavior.
- `--timeout` applies per request; long-running queries will be canceled.
- `--top-k` controls recall and latency; higher values cost more compute.

Examples:
```bash
vectordb query --endpoint http://localhost:8000 --namespace default --top-k 5
```

Failure modes:
- Missing `--api-key` returns 401 on writes.
- Very high `--top-k` may return 400 if it exceeds server limits.
