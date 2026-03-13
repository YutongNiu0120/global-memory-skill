# Memory Model

## Storage Layout

Default root: `~/.codex/memories/global-memory`

- `inbox.json`: session-scoped observations waiting to be reviewed or flushed
- `short-term.json`: tentative or recent observations
- `long-term.json`: stable collaboration rules
- `archive.json`: expired, overridden, promoted, or forgotten entries

Each file stores a JSON object with `version`, `tier`, `updated_at`, and `entries`.

## Inbox Fields

Inbox observations represent candidate memories collected during a task before they are committed to the memory store.

- `id`: stable inbox note id such as `ib-...`
- `session_id`: identifier for the current task or conversation
- `target_tier`: usually `short-term`; use `long-term` only for very strong explicit instructions
- `key`: canonical dedupe key to use when the note is flushed
- `summary`: concrete observation from the session
- `abstract_summary`: reusable abstraction to keep if the pattern stabilizes
- `category`, `scope`, `confidence`, `tags`: same meaning as live memory fields
- `ttl_days`: short-term expiry to apply after flush
- `evidence_note`: brief note for the future evidence trail
- `override`: whether flushing this note should retire older conflicting memories with the same key
- `captured_at`: note capture time

Use the inbox to prevent low-value noise from immediately entering short-term memory.

## Shared Fields

Every live entry uses these common fields:

- `id`: stable entry id such as `st-...` or `lt-...`
- `key`: canonical dedupe key for the rule
- `summary`: current human-readable memory statement
- `abstract_summary`: optional promotion-ready abstraction
- `category`: coarse type such as `language`, `workflow`, or `constraints`
- `scope`: default `global`; reserve narrower scopes for future extensions
- `confidence`: `0.0` to `1.0`
- `evidence_count`: number of observations supporting the memory
- `evidence`: recent evidence notes with timestamps
- `tags`: optional labels for filtering
- `created_at`: first capture time
- `last_seen_at`: most recent observation time
- `last_used_at`: most recent time the memory helped in real work

## Short-Term Fields

Short-term entries add:

- `expires_at`: automatic expiry point

Use short-term memory for fresh observations, unstable habits, or patterns that still need confirmation.

## Long-Term Fields

Long-term entries add:

- `last_validated_at`: most recent explicit validation or helpful reuse
- `last_decay_at`: most recent automatic decay pass
- `source_ids`: short-term entries that were promoted into this rule

Use long-term memory only for compact, reusable rules that should survive across tasks.

## Promotion Rules

- Add new observations to short-term memory first.
- Reuse the same `key` to reinforce an existing memory instead of creating duplicates.
- Promote a short-term entry when its `evidence_count` reaches the promotion threshold.
- Prefer `abstract_summary` over raw `summary` when promoting to long-term memory.
- Use `--tier long` only when the user gives a strong explicit instruction that is already stable enough to keep.

Example:

- Short-term summary: `User asked for a plan before implementing a new global skill.`
- Long-term abstraction: `For reusable or system-level changes, present a plan before implementation.`

## Forgetting Rules

- Short-term memory expires automatically when `expires_at` passes.
- Long-term memory decays when it has not been used or validated for a long period.
- Archive long-term entries once decay pushes confidence below the forget threshold.
- Use `--override` to immediately retire conflicting active memories when the user changes direction.
- Use `forget` when a memory is clearly wrong, obsolete, or harmful.

## Practical Guidance

- Only store facts that reduce future clarification cost.
- Keep evidence notes short and concrete.
- Avoid storing large conversation excerpts; store the conclusion and a short note instead.
- If a memory is useful only for one phase of one task, let it stay short-term and expire.
- If several memories point to the same stable habit, merge them through a shared `key` and promote the abstraction.
- For medium or large tasks, prefer the lightweight rhythm: read memory at the start, queue session notes during work, and flush them at the end.
