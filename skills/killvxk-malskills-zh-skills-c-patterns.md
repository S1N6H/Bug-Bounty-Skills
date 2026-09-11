---
name: c-patterns
description: >
  此技能适用于用户询问关于 "c-patterns"、"编写"、"审查 C 代码（C11+）以及设计具有明确资源生命周期的底层模块" 等内容。C 语言安全编程模式与最佳实践：所有权管理、错误处理、整型安全和 API 设计。
---

# C Patterns

本技能聚焦于**安全 C 编程**：显式所有权、显式错误处理和可预测的控制流。

如需编写测试，请使用 `c-testing`。

## 适用场景

- 编写/重构 C 模块和 API
- 审查内存安全性和整型安全性
- 设计错误处理约定和资源清理路径

---

## 核心规则（高价值）

- 使所有权显式化：在同一抽象层级进行分配和释放。
- 使用一致的错误处理策略（返回码、输出参数）并加以文档化。
- 尽可能避免带内错误指示符 (in-band error indicators)。
- 对管理多个资源的函数使用单一出口的清理路径。
- 将整型转换和大小计算视为潜在的 bug。

---

## 资源

按需加载：

- `references/error-handling.md` — 错误策略、返回码、清理模式
- `references/memory-ownership.md` — 分配/释放规则、零长度分配、free-null 处理
- `references/integers.md` — 溢出、size_t 用法、边界检查
- `references/concurrency.md` — pthreads、C11 原子操作、Win32 线程、竞态检测
- `references/tooling.md` — 警告、sanitizer、静态分析、二进制检查（MinGW/objdump、MSVC/dumpbin、Linux 工具）
