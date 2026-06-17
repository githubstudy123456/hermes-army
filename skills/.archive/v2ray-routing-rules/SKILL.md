---
name: v2ray-routing-rules
description: v2ray 分流规则配置，支持 geosite:cn 直连和 Loyalsoldier 精细分流表
triggers:
  - v2ray routing rules configuration
  - split tunnel configuration
  - geosite:cn direct list
  - Loyalsoldier rules
---

# V2Ray 分流规则配置

## 基础分流配置

在 `/etc/v2ray/config.json` 的 `outbounds` 加 `direct`，然后加 `routing` 规则：

```json
{
  "outbounds": [
    {
      "tag": "proxy",
      "protocol": "trojan",
      "settings": {
        "servers": [{
          "address": "你的服务器",
          "port": 443,
          "password": "你的密码"
        }]
      },
      "streamSettings": {
        "network": "tcp",
        "security": "tls",
        "tlsSettings": {
          "serverName": "SNI地址"
        }
      }
    },
    {
      "tag": "direct",
      "protocol": "freedom",
      "settings": {}
    }
  ],
  "routing": {
    "domainStrategy": "IPIfNonMatch",
    "rules": [
      {
        "type": "field",
        "domain": ["geosite:cn", "geosite:private"],
        "outboundTag": "direct"
      },
      {
        "type": "field",
        "ip": ["geoip:cn", "geoip:private"],
        "outboundTag": "direct"
      }
    ]
  }
}
```

## 重启生效

```bash
sudo systemctl restart v2ray
```

## 规则逻辑

| 流量类型 | 匹配规则 | 出口 |
|---------|---------|------|
| 国内网站 | geosite:cn | direct |
| 国内IP | geoip:cn | direct |
| 私有IP | geoip:private | direct |
| 其他（国外） | 未匹配 | proxy |

## Loyalsoldier 精细分流表（可选）

比 geosite:cn 更精准，11.8万条规则

仓库：https://github.com/Loyalsoldier/v2ray-rules-dat

### 文件说明

| 文件 | 数量 | 用途 |
|------|------|------|
| direct-list.txt | 11.8万条 | 国内网站直连 |
| proxy-list.txt | 几千条 | 需要代理的网站 |
| block-list.txt | - | 广告拦截 |

### 下载地址

```
https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/direct-list.txt
https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/proxy-list.txt
https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/block-list.txt
```

### 配置方法

v2ray 支持 domain 规则引用 .txt 文件：

```json
"routing": {
  "domainStrategy": "IPIfNonMatch",
  "rules": [
    {
      "type": "field",
      "domain": [
        "ext:direct-list.txt",
        "geosite:private"
      ],
      "outboundTag": "direct"
    }
  ]
}
```

## 验证分流是否生效

```bash
# 测试国内网站（应该直连，响应快）
time curl -sI --proxy http://127.0.0.1:10809 https://www.baidu.com

# 测试国外网站（走代理）
time curl -sI --proxy http://127.0.0.1:10809 https://github.com
```

## 订阅链接不含分流规则

订阅链接只提供：服务器地址、端口、密码、SNI
分流规则需要自己在本地配置

## 常见错误排查

### "this rule has no effective fields" 启动失败

**症状：** `sudo systemctl start v2ray` 失败，日志报错：
```
main: failed to create server > v2ray.com/core/app/router: this rule has no effective fields
```

**原因：** 新版 v2ray (4.x+) 要求 field 规则必须包含有效匹配条件（domain/ip/protocol 等），空 field 对象不再允许。

**示例 — 错误配置：**
```json
"rules": [
  { "type": "field", "ip": ["geoip:private"], "outboundTag": "direct" },
  { "type": "field", "outboundTag": "proxy" }   // ← 没有 domain/ip/protocol，报错
]
```

**修复：** 删除空 field 规则：
```json
"rules": [
  { "type": "field", "ip": ["geoip:private"], "outboundTag": "direct" },
  { "type": "field", "protocol": ["bittorrent"], "outboundTag": "direct" }
]
```

**验证：**
```bash
sudo systemctl restart v2ray
sudo ss -tlnp | grep -E "10808|10809"  # 端口监听即成功
```

### 国内域名不在 geosite:cn 里导致走代理失败

**症状：** Node.js 应用（如 openclaw）配置 HTTP_PROXY 后，LLM API（如 MiniMax api.minimaxi.com）报 `network connection error`，但直连正常。

