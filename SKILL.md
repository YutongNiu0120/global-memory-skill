---
name: global-memory
description: "Maintain a global memory for user habits and working preferences with layered short-term and long-term memory, forgetting, and abstraction. Use when Codex should capture, update, consolidate, or apply stable collaboration preferences across tasks; when recurring clarification could be reduced by remembering the user's preferred language, planning style, output style, technical defaults, or standing constraints; or when Codex needs to manage the memory store itself."
---

# Global Memory

## Overview

Use this skill to keep a global memory that survives across tasks. Treat short-term memory as a staging area for recent observations, promote repeated patterns into long-term memory, and forget stale or low-value memories before the store becomes noisy.

## Memory Layers

### Short-term memory

- Store recent or tentative observations that may still change.
- Capture concrete evidence such as phrasing, requests, or repeated corrections.
- Give each entry a stable `key`, an evidence note, and a TTL.

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

1. At task start, review long-term memory and only the most relevant short-term entries.
2. During execution, queue possible observations with `note` instead of writing directly into memory.
3. At task end, flush the session with `flush --consolidate`.
4. When generating documents, reports, or other structured deliverables, prefer Chinese unless the user explicitly requests another language.

Do not force this workflow onto casual chat, one-line requests, or tasks with no likely memory value.

## Storage

Default memory root: `~/.codex/memories/global-memory`

Files:

- `inbox.json`
- `short-term.json`
- `long-term.json`
- `archive.json`

Read [references/memory-model.md](references/memory-model.md) for field definitions, promotion rules, and forgetting heuristics.

## Commands

Initialize the global store:

```bash
python scripts/manage_memory.py init
```

Queue candidate observations during a session:

```bash
python scripts/manage_memory.py note --session current-task --category workflow --key plan-before-execution --summary "User asked to confirm the plan before implementation." --abstract-summary "For reusable or system-level changes, present a plan before implementation." --tag planning --evidence-note "User requested a plan before execution."
```

Review queued observations before writing them:

```bash
python scripts/manage_memory.py list --tier inbox
```

Review current memory:

```bash
python scripts/manage_memory.py list --tier long
python scripts/manage_memory.py list --tier short --limit 10
```

Capture a tentative preference:

```bash
python scripts/manage_memory.py add --tier short --category workflow --scope global --key plan-before-execution --summary "User prefers a plan before implementation for reusable changes." --abstract-summary "For reusable or system-level changes, present a plan before implementation." --tag planning --evidence-note "Requested a plan before creating a global memory skill."
```

Override an outdated preference:

```bash
python scripts/manage_memory.py add --tier short --override --category language --scope global --key response-language --summary "User currently prefers replies in Chinese." --abstract-summary "Default to Chinese unless the user switches languages." --tag language --evidence-note "Conversation continued in Chinese."
```

Mark a memory as validated in real use:

```bash
python scripts/manage_memory.py touch --tier long --key plan-before-execution --note "Plan-first preference helped on a cross-project change."
```

Consolidate, promote, and forget:

```bash
python scripts/manage_memory.py consolidate
```

Flush session observations into memory, then consolidate:

```bash
python scripts/manage_memory.py flush --session current-task --consolidate
```

Remove a bad or obsolete memory:

```bash
python scripts/manage_memory.py forget --tier long --key response-language --reason "User switched to English and asked to keep future replies in English."
```

## Heuristics

- Prefer one memory per stable rule. Reinforce existing entries by key instead of creating near-duplicates.
- Write the short-term `summary` as a concrete observation. Write `abstract_summary` as the reusable rule to promote later.
- Use `--override` when the user explicitly changes a preference and the old rule should stop applying immediately.
- Use categories such as `language`, `workflow`, `output-style`, `engineering`, `tooling`, or `constraints`.
- Keep long-term memory compact. If two entries can be merged into one clearer rule, consolidate them.

## Collaboration Rhythm

1. At the start of substantial work, read long-term memory and the most relevant short-term entries.
2. During the task, queue candidate observations with `note` instead of immediately writing everything into memory.
3. Before finishing the task, review `inbox.json` or `list --tier inbox` to discard weak observations.
4. Flush the session with `flush --consolidate` so useful observations become short-term memory and repeated patterns can promote into long-term memory.
5. Let explicit new user instructions override stored memory on the next turn.
6. Treat this rhythm as the default operating mode for medium or large tasks unless the user asks for a different workflow.
