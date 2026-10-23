# Architecture

ARK is a local-first test layer around an agent workflow. It does not run the agent itself.

```text
Any Python agent or tool
        |
        v
  TraceRecorder.record(...)
        |
        v
   JSONL trace file
     /    |      \
 inspect  diff  evaluate / policy
     \    |      /
   developer / CI feedback
```

## Core components

- `ark.recorder.TraceRecorder`: records one run and writes line-delimited JSON.
- `ark.io.load_trace`: validates event field types and reports malformed records with file and line numbers.
- `ark.diff.diff_traces`: compares behavioral fields, supports dotted ignore paths, and can optionally report nested changed paths for added/removed/changed values.
- `ark.evaluate.evaluate_trace`: runs simple baseline checks.
- `ark.policy.evaluate_policy`: enforces allowlisted/required/forbidden events, event/call limits, total budgets, and per-event duration/token budgets.
- `ark.redact.redact`: best-effort recursive removal of values under common sensitive keys.
- `ark.cli`: command-line interface, with JUnit XML output for evaluation and policy checks.
- `action.yml`: reusable composite GitHub Action that fails a workflow when a JSON policy contract fails.

## Design choices

### JSONL instead of a hosted database
Traces are portable, inspectable with basic tools, and easy to attach to issues. Teams choose their own storage and retention controls.

### Policy-as-code for CI
Explicit JSON rules are version-controlled with the application. Required events, forbidden actions, and metric budgets are reviewable changes instead of hidden dashboard settings. The included GitHub Action makes the same gate reusable across repositories.

### No mandatory framework dependency
The core accepts explicit events. Framework callbacks can be added as optional adapters without forcing one orchestration stack on every user.

### Deterministic checks before model-based scoring
The initial policy engine validates concrete invariants. Model-based judges can be nondeterministic and should be added with explicit thresholds, reproducibility notes, and human review.

## Current limitations

- ARK does not execute an LLM or transmit traces.
- Diffing operates by event position; it does not align reordered events. Opt-in changed-path output narrows field-level differences but is not an edit-distance or semantic alignment algorithm.
- Policy checks only see the events and metrics that instrumentation records.
- Redaction is based on key names and cannot detect every sensitive string.
- Production use needs a team-defined trace retention and access policy.
