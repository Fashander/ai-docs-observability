# Troubleshooting

## TLS handshake errors
If you see TLS handshake errors, double-check that:
- The client trusts the server CA.
- Your certificate CN/SAN matches the hostname.

Common mistake:
- Pointing to a key file that the process cannot read (permissions).

Note: This section is intentionally incomplete to demonstrate “unanswered” and “citation gap” signals.
