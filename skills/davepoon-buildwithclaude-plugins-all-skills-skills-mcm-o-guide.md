---
name: mcm-o-guide
category: research
description: MCM/ICM 优秀论文写作全流程指南——基于 502 篇历年获奖论文（2004–2024）语料库的结构化分析与评委点评提炼。覆盖：摘要逐句模板、6 类题型模型选择矩阵、25 页页预算分配、图表黄金法则、灵敏度/稳健性分析范式、全文一致性检查清单。当用户准备美赛、写论文、打磨论文、查结构、选模型、做摘要、看评委标准、读优秀论文时使用。也适用于任何需要高质量数学建模论文写作的场景。
---

# MCM/ICM 优秀论文写作全流程指南

> **简体中文** · [English](SKILL.en.md)

> 本技能基于 502 篇 MCM/ICM 获奖论文（含 Outstanding / Finalist / Meritorious）的
> 语料统计与逐篇精读，以及 3 篇官方评委点评（2009 A/B、2021 Tips）提炼。
> 核心目标：帮助队伍在 4 天内产出"评委愿意读到第 25 页"的论文。

## 0 快速启动

```
输入: 题目编号（A-F）、6 个子问题原文、附件数据
输出: 论文骨架（含页预算）+ 摘要草稿 + 模型清单 + 图表规划表
```

第一步永远做：**题目拆解 → 模型选择矩阵 → 页预算表**。详见 [references/model-matrix.md](references/model-matrix.md)。

---

## 1 评委视角：三轮淘汰机制

MCM 评审分三轮，论文必须依次过关：

| 轮次 | 时长/论文 | 核心关注 | 淘汰原因 TOP 3 |
|---|---|---|---|
| **初筛** | <5 min | 摘要是否完整 + 全文可读性 | 摘要无数字结论 / 语法混乱 / 无 Summary |
| **筛选** | 15–30 min | 全文一致性 + 模型合理性 + 灵敏度 | 假设与模型脱节 / 无灵敏度 / 图表无解读 |
| **终评** | 1–2 h | 创新深度 + 结果可信度 + 写作质量 | 结论无量化支撑 / 图表与正文不一致 / 无局限讨论 |

> 评委原话（2009 A）：*"It is absolutely essential that a paper be well written and have a clear, concise summary to make it past the initial round."*

**策略：第一轮看摘要，第二轮看摘要与正文的一致性，第三轮看模型深度。摘要决定命运。**

---

## 2 摘要（Summary）——一页定生死

### 2.1 语料库统计基准

| 指标 | 中位数 | p25–p75 | Outstanding 偏好 |
|---|---|---|---|
| 摘要词数 | 437 | 350–520 | 400–500，20–35 个具体数字 |
| 含数字的句子 | ≥6 句 | 4–9 句 | 每个 task 至少 1 个量化结果 |
| 关键词 | 4–5 个 | 3–6 个 | 包含模型名称（如 GIID、CA、BDS） |

### 2.2 逐句模板（10 句黄金结构）

```
第1句:  背景痛点 + 本文目标命名（1 句）
第2句:  数据预处理/分类/参数估计（1–2 句）
第3-4句: Task 1: 模型名 + 方法链 + 核心结果（带数字）
第5-6句: Task 2: 方法 + 核心结果（带数字）
第7句:   Task 3: 方法 + 核心结果（带数字）
第8句:   Task 4/N: 方法 + 核心结果（带数字）
第9句:   灵敏度分析结论
第10句:  优势/局限/结论（1 句）
```

**2023 A O 奖摘要结构拆解（实例）：**

| 句 | 修辞动作 | 含数字 | 兑现位置 |
|---|---|---|---|
| 1 | 领域痛点 → 本文模型命名 (GIID) | 无 | Sec 3 |
| 2 | 数据预处理 | 5 species, 3 categories | Sec 2.3 |
| 3-4 | Task 1: LV 模型 → 验证结果 | "shown in Figure 7" | Sec 3.4 |
| 5-6 | Task 2: TV/CoV/SW/Pielou → 趋势 | "increases then decreases", "at least two" | Sec 4.1 |
| 7 | Task 3: 3 种组合对比 | "moderate differences" | Sec 4.2 |
| 8 | Task 4: 干旱频率/强度 | "complementary effect becomes stronger" | Sec 5.1 |
| 9 | Task 5-6: 栖息地/污染 → 保护措施 | — | Sec 5.2–5.3 |
| 10 | 灵敏度 + 优劣势 + 结论 | — | Sec 6–7 |

