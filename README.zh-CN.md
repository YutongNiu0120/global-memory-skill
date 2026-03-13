# global-memory

[English README](README.md)

## 1. 项目一句话

`global-memory` 是一个面向 Codex 的 skill，用来给 agent 建立跨任务的全局记忆，持续保留用户的稳定偏好和协作习惯。

## 2. 解决什么问题

在重复协作过程中，agent 经常需要反复重新确认同一类偏好：

- 默认应该使用什么语言
- 是否要先给方案再执行
- 输出应该简洁还是详细
- 哪些工程习惯和长期约束需要一直遵守

这种重复澄清会降低协作效率，也会让每次任务都多出很多不必要的沟通成本。

`global-memory` 的作用，就是把这些反复出现的稳定偏好沉淀成可复用的全局记忆，让 agent 在后续任务里优先复用，而不是每次重新问起。

## 3. 核心功能

- 在跨任务场景下维护全局持久记忆
- 区分候选观察、短期偏好、长期规则和归档历史
- 记录语言、工作流、输出风格、工程习惯等稳定偏好
- 由 agent 直接读写 Markdown 记忆文件
- 用户偏好变化时，覆盖旧规则并保留归档记录
- 生成文档和结构化内容时，默认优先中文，除非用户明确切换语言

## 4. 工作流程

```text
任务开始
   ↓
读取长期记忆
   ↓
读取相关短期记忆
   ↓
执行任务
   ↓
把弱观察写入 inbox
   ↓
提升稳定规则 / 归档旧规则
```

推荐流程：

1. 先读取 `long-term.md`
2. 再读取与当前任务相关的 `short-term.md`
3. 执行过程中，把不确定观察先写入 `inbox.md`
4. 任务结束前，把稳定规律提升到 `short-term.md` 或 `long-term.md`
5. 把失效或冲突的旧规则移到 `archive.md`

## 5. 安全设计

- 所有记忆都保存在可直接审阅的 Markdown 文件里
- 弱观察先进入 `inbox.md`，避免直接污染正式记忆
- 短期偏好和长期规则分层管理
- 失效规则进入归档，而不是直接无痕删除
- 当前用户的明确新指令始终优先于历史记忆
- 不允许存储密码、令牌、隐私信息和受监管数据

## 6. 技术实现

`global-memory` 采用纯文本分层记忆模型：

- `inbox.md`：当前任务中的弱观察和候选记忆
- `short-term.md`：近期、待验证的偏好
- `long-term.md`：稳定、可复用的长期协作规则
- `archive.md`：被覆盖、过期或低价值的历史记忆

默认存储路径：

```text
~/.codex/memories/global-memory/
```

仓库结构：

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

## 7. 快速开始

把这个 skill 放到 Codex skills 目录，然后创建记忆目录：

```text
~/.codex/memories/global-memory/
├── inbox.md
├── short-term.md
├── long-term.md
└── archive.md
```

推荐用法：

1. 以 `SKILL.md` 作为入口
2. 每次较大任务开始前先读取 `long-term.md`
3. 按需读取相关的 `short-term.md`
4. 执行过程中把弱观察写入 `inbox.md`
5. 任务结束前把稳定规则整理进 `short-term.md` 或 `long-term.md`

更完整的字段定义和提升规则见 `references/memory-model.md`。
