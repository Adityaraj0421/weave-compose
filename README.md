[![CI](https://github.com/Adityaraj0421/weave-compose/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Adityaraj0421/weave-compose/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/weave-compose.svg)](https://pypi.org/project/weave-compose/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Adityaraj0421/weave-compose/blob/main/LICENSE)

# weave-compose

Platform-aware skill composition layer for AI coding tools.

> "Everyone's building skills. Weave makes them work together."

---

## How It Works

Weave ingests skills from AI coding tools (Claude Code, Cursor, Codex, Windsurf) and normalises them into a universal schema — a single `Skill` object with a name, platform, capabilities, and semantic embedding. At query time it embeds your task description and selects the best skill(s) by cosine similarity against every loaded skill, with no manual routing required. When a task spans multiple skills, Weave composes their contexts into a single merged string ready for injection into any AI coding tool.

---

## Installation

```bash
pip install weave-compose
```

Requires **Python 3.11+**. All embeddings run locally — no API key, no cloud dependency.

---

## Quickstart

```bash
# 1. Load skills from a directory of SKILL.md files
weave load ./tests/fixtures/claude_code
# Loaded 2 skill(s) from ./tests/fixtures/claude_code (platform: claude_code)
# Session saved to .weave_session.json

# 2. Query for the best skill for your task
weave query "design a UI component with Tailwind CSS"
# [1] Naksha Design System (claude_code) — score: 0.6821
#     UI component design and design system implementation for React applications using Tailwind CSS.

# 3. List all loaded skills
weave list
#   Naksha Design System           claude_code     [design, components, ui...]
#   Backend API Engineer           claude_code     [api, rest, fastapi...]
#
# Total: 2 skill(s)
```

---

## CLI Reference

| Command | Description |
|---------|-------------|
| `weave load <path> [--platform] [--verbose]` | Load skills from a directory and save the session |
| `weave query "<text>" [--explain] [--top N]` | Query loaded skills and return the best match(es) |
| `weave list [--platform]` | List all skills in the current session |
| `weave status` | Show skill count, platform breakdown, and session info |
| `weave clear` | Clear all loaded skills and delete the session file |

Session state is stored in `.weave_session.json` in your current working directory. Run `weave load` once; all subsequent `query`, `list`, and `status` calls restore the session automatically — no re-embedding required.

---

## How Weave Selects Skills

Weave uses [`all-MiniLM-L6-v2`](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) (runs on CPU, ~80 MB, cached after first use) to embed both your query and each skill's context. It returns the top match by default. If the confidence gap between the first and second result is less than `0.1`, both skills are returned for composition — Weave assumes the task spans both domains.

Use `--explain` to see the full score table:

```bash
weave query "design a REST API" --explain
```

Use `--top N` to request at least N results:

```bash
weave query "build a feature" --top 2
```

---

## Contributing

Contributions are welcome at every layer — new platform adapters, composition strategies, CLI improvements, and documentation.

- **Contributor guide:** [docs/contributing.md](docs/contributing.md)
- **Writing a new adapter:** [docs/adapters.md](docs/adapters.md)
- **Architecture overview:** [docs/architecture.md](docs/architecture.md)

All code must pass `pytest`, `ruff check .`, and `mypy --strict .` before merging.

---

## License

MIT — see [LICENSE](LICENSE).
