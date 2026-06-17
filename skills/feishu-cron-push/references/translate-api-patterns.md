# 英译中翻译方案参考

本文档汇总所有飞书推送 cron 脚本使用的翻译方案，供下次需要时直接引用。

---

## Google Translate API（curl 走代理）

**适用场景：** 任何需要将英文标题/摘要翻译为中文的 cron 脚本。无需 API Key，免费额度充足。

**底层调用：**
```python
import subprocess, json, urllib.parse

def translate(text: str) -> str:
    encoded = urllib.parse.quote(text[:100])
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={encoded}"
    cmd = [
        "curl", "-s", "--socks5-hostname", "127.0.0.1:10808",
        "-X", "GET", url,
        "--header", "User-Agent: Mozilla/5.0"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    if result.returncode == 0 and result.stdout:
        data = json.loads(result.stdout)
        return "".join(item[0] for item in data[0] if item[0])
    return text  # 失败时返回原文
```

**JSON 响应格式：**
```
[[[翻译文本, 原文片段, null], ...], 原语言, "en"]
```
取 `data[0]` 拼接所有片段即为完整翻译。

**限制：** 单次请求不超过 100 字符（截断传入文本），超时 10 秒。

**已验证（2026-05）：**
- ✅ `translate.googleapis.com` 走 `socks5://127.0.0.1:10808` 代理可用
- ❌ `deep_translator` Python 库无法访问谷歌翻译（返回 "No support for the provided language"）
- ❌ 系统 Python (`/usr/bin/python3`) 可用，hermes-agent venv (`~/.hermes/hermes-agent/venv/bin/python3`) 不能访问系统包

---

## 翻译缓存设计

每个 cron 脚本应使用模块级 `_trans_cache = {}` 缓存已翻译的标题，避免同一条目重复翻译：

```python
_trans_cache = {}

def translate_title(text):
    if not text:
        return text
    key = text[:60]  # 用前60字符作key
    if key in _trans_cache:
        return _trans_cache[key]
    # ... 调用翻译 API ...
    _trans_cache[key] = result
    return result
```

---

## 常见失败情况

| 错误 | 原因 | 解法 |
|------|------|------|
| `deep_translator` → "No support for the provided language: zh" | 目标语言值写错 | 用 `zh-CN` 而非 `zh` |
| curl 超时 | 代理未启动或 DNS 未走代理 | 确认使用 `--socks5-hostname` 而非 `-x` |
| hermes-agent venv 无法 import 第三方包 | venv 隔离，系统包不可用 | cron 脚本 shebang 用 `#!/usr/bin/python3`，或通过 subprocess 调用系统 Python |