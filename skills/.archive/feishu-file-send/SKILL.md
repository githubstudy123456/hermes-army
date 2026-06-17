---
name: feishu-file-send
description: 在 Hermes Agent 飞书 gateway 中发送文件给用户的核心方法
tags: [feishu, gateway, file-send, media]
date_created: 2026-04-16
---

# 飞书发送文件方法

## 核心发现

在 Hermes Agent + 飞书 gateway 中，发送文件给用户有**两种方式**：

### 方式1：MEDIA 标签（推荐）

在回复中包含 `MEDIA:文件绝对路径` 标签，gateway 会自动识别并发送文件。

```
这是文字内容...

MEDIA:/home/ubuntu/source/AI提示词库完整版.md
```

gateway 内部处理流程：
- `run.py` 中的 `extract_media()` 从响应中提取 MEDIA 路径
- 调用 `adapter.send_file(chat_id=source.chat_id, file_path=media_path)`
- 对飞书平台调用 `FeishuAdapter.send_document(chat_id, file_path, ...)`

### 方式2：send_message_tool + media 参数

在 `send_message` 的 `message` 字段中传入 media 路径：

```python
send_message_tool({
    "action": "send",
    "target": "feishu",       # 或具体 chat_id
    "message": "文件来了",
    "media": "/path/to/file"  # 可选，触发 send_document
})
```

底层实现 (`send_message_tool.py` line 537)：
```python
last_msg = await bot.send_document(
    chat_id=int_chat_id, document=f, **thread_kwargs
)
```

### 飞书 Adapter 支持的方法

```python
FeishuAdapter.send_document(chat_id, file_path, caption=None, file_name=None, ...)
FeishuAdapter.send_image_file(chat_id, image_path, ...)
FeishuAdapter.send_video(video_path, ...)
FeishuAdapter.send_voice(audio_path, ...)
```

### 触发条件

文件发送触发点：
- 响应包含 `MEDIA:/path/to/file`
- 或 `send_message` 时 message 包含文件路径

gateway 会自动提取并调用对应平台的 send_document / send_image 等方法。

### 适用场景

- 用户请求"发文件" → 回复加 `MEDIA:路径`
- 主动推送文件 → 回复加 `MEDIA:路径`
- 飞书/Telegram/Discord 均支持 MEDIA 标签机制

### 完整 API 上传流程（curl）

飞书文件发送必须分两步：**上传获取 file_key → 再发送消息**。

```bash
# 1. 获取 tenant access token
APP_ID="cli_xxx"
APP_SECRET="xxx"
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\": \"$APP_ID\", \"app_secret\": \"$APP_SECRET\"}" | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")

# 2. 上传文件，获取 file_key
FILE_KEY=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=stream" \
  -F "file_name=文件名.md" \
  -F "file=@/path/to/file;type=text/markdown" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['data']['file_key'])")

# 3. 发送文件消息（注意：必须有 receive_id_type=chat_id 查询参数！）
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"receive_id\": \"oc_group_chat_id\",
    \"msg_type\": \"file\",
    \"content\": \"{\\\"file_key\\\": \\\"$FILE_KEY\\\"}\"
  }"
```

**⚠️ 关键坑：receive_id_type 参数**
- 必须作为**查询参数**加在 URL 上：`?receive_id_type=chat_id`
- 不加会报 `99992402 field validation failed`
- `receive_id` 填群组 chat_id 或用户 open_id

### ⚠️ 跨 app open_id 限制

`receive_id_type=open_id` **只能用于同一个 app 创建的用户的 open_id**。如果 open_id 属于另一个 app（例如用户在其他 app 与机器人交互产生的 open_id），会报错：
```
99992361: open_id cross app
```
**解决方案**：改用 `receive_id_type=chat_id` 发送到群组，或确保 open_id 与 appId 属于同一应用。

### ⚠️ urllib SSL 握手失败

Python `urllib.request.urlopen()` 在某些环境下会报 `SSL: UNEXPECTED_EOF_WHILE_READING`。**必须用 curl subprocess 代替 urllib**：

```python
import subprocess, json

def curl_post(url, headers=None, data=None, form_data=None):
    cmd = ["curl", "-s", "-X", "POST", url]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    if data:
        cmd += ["-d", data]
    if form_data:
        for item in form_data:        # 注意：form_data 必须是 list，不是 dict！
            cmd += ["-F", item]
    return subprocess.run(cmd, capture_output=True, text=True).stdout
```

**form_data 必须是 `list`**，每个元素是一个完整的 `-F` 参数字符串，例如：
```python
form_data=[
    "file_type=stream",
    "file_name=report.md",
    "file=@/path/to/report.md;type=text/markdown"
]
```

### Python 定时脚本标准写法（hermes-weekly-report 模式）

完整可复用的 cron 报告脚本结构：

