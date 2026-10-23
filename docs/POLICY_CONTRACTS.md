# Policy contracts

ARK can gate a recorded agent workflow against explicit, reviewable JSON rules. Contracts are plain files that can live next to an application's tests and be checked in CI.

## Run the example

From the repository root, install ARK and generate a synthetic support trace:

```bash
python -m pip install -e .
python examples/customer_support_agent.py
ark policy artifacts/customer-support.jsonl --policy policies/customer-support.json
```

For machine-readable results:

```bash
ark policy artifacts/customer-support.jsonl --policy policies/customer-support.json --json
```

## Supported rules

| Key | Meaning |
|---|---|
| `allowed_events` | Fail if any recorded event name is not explicitly allowed |
| `required_events` | Require named events to appear |
| `forbidden_events` | Fail if a named event appears |
| `min_events` / `max_events` | Bound the total number of events |
| `max_calls_per_event` | Bound the number of occurrences of each named event |
| `max_total_duration_ms` | Bound total recorded duration; fails if any event lacks a duration |
| `max_duration_ms_per_event` | Bound each occurrence of selected event names |
| `max_total_tokens` | Bound recorded token totals across events with usage counters |
| `max_tokens_per_event` | Bound each occurrence of selected event names |

## Example: permitted actions and step budgets

```json
{
  "allowed_events": ["retrieve_docs", "answer_question"],
  "required_events": ["retrieve_docs", "answer_question"],
  "forbidden_events": ["delete_account"],
  "max_duration_ms_per_event": {
    "retrieve_docs": 250,
    "answer_question": 1200
  },
  "max_tokens_per_event": {
    "answer_question": 1600
  }
}
```

Each occurrence of a selected event is checked independently. If a selected event is present but its required measurement is missing, that check fails rather than treating the missing value as zero. A per-event cap does not require the event to occur; use `required_events` for that.

If `allowed_events` is present, an unlisted event name fails the contract. This is an audit of recorded event names, **not** a runtime permission system. It only detects actions that were captured in the trace.

## Metric semantics and limitations

- For token usage, ARK uses `token_usage.total_tokens` when present. Otherwise it sums the recorded counters. This avoids double-counting an aggregate together with its input/output breakdown.
- A total token budget requires at least one event with token usage, but cannot prove that instrumentation recorded every LLM call.
- A total duration budget requires `duration_ms` on every event and fails closed if any value is missing.
- Durations must be finite, non-negative numbers. Token counters must be non-negative integers.
- Policy checks are deterministic guardrails, not a safety proof. They cannot detect behavior absent from the trace and are only as complete as the instrumentation.
- ARK does not execute an LLM, intercept provider traffic, estimate invoices, or replace application-level authorization. Use least-privilege tools, application tests, and human review as appropriate.
