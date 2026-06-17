---
name: download-from-restricted-network
description: Download files from the internet in this cloud server environment — handles network restrictions and proxy guidance
---

# Download Files from Restricted Network Environment

## 重要更正：GitHub 直连实际上正常

腾讯云服务器（AS45090 深圳腾讯）可以直接访问 github.com：
- `curl https://github.com` → HTTP 200 ✓
- `git clone https://github.com/...` → 成功 ✓
- `wget https://github.com/...` → 成功 ✓

**"GitHub 需要代理才能访问"这个前提是错误的。** 腾讯云有国际出口，GitHub 直连完全正常。

代理故障（Trojan TLS bug）影响的是**通过 v2ray 代理访问 GitHub**，不是 GitHub 本身不可达。

## Trial & Error Findings

| Source | Result | Notes |
|--------|--------|-------|
| gutenberg.org | Reachable | Works but need correct ebook ID |
| archive.org | Timeout | Cannot reach |
| marxists.org | Timeout | Cannot reach |
| GitHub raw | Timeout | Cannot reach |
| libgen.is | Timeout | Cannot reach |
| Various PDF mirrors | Timeout | Cannot reach |

## Workflow for Future Downloads

1. **First: Check if proxy is available** before attempting downloads
2. **Try Project Gutenberg** for public domain books — it works but you need the correct ebook ID
3. **For any foreign site:** Assume it will fail without proxy

## How to Find Correct Gutenberg ID

```bash
# Search for a book
curl -s "https://www.gutenberg.org/ebooks/search/?query=KEYWORDS"

# Check book metadata (verify it is the RIGHT book)
curl -s "https://www.gutenberg.org/ebooks/BOOK_ID" | grep -i "title\|author"
```

**Important:** Always verify content — do not trust that an ID is correct without checking.

## Proxy Setup (if available)

```bash
curl -x http://proxy:port -L URL -o output.file
# or
export http_proxy=http://proxy:port
export https_proxy=http://proxy:port
```

## Alternative for Restricted Downloads
- Ask user to download locally and upload
- Use domestic Chinese mirrors/sources instead
- For Marx Capital: try 国内镜像 or Baidu/Zhihu search