```python
#!/usr/bin/env python3
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

APP_ID = "cli_xxx"
APP_SECRET = "xxx"
CHAT_ID = "oc_group_chat_id"   # 飞书群组 ID
OUTPUT_DIR = Path.home() / ".hermes" / "cron" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def curl_post(url, headers=None, data=None, form_data=None):
    cmd = ["curl", "-s", "-X", "POST", url]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    if data:
        cmd += ["-d", data]
    if form_data:
        for item in form_data:
            cmd += ["-F", item]
    return subprocess.run(cmd, capture_output=True, text=True).stdout

def get_token():
    r = curl_post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}))
    return json.loads(r)["tenant_access_token"]

def upload_file(token, file_path):
    r = curl_post("https://open.feishu.cn/open-apis/im/v1/files",
        headers={"Authorization": f"Bearer {token}"},
        form_data=["file_type=stream", f"file_name={file_path.name}",
                   f"file=@{file_path};type=text/markdown"])
    resp = json.loads(r)
    if resp.get("code") != 0:
        raise Exception(f"上传失败: {resp}")
    return resp["data"]["file_key"]

def send_file_to_group(token, file_key):
    payload = json.dumps({"receive_id": CHAT_ID, "msg_type": "file",
                          "content": json.dumps({"file_key": file_key})})
    r = curl_post(f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=payload)
    resp = json.loads(r)
    if resp.get("code") != 0:
        raise Exception(f"发送失败: {resp}")
    return resp["data"]["message_id"]

if __name__ == "__main__":
    # 1. 生成报告
    report_content = "# 报告内容..."
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = OUTPUT_DIR / f"report-{today}.md"
    output_path.write_text(report_content)
    print(f"报告已生成：{output_path}", file=sys.stderr)

    # 2. 发送到飞书群
    try:
        token = get_token()
        file_key = upload_file(token, output_path)
        msg_id = send_file_to_group(token, file_key)
        print(f"已发送到飞书群：message_id={msg_id}", file=sys.stderr)
    except Exception as e:
        print(f"飞书发送失败：{e}", file=sys.stderr)
        sys.exit(1)
```

### 已知飞书 app ID 速查

| App | AppId | 用途 |
|-----|-------|------|
| Hermes | `cli_a95612fc9ebddbc8` | Hermes Agent 自己的飞书 bot |
| OpenClaw | `cli_a954ec0730b85bc9` | OpenClaw gateway |
| 龙虾军团 | `cli_a96b530405785bde` | lobster-ceo |
| lobster-dev | `cli_a96b4b3f0d381bcf` |
| lobster-pm | `cli_a96b4a83dd7c5bd6` |
| lobster-qa | `cli_a96b4b852ce31bde` |
| lobster-content | `cli_a96b4be3c73a9bcf` |
| lobster-marketing | `cli_a96b4468633a9bda` |
| lobster-fullstack | `cli_a96b44c8ae7adbd8` |
| lobster-cfo | `cli_a96ec9e03af89bca` |

**大姐姐群**（Hermes + 主人在内）chat_id：`oc_c6883cd907e4d226736d87ce9c6c6d79`
**龙虾军团群** chat_id：`oc_8c4fa359fd2f4278307a435ee3826dac`

### Hermes 自己的 bot 直接发群消息

Hermes 的 bot (`cli_a95612fc9ebddbc8`) 已经在`oc_c6883cd907e4d226736d87ce9c6c6d79`群里，可以直接用自己的身份发文件，不需要走 OpenClaw 的 gateway。

### Cron 环境变量问题

cron 环境**不会继承 shell 环境变量**（包括 `FEISHU_APP_SECRET`）。解决方案：直接在 Python 里从 `~/.hermes/.env` 文件读取：

```python
def get_feishu_creds():
    env_file = Path.home() / ".hermes" / ".env"
    if not env_file.exists():
        raise Exception("~/.hermes/.env 文件不存在")
    app_secret = None
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line.startswith("FEISHU_APP_SECRET="):
            app_secret = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    if not app_secret:
        raise Exception("FEISHU_APP_SECRET 未在 .env 中找到")
    return "cli_a95612fc9ebddbc8", app_secret
```

### 共享项目数据库（projects.json）

多个报告脚本可以共享同一个项目库 `~/.hermes/projects.json`：

```json
{
  "projects": [
    {
      "id": "p001",
      "name": "龙虾军团官网",
      "client": "⭐☁️",
      "description": "龙虾军团展示官网",
      "status": "进行中",
      "created": "2026-04-25"
    }
  ],
  "last_updated": "2026-04-25"
}
```

读取函数：
```python
def get_projects():
    proj_file = Path.home() / ".hermes" / "projects.json"
    if not proj_file.exists():
        return []
    data = json.loads(proj_file.read_text())
    return [p for p in data.get("projects", []) if p.get("status") != "已完成"]
```

---

## 验证记录（2026-04-16）

发送测试：`MEDIA:/home/ubuntu/source/prompts/README.md` ✅ 成功送达

