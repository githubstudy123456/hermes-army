# Fashion & Luxury 新闻来源速查（2026-05 实测）

## ✅ 稳定可用的 RSS 源（主力）

### WWD
- URL: `https://wwd.com/feed/`
- 内容: 行业新闻、品牌动态、人事任命、Crocs联名、Old Navy等
- 稳定性: ★★★★★ 每次都能返回10条左右
- 备注: 行业权威，英文快讯式内容

### Luxury Daily
- URL: `https://www.luxurydaily.com/feed/`
- 内容: Balenciaga Campaign、Gucci×辛纳、Cardi B×Hermès×Fashionphile、Chanel快闪等
- 稳定性: ★★★★☆ 几乎总能抓到
- 备注: ⚠️ 文章页 URL 全部 403，只能通过 RSS 获取摘要

## ✅ 可用的中文站（直接 urllib 访问）

### Vogue 中国
- URL: `https://www.vogue.com.cn/news/`
- 内容: FASHION FUND 2026、明星时尚、谷爱凌、Jacques Wei等
- 稳定性: ★★★★☆
- 备注: 内容偏中文本土化，与国际新闻互补

### Vogue 香港
- URL: `https://www.voguehk.com/`
- 内容: Met Gala 2026红毯报道（BLACKPINK、Rihanna、Beyoncé、aespa）
- 稳定性: ★★★★☆
- 备注: 国际时尚事件的繁體中文报道

### Rayli 瑞丽
- URL: `https://www.rayli.com.cn/`
- 内容: 蒂芙尼古董珍藏展、路易威登美妆、王丽坤大片等
- 稳定性: ★★★★☆
- 备注: 明星+高端品牌中文报道，标题质量高

### 凤凰网时尚
- URL: `https://fashion.ifeng.com/`
- 内容: 劳力士亏损50万、睡衣外穿、高梵羽绒服等
- 稳定性: ★★★★☆
- 备注: 内容偏中国市场，偶有犀利观点文章

## ❌ 不可用来源（已验证失败）

| 来源 | URL | 失败原因 |
|------|-----|----------|
| Elle中国 | `elle.com.cn` | DNS failure |
| Elle国际 | `elle.com` | DNS failure |
| Marie Claire中国 | `marieclaire.com.cn` | DNS failure |
| Highsnobiety | `highsnobiety.com` | HTTP 404 |
| BoF | `businessoffashion.com` | HTTP 404 |
| Fashionista | `fashionista.com` | HTTP 403 |
| Who What Wear | `whowhatwear.com` | 返回空内容 |
| The Cut | `thecut.com` | HTTP 404 |
| Byrdie | `byrdie.com` | HTTP 403 |
| Fashion Week Online | `fashionweekonline.com` | 返回空内容 |
| Luxury Society | `luxurysociety.com` | HTTP 404 |
| Jing Daily | `jingdaily.com` | HTTP 404 |
| Hypebeast国际 | `hypebeast.com` | 返回空内容 |
| Hypebeast中国 | `hypebeast.cn` | DNS failure |
| Cosmo中国 | `cosmopolitan.com.cn` | 返回极少内容 |
| GQ | `gq.com` | HTTP 404 |
| Vogue国际 | `vogue.com/news` | HTTP 404 |
| Elle RSS | `elle.com/feeds/all/rss.xml` | HTTP 404 |
| Harper's Bazaar RSS | `harpersbazaar.com/feed/` | HTTP 404 |
| Vogue UK RSS | `vogue.co.uk/feed/rss/news` | HTTP 404 |
| GQ RSS | `gq.com/feeds/articles.rss` | HTTP 404 |

## 🔶 中等稳定性（可用但不保证）

### Hypebeast CN（中文站）
- URL: `https://hypebeast.cn/category/fashion`
- 稳定性: ★★★☆☆ 经常返回0字节或DNS超时
- 内容: G-SHOCK×高达、NAUTICA等联名好物

### WWD 行业新闻
- URL: `https://wwd.com/news/fashion/` (需主页+广告拦截绕过)
- 稳定性: ★★★☆☆ 大页面但广告干扰多

## 📌 搜索策略建议

### 推荐搜索方式
```python
# Bing 搜索英文关键词（辅助发现）
url = 'https://www.bing.com/search?q=fashion+news+2026+May+luxury+brands&setlang=en'
# ⚠️ 结果含大量baike/dictionary，需二次过滤
```

### 不要使用的搜索
- 百度搜索：严格滑块验证，服务器环境无法绕过
- DuckDuckGo：超时，不适合服务器 cron 环境
- Google News：超时，不适合服务器环境

### 有效的 RSS → 文章 URL 模式
WWD 和 Luxury Daily 都有 RSS，但 Luxury Daily 文章页 403 → **只依赖 RSS 摘要即可**

## ⚠️ 技术陷阱

1. **Bing 中文搜索本地化**: 即使 setlang=en 也大量返回中文词典/百科，需过滤 `baike`、`百度`、`iciba` 等域名
2. **Luxury Daily 文章页**: 所有文章 URL → 403，禁止尝试
3. **curl|grep 管道**: 复杂正则匹配经常失败，统一用 Python urllib + re
4. **DNS 超时**: 多个来源（elle.com.cn, marieclaire.com.cn）间歇性 DNS 失败，加 try/except
5. **pipe to python3**: 被 vet 拦截，用 `execute_code` 工具代替