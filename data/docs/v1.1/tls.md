# TLS (v1.1)

To enable TLS, set:
- `TLS_ENABLED=true`
- Provide certificates via `TLS_CERT_PATH` and `TLS_KEY_PATH`.

Operational guidance:
- Use a certificate with a SAN matching the hostname clients use.
- Keep private keys readable by the VectorDB process only.
- Restart after rotation to pick up new certificates.
- Prefer TLS 1.2 or newer for client connections.

Failure modes:
- Invalid cert/key pairs prevent startup.
- Hostname mismatch results in client handshake failures.
- Missing intermediate certs cause trust errors in some clients.
