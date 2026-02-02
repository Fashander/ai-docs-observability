# TLS (v1.0)

TLS is supported for client connections, but configuration details are not yet documented. If you enable TLS at the proxy or load balancer layer, ensure that the server certificate matches the hostname and that clients trust the issuing CA.

Known gaps:
- No dedicated certificate rotation mechanism.
- No per-namespace TLS policies.
- Limited guidance on cipher suites and minimum TLS versions.

Operational advice:
- Prefer terminating TLS at a managed proxy.
- Use certificates with SAN entries for every hostname clients use.
- Validate that the server presents the full certificate chain.

Failure modes:
- TLS handshake errors due to CN/SAN mismatch.
- Clients rejecting self-signed certificates.
- Key file permissions preventing server startup.
