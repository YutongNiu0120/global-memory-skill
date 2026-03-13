# Long-Term Memory

用于保存稳定、可跨任务复用的协作规则。

## 记录格式

### `<key>`

- category: `workflow | language | output-style | engineering | tooling | constraints`
- confidence: `0.80-1.00`
- last_validated: `YYYY-MM-DD`
- summary: 当前稳定结论
- rule: 清晰、可复用的长期规则
- evidence:
  - `YYYY-MM-DD`: 简短证据

## Example

### `response-language`

- category: `language`
- confidence: `0.95`
- last_validated: `2026-03-13`
- summary: 用户默认偏好中文交流。
- rule: 默认使用中文，除非用户明确切换语言。
- evidence:
  - `2026-03-13`: 用户持续使用中文，并要求输出文档优先中文。
