# Changelog

Notable changes are recorded here. This project is in its initial MVP phase.

## 0.1.0 — initial public MVP

- Added a local-first JSONL trace recorder.
- Added trace loading with line-specific malformed-input errors.
- Added CLI commands for inspection, comparison, and deterministic checks.
- Added a best-effort recursive redaction helper.
- Added JSON policy contracts for allowed/required/forbidden events, event-count and call limits, and total/per-event duration/token budgets with missing-metric failures.
- Added a reusable composite GitHub Action to enforce those contracts in CI.
- Added regression tests for allowlist violations, per-event budget failures, and missing metric handling.
- Added synthetic customer-support trace example.
- Added unit tests and Python 3.10–3.12 GitHub Actions matrix.
- Added contributor, security, community, and release documentation.
