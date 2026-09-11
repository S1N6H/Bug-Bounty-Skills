---
name: kiterunner
description: >
  此技能适用于用户询问关于"kiterunner"、"枚举 API 端点"、"发现 REST/gRPC 服务上的隐藏路由"、"替代 dirbust 用于 API 表面"。使用真实世界 API schema 字典的上下文感知 API 路由发现和暴力破解工具。
---

# Kiterunner

上下文感知 API 路由暴力破解器，使用真实世界 API schema 字典（Assetnote）。

## 快速开始

```bash
# 从 https://github.com/assetnote/kiterunner/releases 下载二进制文件

# 使用默认字典扫描
kr scan https://target.com -w routes-small.kite

# 从 host 文件扫描
kr scan hosts.txt -w routes-large.kite -x 20

# 重放发现结果并查看完整请求详情
kr replay -w routes-small.kite "GET   403 [   191,    9,   1] https://target.com/api/v1/user"
```

## 核心参数

| 参数 | 用途 |
|------|------|
| `-w FILE` | Kite 字典文件（.kite 或 .txt） |
| `-x N` | 并发请求数 |
| `--ignore-length N` | 按响应长度过滤 |
| `-H "K:V"` | 自定义请求头 |
| `-A "bearer:TOKEN"` | 认证头简写 |
| `--fail-status-codes` | 视为失败的状态码 |
| `--success-status-codes` | 视为命中的状态码 |
| `-o json` | JSON 输出 |
| `--delay N` | 每个请求的延迟（毫秒） |

## 常用工作流

**已认证 API 扫描：**
```bash
kr scan https://api.target.com -w routes-large.kite -A "bearer:$TOKEN" -x 30
```

**过滤噪音 — 忽略典型 404/400 长度：**
```bash
kr scan https://api.target.com -w routes-small.kite --ignore-length 19
```

**重放以检查完整响应：**
```bash
kr replay -w routes-large.kite "POST  200 [  512,  10,   2] https://api.target.com/api/v2/admin"
```

## 参考资源

| 文件 | 加载时机 |
|------|----------|
| `references/` | 字典来源和 API 指纹识别说明 |
