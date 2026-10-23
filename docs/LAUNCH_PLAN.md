# ARK launch and adoption plan

**Purpose:** get Agent Reliability Kit in front of developers who can test the current MVP, find real gaps, and help shape its next release.

## Positioning

Lead with one sentence:

> A small, local-first policy gate for recorded AI-agent workflows: define permitted events and execution budgets in JSON, then fail CI when a captured trace violates the contract.

ARK is not trying to replace broad observability and evaluation platforms. Promptfoo is established in prompt/agent evaluation, security testing, and CI workflows; Arize Phoenix covers tracing, evaluation, datasets, experiments, and multiple framework/provider integrations. ARK's current bet is narrower: a dependency-free core, portable JSONL traces, explicit policy contracts, and a small reusable GitHub Action.

References to re-check before public comparisons:
- Promptfoo: https://github.com/promptfoo/promptfoo
- Arize Phoenix: https://github.com/Arize-ai/phoenix
- ARK competitive note: docs/WHY_ARK.md

Do not use competitor star counts as a proxy for product quality, and avoid claims that ARK is unique unless supported by a concrete comparison.

## 60-second demo

Run a fresh clone with Python 3.10 or newer:

```bash
python -m pip install -e .
python examples/customer_support_agent.py
ark policy artifacts/customer-support.jsonl --policy policies/customer-support.json
ark policy examples/sample-trace.jsonl --policy policies/reject-sample.json
ark diff expected.jsonl actual.jsonl --show-paths
```

Explain the two policy outcomes: the first contract passes, while the restrictive allowlist intentionally rejects the second trace. Use the offline viewer at https://portfolio1-tau-sandy.vercel.app/ark-trace-viewer.html to show event browsing. These examples use synthetic data and require no paid API or model key.

## One-week outreach sequence

### Day 1 — make the project easy to assess
- Keep the README's first screen focused on the problem, demo, CI status, and install command.
- Verify the newest tests, lint, and wheel-build jobs before announcing a capability.
- Record a 45–60 second screen capture of the synthetic pass/fail workflow and path-focused diff.

### Day 2 — publish one technical explanation
- Write a short engineering note: "Turning captured agent behavior into a CI policy gate."
- Include the exact commands, a sample policy, one useful failure message, and limitations.
- Link to ARK and the online viewer; don't make star count the headline.

### Day 3 — choose one relevant community
- Share the demo in a community whose rules permit open-source project posts and where agent developers discuss testing/operations.
- State what works today, what is missing, and what kind of feedback would help.
- Do not cross-post the same pitch everywhere in one burst; tailor each post to the audience and follow its self-promotion rules.

### Day 4 — ask for a real workflow
- Invite a few developers who actually build agents to try the tool on a synthetic or non-sensitive trace.
- Ask where setup was confusing, which policy they would add, and whether an unexpected action was caught.
- Do not request a star from someone who hasn't tried the project.

### Day 5 — ship the highest-signal fix
- Convert repeated confusion into a small test or documentation improvement.
- If a report is not reproducible, ask for a minimal synthetic trace and environment details.
- Keep core dependencies at zero unless a real use case justifies an optional integration.

### Day 6 — make contribution easy
- Point contributors to issue #7 for synthetic trace fixtures and issue #5 for an independent consumer repository.
- Keep contributions small, reproducible, and covered by tests.
- Respond to issues with a concrete next step, not just a thank-you.

### Day 7 — report honestly
- Publish what people tried, what broke, and what changed.
- Update the roadmap based on repeated problems, not the loudest feature request.
- If nobody tried it, change the demo or target audience before adding more features.

## Suggested announcement copy

### Technical community post

ARK is a small open-source experiment: a local-first policy gate for recorded AI-agent workflows. It stores JSONL traces, compares runs, checks allowed/required/forbidden events and per-event budgets, and can fail a GitHub Actions job when the recorded contract is broken.

The core has no mandatory dependencies; the sample trace and browser viewer work without an LLM API key. It's an early MVP, not a safety guarantee or replacement for a full observability platform. I'm looking for developers willing to try one workflow and tell me where the contract or output is confusing.

Repository: https://github.com/Hariharans1971/Agent-Reliability-Kit-ARK-
Offline viewer: https://portfolio1-tau-sandy.vercel.app/ark-trace-viewer.html

### LinkedIn version

I've been building Agent Reliability Kit (ARK), an open-source Python tool for checking recorded AI-agent behavior in CI.

The idea is simple: write down which events are allowed, required, or forbidden and set duration/token limits in a JSON policy. ARK evaluates a JSONL trace and can fail a GitHub Actions job when the captured run violates that contract. It also supports focused trace diffs and JUnit XML output.

It's an early MVP, so I'm looking for practical feedback rather than claiming production readiness. The demo uses synthetic traces and doesn't need a model API key.

Repo: https://github.com/Hariharans1971/Agent-Reliability-Kit-ARK-
Try the viewer: https://portfolio1-tau-sandy.vercel.app/ark-trace-viewer.html

## What to measure

Review weekly, not hourly:

- **Qualified visits:** clicks/referrers from people building agents, not just raw traffic.
- **Activation:** developers who can run the sample pass and expected failure in under five minutes.
- **Useful feedback:** reproducible bug reports, policy examples, and docs issues.
- **Adoption:** independent use in another repository, repeat usage, and organic forks.
- **Contribution:** outside pull requests that pass CI and improve a real use case.

Reasonable first-month learning goals are five developer conversations, three independent attempts to run the demo, one outside use case, and one useful external contribution. These are targets to learn from, not promises or indicators of global rank.

## Avoid

- Purchased stars/forks, star rings, bots, or misleading contribution activity.
- Posting the same self-promotion to many communities in one burst.
- Claiming that policy checks prove an agent is safe; they can only check events that were captured.
- Adding heavy dependencies before users demonstrate the need.
- Announcing a formal release before a tagged version exists.

## Current product boundaries

ARK checks recorded traces, not live model behavior. It does not execute agents, automatically instrument arbitrary frameworks, align reordered events, or guarantee trace completeness. Keep these boundaries visible until features and evidence change.