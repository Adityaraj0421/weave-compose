# Weave Inter-Skill Protocol

The Weave Inter-Skill Protocol defines how skills advertise their capabilities to the
Weave broker, how consumers request composed context for a task, and the wire format
for both directions. It sits above the registry and selector layers (which handle
embedding and ranking) and below the CLI and server layers (which surface results to
users and AI tools). The protocol is local-first: in v1.0 all communication happens
in-process or over the local FastAPI server. Remote/multi-process brokering is
reserved for post-v1.0.

---

## Overview

The protocol defines three roles:

| Role | Description |
|------|-------------|
| **Publisher** | A skill that advertises its capabilities to the broker. Every loaded skill is a publisher. |
| **Consumer** | An agent, tool, or user that requests composed context for a task. The CLI (`weave query`), the UI composer, and the `/query` + `/compose` API endpoints are all consumers. |
| **Broker** | The Weave registry + selector + composer stack. It receives advertisements from publishers, answers discovery queries from consumers, and returns merged context. |

### Data flow

```
Publisher                  Broker                      Consumer
   |                          |                            |
   |-- advertise (manifest) ->|                            |
   |                          |-- stored in registry       |
   |                          |                            |
   |                          |<-- WeaveRequest -----------|
   |                          |    (query, top_n, exclude) |
   |                          |                            |
   |                          | select + compose           |
   |                          |                            |
   |                          |-- WeaveResponse ---------->|
   |                          |    (skills[], composed)    |
```

Skills never communicate directly with each other. All routing flows through the
broker.

---

## Skill Advertisement

A skill advertises itself to the broker at load time. The broker stores the
advertisement in the registry and uses it for selection and dependency resolution.

### Advertisement sources (priority order)

1. **`weave.skill.json` sidecar file** *(preferred)* — a JSON file placed alongside
   the skill file. Parsed by adapters in v1.0. When present, its fields take
   precedence over any inferred values.

2. **Inferred from `Skill` object fields** *(fallback)* — when no sidecar exists,
   the adapter builds the advertisement from the parsed skill fields (`name`,
   `platform`, `capabilities`, `trigger_context`). This fallback works for all
   skills loaded today without any manifest file.

### WeaveAdvertisement object

```json
{
  "weave_protocol": "1.0",
  "name": "Naksha Design System",
  "version": "1.2.0",
  "platform": "claude_code",
  "capabilities": ["design", "components", "tokens", "accessibility"],
  "trigger_patterns": [
    "design a component",
    "create a UI layout",
    "build a design system",
    "apply design tokens"
  ],
  "author": "Aditya Raj",
  "dependencies": []
}
```

### Field reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `weave_protocol` | `string` | yes | Protocol version. Must be `"1.0"` for v1.0 skills. |
| `name` | `string` | yes | Human-readable skill name. Must be non-empty. |
| `version` | `string` | no | Semver string, e.g. `"1.0.0"`. Defaults to `"0.0.0"` if absent. |
| `platform` | `string` | yes | One of: `"claude_code"`, `"cursor"`, `"codex"`, `"windsurf"`. |
| `capabilities` | `string[]` | yes | Capability tags used for embedding alongside `trigger_patterns`. |
| `trigger_patterns` | `string[]` | yes | Natural language phrases describing tasks this skill handles. Maps to `trigger_context` in the `Skill` dataclass. At least one entry required. |
| `author` | `string` | no | Skill author name or handle. Defaults to `""`. |
| `dependencies` | `string[]` | no | Names of other skills this skill requires. Weave resolves and co-injects dependencies at query time (v1.0). Defaults to `[]`. |

---

## Context Request / Response

A consumer sends a `WeaveRequest` to the broker when it needs composed context for a
task. The broker selects the best matching skills, composes their contexts, and returns
a `WeaveResponse`.

### WeaveRequest object

```json
{
  "weave_protocol": "1.0",
  "query": "design a REST endpoint with a React form",
  "top_n": 2,
  "exclude": []
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `weave_protocol` | `string` | yes | Must match the broker's supported protocol version. |
| `query` | `string` | yes | Natural language task description. The broker embeds this and ranks skills by cosine similarity. |
| `top_n` | `number` | no | Maximum number of skills to return. Default `1`, max `2`. When the confidence gap between the top two results is below `confidence_threshold` (default `0.1`), the broker may return two skills even if `top_n` is `1`. |
| `exclude` | `string[]` | no | Skill names to exclude from selection. Useful when a consumer has already injected a specific skill and wants complementary context only. |

### WeaveResponse object

```json
{
  "weave_protocol": "1.0",
  "skills": [
    {
      "name": "Naksha Design System",
      "platform": "claude_code",
      "score": 0.847,
      "composed_context": "You are a design system expert..."
    },
    {
      "name": "Backend API Engineer",
      "platform": "claude_code",
      "score": 0.791,
      "composed_context": "You are a REST API expert..."
    }
  ],
  "composed": "You are a design system expert...\n\n---\n\nYou are a REST API expert..."
}
```

| Field | Type | Description |
|-------|------|-------------|
| `weave_protocol` | `string` | Echo of the request protocol version. |
| `skills` | `SkillMatch[]` | Ordered list of matched skills (highest score first). |
| `skills[].name` | `string` | Skill name from the advertisement. |
| `skills[].platform` | `string` | Source platform. |
| `skills[].score` | `number` | Cosine similarity score in range `[0.0, 1.0]`. |
| `skills[].composed_context` | `string` | The individual skill's raw content (pre-merge). |
| `composed` | `string` | Fully merged context ready for system prompt injection. Deduplicated, higher-score skill first, separated by `\n\n---\n\n`. |

---

## JSON Schemas

### WeaveAdvertisement

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/Adityaraj0421/weave-compose/schemas/advertisement.json",
  "title": "WeaveAdvertisement",
  "type": "object",
  "required": ["weave_protocol", "name", "platform", "capabilities", "trigger_patterns"],
  "additionalProperties": false,
  "properties": {
    "weave_protocol": { "type": "string", "const": "1.0" },
    "name":           { "type": "string", "minLength": 1 },
    "version":        { "type": "string", "default": "0.0.0" },
    "platform":       {
      "type": "string",
      "enum": ["claude_code", "cursor", "codex", "windsurf"]
    },
    "capabilities":     { "type": "array", "items": { "type": "string" } },
    "trigger_patterns": {
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1
    },
    "author":       { "type": "string", "default": "" },
    "dependencies": {
      "type": "array",
      "items": { "type": "string" },
      "default": []
    }
  }
}
```

