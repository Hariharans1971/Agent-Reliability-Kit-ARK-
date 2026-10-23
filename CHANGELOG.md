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
- Added JUnit XML output for policy/evaluation checks, with passing and failing report tests.
- Added strict trace-event schema validation with line-specific malformed-input errors.
- Added dotted ignore paths for nested dict keys and indexed list values in trace diffs.
- Added a consumer-style CI workflow that invokes the published composite-action reference on passing and deliberately failing examples.
- Added JUnit XML output for policy/evaluation checks, with regression tests for passing and failing reports.
- Added strict trace-event validation for field types, duration values, and token counters.
- Added synthetic customer-support trace example.
- Added unit tests and Python 3.10–3.12 GitHub Actions matrix.
- Added contributor, security, community, and release documentation.