### 2.3 摘要写作避坑

| 坑 | 正确做法 |
|---|---|
| 大段背景铺垫 | 1–2 句引入，立即进入方法 |
| "The results are shown in Figure X" 却不写具体数字 | 必须写出关键数值（如 "CoV decreased by 58.5%"） |
| 只说模型名不说解决了什么 | "For Task 2, we calculated total biomass, CoV, S-W index to evaluate vigor, stability, evenness respectively" |
| 无关键词 | 4–5 个关键词，含模型名称 |

---

## 3 论文骨架与页预算

### 3.1 25 页黄金分配（2021–2024 O 奖中位数）

| 章节 | 页数 | 占比 | 功能 | 必须含 |
|---|---|---|---|---|
| 摘要 + 目录 | 1.5–2 | 8% | 评委第一印象 | 数字结论、方法链、关键词 |
| 引言（背景+复述+文献） | 2–3 | 10% | 展示理解力 | 问题复述、文献综述图 |
| 假设 + 符号 + 数据 | 2–3 | 10% | 建模合法性 | 假设+理由、参数来源表 |
| **核心模型 + 结果** | **10–13** | **45%** | 回答题目 | 公式、算法、图表、结论 |
| 灵敏度分析 | 1–2 | 6% | 模型可信度 | 参数扰动 + 结果变化 |
| 优劣势 + 结论 | 1–1.5 | 5% | 自我评估 | 至少 3 条优势 + 2 条局限 |
| 参考文献 + 附录 | 1–2 | 8% | 引用合规 | 正文引用一一对应 |
| Memo/Letter（如有要求） | 0.5–1 | 4% | 政策类题必备 | 按题目要求格式 |

### 3.2 图表配额

| 题型 | 中位数图 | 中位数表 | 中位数公式 | 中位数文献 |
|---|---|---|---|---|
| A（连续） | 12 | 3 | 8 | 10 |
| B（离散） | 8 | 2 | 1 | 10 |
| C（数据） | 10 | 5 | 6 | 8 |
| D（网络） | 10 | 3 | 9 | 11 |
| E（环境） | 8 | 4 | 16 | 12 |
| F（政策） | 11 | 3 | 6 | 12 |

**黄金法则：每 2 页至少 1 张图/表，每张图必须被正文显式解读。**

---

## 4 模型选择矩阵

详见 [references/model-matrix.md](references/model-matrix.md)。快速参考：

| 题目类型 | 首选模型族 | 辅助模型 | 验证方式 |
|---|---|---|---|
| A 连续/机理 | 微分方程/PDE/元胞自动机 | 优化 + 数值仿真 | 解析解对比 + 灵敏度 |
| B 离散/组合 | 图论/整数规划/马尔可夫 | 启发式算法 | 小规模精确解对比 |
| C 数据洞察 | ML（XGBoost/LSTM/CNN）+ 统计 | 特征工程 + 交叉验证 | 基准对比 + AUROC/RMSE |
| D 网络/运筹 | 网络流/社区检测/AHP/TOPSIS | 优化 + 仿真 | 情景对比 + 灵敏度 |
| E 环境评价 | 熵权/TOPSIS/AHP/综合指数 | 情景仿真 + 主成分 | 权重敏感性 + 交叉验证 |
| F 政策分析 | 博弈论/系统动力学/AHP | 情景分析 + 成本效益 | 情景压力测试 + 灵敏度 |

### 4.1 模型链设计原则

1. **每个子问题最多 2 个独立模型族**；同一物理机制不同近似阶次算一个模型族
2. **模型间必须耦合**：前一模型输出 = 后一模型输入，或共享参数/数据
3. **Baseline 必须有**：简单模型作为对照组，证明复杂模型的增量价值
4. **命名你的模型**：如 GIID、BDS — 评委喜欢可记忆的标签

---

## 5 假设与数据

### 5.1 假设写作模板（语料库 94%+ O 奖采用）

```
**Assumption N: [陈述]**
Justification: [文献/逻辑/简化理由]
Where used: [在哪个模型/公式中生效]
```

