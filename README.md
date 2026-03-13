# global-memory

`global-memory` is a Codex/OpenAI skill for maintaining durable collaboration preferences across tasks.

It provides:

- A layered memory model with `inbox`, `short-term`, `long-term`, and `archive`
- A lightweight workflow for note capture, consolidation, promotion, and forgetting
- A Python CLI to initialize, inspect, update, flush, and decay memory entries

This skill is useful when you want the agent to remember stable preferences such as language, output style, planning habits, engineering defaults, and standing constraints without polluting each session with one-off notes.

## Repository Layout

```text
.
├── agents/
│   └── openai.yaml
├── references/
│   └── memory-model.md
├── scripts/
│   └── manage_memory.py
└── SKILL.md
```

## Core Model

- `inbox.json`: session observations waiting for review
- `short-term.json`: tentative or recent habits
- `long-term.json`: durable collaboration rules
- `archive.json`: promoted, expired, overridden, or forgotten entries

Default storage root:

```text
~/.codex/memories/global-memory
```

## Quick Start

Initialize the store:

```bash
python scripts/manage_memory.py init
```

Review long-term memory:

```bash
python scripts/manage_memory.py list --tier long
```

Queue a candidate observation:

```bash
python scripts/manage_memory.py note \
  --session current-task \
  --category workflow \
  --key plan-before-execution \
  --summary "User asked for a plan before implementation." \
  --abstract-summary "For reusable or system-level changes, present a plan before implementation." \
  --tag planning \
  --evidence-note "Explicit user request."
```

Flush session notes and consolidate:

```bash
python scripts/manage_memory.py flush --session current-task --consolidate
```

## How To Use In Codex

1. Place this folder under your Codex skills directory.
2. Keep `SKILL.md` as the main entry point.
3. Let the agent read long-term memory first, then only the relevant short-term entries.
4. Queue observations during a task and consolidate near the end of the task.

## Notes

- Do not store secrets, tokens, passwords, or regulated personal data.
- Prefer reusable abstractions over long raw conversation excerpts.
- Use `--override` when the user explicitly changes a standing preference.

For the detailed memory schema and promotion/forgetting rules, see `references/memory-model.md`.
