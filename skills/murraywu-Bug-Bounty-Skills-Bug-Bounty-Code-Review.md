# Bug-Bounty-Code-Review - 代码安全审查技能

**来源**: Bug Bounty 课程学习提取
**版本**: 1.0
**创建时间**: 2026-04-02

---

## 功能描述

自动扫描代码中的常见安全漏洞，提供修复建议。

**检测范围**:
- XSS (跨站脚本)
- SQL Injection (SQL 注入)
- 命令注入
- 路径遍历
- 硬编码敏感信息
- 不安全的反序列化
- CSRF
- SSRF 风险

---

## 触发条件

用户请求代码安全审查时触发，例如:
- "帮我检查这段代码有没有安全问题"
- "这段代码有什么漏洞"
- "审查一下这个函数的安全性"
- "代码里有没有 SQL 注入风险"

---

## 检测规则

### 1. XSS 检测

**高风险模式**:
```javascript
// 直接输出用户输入到 HTML
document.innerHTML = userInput;
element.innerHTML = data;

// 未转义的输出
res.send(`<div>${userInput}</div>`);
return `<h1>${title}</h1>`;

// eval 执行用户输入
eval(userInput);
new Function(userInput)();
```

**中风险模式**:
```javascript
// 拼接 HTML 字符串
let html = '<div>' + userInput + '</div>';

// document.write
document.write(userInput);

// 插入外部脚本
script.src = userInput;
```

**修复建议**:
```javascript
// 使用 textContent 代替 innerHTML
element.textContent = userInput;

// 使用模板引擎自动转义
// EJS/Pug/Handlebars 等

// 手动编码
function escapeHTML(str) {
  return str.replace(/[&<>"']/g, m => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;',
    '"': '&quot;', "'": '&#39;'
  }[m]));
}
```

---

### 2. SQL 注入检测

**高风险模式**:
```javascript
// 字符串拼接 SQL
const sql = `SELECT * FROM users WHERE id = ${userId}`;
const sql = "SELECT * FROM users WHERE name = '" + name + "'";

// 模板字符串拼接
db.query(`DELETE FROM logs WHERE date < '${date}'`);

// 格式化字符串
sql = "SELECT * FROM users WHERE id = %s" % user_id
```

**Python 特定**:
```python
# 字符串格式化
cursor.execute("SELECT * FROM users WHERE id = %s" % user_id)
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

# 字符串拼接
query = "SELECT * FROM users WHERE name = '" + name + "'"
```

**修复建议**:
```javascript
// 使用参数化查询
const sql = 'SELECT * FROM users WHERE id = ?';
db.execute(sql, [userId]);

// 命名参数
const sql = 'SELECT * FROM users WHERE id = :id';
db.execute(sql, { id: userId });
```

```python
# 参数化查询
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```

---

### 3. 命令注入检测

**高风险模式**:
```javascript
// exec/spawn 执行用户输入
exec(`ping ${userInput}`);
child_process.exec(`ls ${dir}`);

// 拼接命令
const cmd = 'cat ' + filePath;
exec(cmd);
```

**Python**:
```python
# shell=True 执行用户输入
os.system(f"ping {user_input}")
subprocess.call(cmd, shell=True)

# 拼接命令
os.popen("ls " + user_dir)
```

**修复建议**:
```javascript
// 使用 execFile 或 spawn，参数分离
execFile('ping', [userInput]);
spawn('ls', [dir], { shell: false });

// 输入验证
if (!/^[a-zA-Z0-9_-]+$/.test(userInput)) {
  throw new Error('Invalid input');
}
```

```python
# 参数列表方式，不使用 shell
subprocess.run(['ls', user_dir])
subprocess.run(['ping', '-c', '1', host])

# 避免 shell=True
```

---

### 4. 路径遍历检测

**高风险模式**:
```javascript
// 直接使用用户输入作为文件路径
fs.readFileSync(userPath);
fs.readFile(`./uploads/${fileName}`);

// 未验证的路径拼接
const filePath = baseDir + userInput;
```

