# Architecture

Weave is a layered pipeline: skill files on disk → normalized schema → in-memory registry → semantic selection → composed context → output interface. Each layer is independently useful and can be used without the others.

---

## Overview Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          Skill Files                            │
│    SKILL.md    .cursorrules    AGENTS.md    .windsurfrules      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                          Adapters                               │
│  ClaudeCodeAdapter  CursorAdapter  CodexAdapter  WindsurfAdapter│
│                   weave/core/adapters/                          │
└────────────────────────────┬────────────────────────────────────┘
                             │  list[Skill]
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Universal Schema                           │
│               Skill dataclass — weave/core/schema.py            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Registry                                │
│           SkillRegistry — weave/core/registry.py                │
│               in-memory  +  .weave_session.json                 │
└──────────────┬──────────────────────────────────┬───────────────┘
               │ query time                        │ load time
               ▼                                  │
┌──────────────────────────────────┐              │
│            Selector              │◄─────────────┘
│   WeaveSelector — selector.py    │  embeddings pre-computed
│   sentence-transformers embed    │  on weave load, stored
│   cosine similarity ranking      │  in session file
└──────────────┬───────────────────┘
               │ list[tuple[Skill, float]]
               ▼
┌──────────────────────────────────┐
│            Composer              │
│   WeaveComposer — composer.py    │
│   dedup + merge context strings  │
└──────────────┬───────────────────┘
               │ merged context string
               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Output Interfaces                          │
│        CLI (typer)       Server (FastAPI)       UI (React)      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layers

### Skill Files

The raw source material — untouched files on disk in their native platform format. Claude Code uses `SKILL.md` files, Cursor uses `.cursorrules` and `.mdc` files, Codex uses `AGENTS.md`, and Windsurf uses `.windsurfrules`. Weave reads these files but never modifies them. They remain fully usable by their original tool.

### Adapters

One adapter per platform, each living in `weave/core/adapters/`. An adapter reads the native file format for its platform and returns a list of normalized `Skill` objects. Adapters are stateless pure I/O — no ML, no network calls, no side effects. Adding support for a new platform means writing one new adapter file. See [adapters.md](adapters.md) for the authoring guide.

### Universal Schema

The `Skill` dataclass in `weave/core/schema.py` is the lingua franca of the entire system. Every platform's skill — regardless of file format — becomes a `Skill` with the same ten fields: id, name, platform, source\_path, capabilities, trigger\_context, raw\_content, embedding, metadata, loaded\_at. All downstream layers work exclusively with `Skill` objects and never need to know the source platform.

### Registry

`SkillRegistry` in `weave/core/registry.py` is an in-memory dictionary keyed by skill ID. It is populated by `weave load` and queried by `weave query`. Because these run as separate CLI processes, the registry serializes itself to `.weave_session.json` after every load. Crucially, embeddings are stored in this file — computed once at load time, reused on every subsequent query with no re-embedding cost.

### Selector

`WeaveSelector` in `weave/core/selector.py` handles semantic skill matching. At query time, it embeds the incoming query string using `sentence-transformers` (`all-MiniLM-L6-v2`, runs fully local on CPU). It then computes cosine similarity between the query embedding and every skill's stored embedding. It returns the top-ranked skill, or two skills if their scores fall within `confidence_threshold` (default 0.1) — signalling that the task may need both.

### Composer

`WeaveComposer` in `weave/core/composer.py` takes one or two selected skills and produces a single merged context string ready for injection into an AI tool's system prompt. It deduplicates instructions that appear in both skills, places the higher-confidence skill's content first, and separates the secondary skill's unique content with a `---` divider. The output is a plain string — no special format, no tool-specific encoding.

### Output Interfaces

The CLI (`weave/cli/main.py`, built with `typer`) is the primary interface in v0.1. It exposes `weave load`, `weave query`, `weave list`, `weave status`, `weave clear`, `weave detect`, and `weave run`. A local FastAPI server (`weave/server/`) and React UI (`ui/`) are added in Phase 4, but they consume the same selector + composer pipeline — the core is interface-agnostic.

---

## End-to-End Query Flow

Tracing a single `weave query "design a button component"` call:

```
1. CLI starts → reads .weave_session.json → restores SkillRegistry
               (includes pre-computed embeddings — no re-embedding needed)

2. WeaveSelector.select() called with query string
   → embeds "design a button component" via sentence-transformers

3. Cosine similarity computed between query embedding and every
   skill embedding in the registry

4. Skills ranked by score (descending)
   → if gap between rank-1 and rank-2 < confidence_threshold: return both
   → otherwise: return rank-1 only

5. WeaveComposer.compose() called with selected (Skill, score) pairs
   → deduplicates overlapping lines
   → merges into a single context string

6. CLI prints: skill name, platform, score, and merged context
   (--output composed flag prints the full merged string)
```

**Key performance property:** embedding runs once at `weave load` time. `weave query` only embeds the short query string — not the skills. This makes repeated queries fast even with large skill registries.

---

## Inter-Skill Protocol

Phase 5 introduces an inter-skill protocol that allows skills to discover and call each other without human involvement. Skills advertise capabilities via a `weave.skill.json` sidecar manifest and can declare dependencies on other skills. The Weave runtime resolves dependencies at load time and injects dependency contexts at a lower weight alongside the primary skill.

See [docs/protocol.md](protocol.md) for the full protocol specification, JSON schema, and request/response format.
