# Weixin (WeChat) 调试参考

## 常见故障排查

### 1. Session Expired（最常见）
**症状：** gateway.log 里持续出现 `ERROR gateway.platforms.weixin: [Weixin] Session expired; pausing for 10 minutes`

**根因：** iLink bot token 过期（微信服务端行为，非 Hermes 配置问题）

**排查步骤：**
```bash
# 查看当前 token 状态
cat ~/.hermes/weixin/accounts/*.json

# 查看最近过期时间
grep "Session expired\|Saved at" ~/.hermes/logs/gateway.log | tail -5
```

**处理：**重新扫码授权（见下文）

---

### 2. QR 登录时报 DNS 解析失败
**症状：** `ClientConnectorDNSError: Cannot connect to host ilinkai.weixin.qq.comilink:443`

**根因：** weixin.py 代码里 `ILINK_BASE_URL = "https://ilinkai.weixin.qq.com"` 末尾没有 `/`，直接拼接 `EP_GET_BOT_QR = "ilink/bot/get_bot_qrcode"` 导致 URL 变成 `https://ilinkai.weixin.qq.comilink/...`（少了斜杠）。aiohttp 对这种畸形 URL 做 DNS 解析时会失败。

**注意：** 这是 weixin.py 自身代码的 bug，不是网络问题。curl 能正常工作因为 curl 对 URL 拼接更宽松。

**Workaround：** 用 curl 直接取 QR，避免通过 Python aiohttp：
```bash
curl -s "https://ilinkai.weixin.qq.com/ilink/bot/get_bot_qrcode?bot_type=3"
```

返回格式：
```json
{"qrcode":"<hex>","qrcode_img_content":"https://liteapp.weixin.qq.com/q/...?qrcode=<hex>&bot_type=3","ret":0}
```

取到 `qrcode_img_content` 后，用 qrcode 库生成图片：
```python
import qrcode
img = qrcode.make(qrcode_img_content)
img.save('/home/ubuntu/weixin_qr.png')
```

---

### 3. Token 刷新机制
- `_poll_loop` 检测到 `errcode=-14`（SESSION_EXPIRED_ERRCODE）时自动 pause 10 分钟重试
- 重试还是过期会继续 pause，导致永久卡住
- **唯一解：** 重新扫码

---

## 重新扫码授权步骤（2026-06-11 验证通过）

### 方式 A：交互式（本地终端）
```bash
hermes gateway stop
hermes gateway setup
# 选 Weixin / WeChat → Reconfigure → Start QR login now → 手机扫码
hermes gateway start
```

### 方式 B：远程服务器（SSH，无图形终端）— 完整流程

**已知限制：** 飞书 `im/v1/images` 上传始终返回 `{"code":234001,"msg":"Invalid request param"}`，图片推送走不通。改用文本消息推送 QR 链接。

```bash
# 1. 彻底停止所有 gateway 进程
hermes gateway stop
pkill -f "hermes.*gateway"
sleep 2

# 2. 确认干净
ps aux | grep "hermes.*gateway" | grep -v grep
# 应无输出

# 3. 写 qr_login 脚本
cat > /home/ubuntu/weixin_qr_login6.py << 'PYEOF'
#!/usr/bin/env python3
import asyncio, sys, os, signal

sys.path.insert(0, os.path.expanduser('~/.hermes/hermes-agent'))
os.chdir(os.path.expanduser('~/.hermes/hermes-agent'))   # 必须在导入前 chdir

from gateway.platforms.weixin import qr_login

HERMES_HOME = os.path.expanduser('~/.hermes')

def handle_term(signum, frame):
    print("收到退出信号")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_term)

async def main():
    print("生成微信登录二维码，请扫码...")
    result = await qr_login(HERMES_HOME)   # qr_login(hermes_home) 位置参数
    if result:
        print(f"登录成功: account_id={result.get('account_id','')[:20]}...")
        return 0
    else:
        print("登录失败或超时")
        return 1

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
PYEOF

# 4. 后台运行
cd ~/.hermes/hermes-agent && ~/.hermes/hermes-agent/venv/bin/python /home/ubuntu/weixin_qr_login6.py > /tmp/weixin_qr6.log 2>&1 &
echo "QR进程 PID=$!"

# 5. 等 QR 生成，看日志
sleep 4 && cat /tmp/weixin_qr6.log
# 看到 ASCII QR 二维码和 "请使用微信扫描以下二维码：" 及链接

# 6. 从日志提取链接，发到飞书群（文字消息）
# 链接格式：https://liteapp.weixin.qq.com/q/<id>?qrcode=<hex>&bot_type=3

# 7. 用户扫码后，日志出现 "登录成功" 或 超时（480秒）后 "登录失败或超时"

# 8. 确认 token 更新
cat ~/.hermes/weixin/accounts/*.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('saved_at:', d.get('saved_at','?'))"

# 9. 重启 gateway
hermes gateway start
```

