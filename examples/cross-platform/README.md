# Cross-Platform Composition Example

This example shows Weave composing a **Claude Code skill** and a **Cursor rules file** together — two different platform formats, unified into a single context for your AI coding tool.

## What This Demonstrates

AI coding tools each have their own skill/plugin format. Claude Code uses `SKILL.md` files with YAML frontmatter. Cursor uses `.cursorrules` plain-text files. Normally these are isolated — you pick one tool and lose the other's context.

Weave loads both, embeds them semantically, and when a query matches both skill sets (e.g. "build an accessible React button component"), it automatically composes them into a single merged context — no manual routing required.

## Directory Structure

```
cross-platform/
├── weave.yaml                  ← Weave config: two skill sources, dynamic strategy
├── claude-skills/
│   └── SKILL.md                ← Claude Code skill: React Component Library rules
├── cursor-rules/
│   └── .cursorrules            ← Cursor rules: TypeScript conventions for the same codebase
└── README.md                   ← This file
```

## How to Run

From the repository root:

```bash
cd examples/cross-platform

# Option A: interactive query mode (recommended)
weave run --config weave.yaml

# Then type any query at the prompt:
# weave> build an accessible React button component
# weave> enforce TypeScript strict mode on a new hook
# weave> add Storybook stories for the Card component
```

```bash
# Option B: one-shot query
weave load ./claude-skills --platform claude_code
weave load ./cursor-rules --platform cursor
weave query "build an accessible React button component"

# With composed output (what gets injected into your AI tool):
weave query "build an accessible React button component" --output composed
```

## Expected Output

```
Loaded 1 skill(s) from ./claude-skills (platform: claude_code)
Loaded 1 skill(s) from ./cursor-rules (platform: cursor)

[1] React Component Library (claude_code) — score: 0.6821
    Building and maintaining reusable React components with design tokens...

[2] cursorrules (cursor) — score: 0.6204
    You are a TypeScript engineer working on a React component library...

── Composed context ──
[React Component Library + TypeScript conventions merged here]
──────────────────────
```

Both skills are selected because the confidence gap between their scores is smaller than `confidence_threshold: 0.1` — Weave treats them as equally relevant and composes them automatically.

## How It Works

1. `weave load` reads each directory with its native adapter and embeds every skill using `all-MiniLM-L6-v2` (runs locally, no API key).
2. At query time, `weave query` embeds the query text and ranks all skills by cosine similarity.
3. When the top two scores are within `confidence_threshold` of each other, Weave returns both.
4. `WeaveComposer` deduplicates overlapping instructions, prepends the higher-confidence skill's context, and appends the secondary skill's unique content.
5. The composed string is ready to paste into any AI tool's system prompt.

## Extending This Example

- Add a third skill source (e.g. `platform: codex`) to `weave.yaml` to pull in agent instructions from a `.codex/` directory.
- Adjust `confidence_threshold` to control how aggressively Weave composes multiple skills.
- Set `explain: true` in the `output` section to see similarity scores for every loaded skill.
- See [`../../examples/weave.yaml.example`](../weave.yaml.example) for all available config options.
- See [`../../docs/architecture.md`](../../docs/architecture.md) for a full explanation of how the composition pipeline works.