**关键规则：**
- 假设数量 4–7 条，每条必须有 justification
- 全局假设放 Sec 2，模型特定假设放对应模型小节
- **假设必须在正文中被引用**（"According to Assumption 2, ..."）
- 最后 Strengths/Weaknesses 中必须讨论假设的局限性

### 5.2 参数来源透明度

| 来源类型 | 写作方式 | 实例 |
|---|---|---|
| 文献直接引用 | "According to [7], parameter X = Y" | 生长率、死亡率 |
| 自行估算 | 给出估算公式 + 过程 | "r = ΔVolume / (Volume × 30 days)" |
| 经验设定 | 给出范围 + 合理性论证 | "α ∈ [0.01, 0.1], tested in sensitivity" |
| 拟合得到 | 说明拟合方法 + R²/残差 | "fitted by least squares, R² = 0.94" |

---

## 6 图表黄金法则

### 6.1 图表必须被正文解读

**错误写法：** "The results are shown in Figure 5."
**正确写法（2023 A O 奖实例）：**

> *"With results in both figures, we can identify several remarkable phenomena:*
> *• The biomass of both plants are influenced by the periodic weather change...*
> *• During the recovery process of the drought, the H.nepalensis recovers relatively quickly..."*

### 6.2 图表类型匹配

| 证明目标 | 推荐图型 | 数量要求 |
|---|---|---|
| 模型验证（与数据/解析解对比） | 折线叠加图 | 至少 1 张 |
| 参数敏感性 | 多折线/热力图（3–5 组参数） | 至少 1 组（3 张） |
| 任务结论（数值对比） | 柱状图/箱线图 + 数值标注 | 每 task ≥ 1 张 |
| 模型框架/工作流程 | 流程图/思维导图 | 至少 1 张 |
| 数据探索/分布 | 散点/地图/直方图 | C/D/E 题各 ≥ 1 张 |
| 情景对比 | 多图并列（baseline vs 本文） | 至少 1 组（2–3 张） |

### 6.3 图表清单（必须在论文中）

每张图/表必须有：编号 + 标题 + 正文中引用 + 解读段落。
语料库统计：O 奖论文中位数 14 图（2021+），Meritorious 仅 6 图。

---

## 7 灵敏度分析——拿 O 的门票

### 7.1 语料库数据

| 指标 | 2014–2016 | 2021–2024 |
|---|---|---|
| 有灵敏度分析 | 58–68% | 82–93% |
| 有稳健性/验证 | 11–42% | 32–49% |
| 有优劣势讨论 | 50–73% | 62–84% |

> 评委原话：*"Every year the judges explicitly discuss the issue of sensitivity and stability. The few teams that make a concerted effort to explore this aspect of their model will almost always stand out."*

### 7.2 灵敏度分析范式

**范式 A：单参数扫描（最常用）**
```
选定 3–5 个关键参数 → 每个参数取 3–5 个值（基准值 ±20%, ±40%）
→ 重跑模型 → 输出对比图 → 结论句："The model is sensitive/robust to X"
```

**范式 B：多情景压力测试**
```
基准情景 → 恶劣情景（×2 压力） → 极端情景（×5 压力）
→ 对比关键指标变化率
```

**范式 C：初始条件扰动 + 置信区间（高级，C 题常见）**
```
扰动初始分布/参数 N 次 → 计算 KL 散度/置信区间
→ 结论："The model is insensitive to reasonable perturbations"
```

**必须包含：**
- 扫哪些参数 + 为什么选这些
- 扰动范围 + 依据
- 呈现方式（图 + 表）
- **结论句**："模型对 X 敏感/稳健，因此在实际应用中需要准确测量 X"

---

## 8 全文一致性检查清单

评委最看重的品质之一。在提交前逐项检查：

### 8.1 假设一致性
- [ ] 摘要中提到的假设，正文中是否存在且一致
- [ ] 模型中使用的假设，假设列表中是否全部列出
- [ ] Strengths/Weaknesses 中讨论的局限，是否对应到具体假设

### 8.2 数字一致性
- [ ] 摘要中的数字结论，正文结果部分是否完全一致
- [ ] 图表中的数值与正文中引用的数值是否一致
- [ ] 符号表中的符号定义与公式中使用的是否一致

