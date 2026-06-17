# MiniMax API 参考

## 端点（Anthropic兼容格式）

```
POST https://api.minimaxi.com/anthropic/v1/messages
```

## 请求

```python
headers = {
    "x-api-key": "sk-cp-...",          # API Key
    "anthropic-version": "2023-06-01",
    "Content-Type": "application/json",
}
payload = {
    "model": "MiniMax-M2.7",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "..."}]
}
```

## 响应结构

```json
{
  "id": "...",
  "type": "message",
  "role": "assistant",
  "model": "MiniMax-M2.7",
  "content": [
    {
      "type": "thinking",
      "thinking": "模型推理过程（不要发给用户）",
      "signature": "..."
    },
    {
      "type": "text",
      "text": "实际回复内容"
    }
  ],
  "usage": {
    "input_tokens": 16,
    "output_tokens": 22
  },
  "stop_reason": "end_turn"
}
```

## 关键点

- **`content` 是数组**，不是字符串
- 有时只有 `thinking` 没有 `text`（`max_tokens` 太小导致输出被截断）
- `thinking` 块里的内容包含中文推理，是思考过程，**不要**发给用户
- 只提取 `type == "text"` 的 `text` 字段

## Python 提取函数

```python
def extract_text(content_list):
    if not content_list:
        return ""
    for block in content_list:
        if isinstance(block, dict) and block.get("type") == "text":
            return block.get("text", "").strip()
    return ""
```

## max_tokens 设置

- 太小（如300）：text 输出被截断，只有 thinking
- 建议：1024 或更大，确保 text 完整输出