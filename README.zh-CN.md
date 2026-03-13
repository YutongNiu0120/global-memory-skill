# global-memory

`global-memory` 是一个面向 Codex/OpenAI 技能体系的纯文本全局记忆技能，用来跨任务维护用户的稳定协作偏好。

它解决的问题很直接：很多偏好并不是当前任务独有的，而是会反复出现，例如默认回复语言、是否先给计划、输出风格、工程习惯、固定约束等。把这些信息只留在当前对话里，下一次还要重新确认；全部硬写死，又会让记忆变得嘈杂。这个 skill 用分层记忆来处理这个问题。

## 能力概览

- 通过 `inbox / short-term / long-term / archive` 四层结构管理记忆
- 支持“先记录候选观察，再整理沉淀”的轻量工作流
- 由 AI 直接读写 Markdown 记忆文件，不依赖 Python
- 通过固定格式和 `key` 约束减少重复、冲突和噪音

## 适用场景

- 用户长期偏好中文或英文回复
- 用户反复要求“先出方案，再动手”
- 用户偏好精简输出、保留关键结论
- 用户对测试、提交、文件修改方式有稳定要求
- 希望把跨项目协作习惯沉淀成可复用规则

## 目录说明

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

- `SKILL.md`：skill 主说明，定义使用方式和默认工作节奏
- `references/memory-model.md`：记忆模型字段、提升规则、遗忘规则
- `templates/*.md`：记忆文件模板，可直接复制到本地记忆目录使用
- `agents/openai.yaml`：技能元信息

## 记忆分层设计

- `inbox.md`：当前会话采集到的候选观察，先放这里，避免低价值信息直接污染正式记忆
- `short-term.md`：短期记忆，适合记录“最近观察到、但还没完全稳定”的偏好
- `long-term.md`：长期记忆，适合沉淀成长期有效的协作规则
- `archive.md`：归档层，保存已过期、被覆盖、被遗忘、或已提升的记录

默认存储路径：

```text
~/.codex/memories/global-memory/
```

## 推荐工作流

1. 任务开始时，先读取长期记忆，再读取少量与当前任务相关的短期记忆。
2. 执行过程中，不急着把每条观察都写入正式记忆，优先先写入 `inbox.md`。
3. 任务结束前，检查 `inbox`，保留真正有复用价值的观察。
4. 把稳定项写入 `short-term.md`，重复出现或强信号项再提升到 `long-term.md`。
5. 如果用户明确改变偏好，把旧规则移到 `archive.md`，再写入新规则。

## 快速开始

创建记忆目录，并拷贝模板：

```text
~/.codex/memories/global-memory/
├── inbox.md
├── short-term.md
├── long-term.md
└── archive.md
```

## 设计原则

- 不存储密码、密钥、令牌、隐私信息、受监管数据
- 不保留没有复用价值的一次性任务细节
- 不基于猜测写入用户画像
- 长期记忆尽量抽象成简洁规则，而不是冗长对话摘录
- 当前用户消息永远优先于历史记忆
- 输出文档和结构化内容时默认优先中文

## 接入建议

如果你想把它作为自己的 Codex skill 使用，直接将本仓库放到技能目录，并保留 `SKILL.md` 作为入口即可。实际执行时，优先让代理读取 `long-term.md`，再按需读取 `short-term.md`；中途把弱观察先写入 `inbox.md`，结束时统一整理，这样既轻量，也更符合 AI 直接工作的方式。

更完整的字段说明和提升/遗忘细节见 `references/memory-model.md`。
