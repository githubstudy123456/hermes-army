# 商业要闻 RSS 源实测记录（2026-05）

## 脚本位置
```
/home/ubuntu/.hermes/scripts/business-news.py
```

## 可用源（curl 直连实测）

| 来源 | URL | HTTP Code | 备注 |
|------|-----|-----------|------|
| Dow Jones Markets | `https://feeds.a.dj.com/rss/RSSMarketsMain.xml` | 200 ✅ | 美股/全球金融 |
| Dow Jones World | `https://feeds.a.dj.com/rss/RSSWorldNews.xml` | 200 ✅ | 国际商业 |
| 新浪财经 | `http://rss.sina.com.cn/news/china/focus15.xml` | 200 ✅ | 国内财经 |

## 封禁源（2026-05 实测）

| 来源 | URL | 原因 |
|------|-----|------|
| BBC Business | `https://feeds.bbci.co.uk/news/business/rss.xml` | 000 timeout |
| FT中文网 | `https://www.ftchinese.com/rss/feed` | 000 timeout |
| WSJ | `https://www.wsj.com/rss/news` | 000 timeout |
| CNBC | `https://www.cnbc.com/id/100003114/rss.xml` | 404 |
| Investing.com | `https://www.investing.com/rss/news.rss` | 403 |
| 彭博 | `https://feeds.bloomberg.cn/press_releases.xml` | 000 |
| 商务部 | `http://www.mofcom.gov.cn/rss/zxfg.xml` | 404 |

## 探测命令

当需要重新验证哪些源可用时，在终端运行：
```bash
for url in \
  "https://feeds.a.dj.com/rss/RSSMarketsMain.xml" \
  "https://feeds.a.dj.com/rss/RSSWorldNews.xml" \
  "http://rss.sina.com.cn/news/china/focus15.xml" \
  "https://feeds.bbci.co.uk/news/business/rss.xml" \
  "https://www.ftchinese.com/rss/feed"; do
  code=$(curl -s --max-time 6 -o /dev/null -w "%{http_code}" -A "Mozilla/5.0" "$url")
  echo "$code $url"
done
```

## ⚠️ 关键陷阱：OUTPUT_DIR 必须写到 cron/output 下

业务日报脚本的 `OUTPUT_DIR` 必须是 `~/.hermes/cron/output/biz-news/`，**不是** `~/.hermes/scripts/cron/output/biz-news/`。

前者是 cron 文件检测机制监听的标准目录，后者是脚本子目录，cron 系统扫不到，会导致"脚本跑成功但群里没收到推送"的静默失败。

验证方法：
```bash
# 正确路径
ls ~/.hermes/cron/output/biz-news/$(date +%Y-%m-%d).md

# 错误路径（写过但不会被推送）
ls ~/.hermes/scripts/cron/output/biz-news/$(date +%Y-%m-%d).md
```

## 修复记录

- **2026-05-22**：发现 business-news.py 写到了 `~/.hermes/scripts/cron/output/biz-news/`（错误），导致 cron 检测机制找不到文件。重建脚本并确认输出到 `~/.hermes/cron/output/biz-news/`。已手动重推今日日报。
- **2026-05-19**：BBC/FT/WSJ 全部封禁，原脚本 `biz-news.py` 不存在。重建为 `business-news.py`，切换到 Dow Jones + 新浪财经双源，14条内容正常。
- **Cron任务名**：ID `347cf635ccbf`，schedule `20 9 * * *`，目标群 `oc_c6883cd907e4d226736d87ce9c6c6d79`
