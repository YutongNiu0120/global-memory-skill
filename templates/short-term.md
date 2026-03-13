# Short-Term Memory

用于保存近期、暂时有效、还需要继续验证的偏好。

## 记录格式

### `<key>`

- category: `workflow | language | output-style | engineering | tooling | constraints`
- confidence: `0.50-0.85`
- last_seen: `YYYY-MM-DD`
- expires_after: `7d | 14d | 30d`
- summary: 近期观察结论
- abstract_rule: 若稳定后可提升的抽象规则
- evidence:
  - `YYYY-MM-DD`: 简短证据

## Example

### `document-language`

- category: `language`
- confidence: `0.80`
- last_seen: `2026-03-13`
- expires_after: `30d`
- summary: 用户当前更偏好文档和结构化输出使用中文。
- abstract_rule: 输出文档优先使用中文，除非用户明确要求其他语言。
- evidence:
  - `2026-03-13`: 用户要求在 skill 中增加“输出文档优先使用中文”的约束。
