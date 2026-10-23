# Roadmap

The roadmap is community input, not a promise that every feature will ship.

## Phase 1 — reliable core
- [x] JSONL trace recorder and reader
- [x] Inspect, diff, and evaluate commands
- [x] Declarative JSON policy contracts (allowlisted/required/forbidden events, call limits, total/per-event duration and token budgets)
- [x] Reusable GitHub Action for CI policy enforcement
- [x] Best-effort recursive key redaction
- [x] Unit tests and CI matrix
- [x] Line-specific trace schema validation for event types, durations, and token counters

## Phase 2 — stronger regression checks
- [x] Dotted ignore paths for dynamic values during trace comparison
- [ ] Golden-trace fixture packs and comparison presets
- [x] Per-event duration/token budgets with explicit missing-metric failures
- [x] JUnit XML output for policy and evaluation checks
- [x] Expected-pass and expected-rejection policy checks in GitHub Actions
- [x] Optional path-focused nested JSON diff output
- [x] Offline single-file HTML viewer for local JSONL traces
- [ ] CLI-exported self-contained report for sharing

## Phase 3 — optional integrations
- [ ] LangChain callback adapter
- [ ] OpenAI-compatible API wrapper
- [ ] FastAPI middleware example
- [ ] Export adapters for observability systems

## Prioritization

A strong proposal describes a repeated developer pain, a small first implementation, and a way to test success. Please open an issue before building a large integration.
