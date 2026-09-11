---
name: cpp-testing
description: >
  此技能适用于用户询问关于"cpp-testing"、"编写"、"修复 C++ 测试和测试基础设施"等问题。
  C++ 测试工作流，涵盖单元测试和集成测试：GoogleTest/GoogleMock、CMake/CTest 集成、
  诊断不稳定测试，以及运行 Sanitizer 和覆盖率以获取正确性信号。
---

# C++ 测试

编写和维护可靠 C++ 测试的高效工作流。

## 激活场景

- 添加新的单元测试、回归测试或集成测试
- 修复失败或不稳定的 C++ 测试
- 将 GoogleTest 与 CMake/CTest 集成
- 启用 Sanitizer 进行内存/未定义行为/竞态条件诊断

---

## 核心规则

- 测试必须是确定性的：不能通过 sleep 来同步。
- 状态验证优先使用 fake，交互验证使用 mock。
- 使用 `ASSERT_*` 检查前置条件，使用 `EXPECT_*` 检查附加断言。
- 保持单元测试快速；将集成测试单独标记。

---

## 参考资源

按需加载：

- `references/googletest-cmake.md` — FetchContent + CTest 发现（gtest_discover_tests）
- `references/test-design.md` — 单元测试 vs 集成测试、测试夹具、参数化测试
- `references/sanitizers-coverage.md` — ASan/UBSan/TSan + 覆盖率配置
- `references/flakes-debugging.md` — 反不稳定规则、gdb/lldb、Valgrind、MinGW objdump/nm、MSVC dumpbin/WinDbg、Sanitizer 环境变量
