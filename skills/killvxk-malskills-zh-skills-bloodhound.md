---
name: bloodhound
description: >
  此技能适用于用户询问关于 "bloodhound"、"测绘 AD 环境"、"寻找到达域管理员的最短路径、枚举 Kerberoastable 账户、AS-REP Roastable 用户"、"ACL 滥用" 等内容。利用图论进行 Active Directory 攻击路径可视化，发现权限提升路径、横向移动机会和配置错误。
---

# BloodHound

Active Directory 攻击路径测绘。

## 快速开始

```
# Collect — run on domain-joined Windows host
SharpHound.exe -c All --outputdirectory C:\loot\

# Import zip into BloodHound GUI (drag & drop), then run queries
```

## SharpHound 参数

| 参数 | 用途 |
|------|---------|
| `-c All` | 收集所有数据类型 |
| `-c DCOnly` | 仅收集 DC 数据（低噪声） |
| `--stealth` | 低噪声模式收集 |
| `--outputdirectory` | 输出路径 |
| `--domain` | 目标域 FQDN |
| `--ldapusername / --ldappassword` | 显式指定凭据 |

## 内置查询

| 查询 | 用途 |
|-------|---------|
| Shortest Paths to Domain Admins | 主要攻击路径 |
| All Kerberoastable Accounts | 密码破解目标 |
| AS-REP Roastable Users | 无需预认证 |
| Principals with DCSync Rights | 通往凭据转储的路径 |
| Computers with Unconstrained Delegation | 票据窃取 |

## 自定义 Cypher 查询

```cypher
-- Non-admin users with local admin on any computer
MATCH (u:User {admincount:false})-[r:AdminTo]->(c:Computer) RETURN u.name, c.name

-- Owned user shortest path to DA
MATCH p=shortestPath((u:User {owned:true})-[*1..]->(g:Group {name:"DOMAIN ADMINS@DOMAIN.LOCAL"})) RETURN p
```

## 资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | Cypher 查询库、CE Docker 部署说明 |
