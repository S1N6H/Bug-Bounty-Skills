---
name: agent-md-creator
description: >
  此技能适用于用户询问关于 "agent-md-creator"、"初始化 AGENTS.md、将特定工具指令文件替换为共享开放格式、压缩过于冗长的 Agent 指令、为 Agent 记录构建/测试命令"、"为单体仓库和子项目设计最简项目指令" 等内容。创建、更新或重构仓库根目录及嵌套目录中供 AI 编码 Agent 使用的 AGENTS.md 文件。
---

# Agent MD Creator

创建技术性、高 token 效率的 `AGENTS.md` 文件，帮助编码 Agent 立即投入工作，同时不臃肿上下文。将 `AGENTS.md` 视为持续演进的操作文件：它应随代码库、已发现的工作流程、当前工具可用性以及真实团队实践而不断更新。优先采用简洁、以事实为依据的指令，而非泛泛的提示语。

## 工作流程

### 1. 发现项目真实结构

起草任何内容之前：

- 搜索已有的指令文件：`AGENTS.md`、`AGENT.md`、`.github/copilot-instructions.md`、`CLAUDE.md`、`.cursorrules`、README 文件以及 CI 工作流。
- 从仓库实际文件中获取构建/测试/lint 命令，而非猜测。
- 识别技术栈、包管理器、子项目、测试框架以及 Agent 可能需要编辑的目录。
- 若为单体仓库 (monorepo)，决定是使用一个根文件还是需要嵌套 `AGENTS.md` 文件。

若需要结构、优先级或章节指导，请加载 [references/agents-md-principles.md](references/agents-md-principles.md)。
若需要来自 2,500+ 个仓库分析得出的 2025 年 GitHub 专项经验，请加载 [references/github-lessons.md](references/github-lessons.md)。

### 2. 选择最小可用范围

默认使用单个根目录 `AGENTS.md`。

仅当满足以下至少一项条件时，才添加嵌套 `AGENTS.md` 文件：

- 子项目使用不同的技术栈或命令
- 前后端/基础设施有各自不同的工作流程
- 根文件会变得冗长或充满例外情况
- 某个子目录需要比其余部分更严格的边界约束

保持指令的局部性：最近的 `AGENTS.md` 只应包含与该子树相关的细节。

### 3. 起草最简化、技术性的 AGENTS.md

仅使用有仓库证据支撑的章节。推荐顺序：

1. Agent 可运行的命令
2. 当前用户决策 / 工作流程选择
3. 测试 / 验证预期
4. 调试预期（有需要时）
5. 项目结构或关键路径
6. 非显而易见的代码风格或架构规则
7. 边界 / 审批规则
8. 可选：已接受的诊断信息或 PR / 提交规则

使用简短条目、具体路径和精确命令。优先选用如下形式：

- `pytest tests/api/test_users.py -q`
- `npm run lint`
- `src/api/` 包含 HTTP 处理器
- `代码注释须技术性、精确，并以英文书写；解释原因或意图，而非显而易见的语法`
- `为 tests/api/ 中行为变更的代码添加或更新测试`
- `若调试在 2–3 次失败迭代后仍无进展，在进行在线调研前先询问用户`
- `需要在线调研时使用 Tavily`
- `在切换工具之前先用 objdump 进行二进制检查`
- `除非用户重新提出，否则忽略 src/ui/App.tsx 中已有的警告`
- `go vet ./... # injection/ 目录中有一处已存在的 unsafe.Pointer 警告 — 不要修复`
- `在修改 evasion/ 或 injection/ 后重新生成资源 blob：bash scripts/gen.sh`

对于 `## Project structure`，停留在**目录层级**，除非某个具体文件在操作上确实至关重要。描述每个目录包含或应包含的内容。**不要**罗列冗长的文件清单。对于会引起混淆的生成文件，在行内标注（例如 `resources.enc ⚡ GENERATED — do not edit`）。当某个子目录有其专属规则时，写 `See <path>/AGENTS.md`，保持根文件精简，而非重复内容。

避免以下情况：

- "使用最佳实践"
- "注意代码质量"
- 重复 README 的长篇叙述
- 接口定义、配置结构体、流水线说明或行为深度解析 — 这些应放入 `README.md` 或参考文件
- 罗列仓库中每个文件的巨大 `Project structure` 章节

若用户请求从零开始生成模板文件，以 [assets/minimal-agents-template.md](assets/minimal-agents-template.md) 为基础，然后用仓库实际信息替换所有占位符。

### 3a. 明确记录用户当前决策

当用户在对话过程中声明操作上的选择时，若文件尚无相应章节，应在一个**独立的专属章节**中捕记这些内容。

典型示例：

- 首选在线调研工具，如 Tavily
- 首选本地分析工具，如 `objdump`、`readelf`、`pytest`、`dlv` 或特定平台调试器
- 明确的工作流程偏好，如 "优先使用本地工具" 或 "在进行网络调研前先询问"
- 当前有效的临时项目选择，用于在多次会话中保持行为一致性

