# Bug-Bounty-Writeup-Helper - CTF Writeup 助手

**来源**: Bug Bounty 课程学习提取
**版本**: 1.0
**创建时间**: 2026-04-02

---

## 功能描述

帮助整理 CTF/漏洞利用的解题思路和 Writeup。

---

## Writeup 结构

```markdown
# [题目/漏洞名称]

## 基本信息
- **类型**: [Web/Pwn/Crypto/Reverse/Misc]
- **难度**: [★☆☆☆☆ - ★★★★★]
- **平台**: [CTF 名称/平台]
- **完成时间**: [日期]

## 题目描述
[题目原文]

## 信息收集
[初步分析过程]

## 漏洞分析
[漏洞原理分析]

## 解题步骤
1. [步骤 1]
2. [步骤 2]
3. [步骤 3]

## 利用过程
[详细利用过程]

## Flag
```
flag{xxx}
```

## 知识点总结
- [知识点 1]
- [知识点 2]

## 参考链接
- [相关链接]
```

---

## 常见类型模板

### Web 类
```markdown
## 漏洞类型
XSS / SQLi / CSRF / IDOR / SSRF / XXE / RCE

## 检测过程
[如何发现漏洞]

## 利用 Payload
[具体 Payload]
```

### Pwn 类
```markdown
## 二进制分析
[文件类型/保护机制]

## 漏洞点
[溢出点/利用点]

## Exploit
[利用脚本]
```

### Crypto 类
```markdown
## 加密算法
[算法类型]

## 分析方法
[解密过程]

## 解密脚本
[Python 脚本]
```

---

## 写作建议

### ✅ 应该做的
- 清晰描述思路
- 包含关键步骤
- 提供完整 Payload/Exploit
- 总结知识点
- 附上截图

### ❌ 不应该做的
- 只贴 Flag 无过程
- 缺少关键步骤
- 无代码/ Payload
- 过于简略

---

## 示例

```markdown
# DVWA SQL Injection (High) Writeup

## 基本信息
- **类型**: Web / SQL Injection
- **难度**: ★★★☆☆
- **平台**: DVWA
- **完成时间**: 2026-04-02

## 题目描述
DVWA High 级别的 SQL 注入挑战

## 信息收集
- 输入点：user_id 参数
- 过滤：移除了 OR/AND 等关键字

## 漏洞分析
虽然过滤了 OR/AND，但未使用参数化查询，
仍可通过其他 Payload 绕过

## 解题步骤
1. 测试输入：1' 报错，存在注入
2. 尝试盲注：1' AND SLEEP(5)-- 被过滤
3. 使用 UNION: 1' UNION SELECT 1,version()-- 成功

## 利用 Payload
```sql
1' UNION SELECT user(),database()--
1' UNION SELECT table_name,NULL FROM information_schema.tables--
1' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='users'--
1' UNION SELECT password,NULL FROM users WHERE user_id='admin'--
```

## Flag
```
flag{sqli_un10n_4tt4ck}
```

## 知识点
- UNION 联合查询
- information_schema 使用
- SQL 注入绕过

## 参考
- PortSwigger SQLi Labs
- OWASP SQL Injection
```

---

## 安全声明

⚠️ **仅用于学习和授权 CTF**

---

*Bug-Bounty-Writeup-Helper v1.0 | 2026-04-02*