**原因：** `geosite:cn` 数据包只覆盖常见国内域名，**LLM 服务商域名（如 api.minimaxi.com）可能不在其中**，被 fallback 到 proxy 规则，代理节点反而访问不了这些国内服务。

**解决：** 在 routing 规则最前面加显式 domain/keyword 规则，确保特定 API 域名直连：

```json
"rules": [
  {
    "type": "field",
    "domain": ["keyword:minimax", "domain:minimaxi.com"],
    "outboundTag": "direct"
  },
  { "type": "field", "ip": ["geoip:private"], "outboundTag": "direct" },
  { "type": "field", "protocol": ["bittorrent"], "outboundTag": "direct" },
  { "type": "field", "domain": ["geosite:cn"], "outboundTag": "direct" },
  { "type": "field", "domain": ["geosite:geolocation-!cn"], "outboundTag": "proxy" }
]
```

**规则顺序很重要**：最具体的规则放前面，v2ray 按顺序匹配，第一个命中的规则生效。`keyword:minimax` 可以匹配任何含 "minimax" 的域名。

### Feishu 走代理返回 503

**症状：** openclaw-gateway 或其他应用走 v2ray 代理时，Feishu API (`open.feishu.cn`) 返回 503，但直连正常。

**原因：** 代理服务器（Trojan 节点）对国内 Feishu 服务不可达或被屏蔽。

**解决：** 在 routing 规则中把 `geosite:cn` 放在 proxy 规则之前，**国内网站全部直连**，只有明确需要代理的才走 proxy：
```json
"routing": {
  "domainStrategy": "IPIfNonMatch",
  "rules": [
    { "type": "field", "ip": ["geoip:private"], "outboundTag": "direct" },
    { "type": "field", "protocol": ["bittorrent"], "outboundTag": "direct" },
    { "type": "field", "domain": ["geosite:cn"], "outboundTag": "direct" },
    { "type": "field", "domain": ["geosite:geolocation-!cn"], "outboundTag": "proxy" }
  ]
}
```

**不要用 NO_PROXY 排除国内域名**，正确做法是分流规则本身就把国内流量引向 direct。

### v2ray Trojan TLS 转发失败（4.34.0 bug）— 完整修复流程

**症状：**
- `curl --proxy http://127.0.0.1:10809 https://github.com` 返回 000
- `journalctl` 有 `crypto/hmac: hash generation function does not produce unique values` panic
- Trojan 节点本身 TLS 连通正常（`openssl s_client` 能握手），但协议转发到境外目标失败
- VMess 节点同样报 AEAD handshake failure

**原因：** v2ray 4.34.0（Go 1.17 编译）有双重 bug：
1. VMess AEAD 实现触发 crypto panic
2. Trojan 协议转发到境外网站失败（TLS 层面正常但应用层失败）

**标准解法（按优先级）：**

#### 方案A：用 Xray 替换 v2ray（推荐）

Xray 是 v2ray 的 fork，对 Trojan/VMess 的修复更及时。

**步骤：**
```bash
# 1. 检查 Go 版本（需要 Go 1.21+，系统旧版可能不够）
go version
# 如果是 Go 1.18/1.19/1.20，需要先装新版：
wget https://go.dev/dl/go1.24.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.24.0.linux-amd64.tar.gz
export PATH=/usr/local/go/bin:$PATH

# 2. 编译 Xray（git clone 源码，避免下载 release 超时）
cd /tmp
git clone --depth=1 https://github.com/XTLS/Xray-core.git
cd Xray-core
go build -o /tmp/xray-test ./main

# 3. 测试（直接用编译出的二进制，不需要安装）
/tmp/xray-test run -c /path/to/config.json

# 4. 正式安装为 systemd service
sudo cp /tmp/xray-test /usr/local/bin/xray
sudo chmod +x /usr/local/bin/xray
# 写入 /etc/systemd/system/xray.service（参考官方模板）
sudo systemctl daemon-reload
sudo systemctl enable --now xray
```

