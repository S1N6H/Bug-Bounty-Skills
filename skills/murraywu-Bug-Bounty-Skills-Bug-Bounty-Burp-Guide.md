# Bug-Bounty-Burp-Guide - Burp Suite 使用指南

**来源**: Bug Bounty 课程学习提取
**版本**: 1.0
**创建时间**: 2026-04-02

---

## 功能描述

提供 Burp Suite 使用教程、配置指南、实战技巧。

---

## 核心模块

### Proxy (代理)
**用途**: 拦截和修改 HTTP/HTTPS 请求

**配置步骤**:
1. 启动 Burp Suite
2. Proxy → Intercept → 点击 "Intercept is on"
3. 浏览器配置代理：127.0.0.1:8080
4. 访问网站，请求被拦截
5. 修改请求 → Forward 发送

**常见操作**:
- 修改参数值
- 添加/删除 Header
- 修改请求方法
- 重放请求

---

### Repeater (重放)
**用途**: 手动重放和修改请求

**使用场景**:
- 测试不同参数值
- 暴力破解
- 漏洞验证

**操作**:
1. 右键请求 → "Send to Repeater"
2. 修改参数
3. 点击 "Send"
4. 观察响应变化

---

### Intruder (入侵)
**用途**: 自动化攻击 (爆破/Fuzzing)

**攻击模式**:
- **Sniper**: 单参数逐个测试
- **Battering Ram**: 多参数同步测试
- **Pitchfork**: 多参数独立字典
- **Cluster Bomb**: 多参数组合字典

**使用场景**:
- 目录爆破
- 密码爆破
- 参数 Fuzzing
- 暴力枚举

---

### Scanner (扫描)
**用途**: 自动漏洞扫描 (仅 Pro 版)

**扫描类型**:
- 主动扫描
- 被动扫描

---

## 必备扩展

| 扩展 | 用途 |
|------|------|
| Logger++ | 日志增强，查看所有请求 |
| Autorize | 自动化授权测试 |
| Param Miner | 发现隐藏参数 |
| Burp Bounty | 自定义扫描规则 |
| Turbo Intruder | 高速请求发送 |

---

## 安装扩展

1. Extender → BApp Store
2. 搜索扩展名称
3. 点击 Install
4. 重启 Burp

---

## 常见场景

### 1. 拦截登录请求
```
1. 开启 Intercept
2. 提交登录表单
3. 拦截请求
4. 修改用户名/密码
5. Forward 发送
```

### 2. 测试 XSS
```
1. 发现输入点
2. Send to Repeater
3. 输入 <script>alert(1)</script>
4. Send 观察响应
5. 检查是否反射
```

### 3. 测试 SQLi
```
1. 发现参数
2. Send to Repeater
3. 输入 ' OR '1'='1
4. Send 观察响应变化
5. 使用不同 Payload 验证
```

### 4. 目录爆破
```
1. Send to Intruder
2. 选择 Sniper 模式
3. 设置字典 (SecLists)
4. 开始攻击
5. 过滤 200 状态码
```

---

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+R | 发送到 Repeater |
| Ctrl+I | 发送到 Intruder |
| Ctrl+Shift+B | 发送到 Scanner |
| F5 | 重放请求 |

---

## 学习资源

- [Hacker101 Burp 教程](https://www.hacker101.com/playlists/burp_suite)
- [PortSwigger 官方文档](https://portswigger.net/burp/documentation)
- [Burp Suite Certified Practitioner](https://portswigger.net/web-security/certifications)

---

## 安全声明

⚠️ **仅用于授权测试和学习**

---

*Bug-Bounty-Burp-Guide v1.0 | 2026-04-02*
