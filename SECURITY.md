# Security policy

## Reporting a vulnerability

Please do not publish exploitable vulnerabilities in a public issue. Contact the repository owner privately through GitHub with reproduction steps, impact, and a suggested mitigation if available.

## Trace privacy

ARK does not transmit traces by itself, but trace files may contain prompts, tool arguments, identifiers, or sensitive customer context.

- Use synthetic data in public issues and examples.
- Review trace files before sharing.
- The redaction helper is best-effort; it does not detect secrets embedded in arbitrary strings.
- Do not commit credentials, access tokens, or production customer traces.