**关键细节（踩坑记录）：**
- `qr_login` 是 `async def` 返回 dict，**不是** `async generator`（不 yield 二元组）
- 必须传 `hermes_home` 位置参数：`await qr_login(HERMES_HOME)`
- 导入前必须 `os.chdir(hermes-agent目录)` 否则模块加载路径可能出错
- Gateway 彻底停掉前不要跑 qr_login，多进程会报 `Weixin bot token already in use`
- 二维码链接格式：`https://liteapp.weixin.qq.com/q/<id>?qrcode=<hex>&bot_type=3`，这是微信专属 URL，非网页 URL
- 手机微信扫一扫：从相册选二维码（需将链接转成 PNG）；或在微信 PC 端文件传输助手打开链接

### 方式 C：直接用 hermes gateway setup（需终端支持 UTF-8 显示）
SSH 终端支持 UTF-8 图形的话，直接跑 `hermes gateway setup`，会打印 ASCII QR 和 URL 链接。

---

## 多 gateway 进程冲突（Session already in use）

**症状：** `ERROR gateway.platforms.base: [Weixin] Weixin bot token already in use (PID N). Stop the other gateway first.`

**根因：** 同时跑着多个 gateway 进程，token 被先启动的占用，后启动的连不上。

**排查：**
```bash
ps aux | grep "hermes.*gateway" | grep -v grep
```

**修复步骤：**
```bash
# 1. 停掉所有 gateway
hermes gateway stop

# 2. 杀掉残留进程
pkill -f "hermes.*gateway"
pkill -f "weixin.*qr_login"

# 3. 确认干净
ps aux | grep "hermes.*gateway" | grep -v grep
# 应该无输出

# 4. 再重新扫码 + 启动
```

---

## QR 链接的格式与正确用法（重要）

微信返回的 QR URL 格式：`https://liteapp.weixin.qq.com/q/...?qrcode=...&bot_type=3`

**这不是网页链接**，不能用手机浏览器打开。正确用法：
- 在**微信 PC 端** → 文件传输助手 → 粘贴链接 → 自动弹出扫码界面
- 在**微信手机端** → 扫一扫 → 从相册选二维码（需将链接转成 PNG 图片才能扫）

生成二维码图片：
```python
import qrcode

qr_url = "https://liteapp.weixin.qq.com/q/...?qrcode=...&bot_type=3"
img = qrcode.make(qr_url)
img.save('/tmp/weixin_qr.png')
```

---

## 后台 qr_login 进程 stdout 不写入日志文件的问题

**症状：** 用 `terminal(background=true)` 跑 qr_login，日志文件查不到输出。

**根因：** qr_login 内部 print 到 stdout，但 stdout 被后台进程机制捕获，不写日志文件。

**解决：** 手动重定向到文件：
```bash
cd ~/.hermes/hermes-agent && ~/.hermes/hermes-agent/venv/bin/python /home/ubuntu/weixin_qr_login6.py > /tmp/weixin_qr6.log 2>&1 &
```
读取日志用 `process(action='log')` 而不是找日志文件。

---

## 飞书图片上传（2026-06-11 验证通过）

**结论：API 本身是通的，问题在 bot 不在群里。**

正确的上传方式（已有有效 tenant_access_token 时）：
```bash
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/images" \
  -H "Authorization: Bearer $TOKEN" \
  -F "image_type=message" \
  -F "image=@/tmp/weixin_qr.png"
# 返回 {"code":0,"data":{"image_key":"img_v3_..."},"msg":"success"}
```

发送图片消息（需要 bot 在群里才能发）：
```bash
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"receive_id":"<chat_id>","msg_type":"image","content":"{\"image_key\":\"<image_key>\"}"}'
# 失败返回：{"code":230002,"msg":"Bot/User can NOT be out of the chat."}
```

**如果 bot 不在群里**（错误码 230002），图片发不进去，换用文字消息推送 QR 链接（webhook 不需要加群）。

获取 tenant_access_token：
```bash
curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id":"<app_id>","app_secret":"<app_secret>"}'
```

---

## 飞书图片上传持续失败（历史记录，可忽略）

`POST /open-apis/im/v1/images?image_type=message` 之前返回 `{"code":234001,"msg":"Invalid request param"}`，已解决——API 本身是通的。

如需上传图片到飞书，正确的 tenant_access_token 获取方式：
如需上传图片到飞书，正确的 tenant_access_token 获取方式：
```python
import subprocess

pid = subprocess.check_output(["pgrep", "-f", "hermes.*gateway"]).decode().split()[0]
with open(f'/proc/{pid}/environ', 'rb') as f:
    data = f.read()
env = {}
for item in data.split(b'\x00'):
    if b'=' in item:
        k, v = item.split(b'=', 1)
        env[k.decode()] = v.decode()

app_id = env.get('FEISHU_APP_ID', '')
app_secret = env.get('FEISHU_APP_SECRET', '')
# 然后 POST https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal
```

---

## 验证是否修复
```bash
hermes gateway status
# 期望看到 ✓ weixin connected 且无 Session expired 错误

tail -f ~/.hermes/logs/gateway.log | grep weixin
# 期望：getUpdates 正常返回，无 expired
```