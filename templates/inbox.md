# Inbox

用于记录当前任务中观察到、但还未确认要长期保留的候选记忆。

## 记录格式

### `<key>`

- category: `workflow | language | output-style | engineering | tooling | constraints`
- confidence: `0.30-0.70`
- captured_at: `YYYY-MM-DD`
- summary: 一条具体观察
- abstract_rule: 如果未来重复出现，可以提升成什么稳定规则
- evidence:
  - `YYYY-MM-DD`: 简短证据
- next_action: `drop | keep-short-term | promote-long-term`

## Example

### `plan-before-execution`

- category: `workflow`
- confidence: `0.60`
- captured_at: `2026-03-13`
- summary: 用户在做全局性调整时希望先明确方案再实施。
- abstract_rule: 对可复用或系统级改动，优先先出方案再执行。
- evidence:
  - `2026-03-13`: 用户要求重新设计方案后再落实现有 skill。
- next_action: `keep-short-term`
