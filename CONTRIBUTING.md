# Contributing to Weave

Weave is fully open source under the MIT license and welcomes contributions
at every layer — new platform adapters, composition strategies, CLI
improvements, selector tuning, and documentation. Whether you're fixing a
typo or adding Gemini CLI support, every contribution moves the project
forward.

## Where to Start

- **Full contributor guide** — dev environment setup, code style rules
  (ruff, mypy, Google-style docstrings), running tests, and the PR process:
  [docs/contributing.md](docs/contributing.md)

- **Writing a new adapter** — how to add support for a new AI coding
  platform in under an hour, with a minimal working example:
  [docs/adapters.md](docs/adapters.md)

All code must pass `pytest`, `ruff check .`, and `mypy --strict .`
before merging. Open an issue first for large changes so we can align
on direction before you invest the time.
