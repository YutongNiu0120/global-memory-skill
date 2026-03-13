# Archive

用于保存已过期、被覆盖、或不再适用的旧记忆，避免直接丢失上下文。

## 记录格式

### `<key>`

- archived_at: `YYYY-MM-DD`
- reason: `expired | overridden | low-value | incorrect`
- previous_summary: 旧结论
- replacement: 新规则或空

## Example

### `response-language-english`

- archived_at: `2026-03-13`
- reason: `overridden`
- previous_summary: 用户当前偏好英文回复。
- replacement: `response-language`
