# Contributing to Agent Reliability Kit

Thank you for helping make agent workflows easier to inspect and test.

## Great first contributions

- Add an edge-case test for JSONL loading or diffing.
- Improve CLI output when a regression is detected.
- Add synthetic example traces.
- Improve documentation for Windows, macOS, or Linux setup.
- Propose an optional adapter for an agent framework.

## Development workflow

1. Open an issue for substantial changes so scope can be discussed.
2. Fork the repository and create a focused branch.
3. Add or update tests for behavioral changes.
4. Run `python -m unittest discover -s tests -v`.
5. Open a pull request describing the problem, solution, and validation.

## Project expectations

- Python 3.10+.
- Keep the core dependency-free when practical.
- Keep public APIs typed and documented.
- Do not add hidden telemetry or unexpected network calls to the core.
- Never commit credentials, secrets, or real production traces.
- Be direct, kind, and constructive in review discussions.

Large integrations should preferably be optional extras instead of mandatory core dependencies.
