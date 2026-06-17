---
name: feishu-messaging
description: 飞书平台全套操作 — 文档(docx)、文件发送、群组通信、MEDIA标签、curl上传、Bot-to-Bot通信、OpenClaw gateway集成
tags: [feishu, lark, messaging, file-send, docx, group-bot, openclaw]
date_created: 2026-04-16
version: 1.0.0
---

# 飞书平台操作全集

覆盖飞书所有核心操作场景：文档创建、文件上传发送、MEDIA标签机制、群组Bot通信、OpenClaw工具集诊断。

---

## 认证（所有飞书API的通用起点）

```python
import subprocess, json

APP_ID = "cli_a95612fc9ebddbc8"      # 从 ~/.hermes/.env 读取
APP_SECRET = "TBNvucvbHCHTeKqYtQ7PGfu1ANe0FSmb"

def run_curl(method, url, headers=None, data=None, form_data=None):
    cmd = ["curl", "-s", "-X", method, url]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    if data:
        cmd += ["-d", data]
    if form_data:
        for item in form_data:
            cmd += ["-F", item]
    return subprocess.run(cmd, capture_output=True, text=True).stdout

token_resp = json.loads(run_curl(
    "POST",
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    headers={"Content-Type": "application/json"},
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET})
))
token = token_resp["tenant_access_token"]
auth = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
```

---

## 发送文件 — MEDIA标签（最简方式）

在回复中包含 `MEDIA:文件绝对路径` 标签，gateway 自动识别并发送文件：

```
这是文字内容...

MEDIA:/home/ubuntu/source/AI提示词库完整版.md
```

gateway 内部流程：`extract_media()` → `adapter.send_file(chat_id=source.chat_id, file_path=media_path)` → `FeishuAdapter.send_document()`

飞书/Telegram/Discord 均支持 MEDIA 标签机制。

---

## 发送文件 — curl三步上传

飞书文件发送必须分两步：**上传获取 file_key → 再发送消息**。

```bash
# 1. 获取 tenant access token
TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d '{"app_id": "cli_xxx", "app_secret": "xxx"}' | python3 -c "import sys,json; print(json.load(sys.stdin)['tenant_access_token'])")

# 2. 上传文件，获取 file_key
FILE_KEY=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file_type=stream" \
  -F "file_name=文件名.md" \
  -F "file=@/path/to/file;type=text/markdown" | python3 -c "import sys,json; r=json.load(sys.stdin); print(r['data']['file_key'])")

# 3. 发送文件消息（必须有 receive_id_type=chat_id 查询参数！）
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"receive_id": "oc_group_chat_id", "msg_type": "file", "content": "{\"file_key\": \"'$FILE_KEY'\"}"}'
```

**⚠️ 关键坑：receive_id_type 参数必须作为查询参数，不加会报 `99992402 field validation failed`。**

---

## 创建文档（docx v1）— feishu-docx 技能的核心

创建并写入云文档，支持 Markdown 转 Feishu 块格式：

### 创建文档

```python
create_resp = json.loads(run_curl(
    "POST",
    "https://open.feishu.cn/open-apis/docx/v1/documents",
    headers=auth,
    data=json.dumps({"title": "文档标题"})
))
doc_id = create_resp["data"]["document"]["document_id"]
```

### Markdown → Feishu 块格式

```python
import re

def md_to_feishu(text):
    runs = []
    parts = re.split(r'\*\*(.+?)\*\*', text)
    for i, part in enumerate(parts):
        if i % 2 == 1:  # bold
            runs.append({
                "type": "text_run",
                "text_run": {"content": part, "text_element_style": {"bold": True}}
            })
        else:
            sub_parts = re.split(r'`(.+?)`', part)
            for j, sp in enumerate(sub_parts):
                if j % 2 == 1:  # inline code
                    runs.append({
                        "type": "text_run",
                        "text_run": {"content": sp, "text_element_style": {"code": True}}
                    })
                elif sp:
                    runs.append({"type": "text_run", "text_run": {"content": sp}})
    return runs if runs else [{"type": "text_run", "text_run": {"content": text}}]

def md_line_to_block(line):
    if line.startswith('####'):
        return {"block_type": 6, "heading4": {"elements": md_to_feishu(line[4:].strip()), "style": {}}}
    elif line.startswith('###'):
        return {"block_type": 5, "heading3": {"elements": md_to_feishu(line[3:].strip()), "style": {}}}
    elif line.startswith('##'):
        return {"block_type": 4, "heading2": {"elements": md_to_feishu(line[2:].strip()), "style": {}}}
    elif line.startswith('#'):
        return {"block_type": 3, "heading1": {"elements": md_to_feishu(line[1:].strip()), "style": {}}}
    elif line.startswith('- '):
        return {"block_type": 12, "bullet": {"elements": md_to_feishu(line[2:].strip()), "style": {}}}
    elif re.match(r'^\d+\.\s', line):
        m = re.match(r'^(\d+)\.\s+(.*)', line)
        return {"block_type": 13, "ordered": {"elements": md_to_feishu(m.group(2).strip()), "style": {}}}
    else:
        return {"block_type": 2, "text": {"elements": md_to_feishu(line), "style": {}}}
```

**关键：** paragraph 块字段名是 `text`，不是 `paragraph`（与 Notion API 的核心区别）。

### 批量写入

