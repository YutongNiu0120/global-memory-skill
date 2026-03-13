# global-memory

[中文介绍](#中文说明)

`global-memory` is a text-first Codex/OpenAI skill for maintaining durable collaboration preferences across tasks.

It provides:

- A layered memory model with `inbox`, `short-term`, `long-term`, and `archive`
- A lightweight workflow for note capture, consolidation, promotion, and forgetting
- Direct Markdown editing by the model, without requiring Python at runtime

This skill is useful when you want the agent to remember stable preferences such as language, output style, planning habits, engineering defaults, and standing constraints without polluting each session with one-off notes.

## Repository Layout

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

## Core Model

- `inbox.md`: session observations waiting for review
- `short-term.md`: tentative or recent habits
- `long-term.md`: durable collaboration rules
- `archive.md`: promoted, expired, overridden, or forgotten entries

Default storage root:

```text
~/.codex/memories/global-memory/
```

## Quick Start

Create a memory folder and copy the templates:

```text
~/.codex/memories/global-memory/
├── inbox.md
├── short-term.md
├── long-term.md
└── archive.md
```

## How To Use In Codex

1. Place this folder under your Codex skills directory.
2. Keep `SKILL.md` as the main entry point.
3. Let the agent read `long-term.md` first, then only the relevant entries from `short-term.md`.
4. During the task, write weak observations into `inbox.md`.
5. Near the end of the task, prune `inbox.md`, promote stable items, and archive obsolete ones.

## Notes

- No Python runtime is required for normal usage.
- The model should read and update the Markdown files directly.
- Do not store secrets, tokens, passwords, or regulated personal data.
- Prefer reusable abstractions over long raw conversation excerpts.
- When generating documents or structured deliverables, prefer Chinese unless the user explicitly requests another language.

For the detailed memory schema and promotion/forgetting rules, see `references/memory-model.md`.

## 中文说明

`global-memory` 是一个面向 Codex/OpenAI 技能体系的纯文本全局记忆技能，用来跨任务维护用户的稳定协作偏好。

它适合沉淀这类会反复出现的信息：

- 默认回复语言
- 是否先给方案再执行
- 输出风格偏好
- 工程习惯与长期约束

### 核心能力

- 用 `inbox / short-term / long-term / archive` 四层结构管理记忆
- 支持“先记录候选观察，再整理沉淀”的轻量工作流
- 直接由 AI 读写 Markdown 文件，不依赖 Python 运行时
- 通过固定格式和 `key` 减少重复与噪音

### 目录结构

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

### 记忆分层

- `inbox.md`：当前会话中的候选观察
- `short-term.md`：短期、待验证的偏好
- `long-term.md`：稳定、可复用的协作规则
- `archive.md`：已提升、过期、被覆盖或遗忘的记录

默认存储路径：

```text
~/.codex/memories/global-memory/
```

### 快速开始

创建记忆目录，并拷贝模板：

```text
~/.codex/memories/global-memory/
├── inbox.md
├── short-term.md
├── long-term.md
└── archive.md
```

### 使用建议

1. 任务开始时先读 `long-term.md`，再按需读相关的 `short-term.md`。
2. 执行过程中把弱观察先写入 `inbox.md`，不要立刻污染正式记忆。
3. 任务结束前整理 `inbox.md`，把稳定项提升到 `short-term.md` 或 `long-term.md`。
4. 用户明确改变偏好时，把旧规则移到 `archive.md`，再写入新规则。

### 注意事项

- 不要存储密码、令牌、隐私信息或受监管数据
- 不要存储没有复用价值的一次性任务细节
- 当前用户消息优先级永远高于历史记忆
- 生成文档和结构化输出时，默认优先中文

更完整的字段定义和提升/遗忘规则见 `references/memory-model.md`。如需独立中文文档，也可以查看 `README.zh-CN.md`。
