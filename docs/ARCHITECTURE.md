# Architecture

ARK is deliberately a small library at the boundary of an agent workflow.

```text
Any Python agent or tool
        |
        v
  TraceRecorder.record(...)
        |
        v
   JSONL trace file
     /    |     \
 inspect  diff  evaluate
     \    |     /
    developer / CI feedback
```

## Core components

- `ark.recorder.TraceRecorder`: records one run and writes line-delimited JSON.
- `ark.io.load_trace`: loads events and reports malformed records with line numbers.
- `ark.diff.diff_traces`: compares behavioral fields while ignoring run-specific IDs and timestamps.
- `ark.evaluate.evaluate_trace`: runs small, deterministic checks.
- `ark.redact.redact`: best-effort recursive removal of values under common sensitive keys.
- `ark.cli`: command-line interface suitable for local use and CI.

## Design choices

### JSONL instead of a hosted database
Traces are portable, inspectable with basic tools, and easy to attach to issues. Teams choose their own storage and retention controls.

### No mandatory framework dependency
The core accepts explicit events. Framework callbacks can be added as optional adapters without forcing a specific orchestration stack on every user.

### Deterministic checks before model-based scoring
The first version validates concrete invariants. Model-based judges can be nondeterministic and should be added with explicit thresholds, reproducibility notes, and human review.

## Current limitations

- ARK does not run agents or call an LLM.
- The diff operates by event position; it does not align reordered events.
- Redaction is based on key names and cannot detect every sensitive string.
- Evaluation checks are intentionally basic.
- Production use needs a team-defined trace retention and access policy.
