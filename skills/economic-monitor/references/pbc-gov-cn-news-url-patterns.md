# 中国人民银行新闻发布页 URL 模式（2026-06-12验证）

## 已验证可用的入口

### 新闻发布首页
```
https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html
```
- 加载时间：约3-5秒
- 显示最新"公告信息区"条目（按时间倒序）
- 每个条目含标题 + 时间戳

### 列表页特征
- 页面结构：左侧"公告信息区"列出最近条目
- 列表项 `<a href*="202606...">` 可用 `browser_console` 提取
- 每条目URL格式：`https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/YYYYMMDDHHMMSSNNNN/index.html`

## 子页面URL格式（已验证）
```
https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/2026061114184126385/index.html
```
-路径段：日期+时间戳+序号（14位+4位）
- 内容加载约2-3秒

## 已知内容判断
- 外交访问类（如"中印尼行长会"）通常P2以下，不含实质货币政策
- 真正有政策含量的条目：降准/降息公告、LPR调整、MLF操作、汇率政策
- 近期（2026-06-12）头条：中印尼联合工作机制、潘功胜会见保尔森、中巴金融战略合作

## browser_console 提取方法
```javascript
JSON.stringify([...document.querySelectorAll('a[href*="202606"]')].slice(0,15).map(e=>({t:e.innerText.trim(),u:e.href})))
```
- 返回最近15条6月发布的条目
- 过滤标题含"降准"、"降息"、"LPR"、"MLF"、"汇率"者为实质政策信号

## 与gov.cn的互补关系
- gov.cn 侧重政策文件全文（国务院、部委正式文件）
- PBC 侧重货币政策操作细节（央行研究、公开市场操作）
- 监测时需同时轮询两个入口，避免遗漏央行侧的实质操作