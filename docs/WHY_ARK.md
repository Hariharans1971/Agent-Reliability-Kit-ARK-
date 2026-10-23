# Why Agent Reliability Kit exists

**Last reviewed:** 23 October 2026

This note records the problem, intended user, current boundary, and competitive landscape so the project can improve based on evidence rather than marketing claims.

## Problem

An agent workflow may look successful in a demo but still exceed an execution budget, invoke an unexpected tool, omit a required step, or change behavior after a code or prompt update. Logs help explain a run, but a team also needs a repeatable way to define what a valid run should look like and fail CI when that contract is broken.

## Intended first user

A Python engineer who already records agent/tool events and wants a local, version-controlled CI gate without adopting a hosted observability platform.

## Current ARK approach

- Store run events in a portable JSONL file.
- Compare recorded behavior across runs.
- Express a small execution contract as JSON.
- Check required and forbidden events, event-count limits, per-event call limits, and recorded total duration/token budgets.
- Reuse the same contract in GitHub Actions.

The current version **does not** run agents, intercept live provider traffic, deterministically replay LLM calls, inspect hidden prompt/context state, or guarantee that a trace captures every action. Its checks are only as accurate as its instrumentation and policy.

## Related projects reviewed

These projects solve adjacent problems and are useful references; they are not proof that ARK is novel.

- [ToolReplay](https://github.com/brandynfisher/ToolReplay) audits recorded agent tool-call transcripts for replay divergence, redundant calls, and declared-scope overreach.
- [AgentTape](https://github.com/MITHRAN-BALACHANDER/AgentTape) records external LLM/tool interactions and replays them offline from cassettes.
- [Agent DevTools](https://github.com/Jacopos311/Agent-Devtools) focuses on local visual debugging, replay, behavior diffs, and inspecting causal context such as memory and retrieval.

## ARK's current positioning

ARK is intentionally narrower: **declarative JSON policy contracts that can gate CI**, with a small dependency-free Python core and a reusable GitHub Action. This is a project focus, not a claim that no other tool offers policy checks or agent guardrails.

| Need | Current ARK support |
|---|---|
| Record events supplied by an application | Yes |
| Compare recorded traces by event position | Yes |
| Require/forbid named events | Yes |
| Limit event counts and named-event repetitions | Yes |
| Gate on recorded total duration/token counters | Yes |
| Reusable GitHub Action | Yes |
| Live provider interception and cassette replay | No |
| Visual causal debugging UI | No |
| Embeddings, LLM judge, hosted dashboard | No |

## What would validate the idea?

1. Have at least three developers apply ARK to a real or synthetic workflow and report setup friction.
2. Collect concrete examples where a policy catches a regression that a normal unit test would miss.
3. Test the action from a separate sample repository, not only from within ARK itself.
4. Prioritize changes based on repeated user problems: per-step budgets, golden traces, clearer diffs, and CI-native reports.
5. Keep the README honest about incomplete features and known limitations.

## Decision rule

Do not add a framework integration just because it is fashionable. Add it when users can describe the use case, the smallest useful implementation, and a test that proves it works.
