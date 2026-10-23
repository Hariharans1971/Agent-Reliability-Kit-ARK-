# Changelog

Notable changes are recorded here. Features under Unreleased are merged on `main` but do not imply that a versioned package release has been published.

## Unreleased

- Added per-event duration and token policy budgets with explicit failures for missing selected metrics.
- Added strict trace-event schema validation with path- and line-specific malformed-input errors.
- Added dotted ignore paths for nested dictionary keys and indexed list values in trace comparisons.
- Added JUnit XML output for `ark evaluate` and `ark policy`, with tests for passing and failing reports.
- Added consumer-style GitHub Actions checks for the composite action's passing and rejection paths.
- Corrected aggregate token accounting so recorded `total_tokens` is not added to its own input/output subtotals.
- Improved regression coverage for trace schema validation, policy budgets, ignored diff paths, and CI report output.

## 0.1.0 — initial public MVP

- Added a local-first JSONL trace recorder and trace loader.
- Added CLI commands for inspection, comparison, and deterministic evaluation.
- Added a best-effort recursive redaction helper.
- Added baseline JSON policy contracts for allowlisted/required/forbidden events, event counts, call limits, and recorded total duration/token budgets.
- Added a reusable composite GitHub Action to enforce policy contracts in CI.
- Added a synthetic customer-support workflow example.
- Added unit tests and a Python 3.10–3.12 GitHub Actions matrix.
- Added contributor, security, community, and release documentation.
