---
name: phoneinfoga
description: >
  此技能适用于用户询问关于 "phoneinfoga"、"在目标画像阶段以电话号码为支点进行信息枢纽"、"社会工程学前期准备" 等内容。电话号码 OSINT 工具，可收集运营商、位置及在线存在数据。
---

# PhoneInfoga

电话号码侦察 —— 运营商、国家、在线存在、数据泄露记录。

## 快速开始

```bash
# 从 GitHub Releases 下载
# 或使用 Docker
docker run --rm sundowndev/phoneinfoga scan -n +1234567890

# 扫描号码（需使用国际格式）
phoneinfoga scan -n +14151234567

# 启动 Web 界面
phoneinfoga serve
# → http://localhost:5000
```

## 核心命令

| 命令 | 用途 |
|------|------|
| `scan -n NUMBER` | 对号码执行完整扫描 |
| `serve` | 启动 Web 控制台 |
| `--output json` | 输出 JSON 格式 |

## 可获取的信息

- 国家、运营商、线路类型（移动 / 固话 / VoIP）
- 通过反向查询获取可能的归属人
- Google dork 结果（社交媒体、号码目录）
- NumVerify / Numinfo API 数据（需配置）
- 数据泄露查询（关联 HaveIBeenPwned 账号）

## 常用工作流程

**快速扫描：**
```bash
phoneinfoga scan -n +14151234567
```

**使用 Web 控制台进行手动调查：**
```bash
phoneinfoga serve &
open http://localhost:5000
```

**JSON 输出用于自动化：**
```bash
phoneinfoga scan -n +14151234567 --output json > phone.json
```

## 资源

| 文件 | 加载时机 |
|------|----------|
| `references/` | API key 配置与 dork 扩展 |
