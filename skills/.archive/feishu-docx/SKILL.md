---
name: feishu-docx
description: Create and populate Feishu Lark documents (docx) via the Feishu Open API v1 — create doc, parse markdown to Feishu block format, batch insert blocks. Covers auth (tenant_access_token), block types, and batch sizing.
tags: [feishu, lark, docx, document, markdown]
date_created: 2026-04-29
---

# Feishu Lark 文档 API（docx v1）

通过 Feishu Open API 创建和写入云文档，支持 Markdown 转 Feishu 块格式。

## 认证

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

## 创建文档

```python
create_resp = json.loads(run_curl(
    "POST",
    "https://open.feishu.cn/open-apis/docx/v1/documents",
    headers=auth,
    data=json.dumps({"title": "文档标题"})
))
doc_id = create_resp["data"]["document"]["document_id"]
```

## Markdown → Feishu 块格式

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

**关键：** paragraph 块字段名是 `text`，不是 `paragraph`（这是与 Notion API 的核心区别）。

## 批量写入

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
    if resp.get("code") != 0:
        print(f"ERROR: {resp}")
        break
    print(f"Batch {batch_start+BATCH}/{len(blocks)}: OK")
```

## 完整流程

1. 读取 APP_ID / APP_SECRET 从 `~/.hermes/.env`
2. 获取 tenant_access_token
3. 创建文档（docx/v1/documents）
4. 解析 Markdown 为块列表
5. 分批插入（每批 ≤50）
6. 文档 URL：`https://feishu.cn/docx/{doc_id}`

## 常见错误

| code | 原因 |
|------|------|
| 1770001 | block 格式错误，检查是否用了 `text` 而非 `paragraph` |
| 99992402 | 每批超过 50 个 block |
| 10014 | APP_SECRET 无效，从 `~/.hermes/.env` 重新读取完整值（不只是 grep 显示的截断值） |
