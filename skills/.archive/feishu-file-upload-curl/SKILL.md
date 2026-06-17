---
name: feishu-file-upload-curl
description: 用 curl subprocess 上传文件到飞书群（绕过 Python urllib SSL 问题）
tags: [feishu, file-upload, curl, python]
date_created: 2026-04-25
---

# 飞书文件上传（curl 方案）

## 核心问题

Python `urllib.request.urlopen()` 对飞书服务器做 SSL 握手时会报 `HTTP Error 400: Bad Request` 或 `SSL: UNEXPECTED_EOF_WHILE_READING`。改用 `curl` subprocess 即可解决。

## 标准流程（3 步）

### Step 1: 获取 tenant_access_token

```python
import subprocess, json

APP_ID = "cli_xxxxxxxx"
APP_SECRET = "xxxxxxxx"

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

token = json.loads(run_curl(
    "POST",
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    headers={"Content-Type": "application/json"},
    data=json.dumps({"app_id": APP_ID, "app_secret": APP_SECRET})
))["tenant_access_token"]
```

### Step 2: 上传文件获取 file_key

```python
file_key = json.loads(run_curl(
    "POST",
    "https://open.feishu.cn/open-apis/im/v1/files",
    headers={"Authorization": f"Bearer {token}"},
    form_data=[
        "file_type=stream",
        f"file_name={file_path.name}",
        f"file=@{file_path};type=text/markdown"
    ]
))["data"]["file_key"]
```

**注意**：`form_data` 必须是 **list**，每个 `-F` 参数单独一个 list item。不能是 dict。

### Step 3: 发送文件消息到群组

```python
chat_id = "oc_xxxxxxxx"  # 群组 chat_id

result = json.loads(run_curl(
    "POST",
    "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    data=json.dumps({
        "receive_id": chat_id,
        "msg_type": "file",
        "content": json.dumps({"file_key": file_key})
    })
))
# result["code"] == 0 即成功
```

## 关键陷阱

1. **urllib SSL 握手失败** → 用 curl subprocess 代替
2. **form_data 传 dict** → curl -F 只能逐个加，改成 list
3. **receive_id_type** → 必须作为**URL 查询参数**，不是 body 或 header
4. **file_key 有效期** → 上传后尽快发送，file_key 会过期

## 适用场景

- 定期报告自动发送到飞书群（周报/月报）
- 文件类消息（markdown、PDF、图片）
- 需要 cron job 无人值守运行的场景
