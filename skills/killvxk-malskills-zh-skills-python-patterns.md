---
name: python-patterns
description: >
  此技能适用于用户询问关于 "python-patterns"、"编写或审查 Python 代码和 API" 等内容。Python 惯用模式与最佳实践：类型注解、错误处理、数据建模、迭代、资源管理、项目布局及工具链。
---

# Python 模式

本技能面向 **日常 Python 代码质量**：可读性、正确性、可维护性。

如果正在进行大量 asyncio 工作，请优先使用 `python-async-patterns`，以获取结构化并发、取消和背压相关指导。

## 激活时机

- 编写 / 重构 Python 模块、库、服务
- 审查 PR 中的惯用写法、清晰度和常见陷阱
- 引入类型注解或改善错误处理
- 设计轻量级数据模型和 API

---

## 核心原则（高优先级）

- 可读性优于技巧性。
- 在边界处（I/O、解析、网络）保持显式；内部代码保持简洁。
- 优先使用小型、带类型的函数，并起清晰的名称。
- 使用上下文管理器保证资源安全。
- 抛出具体异常并保留异常链（`raise ... from e`）。

---

## 快速审查清单

- 无可变默认参数；使用 `None` 哨兵值
- 使用 `is None` / `is not None`（而非 `== None`）
- 具体的 `except` 子句；禁用裸 `except:`
- 类型注解：公共函数/类有注解；复杂类型使用别名
- 文件/路径操作使用 `pathlib.Path`（适用时）
- 迭代：仅在逻辑简单时使用推导式/生成器

---

## 资源

按需加载：

- `references/typing.md` —— 现代类型注解（3.11）、别名、Protocol、泛型
- `references/errors.md` —— 异常规范、自定义异常、异常链、边界处理
- `references/data-models.md` —— dataclass、NamedTuple、不可变性、校验
- `references/iteration.md` —— 推导式 vs 循环、生成器、itertools
- `references/resources.md` —— 上下文管理器、清理、临时文件
- `references/performance.md` —— 简单性能规则（避免过早优化）
- `references/layout-tooling.md` —— 项目布局、ruff/mypy/pytest 说明
