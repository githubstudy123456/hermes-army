# SSH 安全防护 — fail2ban 配置

## 诊断路径：服务器连接不上

当服务器 SSH 连接不上时，按以下顺序排查：

```bash
# Step 1: 查看 SSH 认证日志（成功定位攻击）
journalctl --since "30 minutes ago" | grep -i "error\|fail\|kill" | tail -30

# Step 2: 看登录失败来源
grep "Failed password" /var/log/auth.log | tail -20

# Step 3: 看 SSH 连接重置（kex_exchange_identification 错误 = 攻击者在扫端口）
grep "kex_exchange_identification" /var/log/auth.log | tail -10

# Step 4: 检查当前 SSH 连接数
ss -s

# Step 5: 检查 fail2ban 状态
sudo fail2ban-client status sshd 2>/dev/null || echo "fail2ban not running"
```

**关键判断特征：**
- `Failed password for root from <IP>` + `Failed password for ubuntu from <IP>` → 暴力破解
- `error: kex_exchange_identification: read: Connection reset by peer` → 攻击者扫端口
- `system boot` 在 `last reboot` 中很新 → 可能因上述原因被迫重启

**根因：服务器暴露在公网，大量 IP 持续尝试 SSH 登录，耗尽连接资源导致正常连接被打掉。**

---

## 安装并配置 fail2ban

```bash
# Step 1: 安装
sudo apt-get install -y fail2ban

# Step 2: 启用并启动
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Step 3: 验证启动成功（如果失败会报 socket 错误）
sudo fail2ban-client status sshd

# Step 4: 配置（覆盖默认配置）
sudo cp /etc/fail2ban/jail.local /etc/fail2ban/jail.local.bak  # 备份
sudo bash -c 'cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 86400
findtime = 3600
maxretry = 5
destemail = root@localhost
sender = root@localhost

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 5
bantime = 86400
findtime = 3600
EOF'

# Step 5: 重启生效
sudo systemctl restart fail2ban

# Step 6: 确认状态
sudo fail2ban-client status sshd
```

**验证要点：**
- `Currently banned: N` 应该大于 0（已有攻击 IP 被封）
- `Banned IP list` 应该包含攻击源 IP
- 查看实时日志：`tail -f /var/log/fail2ban.log`

---

## 配置说明

| 参数 | 值 | 含义 |
|------|-----|------|
| `maxretry` | 5 | 5次失败密码后封禁 |
| `bantime` | 86400 | 封禁24小时（秒） |
| `findtime` | 3600 | 1小时内累计次数 |

---

## 进阶安全：禁用密码登录

```bash
# 检查当前配置
grep "^PasswordAuthentication" /etc/ssh/sshd_config

# 如果有 SSH 密钥登录（authorized_keys 存在），可以安全禁用密码登录
# 编辑 /etc/ssh/sshd_config，改成：
# PasswordAuthentication no

# 重启 SSH（当前会话不会断开，但新连接必须用密钥）
sudo systemctl restart sshd
```

**⚠️ 注意：必须先确认 authorized_keys 存在且能登录，否则会把自己锁在外面。**

---

## 已知攻击源（2026-05-29 记录）

| IP | 攻击目标 | 频率 |
|----|---------|------|
| 43.226.79.54 | root 登录 | 每分钟多次 |
| 159.75.82.163 | ubuntu 登录 | 每分钟多次 |

---

## 相关命令速查

```bash
# 查看当前被封的 IP
sudo fail2ban-client status sshd

# 手动解封（测试用）
sudo fail2ban-client set sshd unbanip <IP>

# 手动封禁（测试用）
sudo fail2ban-client set sshd banip <IP>

# 查看 fail2ban 日志
sudo tail -f /var/log/fail2ban.log

# 确认 fail2ban 在运行
sudo systemctl status fail2ban
```