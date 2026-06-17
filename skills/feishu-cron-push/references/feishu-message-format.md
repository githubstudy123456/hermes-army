# 飞书消息推送格式（已验证 2026-05）

## 两种推送机制的区别

### 1. 文件落地 + cron 检测推送（**旧方案，有格式问题**）

cron job 的 `deliver` 设为 `feishu:oc_xxx`，脚本把内容写入 `~/.hermes/cron/output/{job_id}/` 目录。
**问题：** 飞书收到的是原始 markdown 文本，飞书**不渲染**粗体/斜体/代码块等格式，用户看到的是未处理的原始内容。

### 2. 脚本内部调 API 直接推送（**正确方案**）

脚本内部获取 `tenant_access_token`，直接调 `/open-apis/im/v1/messages` API，cron job 的 `deliver` 设为 `local`。

## 正确推送代码模板

```python
import urllib.request, json

APP_ID = "cli_a95612fc9ebddbc8"
APP_SECRET = "TBNvucvbHCHTeKqYtQ7PGfu1ANe0FSmb"
CHAT_ID = "oc_c6883cd907e4d226736d87ce9c6c6d79"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode()).get("tenant_access_token", "")

def send_feishu(text: str, token: str):
    """发送文本消息到飞书群"""
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    payload = {
        "receive_id": CHAT_ID,
        "msg_type": "text",
        "content": json.dumps({"text": text})  # ⚠️ 必须双重序列化
    }
    req = urllib.request.Request(url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
        resp = json.loads(r.read().decode())
        if resp.get("code") != 0:
            print(f"推送失败: {resp}")
        return resp

# 使用
token = get_token()
send_feishu(markdown_content, token)
```

## ⚠️ 关键坑：content 字段必须双重序列化

```python
# 正确 ✅
"content": json.dumps({"text": text})

# 错误 ❌ — 会导致 19001 或 content 格式错误
"content": {"text": text}
"content": text
```

飞书 API 要求 `content` 字段是一个 **JSON 字符串**（序列化后的对象），不是对象本身。这是跨语言 API 的常见陷阱。

## 已知不可用的推送方式

| 方式 | 错误 | 原因 |
|------|------|------|
| Webhook `/open-apis/bot/v2/hook/` | 19001 invalid token | 这是老版机器人协议，已废弃 |
| `im/v1/messages` 但 content 是 dict | 1770001 block error | content 必须是 JSON 字符串 |

## 调试方法

推送后检查返回的 `code`：
- `0` = 成功
- `99992402` = 参数校验失败（通常是 content 未序列化或缺少 `receive_id_type` 查询参数）
- `19001` = webhook token 相关错误（用了废弃的 webhook 模式）
- `230002` = bot 不在群里
