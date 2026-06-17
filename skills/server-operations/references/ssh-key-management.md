# SSH 密钥对管理 — 服务器运维必读

## 核心原则：私钥在客户端，公钥在服务器

```
你的电脑（存私钥 id_rsa）          服务器（存公钥 authorized_keys）
┌─────────────────────┐          ┌────────────────────────────┐
│  id_rsa             │  ──登录─→│  authorized_keys           │
│  （永远不要给任何人）│          │  （可以公开）              │
└─────────────────────┘          └────────────────────────────┘
```

**私钥放在服务器上是严重安全隐患** — 服务器被攻破后私钥就泄露了。

---

## 当前服务器密钥状态（2026-05-29）

| 文件 | 类型 | 已在 authorized_keys | 状态 |
|------|------|---------------------|------|
| `id_rsa` | 私钥 | ✗ 未录入 | ⚠️ 不该在服务器上（已在） |
| `id_rsa.pub` | 公钥 | ✗ 未录入 | 待追加到 authorized_keys |
| `authorized_keys` | — | ✓ ED25519 | 唯一能登录的钥匙 |

**ED25519 公钥**（已录入 authorized_keys）：
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIEfnoFvS2BBwHTE7/BYdjOfQ80DP3U0pLoyZVcyk9KTU physics-upload-81.71.93.113
```
来源：81.71.93.113（本地机器），私钥在其上。

---

## 密钥算法对比

| 算法 | 密钥长度 | 安全性 | 性能 | 推荐 |
|------|---------|--------|------|------|
| **ED25519** | 256-bit | ⭐⭐⭐⭐⭐（现代曲线，性能最佳） | 极快 | ✅ 首选 |
| RSA | 4096-bit | ⭐⭐⭐⭐（老但可靠） | 慢（签名验签都慢） | ⚠️ 备选 |

ED25519 = Curve25519，理论安全性 128-bit，等效 RSA 3072-bit，签名更短。

---

## 添加公钥到服务器（authorized_keys）

### 方案A：把本机 RSA 公钥加入（多设备备用）

```bash
# 在本机上执行（私钥所在机器）
cat ~/.ssh/id_rsa.pub

# 在服务器上执行（追加到 authorized_keys）
echo "ssh-rsa AAAAB3...（公钥内容）" >> ~/.ssh/authorized_keys
```

### 方案B：重新生成一对新密钥对（推荐）

**Step 1：在本机（你的电脑）上生成ED25519密钥**
```bash
ssh-keygen -t ed25519 -C "my-home-pc-2026" -f ~/.ssh/id_ed25519_my
# 会生成：
#   ~/.ssh/id_ed25519_my      （私钥，保密）
#   ~/.ssh/id_ed25519_my.pub  （公钥，给服务器）
```

**Step 2：把公钥内容追加到服务器 authorized_keys**
```bash
# 在本机上
cat ~/.ssh/id_ed25519_my.pub
# 复制输出内容

# 在服务器上
echo "ssh-ed25519 AAAA...（新公钥）" >> ~/.ssh/authorized_keys
```

**Step 3：在本机配置 SSH 别名（~/.ssh/config）**
```
Host my-server
    HostName <服务器IP>
    User ubuntu
    Port 22
    IdentityFile ~/.ssh/id_ed25519_my
    StrictHostKeyChecking no
```

**Step 4：测试登录**
```bash
ssh my-server
```

---

## 验证流程：确认登录正常后再禁用密码

1. 新密钥能成功登录
2. 确认 `PasswordAuthentication yes` 仍开启（备用）
3. 编辑 `/etc/ssh/sshd_config`：`PasswordAuthentication no`
4. `sudo systemctl restart sshd`
5. 测试新密钥登录，确认密码无法登录

---

## 检查服务器上不该有的私钥

```bash
# 列出所有私钥
ls -la ~/.ssh/id_* | grep -v .pub

# 检查 authorized_keys 里的公钥对应的私钥在哪
# ED25519 私钥不存在 → 正确（私钥在本机 81.71.93.113）
# id_rsa 私钥存在 → 错误（应该在本机，不该在服务器）

# 查指纹对比
ssh-keygen -lf ~/.ssh/id_rsa          # 私钥指纹
ssh-keygen -lf ~/.ssh/id_rsa.pub      # 公钥指纹（应相同）
ssh-keygen -lf ~/.ssh/authorized_keys # authorized_keys 里的公钥指纹
```

---

## 已知的攻击源（2026-05-29）

| IP | 目标用户 | 状态 |
|----|---------|------|
| 43.226.79.54 | root | 已 fail2ban 封禁 |
| 159.75.82.163 | ubuntu | 已 fail2ban 封禁 |

封禁命令：
```bash
sudo fail2ban-client set sshd banip <IP>
sudo fail2ban-client set sshd unbanip <IP>  # 解封
```

---

## 禁用密码登录后的检查清单

```bash
# 1. 确认 authorized_keys 至少有一把钥匙
wc -l ~/.ssh/authorized_keys

# 2. 确认新密钥能登录（开另一个终端测）
ssh -i ~/.ssh/<新私钥> ubuntu@<服务器IP>

# 3. 确认密码已禁用
grep "^PasswordAuthentication" /etc/ssh/sshd_config
# 应输出: PasswordAuthentication no

# 4. 确认 sshd 重启生效
sudo systemctl restart sshd

# 5. 确认 fail2ban 在运行
sudo fail2ban-client status sshd
```