推荐的章节名称：

- `## Active user decisions`
- `## Working agreements`
- `## Current tool choices`

将这些决策表述为**当前有效但可修改**的状态。文件应明确表示它们可以随时修改或撤销，而无需改写其他指导内容。

### 3b. 将测试视为变更的一部分

当项目有测试套件或测试约定时，在 `AGENTS.md` 中明确说明：

- Agent 应为其修改的行为添加或更新测试
- Agent 应优先运行最小相关测试命令，若有需要再进行更广泛的验证
- 若仓库没有有意义的自动化测试，文件应说明预期的替代验证方式

不要对那些有意不包含测试、测试在别处生成或不适合该项目类型的仓库盲目承诺创建测试。

### 3c. 将调试视为证据收集工作流程

若仓库经常需要调试，在 `AGENTS.md` 中以简短的操作性条目编码该工作流程：

- 优先使用可用的本地工具：测试、linter、类型检查器、日志、调试器、跟踪输出、复现脚本、性能分析器或已有项目诊断工具
- 当本地工具缺失时，若这是获取清晰答案的最快方式，可用 Python 或项目语言创建小型临时调试辅助工具或脚本
- 优先选用能产生具体证据的工具，而非猜测
- 在同一未解决问题上经历 **2–3 次失败迭代**后，应主动上报，而非盲目重试
- 若需要外部或在线调研，Agent 在使用前应先与用户确认，除非仓库已明确允许该工作流程

### 3d. 记录已接受的诊断信息和有意忽略的 UI 问题

若用户明确表示某条警告、lint 问题或 UI 诊断**不应被修改**，应将其存储在专属章节中，而不是让 Agent 反复重新发现。

良好示例：

- `## Accepted diagnostics`
- `## Known ignored warnings`
- `## Deferred issues`

每条记录应简短且有范围限定：

- 文件或路径范围
- 错误 / 警告摘要
- 是否为有意忽略、推迟处理或超出范围
- 可选：重新审视的条件

这有助于 Agent 避免反复分析同一已接受的警告，并跨会话保持工作流顺畅。

### 4. 为 token 成本优化

默认目标是一个简短的文件，让 Agent 能频繁加载而不浪费上下文。

- 对大多数仓库，目标 **30–120 行**。
- 只保留能改变 Agent 行为的高价值指令。
- 将可执行命令放在前面。
- 一个真实示例优于多条抽象规则。
- 不要重复文件名中已显而易见的内容，除非能节省反复查找的时间。
- 不要记录面向人类的产品历史、动机或入门说明。
- 不要仅仅为了匹配模板而添加章节。
- 保持测试和调试指导简洁且可操作；避免泛泛的质量口号。
- 保持用户声明的决策和已接受的诊断信息简洁、有范围限定且易于修改。

在收紧草稿或审查已有冗长文件时，加载 [references/optimization-checklist.md](references/optimization-checklist.md)。
需要关于命令顺序、示例、边界以及六个高价值章节的具体指导时，使用 [references/github-lessons.md](references/github-lessons.md)。

### 5. 谨慎合并或重构已有文件

当指令文件已存在时：

- 保留已验证的命令、边界约束、仓库特有的注意事项、真实的测试/调试工作流程、当前有效的用户决策以及仍然适用的已接受诊断信息
- 删除过时的命令、重复的解释和泛泛的填充内容
- 仅当用户有明确要求或重复内容明显有害时，才合并重叠的文件
- 当目标是可移植、工具无关的格式时，将结果保存为 `AGENTS.md`
- 当重要的仓库变更、已发现的工作流程或工具可用性影响 Agent 工作方式时，更新 `AGENTS.md`

从工具专属文件迁移时，保持兼容性说明简短，并优先维持单一可信来源。

### 6. 完成前进行验证

检查最终的 `AGENTS.md`：

- 使用仓库中存在的命令
- 引用真实的目录和文件名
- 当用户声明的工具或工作流程选择影响持续行为时，在专属章节中记录
- 当用户要求忽略或推迟某些诊断信息时，在对应章节中记录
- `Project structure` 聚焦于目录和高价值路径，而非详尽的文件清单
- 当测试/调试预期对 Agent 工作方式有实质影响时，明确说明
- 只包含与 Agent 行为相关的指令
- 足够简洁，可频繁加载
- 不遗留占位符、TODO 或虚假示例
- 将面向开发者的细节移至 `README.md` 或参考文件，而非保留在 `AGENTS.md` 中
- 在重要仓库变更后及时刷新，避免与现实脱节

## 起草规则

