# Policy contracts

ARK can gate a trace against explicit, reviewable JSON rules. This is useful when an agent needs a predictable execution envelope before its workflow is promoted.

## Run a policy

Generate the synthetic customer-support trace, then evaluate it:

```bash
python examples/customer_support_agent.py
ark policy artifacts/customer-support.jsonl --policy policies/customer-support.json
```

To emit machine-readable results:

```bash
ark policy artifacts/customer-support.jsonl --policy policies/customer-support.json --json
```

## Supported rules

| Key | Meaning |
|---|---|
| `min_events` / `max_events` | Bound the number of recorded events |
| `required_events` | Require named events to appear |
| `forbidden_events` | Fail if a named event appears |
| `max_total_duration_ms` | Bound the sum of recorded durations |
| `max_total_tokens` | Bound the sum of counters recorded under `token_usage` |
| `max_calls_per_event` | Bound the number of occurrences of each named event |

The policy loader rejects unknown keys and invalid limits instead of silently ignoring them. Budget checks evaluate values already present in the trace; ARK does not infer missing metrics or calculate provider invoices.

## Important limits

Policy checks are deterministic guardrails, not a safety proof. They cannot detect harmful behavior that the trace does not record, and they rely on the instrumentation being complete and truthful. Use them alongside application tests, human review, and least-privilege tool permissions.
