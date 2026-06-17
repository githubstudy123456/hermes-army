# gov.cn zhengce 直接访问工作流（2026-06-14验证）

## 重大发现

**gov.cn 政策文件页可直接访问**，URL格式：`https://www.gov.cn/zhengce/content/YYYYMM/content_XXXXXXX.htm`

本session验证案例：国务院办公厅《关于加强监管防范风险促进私募投资基金高质量发展的指导意见》（国办函〔2026〕54号）
- URL: `https://www.gov.cn/zhengce/content/202606/content_7071204.htm`
- 加载时间：~3秒
- 内容完整度：✅ 正文+发文机关+成文日期+发布日期全部可提取

## URL格式

| 类型 | URL Pattern |
|------|-------------|
| 政策文件 | `https://www.gov.cn/zhengce/content/YYYYMM/content_CONTENTID.htm` |
| 要闻文章 | `https://www.gov.cn/yaowen/liebiao/YYYYMM/content_CONTENTID.htm` |

**Content ID规律**：
- 2026年6月新发布：7071204（6月5日发布）至7072029（6月14日发布）
- ID数字越大越新，同日多条连续递增
- 月份（YYYYMM）在路径中但不是唯一标识，content ID才是

## 标题选择器踩坑（2026-06-14再次确认）

### zhengceku政策文件页超时问题

**问题**：`page.inner_text("h1, h2, .title")` 在部分gov.cn zhengceku政策页超时

**验证案例**：
| URL | 类型 | h1,h2,.title | body.inner_text |
|-----|------|--------------|-----------------|
| `content_7071948`（要闻） | ✅ | 可用（3s） | 正常 |
| `content_7072002`（政策） | ⚠️ | 超时30s | ✅ 正常（5804字） |
| `content_7071204`（政策） | ✅ | 正常（3s） | 正常 |

**通用策略**：对zhengce政策文件页，**优先使用** `page.inner_text("body")` 一次性获取全页文本，避免超时风险。

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp("http://localhost:19825")
    context = browser.contexts[0]
    page = context.pages[0] if context.pages else context.new_page()
    
    page.goto("https://www.gov.cn/zhengce/content/202606/content_7071204.htm", 
              timeout=30000, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)
    
    # 安全策略：直接用body，避免h1/h2/.title超时
    body = page.inner_text("body")
    print(body[:2000])
    
    browser.close()
```

## 正文提取方法

gov.cn政策页段落提取（过滤页眉页脚噪声）：

```python
# 提取正文段落（30字符以上，过滤导航/页脚）
paragraphs = page.eval_on_selector_all("p", 
    "els => els.map(e=>e.innerText.trim()).filter(t=>t.length>30)")

# 打印前10段
for i, para in enumerate(paragraphs[:10]):
    print(f"[{i}] {para[:100]}")
```

## 列表页URL提取失效

**现状（2026-06-14）**：
- `https://www.gov.cn/zhengce/xxgk/` 列表页**可加载**（4秒），含30条政策文件
- 但列表页无法通过CDP提取article URL（`eval_on_selector_all` 返回空列表）
- **实际影响**：无法自动化扫描最新政策，只能依赖新浪财经API作为入口

**工作流替代**：
1. 新浪财经政经API(lid=2517) → 筛选含gov.cn链接的新闻
2. 直接navigate该gov.cn article URL → 获取完整正文
3. 无新浪链接 → 改查36kr RSS补漏

## 本session推送记录

| 时间 | 事件 | 评级 | 文件 |
|------|------|------|------|
| 10:03 | 前5个月人民币贷款增加9.11万亿元 | P2 | `20260614_1030.txt` |
| 11:09 | 国务院办公厅加强私募投资基金监管指导意见 | P2 | `20260614_1109_P2_私募基金监管_国务院办公厅指导意见.md` |

**去重说明**：两次推送均基于央行金融统计数据（5月贷款数据），但：
- 10:03推送：聚焦人民币贷款增量（9.11万亿）
- 11:09推送：聚焦私募基金监管政策（国办函54号）

实质内容不同（一个是金融数据，一个是监管政策），均通过5级审批，判定为不同事件。
