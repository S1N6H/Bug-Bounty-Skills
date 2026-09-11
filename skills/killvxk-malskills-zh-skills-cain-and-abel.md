---
name: cain-and-abel
description: >
  此技能适用于用户询问关于"cain-and-abel"、"恢复 Windows 哈希"、"破解捕获的握手包"、
  "解码 Windows 系统上的缓存凭据"等问题。Windows 密码恢复工具，支持网络嗅探、
  密码破解（字典/暴力破解/密码分析）以及存储凭据解码。
---

# Cain & Abel

Windows 图形界面密码恢复工具——嗅探器、哈希破解器、凭据解码器。

## 快速开始

1. 从 oxid.it（遗留版本）或存档下载
2. 以管理员身份运行
3. 选择 **Cracker** 标签 → 添加哈希
4. 右键点击哈希 → **Dictionary Attack**（字典攻击）/ **Brute-Force Attack**（暴力攻击）/ **Rainbow Table**（彩虹表）

## 核心功能

| 功能 | 用途 |
|---------|---------|
| Sniffer（嗅探器） | 捕获网络凭据（ARP 中毒） |
| Cracker（破解器） | 字典、暴力破解、哈希密码分析 |
| Decoders（解码器） | 解码存储的密码（LSA、VNC、拨号连接） |
| Network（网络） | ARP 中毒、路由发现 |
| Wireless（无线） | WEP/WPA 捕获与破解 |
| Certificate（证书） | 通过 MITM 收集证书 |

## 支持的哈希类型

MD5、SHA-1、LM、NTLM、NTLMv2、MySQL、MS-SQL、Oracle、Cisco PIX/IOS、VNC、RADIUS、WPA。

## 常见工作流程

**从 SAM 转储中破解 NTLM：**
1. Cracker 标签 → `+` → 从 SAM 添加 NT 哈希
2. 右键 → Dictionary Attack → 指向字典文件

**ARP 中毒 + 凭据捕获：**
1. Sniffer 标签 → 启用嗅探器
2. ARP 标签 → 添加目标主机 + 网关
3. Passwords 标签 → 查看捕获的凭据

> **注意**：仅在授权系统上使用。Cain & Abel 会触发大多数杀毒软件报警。

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | 哈希导入格式和字典来源 |
