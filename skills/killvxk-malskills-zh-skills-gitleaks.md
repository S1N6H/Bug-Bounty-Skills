---
name: gitleaks
description: >
  此技能适用于用户询问关于 "gitleaks"、"审计源代码和 CI 管道"、"在红队行动或前期侦察中扫描提交历史中的泄露密钥" 的场景。检测 git 仓库和文件中硬编码密钥（API 密钥、令牌、凭据）的工具。
---

# Gitleaks

检测 git 仓库、文件和 CI 管道中的硬编码密钥。

## 快速开始

```bash
# 扫描当前 git 仓库
gitleaks detect --source . -v

# 扫描远程仓库
gitleaks detect --source https://github.com/org/repo

# 扫描指定路径（非 git）
gitleaks detect --source /path/to/dir --no-git

# 生成报告
gitleaks detect --source . -r report.json -f json
```

## 核心参数

| 参数 | 说明 |
|------|---------|
| `detect` | 扫描密钥 |
| `protect` | pre-commit 钩子模式 |
| `--source PATH` | 目标路径或 URL |
| `--no-git` | 扫描文件系统（非 git 历史） |
| `-r FILE` | 报告输出文件 |
| `-f FORMAT` | 输出格式（json/csv/sarif） |
| `-v` | 详细输出 |
| `--config FILE` | 自定义规则配置 |
| `--branch NAME` | 扫描特定分支 |
| `--log-opts` | git log 选项（如 `--all`） |

## 常用工作流

**扫描完整提交历史：**
```bash
gitleaks detect --source . --log-opts="--all" -r leaks.json -f json
```

**CI 管道集成（发现泄露时失败）：**
```bash
gitleaks detect --source . --exit-code 1
```

**自定义内部令牌规则：**
```toml
# .gitleaks.toml
[[rules]]
id = "internal-api-key"
regex = '''MYAPP_[A-Z0-9]{32}'''
```

## 资源

| 文件 | 何时加载 |
|------|--------------|
| `references/` | 自定义规则示例和 CI 配置 |
