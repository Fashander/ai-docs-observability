# Configuration (v1.1)

Configuration can be set via environment variables or a YAML file. Environment variables are convenient for containers, while the config file is preferred for local development and repeatable scripts.

Environment variables:
- `DB_ENDPOINT`
- `DB_API_KEY`
- `DB_NAMESPACE`
- `DB_TIMEOUT_SECONDS`
- `DB_CONSISTENCY`
- `DB_FILTER_MODE`

Config file (`config.yaml`):
- `endpoint`
- `api_key`
- `namespace`
- `timeout_seconds`
- `consistency`
- `filter_mode`

Resolution order:
1) CLI flags
2) Environment variables
3) Config file
4) Defaults

Example config:
```yaml
endpoint: https://vectordb.example.com
api_key: "prod-key"
namespace: "payments"
timeout_seconds: 45
consistency: "strong"
filter_mode: "strict"
```

Failure modes:
- `filter_mode` set to an unknown value defaults to `auto`.
- Invalid endpoint schemes (e.g., missing https) can break TLS.
