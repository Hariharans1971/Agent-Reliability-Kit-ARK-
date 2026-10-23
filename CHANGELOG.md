# Changelog

Notable changes are listed here. The tagged GitHub release determines which commit and artifacts users receive.

## Unreleased

- Add future changes here after they are merged.

## 0.1.0 — Alpha (2026-10-23)

- Added a local-first JSONL trace recorder and schema-validated trace loader with path/line-specific malformed-input errors.
- Added CLI commands for inspection, positional trace diffs, baseline evaluation, and policy enforcement.
- Added declarative policies for allowed, required, and forbidden events; event/call limits; total and per-event duration/token budgets; and explicit failure when selected metrics are missing.
- Added dotted ignore paths for nested dictionary keys and indexed list values, plus opt-in nested added/removed/changed path reports.
- Added JUnit XML output for `ark evaluate` and `ark policy`.
- Added a reusable composite GitHub Action with expected-pass and expected-rejection consumer smoke tests.
- Added best-effort recursive key redaction and a synthetic customer-support workflow example.
- Added a self-contained offline HTML JSONL viewer with search, event-kind filters, summary metrics, and per-event inspection.
- Added regression tests, Ruff static analysis, Python 3.10–3.12 test matrix, clean wheel build/install verification, and weekly Dependabot updates.
- Added architecture, policy, security, contributor, citation, release, and community-adoption documentation.
