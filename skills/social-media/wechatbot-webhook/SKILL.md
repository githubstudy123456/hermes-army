---
name: wechatbot-webhook
description: WeChat bot webhook 部署与 AI 接入 — 从项目搭建到生产可用的完整流程，基于 danni-cool/wechatbot-webhook
tags: [wechat, webhook, wechaty, bot, ai-integration, flask]
category: social-media
version: 1.0.0
---

# WeChat Bot Webhook — 部署与 AI 接入

基于 [danni-cool/wechatbot-webhook](https://github.com/danni-cool/wechatbot-webhook) 的微信机器人部署、AI 接入生产可用方案。

---

## 项目概述

| 项目 | 信息 |
|------|------|
| GitHub | github.com/danni-cool/wechatbot-webhook |
| 框架 | Node.js (≥18.14.1) + Wechaty + Hono |
| 包管理 | pnpm（不能用 npm/yarn） |
| 协议 | Web 微信协议（≈2天掉线一次，需扫码重登） |
| License | MIT |
| 最新版本 | 2.8.2 |

### 核心能力

**发送：** 文字、图片、视频、文件（本地/URL）、群发  
**接收：** 文字/图片/语音/视频/文件、好友申请、系统上下线通知  
**AI 接入：** 通过 `LOCAL_RECVD_MSG_API` 钩子，消息 POST 到外部 AI 服务，响应自动发回群里

### 局限性

- Web 微信协议本身有被微信限制风险
- 大约每两天掉线一次，无自动恢复，必须重新扫码
- 没有自动拉人/踢人等管理 API，只能发消息

---

## 部署流程

### Step 1: 环境准备

```bash
# 检查 Node 版本（需要 >= 18.14.1）
node --version  # v22.22.2 ✓

# 安装 pnpm（如未安装）
npm install -g pnpm

# 安装项目依赖（pnpm workspace）
cd ~/wechatbot
pnpm install
```

### Step 2: 安装依赖审批问题

pnpm 6+ 会询问 build scripts 审批。两种解法：

**方法一：自动放行（推荐）**
在项目根目录创建 `.npmrc`：
```
approve-builds=true
```

**方法二：交互式选择**
```bash
pnpm approve-builds
# 空格选中所有 → 回车确认
```

> 注意：`package.json` 里的 `pnpm.patchedDependencies` 不要删，patches 目录不要动。

### Step 3: 配置 .env

```bash
PORT=3001
LOG_LEVEL=info
DISABLE_AUTO_LOGIN=           # 空 = 记住上次登录；true = 每次都扫码
ACCEPT_RECVD_MSG_MYSELF=false # 不处理自己发的消息
LOCAL_RECVD_MSG_API=http://localhost:8080/chat
LOCAL_LOGIN_API_TOKEN=your_random_token
```

### Step 4: 启动服务

```bash
cd ~/wechatbot
pnpm start
```

终端输出扫码 URL，访问并扫码登录微信。

---

## AI 接入架构

```
微信群消息
  → wechatbot-webhook (:3001) 收到消息
    → POST multipart/form-data → AI 服务 (:8080)
      → 关键词命中 → 直接返回
      → 未命中 → MiniMax/其他大模型 → 返回
      ← { success: true, data: { content: "回复内容" } }
    → 项目自动把回复发回群里
```

### 关键发现：消息格式是 multipart/form-data，不是 JSON

项目 `msgUploader.js` 上报消息时使用 `multipart/form-data`，字段：

| 字段 | 说明 |
|------|------|
| `source` | JSON 字符串，含 `room`、`from`、`to` 结构 |
| `type` | `text` / `file` / `urlLink` / `friendship` / 系统事件类型 |
| `content` | 消息文本内容 |
| `isMentioned` | `1` = 有人@机器人 |
| `isMsgFromSelf` | `1` = 自己发的消息 |
| `isSystemEvent` | `1` = 系统事件（登录/掉线/异常） |

### 关键发现：AI 回复契约
### 关键发现：AI 回复契约

项目 `msgSender.js` 的 `recvdApiReplyHandler` 处理 AI 响应：
```json
{
  "success": true,
  "data": { "content": "回复内容" }
}
```

- `success: true` + `data.content` → 项目自动发回群里
- `success: false` / 其他格式 → 不发消息，静默
- **不需要调用发消息 API**，项目内置了这个逻辑

---

## API Key 注入方式（重要坑位）

### 情况A：MiniMax 通过 Hermes 平台注入（`MINIMAX_CN_API_KEY`）

`MINIMAX_CN_API_KEY` 由 Hermes 平台注入到环境变量，**终端无法直接读取**完整内容（显示为 `***`）。

MiniMax 作为 Anthropic 代理时，API 端点不同：

| 场景 | 端点 | Header |
|------|------|--------|
| MiniMax 原生 API（text/completion） | `https://api.minimaxi.chat/v1/text/chatcompletion_v2` | `Authorization: Bearer <key>` |
| MiniMax Anthropic 兼容端点 | `https://api.minimaxi.com/anthropic/v1/messages` | `X-Api-Key: <key>` |

> 注意：主人给的 `sk-cp-` 格式 key 是 OpenAI 格式，不是 MiniMax 格式，MiniMax key 通常是 `eyJ...` 开头。

### 情况B：直接使用独立 API Key

如果使用独立部署的 AI 服务（非 Hermes 平台注入），直接 `export MINIMAX_API_KEY="your_key"` 即可。

### 情况C：接硅基流动等 OpenAI 兼容平台

主人如果有 OpenAI 格式的 key（如 `sk-cp-` 开头），可以接入硅基流动（SiliconFlow）等平台，这些平台接受 OpenAI 格式 key：

```python
def call_model(prompt: str) -> str:
    resp = requests.post(
        "https://api.siliconflow.cn/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={"model": "deepseek-ai/DeepSeek-V2.5", "messages": [{"role": "user", "content": prompt}]},
        timeout=30,
    )
    return resp.json()["choices"][0]["message"]["content"]
```

---

## AI 服务模板（Flask）

`~/wechatbot/ai_service.py` — 基于 Flask + MiniMax：

```python
from flask import Flask, request, jsonify
import os, json, requests

app = Flask(__name__)

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimaxi.chat"
MINIMAX_MODEL = "MiniMax-Text-01"

# 关键词快速兜底
AUTO_REPLY_RULES = {
    "帮助": "📌 可用指令：\n1. 帮助 - 查看本消息\n2. 加入 - 获取加群方式\n3. 活动 - 查看最新活动\n4. 联系我 - 获取联系方式",
    "加入": "🔗 点击以下链接申请入群：\nhttps://example.com/join",
    "活动": "🎉 本期活动：\n1. 邀请好友入群送好礼\n2. 每日签到领积分\n详情请私信管理员",
    "联系我": "📨 如需联系，请私信管理员或发送邮件至 admin@example.com",
}

def call_minimax(prompt: str) -> str:
    if not MINIMAX_API_KEY:
        return "[AI服务未配置API Key]"
    headers = {"Authorization": f"Bearer {MINIMAX_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": MINIMAX_MODEL, "messages": [
        {"role": "system", "content": "你是一个微信群管理助手，回复简洁友好，不超过100字。"},
        {"role": "user", "content": prompt}
    ], "temperature": 0.7}
    resp = requests.post(f"{MINIMAX_BASE_URL}/v1/text/chatcompletion_v2",
        headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")

def parse_source(source_json: str) -> dict:
    try: return json.loads(source_json)
    except: return {}

def extract_group_topic(source: dict) -> str:
    room = source.get("room", {}) or {}
    if isinstance(room, dict):
        return room.get("payload", {}).get("topic", "")
    return ""

def extract_nickname(source: dict, default: str = "") -> str:
    from_obj = source.get("from", {}) or {}
    if isinstance(from_obj, dict):
        return from_obj.get("payload", {}).get("name", default)
    return default

@app.route("/chat", methods=["POST"])
def chat():
    source_json = request.form.get("source", "{}")
    msg_type = request.form.get("type", "text")
    content = request.form.get("content", "")
    is_from_self = request.form.get("isMsgFromSelf", "0")
    is_system = request.form.get("isSystemEvent", "0")

    source = parse_source(source_json)
    nickname = extract_nickname(source)
    group_topic = extract_group_topic(source)

    # 过滤
    if is_system == "1" or is_from_self == "1" or msg_type != "text" or not content:
        return jsonify({"success": True})

    # 关键词兜底
    for keyword, reply in AUTO_REPLY_RULES.items():
        if keyword in content:
            return jsonify({"success": True, "data": {"content": reply}})

    # 大模型
    group_hint = f"（来自群：{group_topic}）" if group_topic else ""
    prompt = f"用户「{nickname}」在微信群{group_hint}说：{content}\n\n请以群管理助手的身份回复，语气友好简洁，不超过80字。"
    reply = call_minimax(prompt)
    return jsonify({"success": True, "data": {"content": reply}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
```

### 启动脚本 `start.sh`

```bash
#!/bin/bash
set -e
cd ~/wechatbot

if [ -z "$MINIMAX_API_KEY" ]; then
    echo "[错误] 请先设置 MINIMAX_API_KEY"
    exit 1
fi

python3 ai_service.py &
sleep 2
pnpm start
```

启动：
```bash
export MINIMAX_API_KEY="your_key"
bash ~/wechatbot/start.sh
```

---

## 已知坑位

### 1. pnpm 安装报 [ERR_PNPM_IGNORED_BUILDS]

`pnpm install` 后有些包报了 `[ERR_PNPM_IGNORED_BUILDS]`，依赖没编译完。解决：在 `.npmrc` 加 `approve-builds=true`，或手动 `pnpm approve-builds` 全选所有包。

### 2. 项目用 pnpm patched 机制

`package.json` 里有 `pnpm.patchedDependencies`，用于补丁 wechat4u 等包。不要删 `patches/` 目录。

### 4. Web 微信协议掉线

约每两天掉线，`DISABLE_AUTO_LOGIN` 配置决定是否自动重连（自动登录 = 记住上次账号，快速重连；不自动 = 每次都要扫码）。掉线期间 AI 服务如果还在跑，消息会堆积在内存，项目重连后才会处理。

### 5. 进程不是 Docker，是直接 node 进程

`ps aux | grep node main.js` 可以直接看到进程，不需要 sudo docker。掉线后重启：

```bash
# 重启带 -r 强制重新扫码
node main.js -r
# token 登录地址显示在终端输出
# http://localhost:3002/login?token=<TOKEN>
```

### 4. AI 服务返回格式必须是 `{success, data}`

项目 `recvdApiReplyHandler` 只认 `success: true` + `data.content`。如果返回普通 JSON 或 `success: false`，项目不会发任何消息。

### 6. API Key 注入方式导致无法在终端调试

如果 AI 服务需要使用 `MINIMAX_CN_API_KEY`（Hermes 平台注入的 key），这个 key 在终端里显示为 `***`，无法直接 curl 测试。

**表现：**
```bash
# env 显示有 key，但 curl 测试返回 invalid api key
$ env | grep MINIMAX
MINIMAX_CN_API_KEY=***   # 显示为掩码

$ curl -X POST "https://api.minimaxi.com/anthropic/v1/messages" \
  -H "x-api-key: $MINIMAX_CN_API_KEY" ...
# 返回 {"type":"authentication_error", "message": "login fail"}
```

**解法：**
1. 让主人直接提供可用的 API key 给 AI 服务使用（绕开 Hermes 注入）
2. 或者在 AI 服务代码里写死 key（仅个人使用场景）
3. 或者确认 MiniMax 控制台生成的 key 格式是否正确

> **MiniMax key 格式识别：** MiniMax 生成的 key 通常是 `eyJ...` 开头（JWT），不是 `sk-cp-`（后者是 OpenAI 格式）。如果主人有 `sk-cp-` 开头的 key，说明是 OpenAI 兼容平台（硅基流动等）的 key，不是 MiniMax 原生 key。

```json
{
  "room": {"payload": {"id": "xxx", "topic": "群名"}},
  "from": {"payload": {"id": "xxx", "name": "昵称", "avatar": "url"}},
  "to": {"payload": {"id": "xxx", "name": "机器人名"}}
}
```

解析时注意：`room` / `from` / `to` 是嵌套对象，要 `.payload.topic` / `.payload.name`。

---

## 相关文件

- `references/wechatbot-message-format.md` — 消息格式详细字段说明、source JSON 结构、过滤规则
- `references/wechatbot-ai-service-template.md` — 完整 AI 服务模板（含 MiniMax 调用代码）
- `references/wechatbot-token-login.md` — 重启后 token 失效、重新生成写入、扫码登录流程
- `references/wechat-qr-url-format.md` — QR 登录 URL 格式、token 来源、端口说明（2026-06-16 更新）
- `templates/wechatbot-startup.sh` — 启动脚本模板

---

## Production Hardening (this session's additions)

### MiniMax-M2.7 Content Block Filtering
MiniMax-M2.7 returns `content` array with TWO block types:
- `type:"text"` — actual reply text
- `type:"thinking"` — chain-of-thought, must NOT be sent to users

```python
def extract_text(content_list):
    for block in content_list:
        if isinstance(block, dict) and block.get("type") == "text":
            return block.get("text", "").strip()
    return ""
```
Never concatenate the whole content array — that leaks thinking into the reply.

### Soul/Identity/Memory Personality Files
Three files control bot personality, loaded at startup:
- `soul.md` — tone, forbidden patterns, reply examples
- `identity.md` — bot name (poo), character traits
- `memory.md` — group context, shared knowledge

Load pattern (must avoid f-string triple-quote):
```python
def load_soul():
    base = os.path.dirname(os.path.abspath(__file__))
    parts = []
    for fname in ["soul.md", "identity.md", "memory.md"]:
        path = os.path.join(base, fname)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                parts.append(f.read())
    return "\n".join(parts)

SOUL_PROMPT = load_soul()
# Use string concat, NOT f-string triple-quote:
prompt = SOUL_PROMPT + "\n\n用户..." + content
```

### Permission Architecture
- Owner wxid stored in env var `POO_SUPER_ADMIN` (never in code/config)
- `require_privilege(wxid, level)` returns拒绝消息 if unauthorized
- Levels: `basic` (everyone), `admin` (owner only for sensitive ops)
- Sensitive ops requiring admin: privilege commands, privacy data, funds

### Room Invite Restriction
Only respond in groups invited by owner:
- `src/wechaty/init.js` `room-join` event → writes `room.id → inviterWxid` to `room_invites.json`
- AI service checks this on each message
- Old groups with no record are allowed (graceful fallback)

```python
def is_room_allowed(source: dict) -> bool:
    room_id = source.get("room", {}).get("id", "")
    if not room_id:
        return True  # private chat, no filter
    invite_file = os.path.join(BASE_DIR, "room_invites.json")
    if not os.path.exists(invite_file):
        return True  # old group, no record yet
    with open(invite_file) as f:
        invites = json.load(f)
    inviter = invites.get(room_id, "")
    return is_super_admin(inviter)
```

### Watchdog + Feishu Alert
Cron job every minute checks AI service (:8080 HTTP) + node process. On failure → Feishu webhook notification to owner group. 1-hour cooldown per service.

### Known Python Pitfalls This Session
1. **Triple-quote f-strings**: `f"""{SOUL_PROMPT}..."""` — special chars in soul files break Python's tokenizer. Use string concat.
2. **Duplicate returns after patch**: After replacing code blocks, always verify no accidental `return` duplication.
3. **`global` before assignment**: `global PERMISSIONS` after modifying it raises `SyntaxError`. Instead, just return the modified data and let the next request reload.
4. **YAML top-level text**: `permissions.yaml` must be valid YAML — no stray comments outside dict structure.
5. **`write_file` masks API tokens**: The Hermes `write_file` tool replaces values that look like API keys/tokens with `***`. Never use `write_file` for `.env` or any file containing real credentials. Use terminal `cat > file << 'EOF'` instead.

## Related Skills

- `playwright-browser-automation` — if WeChat needs browser login (currently QR in terminal)
- `server-operations` — server deployment, process management, systemd service