### 8.3 结构一致性
- [ ] 目录中的章节与正文实际章节标题完全一致
- [ ] 图表编号连续且正文中引用正确
- [ ] 参考文献在正文中全部被引用，无"孤儿引用"

### 8.4 任务覆盖一致性
- [ ] 每个子问题都有明确的"Answer to Task N"段落
- [ ] 无遗漏的子问题（评委直接淘汰遗漏）
- [ ] Memo/Letter（如有要求）是否按题目格式独立成节

---

## 9 论文手写作 Checkpoint

### 阶段 1：骨架搭建（拿到题目后 1–2 小时）
1. [ ] 逐句拆解 6 个子问题，写成 checklist
2. [ ] 填写模型选择矩阵（见 Sec 4）
3. [ ] 画出页预算表（见 Sec 3）
4. [ ] 写出摘要草稿（只写框架，留数字空白）

### 阶段 2：模型落地（编程手出结果后）
1. [ ] 每个 task 至少 1 张结论图 + 1 段解读
2. [ ] 参数来源表完成
3. [ ] 假设 + justification 完成
4. [ ] 摘要填入具体数字

### 阶段 3：验证与打磨（提交前 6–8 小时）
1. [ ] 灵敏度分析完成（至少 3 个参数 × 3 个值）
2. [ ] 全文一致性检查（Sec 8 清单）
3. [ ] Strengths ≥ 3 条 + Weaknesses ≥ 2 条
4. [ ] 参考文献格式统一，正文引用一一对应
5. [ ] 摘要最终审查：是否包含方法名、每个 task 的量化结论、关键词

### 阶段 4：合规审查（提交前 1 小时）
1. [ ] 页数 ≤ 25（含摘要/目录/附录/参考文献）
2. [ ] 每页页眉含队号 + 页码
3. [ ] 无队名、校名、队员姓名
4. [ ] PDF < 17MB
5. [ ] 文件名 = 队号.pdf
6. [ ] AI 使用报告（如使用了 AI 工具）

---

## 10 常见致命错误

| 错误 | 淘汰轮次 | 发生率（所有参赛队） |
|---|---|---|
| 摘要无具体数字结论 | 初筛 | ~40% |
| 遗漏子问题 | 筛选 | ~25% |
| 图表无正文解读 | 筛选 | ~30% |
| 无灵敏度分析 | 筛选 | ~35% |
| 假设与模型脱节 | 终评 | ~20% |
| 参考文献格式混乱 | 终评 | ~15% |
| 全文不一致（摘要/正文数字不符） | 终评 | ~10% |

---

## 11 进阶：从 Meritorious 到 Outstanding 的差距

基于语料库对比分析，O 奖与 M 奖的关键差距：

| 维度 | Meritorious | Outstanding |
|---|---|---|
| 摘要数字密度 | 10–15 个 | 20–35 个 |
| 图表被解读率 | 60–70% | 90%+ |
| 模型耦合深度 | 模型独立，结果拼凑 | 模型间有数据/参数流 |
| 基线对比 | 无或简单对比 | 有 baseline + 量化改进幅度 |
| 灵敏度深度 | 扫 1–2 个参数 | 扫 3–5 个 + 多情景 + 结论句 |
| 局限性诚实度 | 泛泛而谈 | 具体到假设/参数/模型局限 + 改进方向 |
| 模型命名 | 无 | 有（如 GIID、BDS）|
| 流程图 | 可选 | 必有（Our Work / Model Framework）|

---

## 12 进阶模块

### 12.1 Strengths & Weaknesses 写作

详见 [references/strengths-weaknesses.md](references/strengths-weaknesses.md)

**核心要点：**
- Strengths ≥ 3 条，每条用 **做法 + 效果 + 为什么有效** 三段式
- Weaknesses ≥ 2 条，每条用 **局限 + 影响 + 改进方向** 三段式
- 90%+ 的 Weakness 必须有改进方向
- Strengths 中提到的假设必须与假设列表一致

**O 奖 Strengths 实例（2023 A）：**
```
• We described the mechanics of the interaction between plant and environment in detail.
  Instead of making the too crude assumption that plant growth rates are directly proportional
  to precipitation, we modeled the interaction by assuming different plants absorb water from
  the soil at different rates. This makes our model more realistic and more convincing.
```

### 12.2 Introduction 写作

详见 [references/introduction-guide.md](references/introduction-guide.md)

