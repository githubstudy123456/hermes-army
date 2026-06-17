---
name: email
description: 使用 himalaya CLI 管理 Proton 邮箱 (817193113@proton.me) — 读取、发送、搜索邮件。
tags: [Email, Proton, IMAP, SMTP, CLI]
version: 1.0.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Email, Proton, IMAP, SMTP]
    homepage: https://github.com/pimalaya/himalaya
prerequisites:
  commands: [himalaya]
  files: [~/.config/himalaya/config.toml]
  credentials: [pass show email/proton/imap, pass show email/proton/smtp]
---

# Email Skill — Proton 邮箱

已配置账户：**817193113@proton.me**（Proton Mail），默认账户。

## 凭证（存储在 pass）

| 用途   | 命令                        |
|--------|-----------------------------|
| IMAP   | `pass show email/proton/imap`  |
| SMTP   | `pass show email/proton/smtp`  |

密码相同：`cumG4DJbXrvgfJ7`

## 常用操作

### 列出邮件（INBOX）

```bash
himalaya envelope list
```

分页查看：
```bash
himalaya envelope list --page 1 --page-size 20
```

### 读取邮件

```bash
himalaya message read <邮件ID>
```

### 搜索邮件

```bash
himalaya envelope list from <发件人> subject <关键词>
himalaya envelope list to <收件人>
```

### 发送邮件

**非交互式（推荐）** — 直接 pipe 内容：

```bash
cat << 'EOF' | himalaya template send
From: 817193113@proton.me
To: <收件人邮箱>
Subject: <主题>

<正文内容>
EOF
```

### 查看发件箱

```bash
himalaya envelope list --folder "Sent"
```

### 移动 / 删除邮件

```bash
himalaya message move <邮件ID> "Archive"    # 移至归档
himalaya message delete <邮件ID>              # 删除
```

### 查看文件夹列表

```bash
himalaya folder list
```

## 代理注意事项

Proton Mail 服务器（mail.protonmail.com / smtp.protonmail.com）在国内可能被墙。发件前建议：
- 确认代理是否可用
- 若使用 v2rayA，确认分流规则覆盖了 protonmail.com

## 调试

```bash
RUST_LOG=debug himalaya envelope list
```