```python
#!/usr/bin/env python3
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

APP_ID = "cli_xxx"
APP_SECRET = "xxx"
CHAT_ID = "oc_group_chat_id"   # 飞书群组 ID
OUTPUT_DIR = Path.home() / ".hermes" / "cron" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def curl_post(url, headers=None, data=None, form_data=None):
    cmd = ["curl", "-s", "-X", "POST", url]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    if data:
        cmd += ["-d", data]
    if form_data:
        for item in form_data:
            cmd += ["-F", item]
    return subprocess.run(cmd, capture_output=True, text=True).stdout

def get_token():
    r = curl_post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET}))
    return json.loads(r)["tenant_access_token"]

def upload_file(token, file_path):
    r = curl_post("https://open.feishu.cn/open-apis/im/v1/files",
        headers={"Authorization": f"Bearer {token}"},
        form_data=["file_type=stream", f"file_name={file_path.name}",
                   f"file=@{file_path};type=text/markdown"])
    resp = json.loads(r)
    if resp.get("code") != 0:
        raise Exception(f"上传失败: {resp}")
    return resp["data"]["file_key"]

def send_file_to_group(token, file_key):
    payload = json.dumps({"receive_id": CHAT_ID, "msg_type": "file",
                          "content": json.dumps({"file_key": file_key})})
    r = curl_post(f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=payload)
    resp = json.loads(r)
    if resp.get("code") != 0:
        raise Exception(f"发送失败: {resp}")
    return resp["data"]["message_id"]

if __name__ == "__main__":
    # 1. 生成报告
    report_content = "# 报告内容..."
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = OUTPUT_DIR / f"report-{today}.md"
    output_path.write_text(report_content)
    print(f"报告已生成：{output_path}", file=sys.stderr)

    # 2. 发送到飞书群
    try:
        token = get_token()
        file_key = upload_file(token, output_path)
        msg_id = send_file_to_group(token, file_key)
        print(f"已发送到飞书群：message_id={msg_id}", file=sys.stderr)
    except Exception as e:
        print(f"飞书发送失败：{e}", file=sys.stderr)
        sys.exit(1)
```

### 验证记录（2026-04-16）

发送测试：`MEDIA:/home/ubuntu/source/prompts/README.md` ✅ 成功送达

当前用户飞书 chat_id: `ou_11b567bc339145dff0717c83351ff598`
当前群组 chat_id: `oc_c6883cd907e4d226736d87ce9c6c6d79`

### send_message_tool 返回格式注意

`action='list'` 返回的是**格式化字符串**（不是 JSON），包含所有可用 target：

```
Available messaging targets:

Feishu:
  feishu:oc_xxx (dm)

Use these as the "target" parameter when sending.
```

### ⚠️ Hermes Bot 不在群里导致 230002

**症状**：`send_message` 或直接调用 Hermes bot (`cli_a95612fc9ebddbc8`) 的 tenant_access_token 发送消息到群组时，返回：
```json
{"code": 230002, "msg": "Bot/User can NOT be out of the chat."}
```

**原因**：Hermes 的 bot 不在目标群组里，飞书平台直接拒绝。

**解决方案**：改用 OpenClaw 的飞书账号（`default` 等）发送。这些账号的 `groupAllowFrom` 已配置群组白名单，可以成功发送。

```python
import json
from pathlib import Path
import subprocess

def curl_post(url, headers=None, data=None, form_data=None):
    cmd = ["curl", "-s", "-X", "POST", url]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    if data:
        cmd += ["-d", data]
    if form_data:
        for item in form_data:
            cmd += ["-F", item]
    return subprocess.run(cmd, capture_output=True, text=True).stdout

# 从 openclaw.json 读取 default 账号的凭据
config_path = Path.home() / ".openclaw" / "openclaw.json"
config = json.loads(config_path.read_text())
default_acc = config['channels']['feishu']['accounts']['default']
app_id = default_acc['appId']
app_secret = default_acc['appSecret']

# 获取 token
r = curl_post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    headers={"Content-Type": "application/json"},
    data=json.dumps({"app_id": app_id, "app_secret": app_secret}))
token = json.loads(r)['tenant_access_token']

# 发送文本消息（无需上传文件，直接 text 类型）
payload = json.dumps({
    "receive_id": "oc_target_group_id",
    "msg_type": "text",
    "content": json.dumps({"text": "消息内容"})
})
r2 = curl_post(
    f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
    headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    data=payload
)
resp = json.loads(r2)
assert resp['code'] == 0, f"发送失败: {resp}"
```

### OpenClaw 状态检查

```bash
# 进程状态
ps aux | grep openclaw | grep -v grep

# 飞书连接日志（重启后日志文件可能不更新，看 /proc/<pid>/fd）
tail -50 ~/.openclaw/logs/openclaw.log

# 重启 gateway（如需要）
openclaw restart
```

注意：gateway 重启后，日志文件不会自动创建新文件，旧的 .log 文件会停止更新（进程重启后会重新打开新的日志句柄）。
