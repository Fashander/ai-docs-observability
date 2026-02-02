# Configuration (v1.0)

Configuration can be set via environment variables or a YAML file. Environment variables are convenient for containers, while the config file is preferred for local development and repeatable scripts.

Environment variables:
- `DB_ENDPOINT`
- `DB_API_KEY`
- `DB_NAMESPACE`
- `DB_TIMEOUT_SECONDS`

Config file (`config.yaml`):
- `endpoint`
- `api_key`
- `namespace`
- `timeout_seconds`
- `consistency`

Resolution order:
1) CLI flags
2) Environment variables
3) Config file
4) Defaults

Behavior notes:
- If both a config file and environment variables are provided, environment values take precedence.
- Missing values fall back to defaults.
- The endpoint must be reachable at startup; the client does not retry by default.

Example config:
```yaml
endpoint: http://localhost:8000
api_key: "test-key"
namespace: "default"
timeout_seconds: 30
consistency: "eventual"
```

Failure modes:
- A malformed config file will prevent startup.
- Invalid consistency values fall back to defaults with a warning.
