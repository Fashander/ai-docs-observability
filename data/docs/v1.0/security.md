# Security (v1.0)

Security is enforced at the API layer and within namespace boundaries. All access is authenticated, and authorization rules are applied before any data is read or modified.

Authentication:
- API keys are required for write operations.
- Read-only keys can be scoped to a namespace.
- API keys are transmitted via the `Authorization: Bearer` header.

Authorization:
- Namespaces enforce tenant isolation.
- Roles: `reader`, `writer`, `admin`.
- Role checks are evaluated per request and per collection.

Threat model assumptions:
- Clients are untrusted; every request must be authenticated.
- Network boundaries are not considered sufficient for trust.
- Audit logs are required for administrative actions.

Failure modes:
- Missing or invalid API keys return 401.
- Cross-namespace access returns 403.
- Excessive failed auth attempts trigger rate limits.

Example request:
```http
POST /collections/articles/query
Authorization: Bearer READ_ONLY_KEY
Content-Type: application/json
```
