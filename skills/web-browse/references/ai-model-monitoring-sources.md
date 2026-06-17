# AI Model Monitoring Sources

## Artificial Analysis（推荐首选）

**站点**: `https://www.artificialanalysis.ai`

### 为什么好用
- **每日模型评测更新**：Changelog 页面按日期列出新加入评测的模型名称、Index 分数、发布平台
- **Intelligence Index 排名**：全球模型综合能力排名，含速度/价格/词密度多维对比
- **无需登录/代理**：服务器环境可直接 `browser_navigate` 访问，走 Chrome 内置 SSL

### 关键页面

| 页面 | URL | 用途 |
|------|-----|------|
| 模型排行榜 | `/` | 首页 Intelligence/Speed/Price 三项排名 |
| Changelog | `/changelog` | 每日新增模型评测记录，含发布日/平台/Index 分数 |
| 模型详情 | `/models/<model-slug>` | 单一模型深度数据（定价/速度/上下文/变体列表） |

### 实用技巧
```python
# 通过 browser_navigate 抓取 changelog 获取本周新模型列表
browser_navigate("https://www.artificialanalysis.ai/changelog")
# 滚动或点击日期按钮过滤到特定日期范围
# 用 browser_snapshot 提取结构化数据
```

### 本周模型（2026-06-09~13 实测）
| 模型 | 发布日 | Index | 特点 |
|------|--------|-------|------|
| Claude Fable 5 (Adaptive Reasoning) | Jun 9 | 65 | Anthropic Mythos 级，#1 排名，自适应推理+Opus 4.8 回退 |
| GPT-5.5 (xhigh) | Jun 10 | — | OpenAI 第一梯队，与 Claude Fable 5 并列 |
| North Mini Code | Jun 9 | 28 | Cohere 编码专家 MoE，30B/3B 激活，开源 |
| MiniMax-M3 | Jun 8 | 55 | 开源权重待发布，发布后将是开源第一 |
| DeepSeek V4 Flash | Jun 10 | — | 高效推理版，DeepInfra/CoreWeave 多平台 |
| Gemma 4 12B (双版) | Jun 10 | 20 | Google 推理版+非推理版同步推出 |
| HyperNova 60B 2605 | Jun 11 | 29 | Multiverse Computing，中等规模 |

---

## 辅助数据源

### 新浪财经政经 API（lid=2517）
- 用途：补充国内AI政策/监管新闻（如特朗普政府禁止境外获取Anthropic模型）
- 注意：过滤关键词 `AI/大模型/Anthropic/OpenAI/开源`，因为默认返回美股/财经
- **已知编码陷阱**：`k=中文` 参数会触发 `UnicodeEncodeError`，最安全方式是不加 `k=` 参数，客户端过滤

### 知乎热搜 API
- `https://www.zhihu.com/api/v4/hot-list?limit=10`
- 返回结构：`data[].target.title`
- 注意：有时返回 404，可能是限流

### GitHub Trending AI 项目
- `https://api.github.com/search/repositories?q=created:>YYYY-MM-DD+AI+LLM&sort=stars&order=desc`
- **已知 403 限流**：同 session 多次调用会被限流，加 `X-GitHub-Token` 或加延迟
- 替代：用 `bb-browser site github/search` 但标题字段失效需降级处理

---

## 踩坑记录

### 1. GitHub Search API 403 Rate Limit
**问题**：`execute_code` 中直调 GitHub Search API 返回 403
**原因**：同 session 频繁调用，触发 rate limit
**解决**：
- 方案A：换用 `bb-browser site github/search "关键词" --json`（bb-browser 内部有延迟）
- 方案B：加 `Authorization: Bearer <token>` header
- 方案C：降级为搜索 GitHub Trending 页面 `https://github.com/trending`（browser_navigate 直读）

### 2. 新浪财经 lid=2517 中文关键词编码
**问题**：`url = '...&k=AI大模型'` 触发 `UnicodeEncodeError: 'ascii' codec can't encode`
**解决**：不加 `k=` 参数，客户端 Python 过滤：
```python
ai_kw = ['AI','大模型','模型','LLM','ChatGPT','开源','Gemini','Claude','DeepSeek']
for item in items:
    if any(kw in item.get('title','') for kw in ai_kw):
        print(item['title'])
```

### 3. 知乎热搜 API 404
**问题**：`/api/v4/hot-list` 返回 404
**原因**：可能需要登录态或 IP 限流
**解决**：换用 `bb-browser site zhihu/hot --json` 或 `browser_navigate` 直访知乎热榜页

### 4. Artificial Analysis Changelog 内容截断
**问题**：Changelog 页面内容被 `browser_snapshot` 截断（多页数据）
**解决**：点击具体日期按钮，或滚动页面分批抓取；也可以直接点击模型名进入详情页获取单模型完整数据

---

## 快速验证脚本

```python
# 验证 Artificial Analysis changelog 可访问
import subprocess
result = subprocess.run(
    ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
     'https://www.artificialanalysis.ai/changelog'],
    capture_output=True, text=True
)
print(f"Status: {result.stdout}")  # 期望 200
```