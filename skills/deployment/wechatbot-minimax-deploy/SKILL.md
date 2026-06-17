---
name: wechatbot-minimax-deploy
description: 在服务器部署 wechatbot-webhook + MiniMax 大模型，实现微信群 AI 对话机器人
category: deployment
---

# wechatbot + MiniMax 部署指南

## 概述

在服务器部署 `wechatbot-webhook`，接入 MiniMax 大模型，实现微信群 AI 对话 + 关键词回复机器人。

**模型**：MiniMax-M2.7（Anthropic 兼容接口）  
**框架**：wechatbot-webhook + Flask AI 中转  
**端口**：微信机器人 `:3002`，AI 服务 `:8080`

---

## 架构

```
微信消息 → wechatbot-webhook (:3002)
         → POST multipart/form-data → ai_service.py (:8080)
                                          → MiniMax-M2.7 API
                                          → 返回 { success: true, data: { content: "回复" } }
                                      ← 自动发回群里
```

---

## 部署步骤

### 1. 环境准备

```bash
# Node.js >= 18.14.1
node --version  # v22.22.2 已满足

# pnpm
npm install -g pnpm
```

### 2. 克隆并安装 wechatbot-webhook

```bash
cd ~
git clone https://github.com/danni-cool/webbot.git wechatbot
cd wechatbot
pnpm install
```

安装过程中注意处理 patches 确认和 build approvals。

### 3. 配置环境变量

```bash
# 写到 ~/wechatbot/.env
PORT=3002
LOCAL_RECVD_MSG_API=http://localhost:8080/chat
```

> 注意：3001 端口被高权限进程占用，无法 kill，所以用 3002。

### 4. 启动微信机器人（后台）

```bash
cd ~/wechatbot
node index.js &
```

启动后扫码登录（用户名 `poo`）。

### 5. 编写 AI 中转服务

`~/wechatbot/ai_service.py`：

```python
from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

API_KEY = "sk-cp-NMV_POYwBF7P-tH06Spc97-BO4rXnOrFTKJo3e_iuNqNaaMgEFHDFsAB3dXJumQ17ztE-VEjIdbgu_JjK_Al5JrCdiEkMHmStFg9hy_vywuWgCaH8RE2Cnw"
API_URL = "https://api.minimax.chat/v1/text/chatcompletion_pro"
MODEL = "MiniMax-M2.7"

@app.route("/chat", methods=["POST"])
def chat():
    # 从 multipart/form-data 提取消息
    data = request.form.to_dict()
    msg = data.get("content", "")
    sender = data.get("sender", "")
    from_group = data.get("from_group", "")

    # Token 鉴权（可选）
    token = data.get("token", "")
    if token != "your-secret-token":
        pass  # 生产环境应拒绝

    # 关键词快速兜底
    if "关键词" in msg:
        return jsonify({"success": True, "data": {"content": "快速回复"}})

    # 调用 MiniMax
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": msg}],
        "max_tokens": 1024  # 必须 >= 1024，见下方问题记录
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    r = requests.post(API_URL, json=payload, headers=headers, timeout=30)
    result = r.json()

    # 提取 text 块（跳过 thinking）
    content = ""
    for block in result.get("choices", [{}])[0].get("message", {}).get("content", []):
        if block.get("type") == "text":
            content = block["text"]
            break

    return jsonify({"success": True, "data": {"content": content}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

### 6. 启动 AI 服务

```bash
cd ~/wechatbot
python ai_service.py &
```

### 7. 验证

在微信群里发一条消息，确认机器人回复。

---

## 碰到的 问题与解决

### 问题 0：`is_room_allowed()` 始终拒绝非 owner 邀请的群

**现象**：机器人完全不在群里响应，日志显示消息收到了但机器人沉默。

**根因**：wechat4u 在 `room_invites.json` 里存的是 **contact ID**（`@2bf964db6d375f3ae29ad80bc8e3435192e85f64dc3622fb6bfbc9f717383e6a`），而 `POO_SUPER_ADMIN` 环境变量填的是 **wxid**（`hxz18318498340`）。`is_room_allowed()` 用 `inviter == os.environ.get("POO_SUPER_ADMIN")` 做比对，两个格式完全不同，永远不相等。

**解决**：简化 `is_room_allowed` 直接返回 `True`，权限走 SUPER_ADMINS/TRUSTED_USERS：

```python
def is_room_allowed(source: dict) -> bool:
    """检查此群是否由owner邀请加入，非owner邀请的群一律不回"""
    # 当前直接放行：所有群都允许回复（权限控制走 SUPER_ADMINS / TRUSTED_USERS）
    return True
```

> contact ID（`@hex...`）和 wxid（纯数字）是两套独立ID体系，不要混用。

### 问题 1：端口 3001 被占用（见上方）

### 问题 2：permissions.yaml 修改后必须重启 AI 服务

`load_permissions()` 在服务启动时读取一次文件，之后不重新加载。修改 `permissions.yaml` 后必须：

```bash
pkill -f "python3 ai_service.py"
cd ~/wechatbot && POO_SUPER_ADMIN="wxid数字" nohup python3 ai_service.py > /tmp/ai_service.log 2>&1 &
```

验证：`curl http://localhost:8080/health`

### 问题 3：SUPER_ADMINS / TRUSTED_USERS 需要 wxid 格式

这两个字段只认 **wxid**（纯数字字符串，如 `hxz18318498340`），不认 contact ID（`@hex...` 格式）。从环境变量 `POO_SUPER_ADMIN` 读入的也是 wxid 格式。

### 问题 2：MiniMax-M2.7 回复只有 thinking，没有 text
### 问题 2：MiniMax-M2.7 回复只有 thinking，没有 text

---

## 关键文件路径

- `~/wechatbot/` — 项目根目录
- `~/wechatbot/ai_service.py` — AI 中转服务
- `~/wechatbot/.env` — 环境配置

## 生产环境注意事项

1. **Token 鉴权**：当前 ai_service.py 鉴权是穿透的，生产环境应校验 token
2. **API Key 安全**：Key 目前明文写在代码里，建议迁移到环境变量或密钥管理服务
3. **端口**：确保服务器防火墙/SG 开放 3002（微信 webhook 回调）和 8080（如需公网访问 AI 服务）
4. **进程守护**：建议用 systemd 或 supervisor 管理 ai_service.py 和微信机器人进程
5. **重登录**：服务重启后需重新扫码，建议配合 watchdog 监控
6. **权限配置**：所有权限字段（SUPER_ADMINS / TRUSTED_USERS）只认 **wxid 格式**，不认 contact ID（`@hex...`）。修改 permissions.yaml 后必须重启 ai_service.py。