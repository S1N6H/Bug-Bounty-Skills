---
name: maltego
description: >
  此技能适用于用户询问关于 "maltego"、"在侦察阶段构建实体关系图"、
  "威胁情报收集"、"可视化 OSINT 链接分析" 的问题。
---

# Maltego

可视化 OSINT (开源情报) 与链接分析 — 针对人员、域名、IP、组织的实体图谱映射。

## 快速开始

1. 从 maltego.com 下载 → 注册社区版（免费）
2. 启动 Maltego → 新建图谱
3. 从面板拖入实体（例如 Domain）
4. 输入目标域名 → 运行全部变换

## 关键实体类型

| 实体 | 可用变换 |
|--------|-----------|
| Domain | DNS、WHOIS、子域名、MX、NS |
| IP Address | 地理位置、反向 DNS、网段、Shodan |
| Person | 社交账号、邮箱、电话 |
| Organization | 人员、域名、证书 |
| Email | 泄露记录、社交账号（Holehe） |
| Website | 技术指纹、链接 |

## 常用变换

| 变换 | 用途 |
|-----------|---------|
| `To DNS Name` | 子域名枚举 |
| `To IP Address` | 解析域名 |
| `To Website` | 枚举 Web 存在 |
| `To Email Address` | 查找邮箱 |
| `To Social Accounts` | 映射社交媒体 |
| `Shodan Search` | 枚举开放端口 |

## 常见工作流

**域名侦察：**
1. 添加 Domain 实体 → target.com
2. 运行：`DNS Name – To DNS Name [MX/NS/A]`
3. 运行：`Domain – To Website`
4. 运行：`IP – To Shodan`

**人员 OSINT：**
1. 添加 Person 实体 → 全名
2. 运行：`Person – To Email`
3. 运行：`Email – To Social Accounts`

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | 自定义变换和 API 集成说明 |