**核心要点：**
- Introduction 2–3 页，包含 4 个小节
- Problem Background：1 张图 + 1 个具体数字 + 1 句动机
- Restatement：逐条列出 6 个子问题（bullet points）
- Literature Review：文献综述图（3 类方法对比）
- Our Work：流程图 + 模型清单（3–5 条 bullet）

### 12.3 Memo / Letter 写作（F 题）

详见 [references/memo-letter.md](references/memo-letter.md)

**核心要点：**
- Memo/Letter 必须独立成节，放在参考文献之后
- 格式完整：TO / FROM / DATE / RE
- 建议 ≥ 3 条，每条必须有数据支撑（引用正文结果）
- 建议必须具体可操作（地点/时间/行动/效果）
- 签名用 "Team #[队号]"，无个人信息

### 12.4 模型创新策略

详见 [references/model-innovation.md](references/model-innovation.md)

**六种创新策略：**
1. **机制耦合创新**：将两个模型的输出/输入耦合（如 2023 A 的种群-环境耦合）
2. **多尺度创新**：在不同时间/空间尺度建立模型（如 2021 C 的微观-宏观耦合）
3. **指标构造创新**：为题目构造新指标（如 CoV、Shannon-Wiener Index）
4. **基线对比创新**：设计对照组，量化改进幅度（如 2024 A 的 with/without 对比）
5. **数据驱动创新**：用数据中发现的模式驱动模型（如 2021 C 用报告数据拟合人口）
6. **算法改进创新**：对经典算法针对性改进（如 2021 D 的 PageRank 反转）

**从 M 到 O 的创新差距：**
- Meritorious：2–3 个独立模型，无命名，隐含创新
- Outstanding：3–5 个耦合模型，有命名（如 GIID），显式创新声明

---

## 13 快速参考

### 13.1 摘要模板（可直接填空）

```
[背景] As [现象/问题] becomes [趋势/严重], [对象] faces [挑战].
To explore this phenomenon, we develop [模型名] model to [目标].

Before modeling, we [数据预处理: classified/estimated/collected].
Parameters are set based on [来源].

For Task 1: We established [模型名] based on [基础理论], incorporating
[关键创新]. The results show that [具体数值结论].

For Task 2: We calculated [指标1], [指标2], and [指标3] to evaluate
[维度]. Results indicate that [具体趋势/数值].

For Task 3: We compared [N] scenarios/combinations and found that
[具体结论带数值].

For Task 4: We varied [参数] and the results show [具体趋势].

Finally, sensitivity analysis on [参数名] confirms model stability.
We also discuss strengths, weaknesses and [结论/建议].

Keywords: [模型名], [关键词2], [关键词3], [关键词4]
```

### 13.2 关键句式库

| 场景 | 句式 |
|---|---|
| 引出模型 | "To simulate/predict/evaluate [X], we developed [模型名] based on [理论]" |
| 连接任务 | "For Task N, we [动作]. The results are shown in Figure/Table X." |
| 量化结论 | "The [指标] [increased/decreased] by [X]%, reaching [Y] under [条件]" |
| 对比结果 | "Compared with [baseline], our model achieves [X]% improvement in [指标]" |
| 灵敏度结论 | "When [参数] varies within [范围], the output changes by [X]%, indicating the model is [sensitive/robust] to [参数]" |
| 优势 | "We [做法], which makes the model more [realistic/convincing/accurate]" |
| 局限 | "We [简化], which may cause [偏差]. Future work could [改进方向]" |
| 假设 | "Assumption N: [陈述]. Justification: [理由]. This assumption is used in [模型/公式]" |

### 13.3 评委点评精华摘录

- *"The summary is the first thing that a judge will read. It is the first impression, and it imparts the expectations for the whole paper."* — 2009 A
- *"Teams that managed to maintain some level of consistency stood out from the entries."* — 2009 A
- *"The few teams that examined a range of values for the parameters in their models immediately caught the judges' attention."* — 2009 A
- *"The best papers not only list trustworthy resources but also document their use throughout the paper."* — 2009 B
- *"The summary should motivate the reader to read the paper. It must not merely restate the problem, but indicate how it was modeled and what conclusions were reached."* — 2009 B

---

## 资源文件

