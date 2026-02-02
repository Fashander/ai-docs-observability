# Security (v1.1)

Security is enforced at the API layer and within namespace boundaries. v1.1 adds JWT support and policy rules for fine-grained access control.

Authentication:
- API keys are required for write operations.
- JWTs are supported for short-lived access tokens.
- Tokens are transmitted via the `Authorization: Bearer` header.

Authorization:
- Namespaces enforce tenant isolation.
- Roles: `reader`, `writer`, `admin`.
- Policy rules can restrict access by collection prefix.
- Admins can rotate keys without downtime.

Audit model:
- Every administrative action is logged with a request ID.
- Failed authentication attempts are rate-limited and logged.
- Token rotation is recommended on a fixed cadence.

Failure modes:
- Expired JWTs return 401 with a `token_expired` reason.
- Policy rules can block writes if collection prefixes change.
- Role mismatches return 403 even with valid tokens.
