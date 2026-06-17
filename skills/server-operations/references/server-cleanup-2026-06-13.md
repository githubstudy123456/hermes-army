# 服务器体检与清理记录 — 2026-06-13

## 本次执行摘要

**触发原因：** 主人问"服务器有什么在跑" → "为什么 openclaw 占这么大" → "有没有不常用的占用服务"

**执行结果：**
- 内存：2.0GB → 1.6GB（省 ~400MB）
- 磁盘：释放约 133MB（ZeroTier 11MB + snapd 122MB）
- 端口关闭：`:9993`(ZeroTier) / `:33859`(containerd) / `:19825`(Chrome调试)
- 进程清理：10+ Chrome 渲染进程、bb-browser daemon、physics-visual-platform (PM2)

---

## 体检 SOP（验证版）

### 问诊命令（一次性执行）

```bash
ps aux --sort=-%mem | grep -v "^\[" | grep -v "grep" | awk '{printf "%-10s %-8s %5s %s\n", $1,$2,$4,$11}' | head -15
free -h
ss -tlnp
```

### 快速识别异常进程

| 特征 | 推断 | 处理 |
|------|------|------|
| `--type=renderer` 多个 Chrome | Playwright/bb-browser 残留 | `killall chrome chrome_crashpad_handler; pkill -f bb-browser; pkill -f playwright` |
| bb-browser daemon 跑着但 `:19825` 无连接 | 孤儿进程 | 同上 |
| `openclaw-gateway` VSize 22GB | 正常（Go 内存分配器预占，RSS 680MB 才真实） | 不处理 |
| `VSize` vs `RSS` 差距大 | Go/Java 进程正常现象 | 只看 RSS |

### 云服务器无用服务清单（已验证可停）

```bash
for svc in acpid avahi-daemon ModemManager gpu-manager nv_gpu_shutdown_pm kdump-tools unattended-upgrades open-iscsi; do
  sudo systemctl stop $svc
  sudo systemctl disable $svc
done
```

### Docker 闲置判断

```bash
sudo docker ps  # 无输出 = 无容器
sudo ss -tp | grep containerd  # 有连接 = 有容器在跑
```

无容器时：`systemctl stop/disable` → `apt purge docker.io containerd.io snapd` → `apt autoremove`

### ZeroTier 判断

```bash
sudo zerotier-cli listnetworks
```

无网络或确认可删：`systemctl stop/disable` → `apt purge zerotier-one` → `rm -rf /var/lib/zerotier-one`

---

## 本次清理明细

### 删除项

| 项目 | 包名/进程 | 释放 |
|------|----------|------|
| ZeroTier 组网 | zerotier-one | 11.3MB 磁盘 |
| snapd + LXD | snapd | 122MB 磁盘 |
| physics-visual-platform | PM2 delete + 目录 rm | 未计算 |
| Docker/containerd | docker.io containerd.io | 实际无包可删（未装） |

### 停用服务

acpid / avahi-daemon / ModemManager / gpu-manager / nv_gpu_shutdown_pm / kdump-tools / unattended-upgrades / open-iscsi

### 杀掉的进程

- 10+ Chrome 渲染进程（内存 ~500MB）
- bb-browser daemon
- Playwright node driver
- PM2: physics-visual-platform

### 保留进程（正常）

| 进程 | 内存 | 说明 |
|------|------|------|
| openclaw-gateway | 17.6% | 正常，RSS 680MB |
| hermes-agent | 10.8% | 正常 |
| YDEyes (腾讯云云镜) | 2.2% | 腾讯云自带，必留 |
| PM2 | 1.0% | 正常（无 app 在跑） |
| systemd-journald | 1.4% | 系统日志，必留 |
| nginx | :80 | teaching-platform 静态 + API 代理 |
| PostgreSQL | :5432 | Hermes 数据存储 |
| xray | :10809 | Trojan 代理 |

---

## 端口速查表（本服务器）

| 端口 | 服务 | 保留？ |
|------|------|--------|
| :22 | SSH | ✅ |
| :80 | Nginx | ✅ teaching-platform |
| :5432 | PostgreSQL | ✅ |
| :10808 | Xray SOCKS | ✅ |
| :10809 | Xray HTTP | ✅ |
| :18789 | Hermes gateway | ✅ |
| :18791 | Hermes CLI | ✅ |
| :8118 | Privoxy | ✅ |
| :9993 | ZeroTier | ❌ 已删 |
| :3000 | Next.js | ❌ 已关 |
| :33859 | containerd | ❌ 已删 |
| :19825 | Chrome调试 | ❌ 已清 |

---

## bb-browser / Chrome 残留根因分析

**现象：** 杀完后 cron job 重新拉起

**根因：** hermes-political 和 hermes-economic（每30分钟一次）使用 web-browse skill，web-browse 底层调用 bb-browser。bb-browser daemon 启动后会驻留，即使任务完成也不自动退出，导致所有 Chrome 渲染进程累积。

**处理方式：** 主人选择"不用管"（暂时容忍）

**已知使用 bb-browser 的 cron jobs：**
- `hermes-political` (job_id: 27433eb6e582) — every 30m
- `hermes-economic` (job_id: df79fff69067) — every 30m
- `bb-browser daemon` (PID 920132) — parent: hermes-agent (PID 864837)

---

## teaching-platform 当前架构

**Nginx 配置：** `/etc/nginx/sites-enabled/teaching-platform`
**静态文件：** `/var/www/teaching-platform/` (8.2MB)
**Flask API：** `127.0.0.1:5001`（被 Nginx 代理）

```nginx
server {
    listen 80 default_server;
    server_name _;
    root /var/www/teaching-platform;
    
    location /api/ {
        proxy_pass http://127.0.0.1:5001/api/;
    }
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```
