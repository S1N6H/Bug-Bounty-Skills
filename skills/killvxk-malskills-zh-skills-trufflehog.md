---
name: trufflehog
description: >
  此技能适用于用户询问关于 "trufflehog"、"在大型代码库中搜寻密钥"、"侦察阶段扫描云存储"。使用熵分析和 700+ 检测器在 git 仓库、S3 存储桶、文件系统及 CI 系统中查找泄露凭据和密钥。
---

# TruffleHog

拥有 700+ 检测器的密钥扫描工具 —— 支持 git 历史、S3、GCS、文件系统及 CI 系统。

## 快速开始

```bash
# Docker 方式
docker run --rm trufflesecurity/trufflehog:latest git https://github.com/org/repo

# 二进制方式
trufflehog git https://github.com/org/repo --only-verified

# 本地仓库
trufflehog git file:///path/to/repo --only-verified

# S3 存储桶
trufflehog s3 --bucket=target-bucket
```

## 核心参数

| 参数 | 用途 |
|------|---------|
| `git <url>` | 扫描 git 仓库 |
| `s3` | 扫描 S3 存储桶 |
| `filesystem` | 扫描本地文件 |
| `--only-verified` | 仅显示已验证的密钥 |
| `--since-commit SHA` | 从指定 commit 开始扫描 |
| `--branch NAME` | 扫描指定分支 |
| `--json` | JSON 格式输出 |
| `--concurrency N` | 线程数 |
| `--include-detectors` | 限制检测器类型 |

## 常用工作流

**仅验证的密钥（适合 CI 集成）：**
```bash
trufflehog git https://github.com/org/repo --only-verified --json > secrets.json
```

**扫描内部 Monorepo 完整历史：**
```bash
trufflehog git file:///repos/monorepo --json --concurrency 8
```

**S3 审计：**
```bash
trufflehog s3 --bucket internal-assets --only-verified
```

## 参考资源

| 文件 | 何时加载 |
|------|--------------|
| `references/` | 检测器列表及自定义检测器配置 |