**配置示例（/etc/xray/config.json）：**
```json
{
  "inbounds": [
    {
      "tag": "socks-in",
      "protocol": "socks",
      "listen": "127.0.0.1",
      "port": 10808,
      "settings": {"auth": "noauth"}
    },
    {
      "tag": "http-in",
      "protocol": "http",
      "listen": "127.0.0.1",
      "port": 10809
    }
  ],
  "outbounds": [
    {
      "tag": "vmess-ws",
      "protocol": "vmess",
      "settings": {"vnext": [{"address": "your-server.com", "port": 443, "users": [{"id": "UUID", "alterId": 0}]}]},
      "streamSettings": {
        "network": "ws",
        "wsSettings": {"path": "/"},
        "security": "tls",
        "tlsSettings": {"serverName": "sni-hostname"}
      }
    },
    {
      "tag": "direct",
      "protocol": "freedom",
      "settings": {}
    }
  ],
  "routing": {
    "domainStrategy": "IPIfNonMatch",
    "rules": [
      {"type": "field", "ip": ["geoip:private"], "outboundTag": "direct"},
      {"type": "field", "domain": ["geosite:cn"], "outboundTag": "direct"},
      {"type": "field", "outboundTag": "vmess-ws"}
    ]
  }
}
```

**验证：**
```bash
sudo systemctl status xray
curl -sI --proxy http://127.0.0.1:10809 https://github.com
curl -sI --proxy http://127.0.0.1:10809 https://www.baidu.com  # 国内直连
```

#### 方案B：v2raya 管理界面（如果已安装）

```bash
sudo systemctl start v2raya
curl http://127.0.0.1:2017  # 访问管理界面
```
v2raya 自带更新的 core，不依赖系统旧版 v2ray。导入订阅即可。

#### 方案C：换节点（临时）

如果 Trojan 节点全部失败，尝试：
1. 解码备用订阅（`base64 -d`）找 VMess WebSocket 节点
2. 在 Xray/v2ray 配置中换成 VMess WebSocket outbound
3. VMess+WebSocket 的兼容性比 Trojan 更好

### 定时检测 & 自动切换订阅节点

**背景：** 主订阅为 Trojan 节点（zz.xg01.fogvip-zz.uk:40001），备用为 VMess WebSocket（planb.mojcn.com:16632）。每3天测试 Trojan 连通性，能通则切换回主订阅。

**测试脚本逻辑：**
```python
#!/usr/bin/env python3
# test_trojan.py — 测试 Trojan 节点是否可达
import socket, ssl

def test_trojan(host, port, target_host='github.com', target_port=443):
    """测试 Trojan 节点是否能通过代理访问境外网站"""
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=10) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            # 发送 CONNECT 请求测试代理转发
            req = f"CONNECT {target_host}:{target_port} HTTP/1.1\r\nHost: {target_host}\r\n\r\n"
            ssock.sendall(req.encode())
            resp = ssock.recv(4096)
            return b"200" in resp or b"Connection established" in resp

# Trojan 主节点
print("测试 Trojan:", test_trojan("zz.xg01.fogvip-zz.uk", 40001))
```

**Cron 表达式：** `0 0 */3 * *`（每3天 00:00 执行）

**切换配置后 reload：**
```bash
sudo systemctl kill -s SIGHUP xray
# 或
sudo systemctl restart xray
```

**订阅信息记录：**
- 主订阅（Trojan）：`https://dawson0207.xn--3iq226gfdb94q.com/api/v1/client/subscribe?token=...`
- 备用订阅（VMess WS）：`https://47.242.128.61:5000/api/v1/client/subscribe?token=...`
- VMess WS 节点池：planb.mojcn.com (端口 16616/16617/16618/16622/16626/16632/16641/16644/16645/16648)，UUID: af820a86-a313-4ad6-9c7e-6c5d970c47c8，Host: 2b23f30244aa7117a6de2be7683ccd4f.mobgslb.tbcache.com，Path: /

### v2raya 替代方案

**已安装：** v2rayA 管理界面，监听 2017 端口
```bash
sudo systemctl start v2raya   # 启动
curl http://127.0.0.1:2017   # 访问管理界面
```
v2raya 会拉取自己的 v2ray core，不依赖系统旧版 v2ray。

### 服务器直连 GitHub 注意事项

**重要发现：** 腾讯云服务器（CN IP）可以直接访问 github.com，`curl https://github.com` 返回 200。git clone 也不需要代理。

**只有代理坏了的情况：** 如果 v2ray Trojan/VMess 代理本身故障，但服务器直连正常，可以：
- git clone / git push 直接走直连
- pip install（腾讯云镜像）不需要代理
- npm install（国内镜像）不需要代理

**不要再假设"GitHub 必须走代理"。** 腾讯云国际出口本来就通，代理只是用于分流/隐私。

## geo数据文件位置

```
/usr/share/v2ray/geosite.dat
/usr/share/v2ray/geoip.dat
```
