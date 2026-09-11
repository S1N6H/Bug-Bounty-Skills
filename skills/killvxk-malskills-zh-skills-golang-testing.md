---
name: golang-testing
description: >
  此技能适用于用户询问关于"golang-testing"、"编写"、"审查 Go 测试以提升正确性、稳定性和可维护性"。Go 测试模式：单元测试、表驱动测试、子测试、测试辅助函数、mock/fake、基准测试、模糊测试和覆盖率。
---

# Go 测试 (Go Testing)

此技能关注编写**可靠**、**可读**且**有文档价值**的测试。

## 激活时机

- 为函数、包或 API 编写新测试
- 重构测试以提高清晰度并减少不稳定性
- 添加基准测试或模糊测试
- 在不刷指标的前提下提升覆盖率

---

## 核心规则（高价值）

- 优先使用**表驱动测试 (table-driven tests)**，提升覆盖度和可读性。
- 使用 **t.Helper()** 和 **t.Cleanup()** 使失败信息更具可操作性。
- 测试应是确定性的：除非不可避免，否则避免使用 `time.Sleep()`。
- 优先使用 **fake**（内存实现）而非重量级 mock。
- 仅在测试真正隔离时才使用 `t.Parallel()`。

---

## 代码审查快速清单

- 设置代码在断言循环外；共享可变状态最小化
- 子测试有有意义的名称（`t.Run("case", ...)`）
- 错误信息显示 got/want 及上下文
- 外部依赖是显式的（数据库、网络、时间）
- 基准测试在相关时报告分配（`b.ReportAllocs()`）

---

## 参考资源

按需加载：

- `references/unit-tests.md` — TDD 循环、表测试、子测试、并行子测试
- `references/helpers-fixtures.md` — 辅助函数、TempDir、Cleanup、testdata、golden files
- `references/mocking-fakes.md` — 依赖接口、fake vs mock、示例
- `references/http-testing.md` — httptest 模式和 JSON 断言
- `references/bench-fuzz.md` — 基准测试和模糊测试最佳实践
- `references/coverage-ci.md` — 覆盖率 profile、coverpkg 注意事项、CI 集成说明
- `references/commands.md` — go test 命令示例（race、timeout、count、patterns）