- 每批最多 **50 个 block**，超过会报 `99992402 field validation failed`
- endpoint: `POST https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children`
- 父 block ID 就是 doc_id 本身

```python
BATCH = 50
for batch_start in range(0, len(blocks), BATCH):
    batch = blocks[batch_start:batch_start + BATCH]
    resp = json.loads(run_curl(
        "POST",
        f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{doc_id}/children",
        headers=auth,
        data=json.dumps({"children": batch})
    ))
```

---

## 群组 Bot 通信 — 找open_id和@mention

### 找Bot的open_id（从gateway日志）

```bash
grep "oc_c6883cd907e4d226736d87ce9c6c6d79" /tmp/openclaw/openclaw-2026-04-21.log \
  | grep "received message from" | tail -20
```

消息里如果有 `<at user_id="ou_XXXX">BotName</at>`，那个 `ou_XXXX` 就是该bot的open_id。

### 发送时正确@mention格式

```python
from tools.send_message_tool import send_message_tool

result = send_message_tool({
    'action': 'send',
    'target': 'feishu:oc_c6883cd907e4d226736d87ce9c6c6d79',
    'message': '<at user_id="ou_CORRECT_OPEN_ID">BotName</at>\n\nMessage text here'
}, task_id='unique-id')
```

**必须用 `<at user_id="...">...</at>` XML标签**，纯文本 `@BotName` 无效。

---

## Bot不在群里导致230002

**症状：** 发消息到群组返回 `{"code": 230002, "msg": "Bot/User can NOT be out of the chat."}`

**原因：** bot 不在目标群组里，飞书平台直接拒绝。

**解决：** 改用 OpenClaw 的飞书账号（`default` 等）发送：

```python
import json
from pathlib import Path

config_path = Path.home() / ".openclaw" / "openclaw.json"
config = json.loads(config_path.read_text())
default_acc = config['channels']['feishu']['accounts']['default']
app_id = default_acc['appId']
app_secret = default_acc['appSecret']
```

---

## Hermes Director Profile — 工具集配置（诊断学）

当工具在 CLI 有效但在 `hermes tools list` 消失时，根因是**profile的toolsets配置缺失**：

```bash
# 检查 profile 工具集
hermes -p <profile> tools list 2>&1 | grep -i <tool-name>

# 修复：在 profile config.yaml 加 messaging toolset
# ~/.hermes/profiles/<profile>/config.yaml
toolsets:
  - hermes-cli
  - messaging    # ← send_message 在这个toolset里
  - web
  - file
```

---

## 已知飞书 App ID 速查

| App | AppId | 用途 |
|-----|-------|------|
| Hermes | `cli_a95612fc9ebddbc8` | Hermes Agent 自己的飞书 bot |
| OpenClaw | `cli_a954ec0730b85bc9` | OpenClaw gateway |
| 龙虾军团 | `cli_a96b530405785bde` | lobster-ceo |
| lobster-dev | `cli_a96b4b3f0d381bcf` | |
| lobster-pm | `cli_a96b4a83dd7c5bd6` | |
| lobster-qa | `cli_a96b4b852ce31bde` | |
| lobster-content | `cli_a96b4be3c73a9bcf` | |
| lobster-marketing | `cli_a96b4468633a9bda` | |
| lobster-fullstack | `cli_a96b44c8ae7adbd8` | |
| lobster-cfo | `cli_a96ec9e03af89bca` | |

**大姐姐群** chat_id：`oc_c6883cd907e4d226736d87ce9c6c6d79`
**龙虾军团群** chat_id：`oc_8c4fa359fd2f4278307a435ee3826dac`

---

## 常见错误

| code | 原因 |
|------|------|
| 1770001 | block 格式错误，检查是否用了 `text` 而非 `paragraph` |
| 99992402 | 每批超过 50 个 block，或缺少 receive_id_type 查询参数 |
| 10014 | APP_SECRET 无效 |
| 230002 | Bot 不在群组里 |
| 99992361 | open_id 属于另一个 app（cross app） |

---

## 定时报告脚本标准写法

完整可复用的 cron 报告脚本结构：

```python
#!/usr/bin/env python3
import json, subprocess, sys
from datetime import datetime
from pathlib import Path

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
    env_file = Path.home() / ".hermes" / ".env"
    app_id, app_secret = None, None
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line.startswith("FEISHU_APP_ID="):
            app_id = line.split("=", 1)[1].strip().strip('"').strip("'")
        if line.startswith("FEISHU_APP_SECRET="):
            app_secret = line.split("=", 1)[1].strip().strip('"').strip("'")
    r = curl_post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"app_id": app_id, "app_secret": app_secret}))
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

def send_file_to_group(token, file_key, chat_id):
    payload = json.dumps({"receive_id": chat_id, "msg_type": "file",
                          "content": json.dumps({"file_key": file_key})})
    r = curl_post(f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        data=payload)
    resp = json.loads(r)
    if resp.get("code") != 0:
        raise Exception(f"发送失败: {resp}")
    return resp["data"]["message_id"]

if __name__ == "__main__":
    report_content = "# 报告内容..."
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = OUTPUT_DIR / f"report-{today}.md"
    output_path.write_text(report_content)
    token = get_token()
    file_key = upload_file(token, output_path)
    msg_id = send_file_to_group(token, file_key, "oc_c6883cd907e4d226736d87ce9c6c6d79")
    print(f"已发送到飞书群：message_id={msg_id}")
```