### WeaveRequest

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/Adityaraj0421/weave-compose/schemas/request.json",
  "title": "WeaveRequest",
  "type": "object",
  "required": ["weave_protocol", "query"],
  "additionalProperties": false,
  "properties": {
    "weave_protocol": { "type": "string", "const": "1.0" },
    "query":   { "type": "string", "minLength": 1 },
    "top_n":   { "type": "integer", "minimum": 1, "maximum": 2, "default": 1 },
    "exclude": { "type": "array", "items": { "type": "string" }, "default": [] }
  }
}
```

### WeaveResponse

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://github.com/Adityaraj0421/weave-compose/schemas/response.json",
  "title": "WeaveResponse",
  "type": "object",
  "required": ["weave_protocol", "skills", "composed"],
  "additionalProperties": false,
  "properties": {
    "weave_protocol": { "type": "string", "const": "1.0" },
    "skills": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "platform", "score", "composed_context"],
        "additionalProperties": false,
        "properties": {
          "name":             { "type": "string" },
          "platform":         { "type": "string" },
          "score":            { "type": "number", "minimum": 0.0, "maximum": 1.0 },
          "composed_context": { "type": "string" }
        }
      }
    },
    "composed": { "type": "string" }
  }
}
```

---

## End-to-End Example

**Scenario:** A user is building a feature that requires designing a React form that
POSTs to a REST endpoint. Two skills are loaded: *Naksha Design System* (design +
components) and *Backend API Engineer* (REST + validation).

**Step 1 — Skills advertise at load time**

`naksha-studio/SKILL.md` has a `weave.skill.json` sidecar:

```json
{
  "weave_protocol": "1.0",
  "name": "Naksha Design System",
  "version": "1.0.0",
  "platform": "claude_code",
  "capabilities": ["design", "components", "tokens", "accessibility"],
  "trigger_patterns": ["design a component", "build a layout", "apply design tokens"],
  "dependencies": []
}
```

Both skills are embedded and stored in the registry by `weave load`.

**Step 2 — Consumer sends a WeaveRequest**

```json
{
  "weave_protocol": "1.0",
  "query": "design a REST endpoint with a React form",
  "top_n": 2,
  "exclude": []
}
```

**Step 3 — Broker selects and composes**

Cosine similarity scores: Naksha Design System → 0.847, Backend API Engineer → 0.791.
Gap is 0.056, below the default `confidence_threshold` of 0.1 — both skills returned.
`WeaveComposer` merges them: Backend API content appended after a `---` separator,
duplicate lines removed.

**Step 4 — Broker returns WeaveResponse**

```json
{
  "weave_protocol": "1.0",
  "skills": [
    {
      "name": "Naksha Design System",
      "platform": "claude_code",
      "score": 0.847,
      "composed_context": "You are a design system expert specializing in..."
    },
    {
      "name": "Backend API Engineer",
      "platform": "claude_code",
      "score": 0.791,
      "composed_context": "You are a REST API engineer specializing in..."
    }
  ],
  "composed": "You are a design system expert specializing in...\n\n---\n\nYou are a REST API engineer specializing in..."
}
```

The `composed` string is injected directly as the system prompt.

---

## Versioning

Every protocol object carries a `"weave_protocol"` field. The current version is
`"1.0"`.

**Breaking changes** (require a version bump):
- Removing or renaming a required field
- Changing a field's type
- Narrowing an enum (removing a valid value)

**Non-breaking changes** (no version bump):
- Adding an optional field with a default
- Widening an enum (adding a new platform)
- Adding a new endpoint to the local server

**Version mismatch handling:** If a consumer sends a request with a `weave_protocol`
value the broker does not recognize, the broker returns HTTP 400 with the message:
`"Unsupported protocol version: <version>. This broker supports: 1.0"`.
For in-process use (CLI), the mismatch raises `ValueError` with the same message.

---

## Implementation Status

| Feature | Spec chunk | Ships in |
|---------|-----------|----------|
| Protocol document (this file) | Chunk 5.1.1 | v1.0 |
| `weave.skill.json` manifest parsing in all adapters | Chunk 5.1.2 | v1.0 |
| Dependency resolution at load time | Chunk 5.2.1 | v1.0 |
| Conflict detection and resolution | Chunk 5.2.2 | v1.0 |
| Remote broker (inter-process / network) | post-v1.0 | TBD |
| Skill marketplace / public registry | post-v1.0 | TBD |
