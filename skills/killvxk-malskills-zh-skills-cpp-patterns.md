---
name: cpp-patterns
description: >
  此技能适用于用户询问关于"cpp-patterns"、"编写"、"审查 C++（C++20+）代码"等问题。
  现代 C++ 模式与最佳实践，涵盖可读、安全、可维护的 C++ 代码：RAII、所有权、错误处理、
  API 设计、并发基础以及构建/工具链规范。
---

# C++ 模式

本技能适用于**日常现代 C++**：安全性、清晰性和可维护的 API。

如果专注于测试编写/工具链，请使用 `cpp-testing`。

## 激活场景

- 编写新的 C++ 模块/库/服务
- 审查 PR 中的所有权、生命周期和异常安全问题
- 重构以获得更简洁的接口和更少的陷阱
- 引入 RAII、智能指针和标准库算法

---

## 核心规则（高优先级）

- 优先使用 **RAII** 管理资源所有权；避免裸 `new`/`delete`。
- 默认使用**值类型**；使用引用/指针来表达可选性和非所有权语义。
- 使用 `std::unique_ptr` 表示独占所有权；仅在需要共享所有权时才使用 `std::shared_ptr`。
- 在能提高清晰度时，优先使用**标准算法**而非手写循环。
- 保持 API 精简；尽可能让无效状态无法被表示。
- 定义清晰的错误处理策略：异常 vs `std::expected` 风格返回值 vs 状态码。

---

## 快速审查清单

- 所有权是明确的（谁分配、谁释放）
- 无内存泄漏或悬空引用（临时对象、`string_view`、迭代器失效）
- 使用了零法则；仅在必要时定义特殊成员函数
- `const` 正确性保持一致
- 没有令人意外的隐式转换；使用 `explicit`
- 并发代码有取消/停止策略

---

## 参考资源

按需加载：

- `references/ownership-raii.md` — 所有权规则、RAII 模式、智能指针、生命周期
- `references/core-guidelines.md` — C++ 核心准则精华要点
- `references/api-design.md` — 接口设计、值语义、错误处理策略
- `references/concurrency.md` — jthread、mutex、atomic、condition_variable、stop_token、竞态检测
- `references/tooling-build.md` — 编译器警告、Sanitizer、静态分析、二进制检查（MinGW/objdump、MSVC/dumpbin、Linux 工具）、CMake 规范
