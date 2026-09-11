---
name: openvas
description: >
  此技能适用于用户询问关于 "openvas"、"对内网进行全面漏洞扫描"、"生成合规报告"、"在渗透测试前对已知 CVE 执行认证扫描" 等内容。OpenVAS (Greenbone Vulnerability Manager)：功能完整的开源漏洞扫描器，内置 60,000+ NVT。
---

# OpenVAS / Greenbone

开源综合漏洞扫描器。

## 快速开始

```bash
# Docker（最简方式）
docker run -d -p 9390:9390 -p 443:443 --name gvm greenbone/community-edition
# Web 界面：https://localhost（默认账号 admin/admin）

# Kali 原生安装
sudo gvm-setup && sudo gvm-start
# 界面：https://127.0.0.1:9392
```

## 常用工作流程（GUI）

1. **配置 → 目标**：添加主机 / CIDR 网段
2. **配置 → 扫描配置**：选择"Full and fast"
3. **扫描 → 任务 → 新建任务**：指定目标与配置
4. 启动任务，等待完成
5. **报告**：导出为 PDF / XML / HTML

## 扫描配置

| 配置 | 用途 |
|------|------|
| Full and fast | 全面扫描（默认） |
| Discovery | 仅网络发现 |
| System Discovery | 主机 / 服务枚举 |
| Host Discovery | 仅 Ping 扫描 |

## 资源

| 文件 | 加载时机 |
|------|----------|
| `references/` | CLI XML API、认证扫描配置 |
