# 微信（Weixin）Token 过期重新授权流程

## 症状

gateway 日志出现：
```
ERROR gateway.platforms.weixin: [Weixin] Session expired; pausing for 10 minutes
```
微信 bot 完全不响应消息，但 gateway 显示 `weixin connected`。

## 根因

微信 iLink 平台的 bot session token 有时效限制，过期后需要重新扫码授权。

## 排查步骤

```bash
# 1. 查看 gateway 日志确认是 session expire
grep -i "weixin\|expired\|session" ~/.hermes/logs/gateway.log | tail -20

# 2. 查看现有 token
cat ~/.hermes/weixin/accounts/*.json
# 记录 saved_at 时间，确认是否已过期
```

## 重新授权流程

### 第一步：获取新二维码

微信 iLink API 直接获取二维码（无需停 gateway）：

```bash
curl -s "https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3"
```

返回：
```json
{
  "qrcode": "60067b4708eecd4870b0a3c52b73fe21",
  "qrcode_img_content": "https://liteapp.weixin.qq.com/q/7GiQu1?qrcode=60067b4708eecd4870b0a3c52b73fe21&bot_type=3",
  "ret": 0
}
```

**URL 拼接注意：** `ILINK_BASE_URL = "https://ilinkai.weixin.qq.com"` + `EP_GET_BOT_QR = "ilink/bot/get_bot_qrcode"` 必须在中间加 `/`。正确完整 URL：
```
https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3
```

> ⚠️ Hermes 源码里 `qr_login()` 函数存在 URL 拼接 bug：没有在 base URL 末尾加 `/`，导致 aiohttp DNS 解析失败（`ilinkai.weixin.qq.comilink` 连在一起）。用 curl 直接拼是正确的。

### 第二步：把二维码发给用户扫码

方式① **文本消息发链接**（推荐，成功率最高）：
```bash
# 用飞书发链接给用户（token 获取见 feishu-message-format.md）
python3 -c "
import json
payload = {
    'receive_id': 'oc_c6883cd907e4d226736d87ce9c6c6d79',
    'msg_type': 'text',
    'content': json.dumps({'text': '微信登录二维码（手机微信扫码）：\nhttps://liteapp.weixin.qq.com/q/xxx'})
}
print(json.dumps(payload))
" > /tmp/feishu_msg.json

TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id": "cli_a95612fc9ebddbc8", "app_secret": "TBNvucvbHCHTeKqYtQ7PGfu1ANe0FSmb"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")

curl -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/feishu_msg.json
```

方式② **生成 QR code 图片**（如果图片能公网访问）：
```bash
# 服务器上生成图片
~/.hermes/hermes-agent/venv/bin/python3 -c "
import qrcode
url = 'https://liteapp.weixin.qq.com/q/xxx'
img = qrcode.make(url)
img.save('/home/ubuntu/weixin_qr.png')
"

# 图片发到飞书群：用 MEDIA 标签（gateway 收到后自动处理）
# 在群消息里发：MEDIA:/home/ubuntu/weixin_qr.png
```

方式③ **SCP 下载到本地**：用户本地执行 `scp ubuntu@服务器IP:/home/ubuntu/weixin_qr.png ./`

### 第三步：用户扫码确认后，重启 gateway

```bash
hermes gateway restart
```

确认连接：
```bash
hermes gateway status
# 应该看到 ✓ weixin connected 且没有 Session expired 错误
```

## 已知限制

- iLink QR login 生成的是 `...@im.bot` 类型的 bot 身份
- 这种 bot 身份通常**无法**被加入普通微信群（只能 DM）
- 如果需要群功能，需要在微信公众平台申请不同类型的应用