**Python**:
```python
open(user_path)
open('./uploads/' + filename)
```

**修复建议**:
```javascript
// 路径规范化 + 白名单验证
const path = require('path');
const safePath = path.normalize(userPath);
if (!safePath.startsWith(baseDir)) {
  throw new Error('Invalid path');
}

// 使用 path.join 并验证
const filePath = path.join(baseDir, path.basename(fileName));
```

```python
# 使用 os.path 验证
import os
safe_path = os.path.normpath(user_path)
if not safe_path.startswith(base_dir):
    raise ValueError('Invalid path')

# 或使用 pathlib
from pathlib import Path
safe_path = (base_dir / filename).resolve()
if not str(safe_path).startswith(str(base_dir)):
    raise ValueError('Invalid path')
```

---

### 5. 硬编码敏感信息检测

**检测模式**:
```javascript
// API Key
const apiKey = 'sk-xxxxxxxxxxxxxxxx';
const API_KEY = "AKIAIOSFODNN7EXAMPLE";

// 密码
const password = 'admin123';
db.password = "hardcoded_password";

// 密钥
const secret = 'my_super_secret_key';
const JWT_SECRET = "jwt_secret_key";

// 数据库连接字符串
const conn = 'mongodb://user:pass@host:27017/db';
```

**修复建议**:
```javascript
// 使用环境变量
const apiKey = process.env.API_KEY;
const password = process.env.DB_PASSWORD;
const secret = process.env.JWT_SECRET;

// 使用密钥管理服务
// AWS Secrets Manager / Azure Key Vault 等
```

---

### 6. 不安全反序列化检测

**高风险模式**:
```javascript
// eval 解析 JSON
eval('(' + jsonString + ')');

// Function 构造器
new Function('return ' + jsonString)();

// 不安全的 deserialize
deserialize(userInput);
```

**Python**:
```python
# pickle 反序列化用户输入
pickle.loads(user_data)
cPickle.loads(user_data)

# yaml 不安全加载
yaml.load(user_data)  # 应该使用 yaml.safe_load
```

**修复建议**:
```javascript
// 使用 JSON.parse
const obj = JSON.parse(jsonString);

// 验证输入来源
if (!isTrustedSource(data)) {
  throw new Error('Untrusted data');
}
```

```python
# 使用 safe_load
import yaml
yaml.safe_load(user_data)

# 避免 pickle
import json
json.loads(user_data)
```

---

### 7. CSRF 检测

**检测模式** (Web 框架):
```javascript
// 缺少 CSRF Token 的表单
// Express 未使用 csurf 中间件
app.post('/transfer', (req, res) => {
  // 没有验证 CSRF token
  transferMoney(req.body.amount);
});
```

**修复建议**:
```javascript
// Express 使用 csurf
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });

app.post('/transfer', csrfProtection, (req, res) => {
  // 自动验证 CSRF token
  transferMoney(req.body.amount);
});
```

```html
<!-- 表单中添加 CSRF Token -->
<form method="POST" action="/transfer">
  <input type="hidden" name="_csrf" value="{{csrfToken}}">
  <input type="number" name="amount">
</form>
```

---

### 8. SSRF 风险检测

**高风险模式**:
```javascript
// 直接使用用户输入的 URL
fetch(userUrl);
axios.get(userUrl);
request(userUrl);

// 未验证的 URL 重定向
res.redirect(userUrl);
```

**修复建议**:
```javascript
// URL 白名单验证
const { URL } = require('url');

function isValidUrl(urlString) {
  try {
    const url = new URL(urlString);
    // 检查协议
    if (!['http:', 'https:'].includes(url.protocol)) {
      return false;
    }
    // 检查是否内网 IP
    const ip = dns.lookup(url.hostname);
    if (isPrivateIP(ip)) {
      return false;
    }
    return true;
  } catch {
    return false;
  }
}

// 使用允许列表
const allowedDomains = ['api.example.com', 'cdn.example.com'];
if (!allowedDomains.includes(url.hostname)) {
  throw new Error('Domain not allowed');
}
```

