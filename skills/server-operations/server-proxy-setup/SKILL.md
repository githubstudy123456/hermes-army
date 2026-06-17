---
name: server-proxy-setup
description: 服务器代理基础设施 — privoxy/SOCKS5 架构、验证方法、外部设备访问方案
trigger: 服务器爬虫访问受限 / 代理故障排查 / 需要从外部设备连代理
---

# Server Proxy Setup

服务器上的代理基础设施，记录配置和访问方式。

## 代理架构

```
宿主机 127.0.0.1:10808 (SOCKS5) ← VMess/V2ray VPN
       ↓
宿主机 127.0.0.1:8118 (privoxy HTTP代理) ← 转发到 SOCKS5
       ↓
应用层 (Playwright/curl 走 http://127.0.0.1:8118)
```

## 关键配置

**privoxy** (`/etc/privoxy/config`)
- 监听地址: `127.0.0.1:8118` 和 `[::1]:8118`
- 转发规则: `forward-socks5 . 127.0.0.1:10808 .`
- ⚠️ 只绑定 localhost，**外网设备无法直接连**
- 如果需要让外部设备用代理，需要修改 `listen-address` 为 `0.0.0.0:8118`（安全风险较大）

**SOCKS5** (127.0.0.1:10808/10809)
- 对内端口，privoxy 内部转发用

**HTTP 服务** (0.0.0.0:80)
- 普通 HTTP 服务，外网可访问

**SSH** (0.0.0.0:22)
- OpenSSH，已启用，外网可连接

## 验证代理是否可用

```bash
# 测试 privoxy（从服务器内部）
curl -s -o /dev/null -w "%{http_code}" --proxy http://127.0.0.1:8118 --max-time 10 https://assetmarketcap.com

# 检查端口监听
ss -tlnp | grep -E "8118|10808"
```

## Playwright 走代理

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled'],
        proxy={'server': 'http://127.0.0.1:8118'}
    )
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36',
        locale='zh-CN',
    )
    page = context.new_page()
    response = page.goto('https://target-site.com', timeout=20000)
```

## 让外部设备使用代理（需要主人授权）

如果外部设备要连这个代理，有两个方案：

1. **SSH 隧道**（推荐，安全）
   - 用户在自己电脑上: `ssh -D 10808 -C -N ubuntu@81.71.93.113`
   - 然后本地浏览器/SOCKS 客户端连 `127.0.0.1:10808`

2. **修改 privoxy 监听地址**（风险大，不推荐）
   - 改 `/etc/privoxy/config` 的 `listen-address` 从 `127.0.0.1:8118` 改为 `0.0.0.0:8118`
   - 重启服务: `sudo systemctl restart privoxy`
   - ⚠️ 任何人都能用这个代理，风险极高

## 故障排查

- `curl` 超时但浏览器能访问 → 目标站可能有 JS 反爬，换 Playwright
- `privoxy` 返回 403 → 目标站封锁了数据中心 IP，需要住宅代理
- SOCKS5 连不上 → 检查 VPN 是否掉线 `systemctl status v2ray`

## 相关文件

- `/etc/privoxy/config` — privoxy 主配置
- `~/.ssh/authorized_keys` — SSH 公钥（用户从其他设备登录用）