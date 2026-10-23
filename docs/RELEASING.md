# Release checklist

Use this checklist before creating a public GitHub release or publishing the action to the GitHub Marketplace.

## Automated gate

1. Confirm the release is intended to be `v0.1.0` and package metadata in `pyproject.toml` reports `0.1.0`.
2. Review current open issues and the explicit limitations in `docs/ARCHITECTURE.md`.
3. Verify CI is green on the exact `main` commit being released: Ruff, Python 3.10/3.11/3.12 tests, CLI smoke tests, expected policy-rejection tests, composite-action smoke tests, and wheel build/install.
4. From **Actions → Release → Run workflow**, choose version `0.1.0` and release type `alpha`. The workflow re-runs verification, builds the source distribution and wheel, creates `SHA256SUMS`, and publishes a GitHub pre-release with the assets attached.
5. Inspect the published tag, release notes, attached artifacts, and checksums before sharing the release URL.
6. If the workflow fails, fix the failure and rerun it. Do not bypass its checks or manually tag a different commit.

## GitHub Marketplace publication

1. Open `action.yml` on the repository's default branch and select **Draft a new release** (or open the Releases page).
2. Ensure tag `v0.1.0` is selected and the release title/notes match `docs/releases/v0.1.0.md`.
3. Check **Publish this Action to the GitHub Marketplace**.
4. If the checkbox is disabled, accept the GitHub Marketplace Developer Agreement from the owner's account first.
5. Select an accurate primary category (Continuous integration) and a useful secondary category (Developer tools, if available).
6. Select **This is a pre-release** for the first alpha, review all assets and notes, and publish only after GitHub shows no metadata warnings. GitHub requires two-factor authentication for publication.

Marketplace publication, the developer agreement, repository About/topics, profile pins, social-preview setting, and creating the special profile README repository are account/UI tasks. The GitHub connector cannot perform those settings directly. See `LAUNCH_CHECKLIST.md` for the remaining profile settings.

## Artifact and security rules

- Publish source and wheel distributions plus `SHA256SUMS`; do not attach trace examples that contain customer data.
- Keep synthetic examples only. Never ship credentials, production prompts, or real customer traces.
- Verify the wheel installs in a clean Python 3.10+ environment and that `ark --help` works.
- Do not claim that passing policy checks proves agent correctness or safety.