---

## 输出格式

发现漏洞时，按以下格式输出:

```
🔍 代码安全审查结果

⚠️ 发现 [数量] 个潜在安全问题:

---

1. [漏洞类型] - [风险等级]
   📍 位置：[文件名/行号]
   📄 代码：[问题代码]
   
   📖 说明：[漏洞原理简述]
   
   ✅ 修复建议:
   ```[语言]
   [修复后的代码]
   ```

---

[重复以上格式...]

---
📊 风险统计:
- 🔴 高风险：X 个
- 🟡 中风险：X 个
- 🟢 低风险：X 个

⚠️ 注意：此审查为自动化检测，可能存在误报或漏报。
   建议结合人工审查和渗透测试进行全面评估。
```

---

## 示例对话

### 示例 1: XSS 检测

**用户**:
```javascript
function renderUserComment(comment) {
  return `<div class="comment">${comment}</div>`;
}
```

**助手**:
```
🔍 代码安全审查结果

⚠️ 发现 1 个潜在安全问题:

---

1. XSS (跨站脚本攻击) - 🔴 高风险
   📍 位置：renderUserComment 函数
   📄 代码：return `<div class="comment">${comment}</div>`;
   
   📖 说明：用户输入直接插入 HTML，攻击者可注入恶意脚本。
          例如输入：<script>alert(document.cookie)</script>
   
   ✅ 修复建议:
   ```javascript
   // 方法 1: 使用 textContent
   function renderUserComment(comment) {
     const div = document.createElement('div');
     div.className = 'comment';
     div.textContent = comment;  // 自动转义
     return div.outerHTML;
   }
   
   // 方法 2: 手动 HTML 编码
   function escapeHTML(str) {
     return str.replace(/[&<>"']/g, m => ({
       '&': '&amp;', '<': '&lt;', '>': '&gt;',
       '"': '&quot;', "'": '&#39;'
     }[m]));
   }
   
   function renderUserComment(comment) {
     return `<div class="comment">${escapeHTML(comment)}</div>`;
   }
   ```

---

📊 风险统计:
- 🔴 高风险：1 个
```

### 示例 2: SQL 注入检测

**用户**:
```python
def get_user(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)
```

**助手**:
```
🔍 代码安全审查结果

⚠️ 发现 1 个潜在安全问题:

---

1. SQL Injection (SQL 注入) - 🔴 高风险
   📍 位置：get_user 函数
   📄 代码：query = f"SELECT * FROM users WHERE username = '{username}'"
   
   📖 说明：使用 f-string 拼接 SQL 查询，攻击者可输入：
          admin' OR '1'='1 来绕过认证
          admin'; DROP TABLE users;-- 来删除数据
   
   ✅ 修复建议:
   ```python
   # 使用参数化查询
   def get_user(username):
       query = "SELECT * FROM users WHERE username = %s"
       return db.execute(query, (username,))
   
   # 或使用 SQLAlchemy ORM
   def get_user(username):
       return session.query(User).filter_by(username=username).first()
   ```

---

📊 风险统计:
- 🔴 高风险：1 个
```

---

## 限制说明

1. **静态分析限制**: 无法检测运行时动态生成的代码
2. **上下文理解**: 可能无法完全理解复杂的业务逻辑
3. **误报可能**: 某些模式可能是安全的 (如有完善的输入验证)
4. **漏报可能**: 新型攻击模式可能未被覆盖
5. **语言覆盖**: 主要支持 JavaScript/Python/Java/PHP 等常见语言

---

## 安全声明

⚠️ **本技能仅用于**:
- 代码安全自查
- 学习安全编码实践
- 授权的安全审计

❌ **禁止用于**:
- 未经授权的代码扫描
- 恶意目的
- 侵犯他人隐私

使用本技能请遵守当地法律法规，仅在授权范围内使用。

---

*Skill 版本：1.0 | 基于 Bug Bounty 课程提取 | 2026-04-02*
