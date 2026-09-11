---
name: skill-creator
description: >
  此技能适用于用户询问关于"skill-creator"、"创建新技能、改进现有技能、搭建技能目录框架、验证 SKILL.md"、"将技能打包为可分发的 .skill 文件"。按照开放的 AgentSkills 规范（agentskills.io）设计、创建、更新和打包 Agent Skills。
---

# Skill Creator

创建和维护高质量 Agent Skills 的指导，适用于所有 AI Agent。

## 什么是技能 (Skill)

技能是一个自包含的文件夹，为任何 AI Agent 提供特定领域的专业知识、工作流和工具。技能遵循开放的 [AgentSkills 规范](https://agentskills.io/specification)。

### 目录结构

```
skill-name/
├── SKILL.md          # 必须 — frontmatter + 指令
├── scripts/          # 可选 — Agent 可执行的代码
├── references/       # 可选 — 按需加载到上下文的文档
└── assets/           # 可选 — 用于输出的模板、图片、数据文件
```

### 技能提供的内容

- 特定领域的多步骤工作流
- 用于确定性、可重复操作的可复用脚本
- Agent 无法自行推断的领域知识、schema 和策略
- 用于一致性输出的模板和样板资产

---

## 核心设计原则

### 1. 简洁为要

上下文窗口是共享资源。技能中的每个 token 都在与用户请求、对话历史及其他技能竞争。审视每一句话：*Agent 真的需要这个吗？* 优先使用简短示例而非冗长说明。

### 2. 渐进式披露 (Progressive Disclosure)

按分阶段加载进行设计：

- **发现阶段**：仅 `name` + `description`
- **激活阶段**：完整的 `SKILL.md` 正文（保持 **500 行以内**）
- **按需加载**：`scripts/`、`references/`、`assets/` 中的文件

将详细内容移至 `references/`，让 Agent 仅加载所需内容。

### 3. Agent 中立语言

技能由不同 AI Agent（Claude、Gemini、Codex 等）执行。使用祈使句形式编写指令。永远不要在技能正文中硬编码产品名称，应使用"the agent"（该 Agent）代替。

---

## 技能创建流程

1. 理解技能（示例 + 成功标准）
2. 规划可复用资源（scripts/references/assets）
3. 初始化目录（搭建框架）
4. 编写 SKILL.md + 资源文件
5. 验证并打包
6. 安装并测试
7. 根据实际使用情况迭代

---

### 第一步：理解技能

在编写任何内容之前，收集具体的使用示例。每次最多提出两个澄清性问题；倾向于立即行动。

有用的问题：
- "这个技能应该处理哪些具体任务？"
- "用户输入什么内容应该触发这个技能？"
- "成功是什么样子的？"

完成本步骤时，应有清晰的 3-5 个具体使用示例。

### 第二步：规划资源

对每个示例，问：*Agent 需要什么才能反复执行这个操作？*

| 资源类型 | 使用场景 |
|---------|---------|
| `scripts/` | 每次都需要重写相同代码；需要确定性输出 |
| `references/` | Agent 在运行时需要详细文档、schema 或策略 |
| `assets/` | 输出包含 Agent 复制的模板、图片或样板内容 |

在编写任何代码之前，先输出一份简短的资源规划。

### 第三步：初始化

运行初始化脚本搭建目录框架：

```bash
python scripts/init_skill.py <skill-name> --path <output-dir>
# 含可选资源目录和示例占位符：
python scripts/init_skill.py <skill-name> --path <output-dir> --resources scripts,references,assets --examples
```

该脚本会创建技能文件夹、含 TODO 占位符的 `SKILL.md` 模板，以及各资源目录中的可选示例文件。

> **注意：** 使用此 skill-creator 的 `scripts/` 目录的绝对路径。

### 第四步：编写

#### SKILL.md — Frontmatter

仅使用必填字段，不添加多余内容：

```yaml
---
name: my-skill                  # 小写字母、连字符，最多 64 个字符，与文件夹名一致
description: >                  # 功能描述 + 使用时机；最多 1024 个字符
  单段连贯文字，涵盖功能和触发条件。
---
```

可选字段（仅在有意义时添加）：

```yaml
license: MIT
compatibility: Requires Python 3.11+, git
metadata:
  author: your-org
  version: "1.0"
allowed-tools: Bash(python:*) Read   # 实验性
```

**description 规则：**
- 同时包含技能的*功能*和*激活时机*
- 提及文件类型、任务关键词和激活短语
- 最多 1024 个字符；不含尖括号
- 这是主要的路由信号 — 务必精确

#### SKILL.md — 正文

编写 Agent 遵循的分步指令。常见结构模式：

| 模式 | 最适合 |
|------|--------|
| 基于工作流 | 有明确步骤的顺序流程 |
| 基于任务 | 包含不同操作的工具集合 |
| 参考/指南 | 标准、策略、品牌规范 |
| 基于能力 | 具有相互关联功能的集成系统 |

按需混合使用各种模式。始终以 **Resources（资源文件）** 章节结尾，列出 `scripts/`、`references/` 和 `assets/` 中的内容及各文件的使用时机。

#### 脚本 (`scripts/`)

- 优先使用 Python 3（或 Bash）编写
- 输出必须对 LLM 友好：简洁的成功/失败字符串，不输出原始堆栈跟踪，截断过长输出
- 提交前测试每个脚本
- 使用 `# requires: package` 注释或 `requirements.txt` 记录依赖

#### 参考文件 (`references/`)

- 每个域/主题一个文件 — Agent 会单独加载这些文件
- 超过 100 行的文件在顶部添加目录
- 在 `SKILL.md` 中明确链接所有参考文件，并注明加载时机
- 切勿在 `SKILL.md` 和参考文件之间重复内容

#### 资产 (`assets/`)

- 在 Agent 输出中复制或使用的静态文件
- 不加载到上下文中 — 大小不是问题
- 对复杂模板使用子目录（如 `assets/project-template/`）

#### 不应包含的内容

不要创建：`README.md`、`CHANGELOG.md`、`INSTALLATION_GUIDE.md` 或任何记录技能创建过程而非技能领域本身的文件。每个文件必须能向执行技能的 Agent 证明其存在的必要性。

### 第五步：验证与打包

**验证：**

```bash
python scripts/quick_validate.py <path/to/skill-folder>
# 或官方 CLI（如已安装）：
skills-ref validate <path/to/skill-folder>
```

修复所有错误。打包前解决所有 `TODO` 标记。

**打包：**

```bash
python scripts/package_skill.py <path/to/skill-folder>
# 可选输出目录：
python scripts/package_skill.py <path/to/skill-folder> ./dist
```

打包工具先验证，然后创建 `<skill-name>.skill`（zip 文件）。成功时会打印输出路径。

### 第六步：安装与测试

使用你的 Agent 平台的安装机制（CLI/UI）安装打包好的技能。如果平台支持作用域，迭代开发期间优先选择**工作区/仓库作用域**。

安装完成后，重新加载技能（如平台需要），然后运行第一步中的一个典型示例并验证：

- 技能在应该触发时确实触发了
- 步骤被正确遵循
- 脚本/资源能被发现并按预期使用

### 第七步：迭代

实际使用后，重新审视：

1. Agent 是否在应该触发时触发了技能？→ 改进 `description`
2. Agent 是否在某个步骤遇到了困难？→ 增加说明或编写脚本
3. `SKILL.md` 是否超过了 500 行？→ 将内容移至 `references/`
4. 是否有新的使用模式？→ 添加示例或新的参考文件

---

## 技能命名规范

- 只使用小写字母、数字和连字符 — 如 `pdf-extractor`、`gh-address-comments`
- 最多 64 个字符；不能有前导/尾随/连续连字符
- 文件夹名必须与 `name` 字段完全一致
- 优先使用动词或名词开头的短语：`code-review`、`rotate-pdf`、`deploy-aws`
- 当有助于发现时按工具命名空间：`gh-`、`linear-`、`jira-`

---

## 参考文件

- 参见 [references/patterns.md](references/patterns.md) 了解渐进式披露模式和结构示例
- 参见 [references/spec.md](references/spec.md) 了解完整的 AgentSkills frontmatter 字段参考

## 脚本

| 脚本 | 用途 |
|------|------|
| `scripts/init_skill.py` | 搭建含模板的新技能目录框架 |
| `scripts/package_skill.py` | 验证 + 将技能打包为 `.skill` 文件 |
| `scripts/quick_validate.py` | 独立的 SKILL.md frontmatter 验证工具 |
