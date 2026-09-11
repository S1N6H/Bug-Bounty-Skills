---
name: shellcode-fluctuation
description: >
  此技能适用于用户询问关于"shellcode-fluctuation"、"植入程序在休眠期间被内存扫描 EDR 产品检测到"。C++ Shellcode 波动技术，在 C2 休眠间隔期间对注入的 Shellcode 进行加密，以规避 EDR 内存扫描。
---

# Shellcode Fluctuation

C++ 内存规避技术 — 在 C2 休眠期间对 RX 页面中的 Shellcode 进行 XOR 加密，以对抗内存扫描器。

## 快速开始

```bash
# 使用 MSVC 克隆并构建
git clone https://github.com/mgeeky/ShellcodeFluctuation
# 在 Visual Studio 中打开，构建 Release x64

# 或使用 MinGW
x86_64-w64-mingw32-g++ -O2 -o fluctuator.exe main.cpp -lntdll
```

## 核心机制

```
[内存中的 Shellcode]
  唤醒：→ 解密 → 执行 → 休眠
  休眠：→ 加密（XOR）→ 将内存保护改为 RW → 扫描器看到的是乱码
  唤醒：→ 将内存保护改回 RX → 解密 → 恢复执行
```

## 配置项 (main.cpp)

```cpp
#define SHELLCODE_FLUCTUATE   true
#define XOR_KEY               0xdeadbeef
#define SLEEP_INTERVAL_MS     5000
```

## 常用工作流

**集成到 Cobalt Strike BOF 加载器：**
1. 从 CS 监听器生成原始 Shellcode
2. 嵌入到 fluctuator 加载器源码中
3. 在 Sleep() 之前调用 `FluctuateShellcode()` 包装器

**结合间接系统调用 (indirect syscalls)：**
```cpp
// 用直接的 NtProtectVirtualMemory 系统调用存根替换 VirtualProtect
// 以绕过 API 钩子
```

## 资源文件

| 文件 | 加载时机 |
|------|----------|
| `references/` | 钩子规避与内存保护模式 |
