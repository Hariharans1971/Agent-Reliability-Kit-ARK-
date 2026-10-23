# Trace format

ARK uses JSON Lines (JSONL): one JSON object per event. Each event currently supports:

| Field | Meaning |
|---|---|
| `event_id` | Unique event identifier |
| `run_id` | Identifier shared by all events in one run |
| `timestamp` | ISO-8601 UTC timestamp |
| `kind` | Broad category, e.g. `tool`, `decision`, `response`, or `llm` |
| `name` | Human-readable operation name |
| `inputs` | JSON-compatible input object |
| `outputs` | JSON-compatible output value |
| `duration_ms` | Optional operation duration |
| `token_usage` | Optional integer counters |
| `metadata` | Optional tags and implementation context |

The diff command compares `kind`, `name`, `inputs`, `outputs`, and `token_usage`. It deliberately ignores generated IDs and timestamps because these commonly differ between executions.

Keep trace values JSON-serializable. Use synthetic data in public examples and define retention/access rules before capturing production events.

## Trace comparisons

By default, `ark diff EXPECTED ACTUAL` compares `kind`, `name`, `inputs`, `outputs`, and `token_usage`, while ignoring generated event/run IDs and timestamps.

Use repeatable `--ignore-path` flags for dynamic values that should not trigger a behavioral diff:

```bash
ark diff expected.jsonl actual.jsonl \
  --ignore-path inputs.request_id \
  --ignore-path outputs.metadata.generated_at \
  --ignore-path outputs.messages.0.trace_id
```

Paths use dot notation relative to the compared event fields. Numeric segments address list indexes. Dict fields are removed from a comparison copy; indexed list items are replaced by a stable sentinel to preserve list positions. Missing paths have no effect. Input trace objects are never mutated.

Use ignore paths narrowly. Ignoring `kind`, `name`, or an entire `outputs` object can hide meaningful behavior changes. `metadata` is not compared by default, so `metadata.some_field` is unnecessary unless metadata becomes part of the comparison contract later.
