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
- [x] Weekly Dependabot updates configured for Python packaging and GitHub Actions
- [x] Profile/project README and portfolio project links refreshed
- [x] Offline JSONL trace viewer added with no third-party runtime dependencies
- [x] Portfolio live-site verification passing

## Recommended profile settings

- **Display name:** `Hariharan S.`
- **Bio:** `Python · Backend APIs · Applied AI | CSE (AI & ML), 2026 | Building agent reliability tools`
- **Website:** `https://portfolio1-tau-sandy.vercel.app/`
- **Pinned repositories:** ARK, `document_analysis`, `portfolio`, and the strongest reproducible project with a clear README and passing tests.
- **Profile README:** copy `PROFILE_README.md` into a new public repository named exactly `Hariharans1971`. GitHub only renders it at the top of your profile when that repository name matches the username.

## Complete manually in GitHub settings
- [ ] Optional branding cleanup: rename `Agent-Reliability-Kit-ARK-` to `agent-reliability-kit` in Settings → General; this changes the canonical URL, so update links and `uses:` examples afterward.
- [ ] Set the repository About description to: "Local-first policy-as-code guardrails and JSONL trace diffs for AI-agent workflows."
- [ ] Add topics: `ai-agents`, `agent-evaluation`, `observability`, `python`, `developer-tools`, `testing`, `llm`, `policy-as-code`, `github-actions`.
- [ ] Upload a PNG/JPG social preview (1280 × 640 recommended).
- [ ] Pin the repository on your profile once it is stable.
- [ ] Create the profile README repository named exactly `Hariharans1971` and copy `PROFILE_README.md` to its root `README.md`.

## Before tagging a release
- [x] Confirm all GitHub Actions matrix jobs pass on the latest verified main commits.
- [x] Build and install the wheel in a clean virtual environment in CI; Python 3.10–3.12 tests pass.
- [x] Review and document the known limitations in `docs/ARCHITECTURE.md`.
- [x] Align `CHANGELOG.md` and staged v0.1.0 alpha release notes with package version 0.1.0.
- [x] Add action branding metadata and an automated, validation-gated release workflow.
- [x] Add regression coverage for Marketplace metadata and staged release artifacts.
- [x] Validate every GitHub Actions workflow's YAML syntax/structure in CI, including the release workflow.
- [x] Pin the README composite-action example to a reviewed full commit SHA.
- [x] Create the `v0.1.0` alpha draft release through the validation-gated workflow; attach wheel, source archive, and SHA256SUMS.
- [ ] Review the [v0.1.0 draft release](https://github.com/Hariharans1971/Agent-Reliability-Kit-ARK-/releases/tag/untagged-3a4207a8b1f2855de01c), uploaded assets, and SHA256SUMS; publish it in GitHub only after selecting the Marketplace option and category.
- [ ] Publish the action to GitHub Marketplace after accepting the developer agreement and selecting categories.
- [ ] Apply repository About/topics, upload the social-preview image in Settings, pin repositories, and create the special profile README repository.
