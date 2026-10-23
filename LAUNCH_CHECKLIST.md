# Launch checklist

## Initial publication
- [x] Public repository created
- [x] README with quick start and project scope
- [x] Python package and CLI files published
- [x] Unit tests and GitHub Actions workflow added
- [x] JSON policy contracts and reusable GitHub Action published
- [x] MIT license, security policy, and contributing guide added
- [x] Roadmap and issue templates added
- [x] Project mark and branded banner assets added
- [x] Strict JSONL trace schema validation and regression tests
- [x] Allowlisted/required/forbidden events and per-event duration/token policy budgets
- [x] Nested diff-path reporting and dotted ignore-path support
- [x] JUnit XML output for evaluation and policy checks
- [x] Consumer-style pinned-action smoke test: passing and expected-rejection paths
- [x] Package metadata, classifiers, and project links improved
- [x] Profile/project README and portfolio project links refreshed
- [x] Portfolio live-site verification passing

## Complete manually in GitHub settings
- [ ] Optional branding cleanup: rename `Agent-Reliability-Kit-ARK-` to `agent-reliability-kit` in Settings → General; this changes the canonical URL, so update links and `uses:` examples afterward.
- [ ] Set the repository About description to: "Local-first policy-as-code guardrails and JSONL trace diffs for AI-agent workflows."
- [ ] Add topics: `ai-agents`, `agent-evaluation`, `observability`, `python`, `developer-tools`, `testing`, `llm`, `policy-as-code`, `github-actions`.
- [ ] Upload a PNG/JPG social preview (1280 × 640 recommended).
- [ ] Pin the repository on your profile once it is stable.
- [ ] Create the profile README repository named exactly `Hariharans1971` and copy `PROFILE_README.md` to its root `README.md`.

## Before tagging a release
- [ ] Confirm all GitHub Actions matrix jobs pass.
- [ ] Run the package in a clean virtual environment on Windows and Linux/macOS.
- [ ] Review the known limitations in `docs/ARCHITECTURE.md`.
- [ ] Update `CHANGELOG.md` and the package version.
- [ ] Publish only after the interface and docs match the released behavior.
