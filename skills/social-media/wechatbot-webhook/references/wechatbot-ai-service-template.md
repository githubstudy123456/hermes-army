# wechatbot-webhook AI 服务模板

基于 Flask 的 AI 服务，接收微信机器人消息，返回回复。完整模板存于 `~/wechatbot/ai_service.py`。

## 目录位置

- 模板文件：`~/wechatbot/ai_service.py`
- 启动脚本：`~/wechatbot/start.sh`
- 环境配置：`~/wechatbot/.env`

## MiniMax API 调用

```python
def call_minimax(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {MINIMAX_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "MiniMax-Text-01",
        "messages": [
            {"role": "system", "content": "你是一个微信群管理助手，回复简洁友好，不超过100字。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
    }
    resp = requests.post(
        "https://api.minimaxi.chat/v1/text/chatcompletion_v2",
        headers=headers,
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
```

**API 端点：** `https://api.minimaxi.chat/v1/text/chatcompletion_v2`  
**模型：** `MiniMax-Text-01`（支持 function call 则用 `MiniMax-Text-01`）

## AI 回复契约（关键）

项目 `msgSender.js` 的 `recvdApiReplyHandler` 处理响应，**必须**返回：

```json
{
  "success": true,
  "data": { "content": "回复内容" }
}
```

- `success: true` → 项目自动把 `data.content` 发回群里
- `success: false` / 其他格式 → 不发消息，静默丢弃
- **不需要手动调用发消息 API**

## 完整 Flask 服务模板

```python
import os, json, requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ============ 配置 ============
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")
MINIMAX_BASE_URL = "https://api.minimaxi.chat"
MINIMAX_MODEL = "MiniMax-Text-01"

# 关键词规则（快速兜底，命中后不走大模型）
AUTO_REPLY_RULES = {
    "帮助": "📌 可用指令：\n1. 帮助 - 查看本消息\n2. 加入 - 获取加群方式\n3. 活动 - 查看最新活动",
    "加入": "🔗 点击以下链接申请入群：\nhttps://example.com/join",
    "活动": "🎉 本期活动：xxx，详情请私信管理员",
}

# 允许的群名（留空 = 所有群都回复）
ALLOWED_GROUPS = []

# ============ 工具函数 ============
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

def check_auto_reply(content: str) -> str | None:
    content = content.strip()
    for keyword, reply in AUTO_REPLY_RULES.items():
        if keyword in content:
            return reply
    return None

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

# ============ 核心接口 ============
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

    # 过滤规则
    if is_system == "1" or is_from_self == "1" or msg_type != "text" or not content:
        return jsonify({"success": True})
    if ALLOWED_GROUPS and group_topic not in ALLOWED_GROUPS:
        return jsonify({"success": True})

    # 关键词命中
    auto_reply = check_auto_reply(content)
    if auto_reply:
        return jsonify({"success": True, "data": {"content": auto_reply}})

    # 大模型
    group_hint = f"（来自群：{group_topic}）" if group_topic else ""
    prompt = f"用户「{nickname}」在微信群{group_hint}说：{content}\n\n请以群管理助手的身份回复，语气友好简洁，不超过80字。"
    reply = call_minimax(prompt)
    return jsonify({"success": True, "data": {"content": reply}})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
```

## 依赖安装

```bash
pip3 install flask requests
```

或 `pip3 install -r requirements.txt`（文件内容）：
```
flask>=3.0.0
requests>=2.31.0
```

## 启动方式

```bash
export MINIMAX_API_KEY="your_api_key_here"
python3 ai_service.py
```

## .env 配置

```bash
PORT=3001
LOG_LEVEL=info
DISABLE_AUTO_LOGIN=
ACCEPT_RECVD_MSG_MYSELF=false
LOCAL_RECVD_MSG_API=http://localhost:8080/chat
LOCAL_LOGIN_API_TOKEN=wechat123456
```

## 健康检查

```bash
curl http://localhost:8080/health
# 返回 {"status": "ok"}
```

## 扩展：接入其他模型

如果不用 MiniMax，换掉 `call_minimax()` 函数即可：

```python
# OpenAI
def call_openai(prompt: str) -> str:
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}]},
        timeout=30,
    )
    return resp.json()["choices"][0]["message"]["content"]
```

## 调试技巧

### 测试 AI 服务独立运行

```bash
# 模拟项目发来的 multipart 请求
curl -X POST http://localhost:8080/chat \
  -F "source={\"room\":{\"payload\":{\"topic\":\"测试群\"}},\"from\":{\"payload\":{\"name\":\"张三\"}}}" \
  -F "type=text" \
  -F "content=帮助" \
  -F "isMentioned=0" \
  -F "isMsgFromSelf=0" \
  -F "isSystemEvent=0"
```

### 查看项目日志

```bash
# 项目日志（LOG_LEVEL=debug）
tail -f ~/wechatbot/logs/*.log
```

### 确认 AI 服务在跑

```bash
ps aux | grep ai_service | grep -v grep
ss -tlnp | grep 8080
```