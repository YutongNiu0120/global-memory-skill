---
name: global-memory
description: "Maintain a global memory for user habits and working preferences with layered short-term and long-term memory, forgetting, and abstraction. Use when Codex should capture, update, consolidate, or apply stable collaboration preferences across tasks; when recurring clarification could be reduced by remembering the user's preferred language, planning style, output style, technical defaults, or standing constraints; or when Codex needs to manage the memory store itself."
---

# Global Memory

## Overview

Use this skill to keep a global memory that survives across tasks. This version is text-first: the agent should read and edit plain Markdown memory files directly instead of calling Python scripts.

## Memory Layers

### Inbox

- Store weak or fresh observations from the current task.
- Keep entries concrete and easy to discard.
- Promote only if they look reusable.

### Short-term memory

- Store recent or tentative observations that may still change.
- Capture concrete evidence such as phrasing, requests, or repeated corrections.
- Give each entry a stable `key`, concise evidence, and a decay hint.

Examples:

- "User asked for a plan before implementing a new global skill."
- "User currently prefers Chinese for this workflow."

### Long-term memory

- Store durable collaboration rules that have held across tasks.
- Keep entries abstract and reusable.
- Prefer one clean rule over many near-duplicate notes.

Examples:

- "For reusable or system-level changes, present a plan before implementation."
- "Default to Chinese unless the user switches languages."

### Never store

- Secrets, tokens, passwords, private personal data, or regulated data.
- One-off task details with no likely reuse value.
- Personality judgments, speculation, or anything unsupported by user behavior.
- Rules that conflict with the current explicit user message.

## Working Loop

1. Read relevant long-term entries first.
2. Read only recent short-term entries that are clearly relevant to the request.
3. Let the current user message override memory.
4. Add or reinforce short-term memory when the user explicitly states a preference or repeats a pattern.
5. Promote to long-term only after repeated evidence or a strong explicit signal.
6. Forget stale entries rather than preserving everything.

## Default Lightweight Policy

Use this lightweight policy by default for medium or large tasks:

1. At task start, review `long-term.md` and only the most relevant entries from `short-term.md`.
2. During execution, write weak or fresh observations into `inbox.md`.
3. At task end, prune `inbox.md`, then promote stable items into `short-term.md` or `long-term.md`.
4. When generating documents, reports, or other structured deliverables, prefer Chinese unless the user explicitly requests another language.

Do not force this workflow onto casual chat, one-line requests, or tasks with no likely memory value.

## Storage

Default memory root: `~/.codex/memories/global-memory`

Files:

- `inbox.md`
- `short-term.md`
- `long-term.md`
- `archive.md`

Copy the starter files from `templates/` into the memory root. Read [references/memory-model.md](references/memory-model.md) for field definitions, promotion rules, and forgetting heuristics.

## Direct Editing Pattern

Read durable rules first:

```text
long-term.md
```

Read only relevant recent observations:

```text
short-term.md
```

Write tentative notes during the task:

```text
inbox.md
```

Promote stable rules by rewriting them into:

```text
short-term.md
long-term.md
archive.md
```

## Heuristics

- Prefer one memory per stable rule. Reinforce existing entries by key instead of creating near-duplicates.
- Write short-term `summary` as a concrete observation. Write long-term `rule` as the reusable abstraction.
- When the user explicitly changes a preference, archive the old rule and write the new one immediately.
- Use categories such as `language`, `workflow`, `output-style`, `engineering`, `tooling`, or `constraints`.
- Keep long-term memory compact. If two entries can be merged into one clearer rule, consolidate them.

## Collaboration Rhythm

1. At the start of substantial work, read `long-term.md` and the most relevant entries from `short-term.md`.
2. During the task, append candidate observations to `inbox.md` instead of immediately rewriting durable memory.
3. Before finishing the task, review `inbox.md` and discard weak observations.
4. Rewrite useful observations into `short-term.md` and promote repeated patterns into `long-term.md`.
5. Move obsolete or conflicting rules into `archive.md`.
6. Let explicit new user instructions override stored memory on the next turn.
7. Treat this rhythm as the default operating mode for medium or large tasks unless the user asks for a different workflow.
