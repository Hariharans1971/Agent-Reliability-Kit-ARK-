# Enforce agent reliability in CI

This guide shows how to turn a recorded agent run into a deterministic CI gate with ARK. It uses synthetic refund events; it does not call a payment provider or an LLM.

## The idea

1. Instrument your existing agent or tool wrappers to record events.
2. Save the trace as JSONL in the workspace.
3. Version a JSON policy alongside the application.
4. Run the ARK policy command before merging or deploying.
5. Treat a non-zero exit as a failed contract that needs investigation.

## Try the duplicate-refund example

Install ARK in an environment with Python 3.10 or newer:

```bash
python -m pip install -e .
ark policy examples/expected-refund-trace.jsonl --policy policies/refund-safety.json
```

The expected trace should pass. Now run the deliberately unsafe fixture:

```bash
ark policy examples/actual-refund-trace.jsonl --policy policies/refund-safety.json
```

The second command is expected to exit with code `1`: the trace contains two `refund_submit` events, while the policy allows at most one. The fixture is synthetic and demonstrates a guardrail, not a guarantee that a real payment system is safe.

## Compare a baseline with a new run

```bash
ark diff examples/expected-refund-trace.jsonl examples/actual-refund-trace.jsonl --show-paths
```

This produces a behavioral comparison of two different runs. Event IDs, run IDs, and timestamps differ intentionally; use `--ignore-path` for other volatile fields in your own traces.

## GitHub Actions

Generate or collect the trace before invoking the ARK action. Keep the trace and policy paths inside the checked-out workspace.

```yaml
- uses: actions/checkout@v4

- uses: actions/setup-python@v5
  with:
    python-version: "3.12"

- name: Install ARK
  run: python -m pip install .

- name: Generate agent trace
  run: python your_agent_test.py

- name: Enforce agent contract
  uses: Hariharans1971/Agent-Reliability-Kit-ARK-@<REVIEWED_COMMIT_SHA>
  with:
    trace: artifacts/agent-trace.jsonl
    policy: policies/agent-policy.json
    python-version: "3.12"
```

Replace `<REVIEWED_COMMIT_SHA>` with a reviewed full commit SHA before using the example in a production workflow. Pinning a SHA avoids silently pulling a moving branch. The exact event names and budget values should be tailored to your own workflow.

## What this gate can and cannot prove

ARK checks only the events and metrics that your instrumentation records. Missing instrumentation can hide behavior; trace data can contain sensitive values; and deterministic policy success does not establish that an agent's decision is correct. Use synthetic examples in public repositories, define retention and access controls for real traces, and review security-sensitive actions separately.
