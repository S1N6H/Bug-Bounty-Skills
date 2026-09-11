---
name: scoutsuite
description: >
  此技能适用于用户询问关于"scoutsuite"、"评估云端错误配置"、"审查 IAM 策略、安全组、存储权限并生成审计报告"。多云安全审计工具，支持 AWS、Azure、GCP 等平台。
---

# ScoutSuite

多云安全审计工具 — 支持 AWS、Azure、GCP、OCI、阿里云。

## 快速开始

```bash
pip install scoutsuite

# AWS（使用默认 ~/.aws/credentials 配置文件）
scout aws

# Azure
scout azure --cli

# GCP
scout gcp --project PROJECT_ID

# 输出到指定目录
scout aws -r ./report-dir
```

## 常用参数

| 参数 | 用途 |
|------|------|
| `aws/azure/gcp/oci` | 云服务提供商 |
| `--profile NAME` | AWS 命名配置文件 |
| `--regions us-east-1` | 限定区域 |
| `--services s3,iam` | 限定服务 |
| `--skip-services ec2` | 跳过指定服务 |
| `-r DIR` | 输出目录 |
| `--no-browser` | 不自动打开 HTML 报告 |
| `--max-workers N` | 并发数量 |

## 常用工作流

**完整 AWS 审计：**
```bash
scout aws --profile pentest-account -r ./aws-report
```

**Azure 含多因素认证 (MFA)：**
```bash
az login
scout azure --cli -r ./azure-report
```

**打开 HTML 报告：**
```bash
# 报告会自动打开；或手动执行：
start ./aws-report/scoutsuite-report/index.html
```

## 资源文件

| 文件 | 加载时机 |
|------|----------|
| `references/` | 发现项分类与修复建议 |
