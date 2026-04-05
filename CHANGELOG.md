# Changelog

## [v0.1] - 2026-04-05

### Added
- `Skill` dataclass (`frozen=True`) with `to_dict()`, `validate()`, and `__repr__`
- `BaseAdapter` abstract class with `_generate_id()`, `_timestamp()`, and `_extract_capabilities()` helpers
- `ClaudeCodeAdapter` for SKILL.md files with YAML frontmatter parsing and graceful fallbacks
- `SkillRegistry` in-memory store with `save_session()` / `load_session()` for `.weave_session.json` persistence
- `WeaveSelector` using `sentence-transformers` (`all-MiniLM-L6-v2`) and cosine similarity for semantic skill selection
- Dynamic multi-skill selection: when confidence gap between top two skills is below threshold, both are returned for composition
- CLI commands: `weave load`, `weave query`, `weave list`, `weave status`, `weave clear`
- Cross-process session persistence: `weave load` saves session; `weave query`, `weave list`, `weave status` restore it automatically — no re-embedding on every query
- End-to-end tests: design query → Naksha Design System; backend query → Backend API Engineer
- Full test suite: 38 tests across schema, adapters, registry, selector, CLI, and e2e modules
- Realistic Claude Code fixtures: `naksha_design.md` (design system) and `backend_api.md` (REST API)
- Open source scaffold: LICENSE (MIT), README, CHANGELOG, CONTRIBUTORS, docs/, GitHub issue templates, CI workflow

## [v0.2] - 2026-04-05

### Added
- `WeaveComposer` with dynamic (full `raw_content`) and minimal (`trigger_context` + capabilities) merge strategies; line-level deduplication across skill blocks
- `weave.yaml` config loader with full validation: required fields, supported platforms (`claude_code`, `cursor`, `codex`, `windsurf`), supported strategies; typed `WeaveConfig` dataclass
- `weave run` interactive mode: readline-powered query loop driven by `weave.yaml`
- `always-merge` and `manual` activation strategies on `WeaveSelector` (`select_all`, `select_manual`)
- `weave query --output composed` flag: prints full merged context via `WeaveComposer`
- `SentenceTransformerEmbedder` and `cosine_similarity` extracted to `embedder.py` (clean separation from selection logic)
- Annotated `examples/weave.yaml.example` covering every config field with inline comments
- Config tests, composer tests, selector strategy tests — 60 total

## [v0.3] - 2026-04-05

### Added
- `CursorAdapter`: reads `*.cursorrules` (plain text) and `.cursor/rules/*.mdc` (YAML frontmatter) files; `platform="cursor"`
- `CodexAdapter`: reads `AGENTS.md` and `.codex/*.md` files with heading-based name extraction; `platform="codex"`
- `WindsurfAdapter`: reads `*.windsurfrules` plain-text files; `platform="windsurf"`
- Platform auto-detector (`detect_platform()`): infers platform from directory structure; covers all 4 supported platforms
- `weave detect <path>` CLI command
- Cursor fixtures: `frontend.cursorrules` + `.cursor/rules/typescript.mdc` (MDC format)
- Codex fixtures: `AGENTS.md` (Security Code Reviewer) + `.codex/devops.md` (DevOps Agent)
- Windsurf fixtures: `python_standards.windsurfrules` + `api_design.windsurfrules`
- Cross-platform e2e tests: loads claude_code + cursor + codex fixtures and asserts domain-specific queries route to the correct platform's skill
- `examples/cross-platform/`: working example with `SKILL.md` + `.cursorrules` composing together, with full README
- PyPI release workflow (`.github/workflows/release.yml`): OIDC trusted publishing on `v*` tags
- `pyproject.toml` updated with classifiers, `[project.urls]`, keywords, README, and license metadata
- 93 tests passing across all modules and all 4 platform adapters

## [v0.4] - 2026-04-05

### Added
- `PersistentRegistry` with optional ChromaDB backend (`pip install weave-compose[persist]`); falls back to in-memory if ChromaDB not installed
- `--persist` flag on `weave load`, `weave run`, and `weave clear` for cross-session skill persistence
- FastAPI local server (`weave serve --port 7842`) with endpoints: `GET /skills`, `POST /load`, `POST /query`, `POST /compose`, `GET /status`
- React + Vite + Tailwind UI at `http://localhost:5173` — connects to the local FastAPI server
- Skill browser: responsive card grid with platform filter and full-detail slide-in panel
- Visual composer: query input → matched skills with confidence scores → composed context with one-click copy
- Load panel: directory path input + platform selector → live registry status breakdown after load
- 106 tests passing (1 skipped — ChromaDB integration, requires optional dep)

## [v1.0] - 2026-04-05

### Added
- Weave inter-skill protocol spec (`docs/protocol.md`) — advertisement, request/response wire format, JSON schemas for `WeaveAdvertisement`, `WeaveRequest`, `WeaveResponse`
- `weave.skill.json` manifest support in all four adapters (Claude Code, Cursor, Codex, Windsurf) — `name`, `version`, `capabilities`, `trigger_patterns`, `author`, `dependencies` override adapter-inferred values
- Skill-specific manifest lookup (`<stem>.skill.json` preferred over `weave.skill.json`) for directories containing multiple skill files
- Dependency resolution at skill load time: `SkillRegistry.get_by_name()` and `resolve_dependencies()` — declared dependencies looked up by name, missing deps log a `WARNING`; `weave load` prints resolved link count
- Conflict detection in `WeaveComposer`: `detect_conflicts()` flags skill pairs with embedding similarity ≥ 0.9 AND opposing keyword pairs (`always/never`, `use/avoid`, `enable/disable`, etc.); `WARNING` logged per conflict, higher-score skill preferred automatically via score-sort
- 119 tests passing (1 skipped — ChromaDB integration, requires optional dep)

## [Unreleased]
