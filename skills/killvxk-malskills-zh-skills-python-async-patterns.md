---
name: python-async-patterns
description: >
  此技能适用于用户询问关于 "python-async-patterns"、"实现并发网络/数据库工作流"、"async 服务" 等内容。使用 asyncio 和 async/await 构建非阻塞 I/O 的异步 Python 模式：任务编排、取消、超时、背压、限流及 sync/async 边界安全处理。
---

# Async Python 模式

本技能聚焦于 **asyncio 实用并发模式**，适用于 I/O 密集型场景。

## 激活时机

- 正在构建 async 服务/客户端（HTTP、数据库、消息队列、WebSocket）
- 需要带限制的并发（限流、信号量）
- 需要安全的取消与超时机制
- 怀疑存在事件循环阻塞（async 路径中调用了同步代码）

## 使用原则

- async 仅适用于 **I/O 密集型**工作负载。
- 永远不要阻塞事件循环（禁用 `time.sleep()`，禁止在 async 代码中调用同步 HTTP/DB）。
- 显式声明取消和超时。
- 限制并发数量；无限制的 `gather()` 可能将内存变成队列。

## 常用模式

### 有限制的并发扇出

- 使用 `asyncio.TaskGroup`（Python 3.11+）实现结构化并发。
- 使用信号量（semaphore）限制并发数。

### 超时

- 优先使用 `asyncio.timeout()`（3.11+）设置作用域超时。

### 取消

- 捕获 `asyncio.CancelledError` 仅用于清理资源，之后必须重新抛出。

### Sync/async 边界

- 通过 `asyncio.to_thread()` 将真正阻塞的工作卸载到线程。

## 资源

按需加载：

- `references/foundations.md` —— 事件循环、协程 vs 任务、TaskGroup vs gather
- `references/cancellation-timeouts.md` —— 取消语义与超时模式
- `references/backpressure-rate-limit.md` —— 队列、信号量、生产者/消费者、限流
- `references/sync-async-interop.md` —— to_thread、executor、避免隐藏阻塞
- `references/testing.md` —— 异步代码测试模式（pytest-asyncio）与不稳定性规避
