# WeChatBot Token 登录流程

## 登录 token 生成

重启后原有的登录 token 会失效（因为 `DISABLE_AUTO_LOGIN=false` 时 token 和微信 session 绑定）。生成新 token：

```bash
cd ~/wechatbot
node -e "const generateToken = require('./packages/cli/lib/generateToken'); console.log(generateToken())"
```

输出示例：`4lvG5W_su2IU`

## 写入 .env

```bash
# 方式1：sed 精确替换（推荐）
sed -i 's/^LOCAL_LOGIN_API_TOKEN=.*/LOCAL_LOGIN_API_TOKEN=4lvG5W_su2IU/' .env

# 方式2：确认写入成功（读原始字节）
python3 -c "
with open('.env', 'rb') as f:
    raw = f.read()
idx = raw.find(b'LOCAL_LOGIN')
print(raw[idx:idx+40])
"
```

## 登录地址

```
http://81.71.93.113:3002/login?token=4lvG5W_su2IU
```

扫码后 token 生效，机器人变为已登录状态。

## 登录地址格式

```
http://<服务器公网IP>:3002/login?token=<token>
```

本地监听 `3002`，需用**公网IP**访问。获取公网IP：

```bash
curl -s ifconfig.me
# 或
curl -s ipinfo.io/ip
```

> 本次服务器公网IP：`81.71.93.113`（2026-06-16 session）

## 判断是否需要重新扫码

| 现象 | 原因 | 解法 |
|------|------|------|
| 访问 `/login?token=xxx` 返回 `Unauthorized` | token 不匹配或已过期 | 重新生成 token |
| 扫码页面能打开但扫码后无效 | 微信风控/协议问题 | 等待或重启服务 |
| `pnpm start` 直接显示已登录 | 有持久化 session | 无需操作 |

## 进程架构

**微信机器人不是 Docker 容器**，是直接跑在服务器上的 Node 进程。

```bash
# 查找进程
ps aux | grep "node main.js" | grep -v grep
# 输出：ubuntu 1794244 node main.js   ← 直接kill即可

# 查找端口
ss -tlnp | grep 3002
# 输出：LISTEN 0.0.0.0:3002

# Docker 和 systemctl 里找不到是正常的
```

## Session 持久化

`DISABLE_AUTO_LOGIN=`（空）时，项目会把登录态写入 `wechaty-puppet-wechat.state.json`。重启后自动恢复，无需扫码。

但 token 本身也会过期，如果 token 变了而 session 还在，可能需要同时满足两者。