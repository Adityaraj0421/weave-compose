# Basic Composition Example

This example shows Weave automatically routing between two **Claude Code skills** — a Design System skill and a Backend API skill — based on the meaning of your query.

## What This Demonstrates

When you have multiple skills loaded, Weave selects the right one for each task without you specifying which to use. A design query activates the Design System skill. A backend query activates the Backend API skill. When a task spans both domains, Weave composes both skills together automatically.

This is the simplest Weave use case: one platform, two skills, zero manual routing.

## Directory Structure

```
basic-composition/
├── weave.yaml          ← Weave config: one skill directory, dynamic strategy
├── skills/
│   ├── design_system.md  ← Claude Code skill: Design System Engineer
│   └── backend_api.md    ← Claude Code skill: Backend API Engineer
└── README.md           ← This file
```

## How to Run

From the repository root:

```bash
cd examples/basic-composition

# Option A: interactive query mode (recommended)
weave run --config weave.yaml

# Then type any query at the prompt:
# weave> design a button component with Tailwind CSS
# weave> write a REST endpoint for creating a user
# weave> add accessibility labels to a form
```

```bash
# Option B: one-shot query
weave load ./skills --platform claude_code
weave query "design a button component with Tailwind CSS"

# See all loaded skills:
weave list

# With similarity scores for all skills:
weave query "write a REST endpoint" --explain
```

## Expected Output

```
Loaded 2 skill(s) from ./skills (platform: claude_code)
Session saved to .weave_session.json

# Design query → Design System skill selected
$ weave query "design a button component with Tailwind CSS"
[1] Design System Engineer (claude_code) — score: 0.7214
    Building and maintaining UI components, design tokens, and accessibility
    standards for a consistent design system using Tailwind CSS and React.

# Backend query → Backend API skill selected
$ weave query "write a REST endpoint for creating a user"
[1] Backend API Engineer (claude_code) — score: 0.6891
    Designing and implementing RESTful APIs, database schemas, and server-side
    business logic using FastAPI and PostgreSQL.
```

## How It Works

1. `weave load ./skills` reads both SKILL.md files and embeds each skill's
   `trigger_context` and `capabilities` using `all-MiniLM-L6-v2` (local, no API key).
2. At query time, `weave query` embeds the query text and computes cosine similarity
   against every loaded skill's embedding.
3. The highest-scoring skill is returned. If the top two scores fall within
   `confidence_threshold: 0.1` of each other, both are returned for composition —
   Weave assumes the task spans both domains.
4. `WeaveComposer` merges the contexts: higher-confidence skill first,
   deduplicated, with a `---` separator before the secondary skill's unique content.

## Extending This Example

- Add a third SKILL.md to `skills/` (e.g. a DevOps skill) — Weave picks it up
  automatically on the next `weave load`.
- Adjust `confidence_threshold` in `weave.yaml` to control how aggressively
  Weave composes multiple skills per query.
- Set `explain: true` in the `output` section to see similarity scores for every
  loaded skill on every query.
- See the **[cross-platform example](../cross-platform/)** to compose skills from
  different AI coding tools (Claude Code + Cursor) together.
- See **[`../weave.yaml.example`](../weave.yaml.example)** for all available config options.
- See **[`../../docs/architecture.md`](../../docs/architecture.md)** for a full explanation
  of the composition pipeline.
