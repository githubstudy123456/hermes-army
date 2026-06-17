# VLESS + REALITY 协议详解

> 基于日本服务器 207.56.226.147 实际配置整理，2026-05-17

---

## 一、VLESS vs VMess vs Trojan

| 协议 | 加密 | 身份验证 | 伪装修复 | 备注 |
|------|------|---------|---------|------|
| VMess | 内部加密 | UUID+时间 | 无，需要 TLS 伪装 | 老协议，逐渐淘汰 |
| Trojan | TLS 伪装 | 密码 | 无，依赖 TLS SNI | 简单稳定 |
| VLESS | TLS | UUID（无时间） | 无，需要 REALITY | 性能好，无时间检测 |
| VLESS+REALITY | TLS | UUID | **有**（流量伪装） | 当前最优方案 |

**REALITY 的核心价值：流量伪装**

VMess/Trojan 的问题是：流量加密了，但审查者能看出"这是翻墙流量"（因为TLS握手特征或者目标IP）。

REALITY 的做法：
```
发往 amazon.com:443 的流量 → 但实际是翻墙代理
审查系统：看到的是 → "正常访问亚马逊" → 不封锁
```

---

## 二、配置结构（/etc/xray/config.json）

```json
{
  "inbounds": [{
    "port": 443,
    "protocol": "vless",
    "settings": {
      "clients": [{
        "id": "b831381d-6324-4d53-ad4f-8cda48b30811",
        "flow": "xtls-rprx-vision"
      }]
    },
    "streamSettings": {
      "network": "tcp",
      "security": "reality",
      "realitySettings": {
        "dest": "www.amazon.com:443",
        "serverNames": ["www.amazon.com", "www.amazon.co.uk", "www.amazon.de"],
        "privateKey": "mKskS4r2l68V3Zf-MHyxon2q3gax-1-FZCbxYI_3rXI",
        "shortIds": ["abcd1234"]
      }
    },
    "sniffing": { "enabled": true, "destOverride": ["http", "tls"] }
  }],
  "outbounds": [
    { "protocol": "freedom", "tag": "direct" },
    { "protocol": "blackhole", "tag": "block" }
  ]
}
```

### 关键字段解析

| 字段 | 值 | 含义 |
|------|-----|------|
| `protocol` | vless | 不是 vmess，VLESS 无时间验证 |
| `id` (UUID) | b831381d-... | 用户凭证，客户端需要匹配 |
| `flow` | xtls-rprx-vision | 浏览器/客户端兼容模式 |
| `network` | tcp | 传输层 |
| `security` | reality | 启用 REALITY 流量伪装 |
| `dest` | www.amazon.com:443 | 伪装目标（告诉审查者这是访问亚马逊） |
| `serverNames` | amazon.com 系列 | 允许的伪装域名列表 |
| `sniffing` | 开启 | 读取实际访问目标，辅助路由 |

---

## 三、REALITY 流量伪装原理

### 步骤1：客户端发出请求
```
你的浏览器 → 访问 google.com
↓ 加密（TLS）
→ 发往 207.56.226.147:443
```

### 步骤2：服务器接收并解密
```
207.56.226.147:443 的 Xray 接收流量
↓ 解密 TLS
→ 看到 UUID: b831381d-... → 验证通过
```

### 步骤3：REALITY 掉包
```
原始目标：google.com
↓
REALITY 把请求"掉包"
伪装成访问 www.amazon.com:443
（审查系统看到这个包，会认为是正常浏览亚马逊）
```

### 步骤4：REALITY 再次掉包
```
亚马逊返回内容（真实浏览亚马逊的内容）
↓
REALITY 把内容"掉包"
换回 google.com 的内容
```

### 步骤5：加密返回
```
→ 通过 TLS 加密 → 回到你的 Xray 客户端
→ 解密 → 你的浏览器看到 google.com
```

---

## 四、监听端口的含义

**443端口守门员：**

```
任何发到 207.56.226.147:443 的流量
         ↓
   Xray/VLESS 守门员接收
         ↓
   验证 UUID 是否正确
         ↓
   正确 → REALITY 掉包 → 帮你翻墙
   错误 → 直接拒绝（不是转发）
```

**结论：服务器不会帮别人转发**

配置里只有1个UUID（你自己的），别人没有正确凭证，根本进不来。443端口就像一个需要钥匙的门。

---

## 五、加密层级

| 层级 | 技术 | 说明 |
|------|------|------|
| 传输加密 | TLS | 和 HTTPS 网站一样强，任何人中途都看不到内容 |
| 身份验证 | UUID | 每个用户独立凭证 |
| 流量伪装 | REALITY | 审查者看不出你在翻墙 |

---

## 六、获取订阅链接

VLESS+REALITY 节点不是从服务器直接获取的，配置里没有订阅功能。

**如果是机场（代理商）节点：**
- 订阅链接从代理商后台获取
- 格式：`https://<代理商域名>/api/v1/client/subscribe?token=xxx`

**如果是自建节点：**
- 需要自己搭建 VLESS+REALITY
- 客户端配置需要：地址、端口、UUID、flow、security=reality
- `dest` 和 `serverNames` 需要与服务器配置一致

---

## 七、与其他翻墙协议的对比

| 协议 | 隐蔽性 | 性能 | 配置难度 | 备注 |
|------|--------|------|---------|------|
| OpenVPN | 低（UDP容易被识别） | 一般 | 中 | 容易被封锁 |
| Shadowsocks | 中（协议特征明显） | 好 | 低 | 国内已大部分被封 |
| WireGuard | 低（容易被识别） | 最好 | 中 | 特征明显 |
| Trojan | 高（依赖TLS） | 好 | 中 | 需要有效域名 |
| VLESS+REALITY | **最高** | 好 | 中 | 当前最优解 |