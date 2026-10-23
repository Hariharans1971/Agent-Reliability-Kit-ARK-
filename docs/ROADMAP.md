# Roadmap

The roadmap is community input, not a promise that every feature will ship.

## Phase 1 — reliable core
- [x] JSONL trace recorder and reader
- [x] Inspect, diff, and evaluate commands
- [x] Best-effort recursive key redaction
- [x] Unit tests and CI matrix

## Phase 2 — stronger regression checks
- [ ] Golden trace fixtures with ignore-path rules for dynamic values
- [ ] Latency and token budget assertions
- [ ] JUnit-compatible CI output
- [ ] Better nested JSON diff output
- [ ] Exportable HTML trace viewer

## Phase 3 — optional integrations
- [ ] LangChain callback adapter
- [ ] OpenAI-compatible API wrapper
- [ ] FastAPI middleware example
- [ ] Export adapters for observability systems

## Prioritization

A strong proposal describes a repeated developer pain, a small first implementation, and a way to test success. Please open an issue before building a large integration.
