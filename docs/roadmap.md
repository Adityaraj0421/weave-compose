# Roadmap

Weave ships in five phases. Each phase ends with a release tag on `main`. This file is updated at every release tag.

---

## v0.1 — Phase 1: Core Engine `[SHIPPED — 2026-04-05]`

**Goal:** Skills can be loaded, normalized, embedded, and queried from the CLI.

### Ships in v0.1
- ClaudeCodeAdapter — reads SKILL.md files from Claude Code skill sets
- Universal Skill schema — normalized dataclass for all platforms
- SkillRegistry — in-memory store with session persistence via `.weave_session.json`
- WeaveSelector — sentence-transformers embeddings + cosine similarity ranking
- CLI: `weave load`, `weave query`, `weave list`, `weave status`, `weave clear`, `weave detect`
- Embeddings computed once at load time, reused on every query

---

## v0.2 — Phase 2: Composition Engine `[SHIPPED — 2026-04-05]`

**Goal:** Weave composes multiple skills together and injects a merged context.

### Ships in v0.2
- WeaveComposer — dynamic merge strategy (dedup + ordered) and minimal strategy
- `weave.yaml` config file support — declare skill paths, composition settings
- `weave run` — interactive query loop powered by config file
- Multi-skill activation strategies: `always-merge` and `manual`

---

## v0.3 — Phase 3: Multi-Platform Adapters `[SHIPPED — 2026-04-05]`

**Goal:** Weave works with Cursor, Codex, and Windsurf out of the box.

### Ships in v0.3
- CursorAdapter — reads `.cursorrules` and `.cursor/rules/*.mdc` files
- CodexAdapter — reads `AGENTS.md` and `.codex/*.md` files
- WindsurfAdapter — reads `.windsurfrules` files
- Platform auto-detector — infers platform from directory structure
- PyPI release — `pip install weave-compose` works from the public registry

---

## v0.4 — Phase 4: Persistence + UI `[SHIPPED — 2026-04-05]`

**Goal:** Skills persist between sessions. Visual composer for non-technical users.

### Ships in v0.4
- PersistentRegistry — optional ChromaDB backend (`pip install weave-compose[persist]`)
- FastAPI local server — REST API for load, query, compose, and status
- `weave serve` CLI command — starts the local server
- React UI — skill browser with platform filter, visual composer, load panel

---

## v1.0 — Phase 5: Agent-to-Agent Protocol `[SHIPPED — 2026-04-05]`

**Goal:** Skills can discover and call each other without human involvement.

### Ships in v1.0
- Weave inter-skill protocol spec (`docs/protocol.md`)
- `weave.skill.json` manifest — per-skill capabilities, trigger patterns, dependencies
- Dependency resolution — load skill A and its declared dependencies automatically
- Conflict detection — identifies and resolves contradicting instructions between skills

---

## What's Next — Post-v1.0 Community Priorities

Weave v1.0 is complete. The following are the highest-priority areas for
community contributions and future development:

- **Gemini CLI adapter** — the only major platform without an adapter;
  see [docs/adapters.md](adapters.md) to get started
- **Skill marketplace / registry** — a public index of community-published
  skills, discoverable by name and capability
- **VS Code extension** — surface Weave's skill selection and composition
  directly inside the editor sidebar
- **Cloud skill sync (opt-in)** — sync loaded skills across machines via a
  user-controlled remote store (no telemetry, fully opt-in)
- **Benchmarks and performance docs** — measure and document selector
  latency, embedding throughput, and composition quality across skill sets

If you want to work on any of these, open an issue on GitHub to coordinate
before starting. See [CONTRIBUTING.md](../CONTRIBUTING.md) for the process.

---

> This file is updated at every release tag. See [CHANGELOG.md](../CHANGELOG.md) for the full release history.
