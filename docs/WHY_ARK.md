# Why Agent Reliability Kit exists

**Last reviewed:** 23 October 2026

This note records the problem, intended user, product boundary, and adjacent tools so ARK can compete through a clear use case rather than marketing claims.

## Problem

An agent workflow may look successful in a demo but still exceed an execution budget, invoke an unexpected tool, omit a required step, or change behavior after a code or prompt update. Logs explain a run; a policy contract states which recorded behaviors are permitted and what limits must be respected.

## Intended first user

A Python engineer who already records agent/tool events and wants a local, version-controlled CI gate without adopting a hosted observability platform.

## ARK's current approach

- Store caller-supplied events in a portable JSONL trace.
- Compare recorded behavior across runs, optionally showing exact nested paths that changed and ignoring selected volatile fields.
- Express permitted, required, and forbidden event names as JSON.
- Limit total event counts, repeated calls, total recorded duration/tokens, and per-event duration/token use.
- Fail a GitHub Actions job when the trace violates its policy contract, and emit JUnit XML for CI reporting.

ARK does not yet run agents, automatically instrument arbitrary frameworks, intercept live provider traffic, replay provider calls, inspect hidden prompt/context state, or guarantee that a trace captures every action. Its checks are only as good as its instrumentation and policy.

## Adjacent tools reviewed

These projects are established references in neighboring categories. Their existence means ARK should not be positioned as a universal tracing/evaluation platform or claim uniqueness without evidence.

- [Promptfoo](https://github.com/promptfoo/promptfoo) focuses on LLM evaluation, red-teaming, and test workflows that can run in CI.
- [Langfuse](https://github.com/langfuse/langfuse) provides tracing, prompt management, datasets, and evaluations.
- [Arize Phoenix](https://github.com/Arize-ai/phoenix) provides AI observability, tracing, evaluation, datasets, experiments, and broad framework/provider integrations.
- [ToolReplay](https://github.com/brandynfisher/ToolReplay) focuses on auditing recorded tool-call transcripts for replay divergence, redundant calls, and declared-scope overreach.
- [AgentTape](https://github.com/MITHRAN-BALACHANDER/AgentTape) records external LLM/tool interactions and replays them offline from cassettes.
- [Agent DevTools](https://github.com/Jacopos311/Agent-Devtools) focuses on local visual debugging, replay, behavior diffs, and causal context such as memory and retrieval.

## ARK's proposed wedge

**A tiny policy file that can block a CI build when recorded agent actions violate a team's explicit contract.**

| Need | ARK today |
|---|---|
| Read caller-supplied JSONL events | Yes |
| Compare traces by event position | Yes |
| Show nested added/removed/changed field paths | Yes, opt-in |
| Ignore selected dotted paths during diffs | Yes |
| Emit JUnit XML for policy/evaluation checks | Yes |
| Allowlist and require/forbid named events | Yes |
| Limit total events and repeated event calls | Yes |
| Gate on total recorded duration/token counters | Yes |
| Gate on per-event duration/token budgets | Yes |
| Reusable GitHub Action | Yes |
| Auto-instrument common frameworks | No |
| Provider cassette recording or replay | No |
| Visual trace explorer / hosted dashboard | No |
| LLM-as-judge and dataset experiments | No |

This is a focused product position, not a claim that other platforms never implement policies or guardrails.

## What would validate the idea?

1. Ask at least three developers to apply ARK to a workflow and report setup friction.
2. Capture concrete examples where the policy gate catches a regression that ordinary unit tests missed.
3. Test the composite action from a separate sample repository, not only from the ARK repository itself.
4. Prioritize repeated user problems over fashionable integrations.
5. Keep the README honest about limitations and incomplete features.

## Decision rule

Do not add a framework integration just because it is fashionable. Add it when users can describe the use case, the smallest useful implementation, and a test that proves it works.