| 文件 | 用途 |
|---|---|
| [references/model-matrix.md](references/model-matrix.md) | 6 类题型的模型选择矩阵、基线推荐、验证方式 |
| [references/summary-template.md](references/summary-template.md) | 摘要逐句模板 + 5 篇 O 奖摘要完整拆解 |
| [references/checklist.md](references/checklist.md) | 全文一致性检查清单 + 提交前审查清单 |
| [references/judge-commentary.md](references/judge-commentary.md) | 3 篇官方评委点评全文 + 结构化提取 |
| [references/strengths-weaknesses.md](references/strengths-weaknesses.md) | Strengths/Weaknesses 写作模板 + O 奖实例 |
| [references/introduction-guide.md](references/introduction-guide.md) | Introduction 写作指南 + 4 小节模板 |
| [references/memo-letter.md](references/memo-letter.md) | Memo/Letter 格式模板 + F 题建议写作 |
| [references/model-innovation.md](references/model-innovation.md) | 6 种模型创新策略 + 从 M 到 O 的差距 |
| [references/end-to-end-case.md](references/end-to-end-case.md) | 端到端案例 A：2023 干旱（连续/机理） |
| [references/end-to-end-case-B.md](references/end-to-end-case-B.md) | 端到端案例 B：2022 水资源（离散/优化） |
| [references/end-to-end-case-C.md](references/end-to-end-case-C.md) | 端到端案例 C：2021 大黄蜂（数据洞察） |
| [references/end-to-end-case-DEF.md](references/end-to-end-case-DEF.md) | 端到端案例 D/E/F：网络/环境/政策（含六题全景对照表） |
| [references/page-by-page.md](references/page-by-page.md) | 25 页逐页解剖（以 2023 A O 奖为蓝本，每页做什么/放什么/评委看什么） |
| [references/advanced-techniques.md](references/advanced-techniques.md) | 高级技术手册：灵敏度 6 法 / 验证 6 法 / 可视化决策树 / 方程规范 / 六题技术组合拳 |
| [references/top-award-strategy.md](references/top-award-strategy.md) | 🏆 顶尖 O 奖策略：基于 502 篇真实语料的数据洞察（摘要数字/图表/灵敏度三大特征） |
| [references/top-paper-anatomy.md](references/top-paper-anatomy.md) | 🏆 顶尖 O 奖解剖：2022 C 比特币策略（117 数字，17 图，逐页拆解） |
| [playbooks/modeling-playbook.md](playbooks/modeling-playbook.md) | 🧮 建模手能力强化（问题拆解/假设制定/模型库/检验方法） |
| [playbooks/coding-playbook.md](playbooks/coding-playbook.md) | 💻 编程手能力强化（Python/Matlab/Lingo 模板 + 图表规范） |
| [playbooks/writing-playbook.md](playbooks/writing-playbook.md) | ✍️ 写作手能力强化（摘要优先/学术英文/排版规范） |
| [playbooks/research-playbook.md](playbooks/research-playbook.md) | 📚 资料检索能力强化（文献检索/数据集来源/研究思路） |
| [templates/latex-template.tex](templates/latex-template.tex) | 📄 可直接编译的 LaTeX 骨架模板（合规 25 页，含注释引导） |
| [templates/markdown-template.md](templates/markdown-template.md) | 📄 Markdown 版骨架（Pandoc 转 DOCX/PDF） |
| [templates/README.md](templates/README.md) | 模板使用说明 |
| [references/quick-reference-card.md](references/quick-reference-card.md) | ⚡ 快速参考卡（提交前 30 分钟必查） |
| [references/team-workflow.md](references/team-workflow.md) | 👥 团队工作流程指南（4 天赛制） |
| [references/self-evaluation.md](references/self-evaluation.md) | 📊 论文自评打分表（100 分制） |
| [references/sentence-patterns.md](references/sentence-patterns.md) | 📝 学术句式库（从 498 篇论文数据挖掘） |
| [references/common-errors.md](references/common-errors.md) | ❌ 常见错误示例库（反面教材） |
| [scripts/](scripts/) | 🔧 自动化脚本（PDF 提取 + 一致性检查 + 参数扫描 + 顶尖对标） |

---

*本技能基于 502 篇论文语料库（449 篇正文 ≥5 页的有效论文）和官方评委点评构建。
统计基准：2014–2024 年 Outstanding / Finalist / Meritorious 论文。
最后更新：2026-01.*
