# CLI reference

ARK exposes four local commands. Run `ark --help` or `ark <command> --help` for the installed version's exact options.

## Inspect a trace

```bash
ark inspect examples/sample-trace.jsonl
```

Summarizes event count, event types, duration, and token totals.

## Compare two runs

```bash
ark diff examples/expected-refund-trace.jsonl examples/actual-refund-trace.jsonl --show-paths
```

Compares expected and actual JSONL traces by event position. Use repeated `--ignore-path` flags to ignore dynamic fields:

```bash
ark diff expected.jsonl actual.jsonl --ignore-path inputs.request_id --ignore-path metadata.request_id
```

The current diff does not align reordered events. If events move, inspect the output carefully instead of assuming semantic equivalence.

## Run baseline checks

```bash
ark evaluate examples/sample-trace.jsonl --min-steps 2
ark evaluate examples/sample-trace.jsonl --require order_lookup --json
ark evaluate examples/sample-trace.jsonl --junit-xml artifacts/ark-evaluation.xml
```

Baseline checks support a minimum event count, required event names, JSON output, and JUnit XML.

## Enforce a policy

```bash
ark policy examples/expected-refund-trace.jsonl --policy policies/refund-safety.json
ark policy examples/actual-refund-trace.jsonl --policy policies/refund-safety.json --json
ark policy examples/actual-refund-trace.jsonl --policy policies/refund-safety.json --junit-xml artifacts/ark-policy.xml
```

A policy can restrict allowed events, require or forbid events, cap event counts, and set total or per-event duration/token budgets. If a policy includes a metric budget, missing required metrics fail closed.

## Exit codes

- `0`: configured checks passed.
- `1`: one or more checks failed.
- `2`: invalid input or unreadable trace.

A passing result means the configured checks passed for the recorded data; it is not a guarantee of agent correctness.
