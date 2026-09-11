---
name: deep-research-generic
description: >
  此技能适用于用户询问关于"deep-research-generic"、"研究、调查"、"分析"、"总结某个主题"、
  "需要收集和交叉参考多个来源才能给出完整答案"、"输出必须包含引用和可信度评估"等问题。
  系统性多来源研究，包含引用、冲突分析和置信度评分。
---

# 深度研究——通用

适用于任何领域的系统性研究工作流。生成带有引用、结构化分析和明确置信度等级的研究报告。

## 流程

按顺序执行以下步骤。仅当某步骤明显不适用时才跳过。

### 1. 澄清

搜索前先消除歧义：
- 确切的问题或论点是什么？
- 需要什么深度和广度？
- 请求者期望什么格式？
- 是否有约束条件（日期范围、语言、地域）？

每次最多提出两个澄清性问题。如果请求已足够清晰，则直接进行。

### 2. 分解

将主题分解为 3–7 个子问题或维度。对每个维度：
- 明确命名
- 陈述它所回答的关键问题
- 估计优先级（高 / 中 / 低）

### 3. 来源与搜索

对每个子问题收集证据：
- 使用可用的网络搜索/检索工具
- 优先使用一手来源：同行评审论文、官方报告、原始数据
- 接受二手来源（高质量新闻报道、专家评论），但需明确标注
- 记录每个来源的 URL、标题、日期、作者/机构

**来源等级（用于引用）：**
| 等级 | 示例 | 默认可信度 |
|---|---|---|
| 1 | 同行评审期刊、官方统计数据 | 高 |
| 2 | 政府/NGO 报告、行业标准 | 高 |
| 3 | 知名新闻媒体、专家访谈 | 中 |
| 4 | 博客、论坛、未经核实的说法 | 低——需独立核实 |

### 4. 综合

收集完成后：
- 识别模式和反复出现的主题
- 记录明确的共识和明确的分歧
- 为每个主要发现分配置信度：`高` / `中` / `低`
- 如果来源相互矛盾，陈述双方立场并解释冲突

### 5. 输出

使用以下结构（根据需要调整章节）：

```
## Executive Summary（执行摘要）
[2–3 句话。主要结论 + 置信度。]

## Key Findings（关键发现）
- **[发现]**：[1 句话] — 置信度：高/中/低 [1]

## Detailed Analysis（详细分析）

### [维度 1]
[带内联引用的分析。]

### [维度 2]
...

## Consensus（共识）
[来源达成共识的内容。]

## Conflicts and Uncertainty（冲突与不确定性）
[来源分歧或数据缺失之处。需明确说明。]

## Sources（来源）
[1] 作者, "标题", 媒体, 日期 — 等级 1 / 可信度说明
[2] ...

## Gaps and Follow-up Questions（空白与后续问题）
[本次研究未回答的内容。建议的后续查询。]
```

## 使用 MCP 工具进行网络搜索

当网络搜索工具可用时，使用以下模式：

### 工具选择
| 目标 | 工具 |
|---|---|
| 广泛关键词搜索（任意主题） | `mcp_io_github_tav_tavily_search` |
| 从已知 URL 获取完整页面内容 | `mcp_firecrawl_fir_firecrawl_scrape` |
| 从已知 URL 提取结构化数据字段 | `mcp_firecrawl_fir_firecrawl_extract` |
| JS 渲染页面（scrape 返回空结果） | `mcp_microsoft_pla_browser_run_code` |

### Tavily 查询模式

```
# Discovery sweep  — run all sub-questions in one parallel batch
search_depth: basic      # 1 credit; sufficient for general research
max_results: 5           # default; increase to 10 only for broad sweeps
topic: general           # default; use "news" for current events (adds published_date)
time_range: year         # restrict to recent content when recency matters
include_domains: [...]   # pin to authoritative sources (gov, edu, official org)

# Precise fact extraction  — when you need a specific data point
search_depth: advanced   # 2 credits; returns ranked content chunks
chunks_per_source: 3     # include up to 3 chunks per result (advanced only)
max_results: 5
```

**规则：**
- 每个查询最多 400 个字符；超过则拆分为两个查询
- 每个查询一个主题；并行运行独立子问题（非串行）
- 使用 `include_domains` 而非在查询字符串中使用 `site:`
- 在获取完整内容前过滤 `score > 0.7` 的结果
- 获取完整页面内容：搜索 → 找到 URL → Firecrawl scrape（两步，优于 `include_raw_content: true`）

## 质量规则

- 每个事实性声明必须有引用
- 不得伪造来源——如果找不到，明确说明"未找到"
- 区分"无证据"和"有证据证明不存在"
- 将超过 2 年的信息标记为可能过时
- 不进行评论；呈现分析，而非倡导立场

## 深度等级

根据用户意图调整：

| 等级 | 描述 | 长度 |
|---|---|---|
| 快速 | 3–5 个发现，最少细节 | 300–500 字 |
| 标准 | 完整上述工作流 | 800–1500 字 |
| 深度 | 多轮搜索，每个维度进行子研究 | 2000+ 字 |

默认为**标准**，除非用户另行指定或主题较为简单。
