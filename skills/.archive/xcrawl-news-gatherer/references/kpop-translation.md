# K-pop 新闻翻译实战参考

## 翻译 API 选择

**结论：只用 curl + `translate.googleapis.com`**，不依赖任何 Python 翻译库。

```python
import subprocess, urllib.parse, json

def translate_title(text, timeout=8):
    clean = text[:100].replace("!", "").replace("'", "").replace('"', "").replace("–", "-")
    encoded = urllib.parse.quote(clean)
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=zh-CN&dt=t&q={encoded}"
    cmd = ["curl", "-s", "--socks5-hostname", "127.0.0.1:10808", url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if r.returncode == 0 and r.stdout:
        data = json.loads(r.stdout)
        return "".join(item[0] for item in data[0] if item[0])
    return text
```

**已知失败方案：**
- `deep-translator` / `GoogleTranslator` Python 库：网络超时，连不上谷歌翻译服务器
- `translate` PyPI 包：模块不存在
- 直接 `subprocess.list2cmdline()` 做 URL 编码：生成的 URL 代理解析错误

## 并发翻译（防止超时）

单线程顺序翻译 28 条约 60-90 秒，超出 cron timeout。

```python
import concurrent.futures

def translate_titles_concurrent(texts, concurrency=6):
    trans_map = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = {ex.submit(translate_title, t): t for t in texts}
        for fut in concurrent.futures.as_completed(futures):
            orig, translated = fut.result()
            trans_map[orig] = translated
    return trans_map
```

## 执行顺序（关键）

```
1. XCrawl / RSS 抓取原始数据（英文标题）
2. 去重（normalize_title 用翻译前原始英文）
3. 翻译（批量并发，只翻标题）
4. 输出 markdown
```

**不能翻译后再去重**：翻译质量不稳定，同一篇文章节选不同英文表述会被翻成不同中文，导致重复条目逃过去重。

## Soompi 中文源

中文版 Feed：`https://ch.soompi.com/feed/`（无需翻译）

## 代理注意事项

`--socks5-hostname` 而非 `-x socks5://` — 前者 DNS 也走代理，后者可能 DNS 泄漏。

## 已验证的 K-pop 搜索词

```
aespa 2026 / aespa world tour / aespa comeback
BLACKPINK 2026 / BLACKPINK Jisoo Jennie Lisa Rosé
NewJeans 2026 / NewJeans comeback
IVE 2026 / IVE tour
LE SSERAFIM 2026 / LE SSERAFIM 回归
Red Velvet 2026 / Red Velvet 回归
TWICE 2026 / TWICE 巡演
```