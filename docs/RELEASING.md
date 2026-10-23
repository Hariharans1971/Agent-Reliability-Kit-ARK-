# Release checklist

A release represents tested behavior, not a roadmap promise.

1. Review open bugs and document known limitations.
2. Run `python -m unittest discover -s tests -v`.
3. Install the package in a clean Python 3.10+ environment.
4. Smoke-test `ark inspect`, `ark diff`, and `ark evaluate` using synthetic traces.
5. Confirm the GitHub Actions matrix passes.
6. Update the version in `pyproject.toml` and `ark/__init__.py`.
7. Update `CHANGELOG.md`.
8. Create a GitHub release with a concise summary, examples, and upgrade notes.

Do not publish API keys, customer prompts, or production traces in release assets.
