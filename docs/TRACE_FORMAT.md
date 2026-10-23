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
