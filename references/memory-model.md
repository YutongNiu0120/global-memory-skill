# Memory Model

## Positioning

This skill uses a text-first memory model. The agent reads and edits plain Markdown files directly instead of calling a Python CLI.

Default root:

```text
~/.codex/memories/global-memory/
```

Recommended files:

- `inbox.md`
- `short-term.md`
- `long-term.md`
- `archive.md`

## Why Text-First

- Lower runtime overhead
- Easier for the model to inspect and update directly
- Transparent to the user
- Simple to version with Git or review manually

The tradeoff is that consolidation is a skill behavior, not a backend guarantee. Keep the format simple so the model can maintain it reliably.

## Entry Shape

Use one heading per memory key. Keep the fields compact and predictable.

Example:

```md
### `response-language`

- category: `language`
- confidence: `0.95`
- last_validated: `2026-03-13`
- summary: 用户默认偏好中文交流。
- rule: 默认使用中文，除非用户明确切换语言。
- evidence:
  - `2026-03-13`: 用户持续使用中文，并要求输出文档优先中文。
```

## File Roles

### `inbox.md`

Use for candidate observations from the current task.

- Low confidence is acceptable
- Prefer concrete observations
- Decide later whether to discard, keep short-term, or promote

### `short-term.md`

Use for recent or tentative preferences.

- Keep only likely reusable items
- Add `expires_after` or a similar decay hint
- Promote only after repeated evidence or a strong explicit signal

### `long-term.md`

Use for durable collaboration rules.

- Keep entries abstract and reusable
- Prefer one clear rule over many similar notes
- Update evidence instead of creating duplicates

### `archive.md`

Use for overridden, expired, or low-value memories.

- Keep a short reason
- Optionally link the replacement key
- Do not let archive grow without bound; summarize when needed

## Promotion Rules

- Start in `inbox.md` when confidence is low or the pattern is new.
- Move to `short-term.md` when the observation is likely reusable.
- Move to `long-term.md` only after repeated evidence or a strong explicit instruction.
- Let the current user message override stored memory immediately.
- Archive the old rule when a new rule clearly replaces it.

## Writing Rules

- Do not store secrets, tokens, passwords, private personal data, or regulated data.
- Do not store one-off task details with no reuse value.
- Prefer short evidence notes over long conversation excerpts.
- Keep one canonical `key` per stable rule.
- When generating documents, reports, or structured deliverables, prefer Chinese unless the user explicitly requests another language.

## Recommended Rhythm

1. Read `long-term.md` first.
2. Read only the relevant entries from `short-term.md`.
3. During the task, write weak or fresh observations into `inbox.md`.
4. Before finishing, prune `inbox.md`.
5. Promote strong items into `short-term.md` or `long-term.md`.
6. Archive obsolete items in `archive.md`.
