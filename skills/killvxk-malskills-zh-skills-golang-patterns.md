---
name: golang-patterns
description: >
  此技能适用于用户询问关于 "golang-patterns"、"编写符合 Go 惯用法的代码"、"审查 Go PR 的最佳实践"、"重构 Go 错误处理、接口或并发" 的场景。用于构建健壮、可读、可维护 Go 代码的惯用模式、最佳实践和规范。
---

# Go 模式

本技能聚焦于**符合 Go 惯用法的设计和代码审查指导**。

如果你的任务主要是性能测量/分析/优化，请使用 `golang-performance`。

## 适用场景

- 编写新的 Go 代码（包、API、服务）
- 审查 PR 的惯用法、可读性和可维护性
- 重构以实现更简洁的错误处理和更小的接口
- 设计带有取消和背压的并发流程

---

## 核心原则（高价值）

- **gofmt 不可协商。** 风格争论以 `gofmt` 为准。
- 优先**清晰**：小函数、尽早返回、显式控制流。
- 使**零值有意义**。
- 保持**接口小巧**；在使用处定义接口。
- **显式处理错误**；用上下文包装；避免用 `panic` 控制流。
- 并发应**有界**且**可取消**；避免 goroutine 泄漏。

---

## 快速审查检查清单

- 命名：导出标识符用 MixedCaps，无下划线，包名简短小写
- 错误：`fmt.Errorf("context: %w", err)`，正确使用 `errors.Is/As`
- Context：`ctx` 作为第一个参数；取消信号向下传播；不在结构体中存储 `context.Context`
- 接口：接受接口，返回具体类型；不使用"大而全"的接口
- 并发：goroutine 有停止条件；channel 由发送方关闭；存在背压机制
- 工具链：`go test ./...`，`go test -race ./...`，`go vet ./...`

---

## 资源

按需加载（渐进式披露）：

- `references/effective-go.md` — 精简版 Effective Go + Code Review Comments 要点
- `references/errors.md` — 错误包装、哨兵错误 vs 类型化错误、校验、可重试错误
- `references/interfaces.md` — 接口放置位置、设计模式、可选行为
- `references/concurrency.md` — 取消、errgroup、泄漏、工作池、背压
- `references/api-and-structs.md` — 接收者规则、函数选项模式、嵌入
- `references/package-layout.md` — 项目布局、包命名、依赖注入
- `references/tooling.md` — gofmt/goimports、vet、staticcheck、golangci-lint 指导
