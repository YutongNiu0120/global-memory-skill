# global-memory

[中文介绍](#中文说明)

`global-memory` is a Codex/OpenAI skill for maintaining durable collaboration preferences across tasks.

It provides:

- A layered memory model with `inbox`, `short-term`, `long-term`, and `archive`
- A lightweight workflow for note capture, consolidation, promotion, and forgetting
- A Python CLI to initialize, inspect, update, flush, and decay memory entries

This skill is useful when you want the agent to remember stable preferences such as language, output style, planning habits, engineering defaults, and standing constraints without polluting each session with one-off notes.

## Repository Layout

```text
.
├── agents/
│   └── openai.yaml
├── references/
│   └── memory-model.md
├── scripts/
│   └── manage_memory.py
└── SKILL.md
```

## Core Model

- `inbox.json`: session observations waiting for review
- `short-term.json`: tentative or recent habits
- `long-term.json`: durable collaboration rules
- `archive.json`: promoted, expired, overridden, or forgotten entries

Default storage root:

```text
~/.codex/memories/global-memory
```

## Quick Start

Initialize the store:

```bash
python scripts/manage_memory.py init
```

Review long-term memory:

```bash
python scripts/manage_memory.py list --tier long
```

Queue a candidate observation:

```bash
python scripts/manage_memory.py note \
  --session current-task \
  --category workflow \
  --key plan-before-execution \
  --summary "User asked for a plan before implementation." \
  --abstract-summary "For reusable or system-level changes, present a plan before implementation." \
  --tag planning \
  --evidence-note "Explicit user request."
```

Flush session notes and consolidate:

```bash
python scripts/manage_memory.py flush --session current-task --consolidate
```

## How To Use In Codex

1. Place this folder under your Codex skills directory.
2. Keep `SKILL.md` as the main entry point.
3. Let the agent read long-term memory first, then only the relevant short-term entries.
4. Queue observations during a task and consolidate near the end of the task.

## Notes

- Do not store secrets, tokens, passwords, or regulated personal data.
- Prefer reusable abstractions over long raw conversation excerpts.
- Use `--override` when the user explicitly changes a standing preference.

For the detailed memory schema and promotion/forgetting rules, see `references/memory-model.md`.

## 中文说明

`global-memory` 是一个面向 Codex/OpenAI 技能体系的全局记忆技能，用来跨任务维护用户的稳定协作偏好。

它适合沉淀这类会反复出现的信息：

- 默认回复语言
- 是否先给方案再执行
- 输出风格偏好
- 工程习惯与长期约束

### 核心能力

- 用 `inbox / short-term / long-term / archive` 四层结构管理记忆
- 支持“先记录候选观察，再整理沉淀”的轻量工作流
- 提供 `manage_memory.py` 命令行工具，用于初始化、查看、写入、提升、遗忘记忆
- 通过 `key` 和证据计数减少重复与噪音

### 目录结构

```text
.
├── agents/
│   └── openai.yaml
├── references/
│   └── memory-model.md
├── scripts/
│   └── manage_memory.py
└── SKILL.md
```

### 记忆分层

- `inbox.json`：当前会话中的候选观察
- `short-term.json`：短期、待验证的偏好
- `long-term.json`：稳定、可复用的协作规则
- `archive.json`：已提升、过期、被覆盖或遗忘的记录

默认存储路径：

```text
~/.codex/memories/global-memory
```

### 快速开始

初始化：

```bash
python scripts/manage_memory.py init
```

查看长期记忆：

```bash
python scripts/manage_memory.py list --tier long
```

记录候选观察：

```bash
python scripts/manage_memory.py note \
  --session current-task \
  --category workflow \
  --key plan-before-execution \
  --summary "用户要求实现前先给方案。" \
  --abstract-summary "对于可复用或系统级改动，优先先给方案再实施。" \
  --tag planning \
  --evidence-note "用户明确提出先出方案。"
```

整理并写入正式记忆：

```bash
python scripts/manage_memory.py flush --session current-task --consolidate
```

### 使用建议

1. 任务开始时先读长期记忆，再按需读相关短期记忆。
2. 执行过程中优先把观察写入 `inbox`，不要立刻污染正式记忆。
3. 任务结束时统一 `flush --consolidate`。
4. 用户明确改变偏好时，用 `--override` 覆盖旧规则。

### 注意事项

- 不要存储密码、令牌、隐私信息或受监管数据
- 不要存储没有复用价值的一次性任务细节
- 当前用户消息优先级永远高于历史记忆

更完整的字段定义和提升/遗忘规则见 `references/memory-model.md`。如需独立中文文档，也可以查看 `README.zh-CN.md`。
