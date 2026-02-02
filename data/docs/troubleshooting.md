# Troubleshooting

This section contains common operational issues encountered when running VectorDB. It is intentionally incomplete so that unanswered and citation gap signals can be observed.

## TLS handshake errors
If you see TLS handshake errors, double-check that:
- The client trusts the server CA.
- Your certificate CN/SAN matches the hostname.
- The certificate chain is complete and ordered correctly.

Common mistakes:
- Pointing to a key file that the process cannot read (permissions).
- Using a certificate generated for a different environment.

Note: This section is intentionally incomplete to demonstrate unanswered signals.
