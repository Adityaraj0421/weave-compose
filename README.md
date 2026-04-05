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

## Demo

![Weave demo](https://raw.githubusercontent.com/Adityaraj0421/weave-compose/main/demo.gif)

<details>
<summary>Record your own terminal demo</summary>

Install [VHS](https://github.com/charmbracelet/vhs) and run:

```bash
brew install vhs
vhs demo.tape
```

The `demo.tape` script in the repo root records all five CLI commands and saves `demo.gif`.
</details>

---

## Installation

```bash
pip install weave-compose
```

Requires **Python 3.11+**. All embeddings run locally — no API key, no cloud dependency.

---

## Quickstart

```bash
# 1. Create a minimal SKILL.md file
mkdir my-skills
cat > my-skills/SKILL.md << 'EOF'
---
description: React component design with Tailwind CSS and accessibility best practices.
capabilities: [react, tailwind, components, accessibility]
---
Always use semantic HTML. Never hardcode colours — use Tailwind tokens only.
EOF

# 2. Load and query
weave load ./my-skills
# Loaded 1 skill(s) from ./my-skills (platform: claude_code)
# Session saved to .weave_session.json

weave query "design a button component"
# [1] my-skills (claude_code) — score: 0.61
#     React component design with Tailwind CSS and accessibility best practices.

# 3. Explore further
weave list    # see all loaded skills
weave status  # session info and embedding model in use
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
| `weave detect <path>` | Auto-detect the platform of a skill directory |
| `weave run [--config <path>]` | Load skills from weave.yaml and start an interactive query loop |
| `weave serve [--port <n>]` | Start the local FastAPI server on localhost (default port: 7842) |

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

## FAQ

**Does Weave call any AI API or send data to the cloud?**
No. Weave never calls any AI API. All embeddings run locally via `sentence-transformers`. No telemetry, no network calls after the model is cached.

**Where is my session stored?**
In `.weave_session.json` in your current working directory. It is created by `weave load` and read by `weave query`, `weave list`, and `weave status`. It is never committed — it is in `.gitignore` by default.

**Does it work offline?**
Yes, after the first run. The embedding model (`all-MiniLM-L6-v2`, ~80 MB) is downloaded from HuggingFace on first use and cached at `~/.cache/huggingface/`. All subsequent runs are fully offline.

**Can I use Weave with Gemini CLI?**
A Gemini CLI adapter is not yet included — the entry in `weave/core/adapters/` is a stub. It is the top community contribution priority. See [docs/adapters.md](docs/adapters.md) to write one.

**How do I add support for a custom platform?**
Subclass `BaseAdapter` in `weave/core/adapters/`, implement `load(path)` and `detect(path)`, then register it in `weave/core/detector.py`. The full guide is in [docs/adapters.md](docs/adapters.md).

---

## Learn More

- [Full changelog](CHANGELOG.md) — every release, what changed and why
- [GitHub Releases](https://github.com/Adityaraj0421/weave-compose/releases) — tagged release notes
- [Known limitations](docs/limitations.md) — documented gaps before you file an issue
- [Project roadmap](docs/roadmap.md) — what shipped and what's coming next

---

## Contributing

Contributions are welcome at every layer — new platform adapters, composition strategies, CLI improvements, and documentation.

- **Contributor guide:** [docs/contributing.md](docs/contributing.md)
- **Writing a new adapter:** [docs/adapters.md](docs/adapters.md)
- **Architecture overview:** [docs/architecture.md](docs/architecture.md)
- **Inter-skill protocol spec:** [docs/protocol.md](docs/protocol.md)

All code must pass `pytest`, `ruff check .`, and `mypy --strict .` before merging.

---

## License

MIT — see [LICENSE](LICENSE).

---

See [CHANGELOG.md](CHANGELOG.md) for the full release history.
