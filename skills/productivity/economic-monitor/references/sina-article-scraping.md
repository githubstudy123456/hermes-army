# 新浪财经文章正文提取（2026-06-11 实测）

## 问题

新浪财经文章页（如 `https://finance.sina.com.cn/jjxw/2026-06-11/doc-iniaysmc0881571.shtml`）直接用 urllib 读取 HTML 后，用正则 `re.sub(r'<[^>]+>', '', html)` 提取正文会失败——页面含大量 JS 干扰，正文区域无法被简单标签清除。

## 原因

新浪文章页是典型 JS 动态渲染：正文在 `<div class="article-content">` 内部，但 HTML 结构复杂，Python 正则无法完整还原文本。浏览器打开后 `inner_text("body")` 才是干净的纯文本。

## 解决方案：browser_navigate

```python
# ✅正确方式：browser_navigate 直接读取干净正文
browser_navigate("https://finance.sina.com.cn/jjxw/2026-06-11/doc-iniaysmc0881571.shtml")
# → 返回 snapshot，正文段落直接可见
# → 也可直接 inner_text("body") 获取全部文本
```

## 适用场景

- CPI/PPI 数据原文（`doc-iniaysmc0881571.shtml`）
- 四大证券报头版原文（`doc-iniaysky*.shtml`）
- 工信部政策原文
- 任何新浪财经深度文章

## 替代：bb-browser site模式

`bb-browser open<url>` 也可工作，但有时超时。browser_navigate 更稳定。

## 不要用

❌ `urllib + re.sub(r'<[^>]+>', '', html)` → 正则提取，正文丢失
❌ `curl ... | python3` → vet拦截  
❌ `bb-browser eval` → 对新浪文章不稳定