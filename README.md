# global-memory

[中文介绍](README.zh-CN.md)

## 1. One-Line Summary

`global-memory` is a Codex skill that gives the agent a persistent cross-task memory for stable user preferences and collaboration habits.

## 2. What Problem It Solves

Across repeated sessions, an agent often has to rediscover the same user preferences again and again:

- which language to use by default
- whether to give a plan before execution
- how concise or detailed the output should be
- which engineering habits or standing constraints should be respected

That repeated clarification slows collaboration down and creates unnecessary noise.

`global-memory` turns those recurring preferences into reusable working memory, so the agent can carry stable collaboration context across tasks instead of reconstructing it every time.

## 3. Core Features

- Maintain persistent global memory across tasks
- Separate candidate observations, recent preferences, durable rules, and archived history
- Capture stable habits such as language, workflow, output style, and engineering defaults
- Let the agent read and update memory directly in Markdown
- Override outdated preferences while keeping a record in archive
- Prefer Chinese for generated documents and structured deliverables unless the user switches language

## 4. Workflow

```text
task start
   ↓
read long-term memory
   ↓
read only relevant short-term memory
   ↓
do the work
   ↓
write weak observations into inbox
   ↓
promote stable rules / archive obsolete ones
```

Recommended memory flow:

1. Read `long-term.md` first
2. Read only relevant entries from `short-term.md`
3. During the task, write uncertain observations into `inbox.md`
4. Promote stable patterns into `short-term.md` or `long-term.md`
5. Move outdated or conflicting rules into `archive.md`

## 5. Safety Design

- Memory is stored in plain Markdown files that are easy to inspect
- Weak observations go to `inbox.md` first instead of immediately polluting durable memory
- Stable rules and tentative preferences are stored in separate layers
- Obsolete rules are archived instead of silently discarded
- Explicit new user instructions always override stored memory
- Secrets, tokens, passwords, private personal data, and regulated data must not be stored

## 6. Technical Implementation

`global-memory` uses a text-first layered memory model:

- `inbox.md`: weak or fresh observations from the current task
- `short-term.md`: recent or tentative preferences
- `long-term.md`: durable collaboration rules
- `archive.md`: overridden, expired, or low-value memory

Default memory root:

```text
~/.codex/memories/global-memory/
```

Repository layout:

```text
.
├── agents/
│   └── openai.yaml
├── references/
│   └── memory-model.md
├── templates/
│   ├── archive.md
│   ├── inbox.md
│   ├── long-term.md
│   └── short-term.md
└── SKILL.md
```

## 7. Quick Start

Place this skill in your Codex skills directory, then create a memory folder like this:

```text
~/.codex/memories/global-memory/
├── inbox.md
├── short-term.md
├── long-term.md
└── archive.md
```

Recommended usage:

1. Use `SKILL.md` as the entry point
2. Start each substantial task by reading `long-term.md`
3. Read only the relevant entries from `short-term.md`
4. Record weak observations in `inbox.md` during the task
5. Consolidate stable rules into `short-term.md` or `long-term.md` before finishing

For the detailed memory schema and promotion rules, see `references/memory-model.md`.
