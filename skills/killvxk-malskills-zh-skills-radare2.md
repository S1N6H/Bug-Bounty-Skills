---
name: radare2
description: >
  此技能适用于用户询问关于 "radare2"、"无头模式分析二进制文件、脚本化逆向工程任务、修补可执行文件"、"在资源受限环境中工作" 等内容。CLI 逆向工程框架，支持反汇编、调试、脚本化和二进制修补。
---

# Radare2

CLI 逆向工程框架 —— 反汇编、调试、修补和脚本化二进制分析。

## 快速开始

```bash
# 以只读方式打开二进制文件
r2 ./binary

# 全量分析（自动分析）
> aaa

# 列出函数
> afl

# 反汇编函数
> pdf @ main

# 打印字符串
> iz

# 退出
> q
```

## 核心命令

| 命令 | 用途 |
|------|------|
| `aaa` | 完整自动分析 |
| `afl` | 列出所有函数 |
| `pdf @ FUNC` | 反汇编函数 |
| `s ADDR` | 跳转到地址 |
| `iz` | 打印二进制中的字符串 |
| `iS` | 列出节区 |
| `ii` | 列出导入表 |
| `px N @ ADDR` | 在 ADDR 处 hex dump N 字节 |
| `ood` | 以调试模式重新打开 |
| `dc` | 继续执行 |
| `dr` | 显示寄存器 |
| `VV` | 可视化图形模式 |
| `/` | 搜索字节/字符串 |

## 常用工作流程

**快速静态分析：**
```
r2 malware.exe
> aaa; afl; iz; ii
> pdf @ sym.main
```

**修补跳转指令：**
```
r2 -w ./binary
> s 0x401234       # 跳转到指令地址
> wa jmp 0x401300  # 写入汇编
> q
```

**通过 r2pipe（Python）编写脚本：**
```python
import r2pipe
r2 = r2pipe.open('./binary')
r2.cmd('aaa')
print(r2.cmd('afl'))
```

## 资源

| 文件 | 加载时机 |
|------|----------|
| `references/` | r2pipe 脚本化与调试快捷键 |
