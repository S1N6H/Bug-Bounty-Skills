---
name: mitmproxy
description: >
  此技能适用于用户询问关于 "mitmproxy"、"在 Web 应用测试期间代理应用流量并动态修改请求/响应"、
  "使用 Python 插件脚本化请求拦截" 的问题。
---

# mitmproxy

交互式 HTTP/HTTPS 中间人代理 (MITM Proxy)。

## 快速开始

```bash
mitmproxy -p 8080
mitmweb -p 8080
mitmdump -p 8080 -w traffic.dump
```
安装 CA 证书：代理运行时访问 `http://mitm.it`。

## 工作模式

| 模式 | 命令 | 使用场景 |
|------|---------|----------|
| 常规代理 | `mitmproxy` | 浏览器/工具代理 |
| 透明代理 | `--mode transparent` | 无需代理配置即可拦截 |
| 反向代理 | `--mode reverse:http://target` | 反向代理模式 |
| SOCKS5 | `--mode socks5` | SOCKS 代理 |

## TUI 快捷键

| 按键 | 操作 |
|-----|--------|
| `Enter` | 检查请求 |
| `e` | 编辑请求/响应 |
| `r` | 重放请求 |
| `f` | 设置过滤器 |
| `i` | 设置拦截过滤器 |

## Python 插件

```python
from mitmproxy import http

def request(flow: http.HTTPFlow):
    if flow.request.method == "POST":
        print(flow.request.pretty_url, flow.request.get_text())
```
```bash
mitmproxy -s addon.py
```

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | 插件 API 参考、透明代理配置 |
