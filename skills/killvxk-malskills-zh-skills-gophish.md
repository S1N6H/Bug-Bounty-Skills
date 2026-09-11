---
name: gophish
description: >
  此技能适用于用户询问关于"gophish"、"搭建钓鱼活动"、"创建凭证收集页面，发送鱼叉式钓鱼邮件"、"生成钓鱼基础设施"。开源钓鱼活动框架，提供 Web UI 用于创建凭证收集活动、跟踪点击率和管理目标。
---

# GoPhish

完整的钓鱼活动框架 — 通过 Web UI 管理目标、模板、落地页并捕获凭证。

## 快速开始

```bash
# 启动 GoPhish（默认：管理 UI 在 :3333，钓鱼服务在 :80）
./gophish

# 自定义配置
./gophish --config config.json

# 访问管理 UI
# https://127.0.0.1:3333（默认 admin:gophish，首次登录时修改）
```

## 配置文件 (config.json)

```json
{
  "admin_server": {
    "listen_url": "127.0.0.1:3333",
    "use_tls": true,
    "cert_path": "gophish_admin.crt",
    "key_path": "gophish_admin.key"
  },
  "phish_server": {
    "listen_url": "0.0.0.0:443",
    "use_tls": true,
    "cert_path": "/etc/letsencrypt/live/phish.example.com/fullchain.pem",
    "key_path": "/etc/letsencrypt/live/phish.example.com/privkey.pem"
  },
  "db_name": "sqlite3",
  "db_path": "gophish.db"
}
```

## 活动工作流程

1. **发送配置文件 (Sending Profile)** — 配置 SMTP 中继（host、port、from、username、password）
2. **邮件模板 (Email Template)** — 包含 `{{.FirstName}}`、`{{.URL}}`、`{{.Tracker}}` 的 HTML/文本正文
3. **落地页 (Landing Page)** — 克隆目标登录页面；启用"捕获凭证"并设置跳转目标
4. **用户与分组 (User & Group)** — 导入 CSV：`First Name, Last Name, Email, Position`
5. **活动 (Campaign)** — 关联以上所有内容，设置发送计划，启动

## 邮件模板变量

| 变量 | 说明 |
|------|------|
| `{{.FirstName}}` | 目标名字 |
| `{{.LastName}}` | 目标姓氏 |
| `{{.Email}}` | 目标邮箱 |
| `{{.Position}}` | 目标职位 |
| `{{.From}}` | 发送地址 |
| `{{.URL}}` | 唯一钓鱼链接（自动生成） |
| `{{.Tracker}}` | 开信追踪像素 |
| `{{.RId}}` | 唯一收件人 ID |

## 常用工作流

```bash
# 从 CSV 导入目标
# CSV 格式: First Name,Last Name,Email,Position
cat > targets.csv << 'EOF'
First Name,Last Name,Email,Position
John,Doe,jdoe@target.com,Developer
EOF

# API: 列出活动
curl -k -H "Authorization: Bearer API_KEY" https://127.0.0.1:3333/api/campaigns/

# API: 获取活动结果
curl -k -H "Authorization: Bearer API_KEY" https://127.0.0.1:3333/api/campaigns/1/results
```

## SMTP 中继选项

- **Sendgrid / Mailgun** — 提供免费套餐
- **自建 Postfix** — 配置 SPF/DKIM/DMARC 提升投递率
- **SMTP2GO** — 投递率好，提供免费套餐

## 基础设施建议

- 注册仿冒域名（如 `target-helpdesk.com`）
- 在钓鱼服务器上配置 Let's Encrypt TLS
- 为发送域添加 SPF、DKIM、DMARC 记录
- 使用邮件预热提升收件箱落地率

## 参考资源

| 文件 | 加载时机 |
|------|----------|
| `references/campaign-setup.md` | 完整搭建指南：SMTP 配置、DNS 记录、落地页克隆、API 使用 |