- 精确、技术性、最简化。
- 使用祈使句。
- 优先使用条目而非段落。
- 优先引用仓库事实而非泛泛建议。
- 提及命令时带上 flag，以减少歧义。
- 将对话中形成的持久性决策放在明确的章节中，而非隐藏在对话历史里。
- 在 `Project structure` 中，优先列出目录及每个目录的简短说明。
- 在 `Testing` 中，说明行为变更是否必须添加或更新测试。
- 在 `Debugging` 中，优先给出简短的升级规则：先用本地工具，若多次尝试失败再进行用户批准的在线调研。
- 若用户不希望触碰某条警告或 lint 问题，明确记录并限定范围。
- 记录代码注释预期时，优先给出定性指导：注释应技术性、精确、使用英文且简洁。解释意图、不变量、边界情况或非显而易见的权衡 — 而非逐行的机械说明。
- 仅在能防止真实风险时才提及审批边界。
- 若无可靠命令，如实说明而非凭空捏造。
- 将 `AGENTS.md` 视为持续演进的操作文件：当项目发生变化、发现更好的工作流程或可用工具发生重大变化时，及时更新。
- 区分**Agent 指令**（做什么、如何验证、避免什么）和**开发者文档**（代码如何运作、接口定义、设计理由）。前者属于 `AGENTS.md`；后者默认属于 `README.md`，若内容过于详细则放入专属参考文件。若某个章节描述的是代码内部原理而非指导 Agent 行为，应移除或移至他处。
- 对于违反后果隐蔽但代价高昂的硬性技术约束（安全性、OPSEC、兼容性），优先使用 `禁止 → 替代方案` 的双列表格，而非散文式规则。
- 对于模块化或插件式架构，一个简短的编号式"如何添加新 X"指南（4–8 步）能有效防止结构性错误，且不会重复 README 内容。
- 单条已接受的诊断信息可以作为行内注释附在产生该信息的命令后，而无需为此单独创建一个章节。

## 常见章节模式

### 小型仓库

- `## Commands`
- `## Active user decisions`
- `## Testing`
- `## Debugging`
- `## Project structure`
- `## Accepted diagnostics`
- `## Boundaries`

### 单体仓库根目录

- `## Workspace commands`
- `## Working agreements`
- `## Package discovery tips`
- `## Testing strategy`
- `## Debugging strategy`
- `## Accepted diagnostics policy`
- `## Nested AGENTS.md policy`

### 专属子树

- `## Local commands`
- `## Local decisions`
- `## Local testing`
- `## Local debugging`
- `## Local accepted diagnostics`
- `## Files in scope`
- `## Local conventions`
- `## Do not touch`

### 硬性约束表格

对于使用某些模式会造成安全问题、OPSEC 风险或兼容性破坏的项目，以紧凑的双列表格（`禁止模式 → 安全替代方案`）记录。为每条约束配上明确的替代方案，让 Agent 有路可走。示例：

| 禁止 | 替代方案 |
|-----------|-------------|
| `crypto/rand` | `math/rand` seeded via `time.Now().UnixNano()` |
| `math/rand/v2` | `math/rand` (v1) for TinyGo compatibility |

将此放在专属章节（如 `## Hard constraints`）中，或在 `## Conventions` 下内联展示。

### `## Checklist for new code`

对于规则繁多且不易察觉的复杂项目，条目式清单比散文式约定更具可操作性 — 每一项都是 Agent 在完成前可以明确核查的内容。仅保留 Agent 实际可能遗漏的规则。适用于违反后难以在审查中发现且影响重大（安全、OPSEC、ABI 兼容性、命名约定）的情况。

### 注释指导

若仓库对源码注释有较强预期，在 `## Conventions` 或 `## Code style` 下用 1–3 条简短条目捕记。好的指导是定性的，而非定量的：注释应技术性、精确、以英文书写，用于表达意图、不变量、危险点或非显而易见的推理。避免鼓励为每行或每个函数都添加注释的规则。

### 扩展指南

对于模块化或插件式架构（接口 + `init()` 注册、策略模式、编码器栈），一个简短的编号式"如何添加新 X"章节（4–8 步）可防止 Agent 遗漏必要步骤。涵盖：文件放置、接口实现、自注册、flag 配置以及任何别名或构建更新。**不要**复制完整的接口规格 — 只需列出正确添加新实例所需的步骤。

## 资源

### references/

- [references/agents-md-principles.md](references/agents-md-principles.md) — 在决定结构、优先级、章节选择或迁移规则时加载。
- [references/optimization-checklist.md](references/optimization-checklist.md) — 在压缩草稿、检查质量或将模糊指令转化为简洁可操作条目时加载。
- [references/github-lessons.md](references/github-lessons.md) — 需要 GitHub 2025 年 11 月分析 2,500+ 个 `AGENTS.md` 文件所得出的可操作经验时加载。

### assets/

- `assets/minimal-agents-template.md` — 根目录 `AGENTS.md` 的最简起始模板；保存前须将每个占位符替换为仓库实际信息。
