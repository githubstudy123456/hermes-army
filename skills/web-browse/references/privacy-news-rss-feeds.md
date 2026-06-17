# Privacy & Security News RSS Feed Sources

Reliable RSS/Atom feeds for privacy, security, and data protection news.
**Last verified: 2026-06-13** (supersedes all prior test dates)

## ✅ Confirmed Working Sources

### EFF (Electronic Frontier Foundation)
- **URL**: `https://www.eff.org/rss/updates.xml`
- **No proxy needed**
- ✅ **Best primary source for privacy policy & tools.** Returns ~50 recent items (mid-June 2026), topics include: FISA 702 expiration, California surveillance pricing ban, Meta facial recognition removal, LGBTQ+ online safety, copyright overreach, social media bans.
- **Key topics covered**: surveillance, encryption, FISA/NSA, facial recognition, state privacy laws, platform accountability
- **RSS item format** (2026-06 verified):
```python
import subprocess, re
r = subprocess.run(['curl', '-s', '--max-time', '15', '-A', 'Mozilla/5.0',
                   'https://www.eff.org/rss/updates.xml'],
                  capture_output=True, text=True, timeout=20)
raw = r.stdout
items = re.findall(r'<item>(.*?)</item>', raw, re.DOTALL)
for item in items:
    title = re.search(r'<title>([^<]+)</title>', item)
    link  = re.search(r'<link>([^<]+)</link>', item)
    date  = re.search(r'<pubDate>([^<]+)</pubDate>', item)
    # title/date/link groups are clean, no CDATA
```

### Krebs on Security
- **URL**: `https://krebsonsecurity.com/feed/`
- **No proxy needed**
- ✅ **Best source for data breaches and cybercrime incidents.**
- **Verified 2026-06**: Recent items include ransomware group analysis, record-breaking Microsoft Patch Tuesday, Meta AI bot account takeover, Dutch server seizure.
- **抓取方式**: `curl -s --max-time 15 -A "Mozilla/5.0" "https://krebsonsecurity.com/feed/"`

### Wired RSS
- **URL**: `https://www.wired.com/feed/rss`
- **No proxy needed**
- ⚠️ **Caveat: Returns 50 items, but ~90% are non-privacy (World Cup, product deals, gear reviews, Meta/Elon business news).**
- **Only use if filtering aggressively.** Privacy/security items in June 2026 include: Grok deepfakes scandal, Palantir NHS protests, Signal encrypted collaboration tool.
- **Wired privacy items are sparse** — supplement with EFF + Krebs as primary sources.

### Hacker News (Algolia API) — Privacy/Security Filter
- **URL**: `https://hn.algolia.com/api/v1/search?query=privacy+security&tags=story&hitsPerPage=10`
- **JSON API, no RSS**
- ✅ Fastest source, good for filling gaps
- Filter keywords: `privacy`, `data breach`, `encrypt`, `surveill`, `GDPR`, `leak`

---

## ❌ Confirmed Unavailable / Unusable Sources

| Source | URL | Problem |
|--------|-----|---------|
| The Hacker News RSS | `https://feeds.feedburner.com/TheHackersNews` | Returns empty (0 titles) |
| BleepingComputer | `https://www.bleepingcomputer.com/feed/` | Cloudflare blocks, returns verification page |
| The Register | Various | Cloudflare blocks |
| Ars Technica | `https://feeds.arstechnica.com/arstechnica/index` | Returns empty |
| SecurityWeek | `https://www.securityweek.com/feed/` | 403 Forbidden |
| DarkReading | `https://www.darkreading.com/feed` | 403 Forbidden |
| Reddit r/privacy RSS | `https://www.reddit.com/r/privacy/.rss` | Returns empty |

---

## ❓ Unverified (Use with Caution)

| Source | URL | Notes |
|--------|-----|-------|
| Privacy International | `http://privacyinternational.org/rss.xml` | Not tested this session |
| Schneier on Security | `https://www.schneier.com/feed/atom/` | Not tested this session |
| 嘶吼 (4hou) | `https://www.4hou.com/feed` | Not tested this session |
| Troy Hunt / HIBP | `https://www.troyhunt.com/rss/` | Not tested this session |

---

## Recommended Minimum Set for Weekly Privacy Digest

| Source | Role | Coverage |
|--------|------|----------|
| **EFF feed** | Primary | Privacy tools, US surveillance policy, platform accountability, legislation |
| **Krebs feed** | Primary | Data breaches, ransomware, cybercrime incidents |
| **Wired RSS** | Secondary (filtered) | Deepfakes, AI privacy risks, corporate surveillance |
| **HN Algolia API** | Gap-filler | Broader security/privacy discussions |

---

## Keyword Filtering

When scanning feeds, filter by these keywords:
- **English**: `privacy`, `data breach`, `leak`, `encrypt`, `track`, `GDPR`, `consent`, `surveillance`, `password`, `facial recogn`, `biometric`, `personal data`
- **中文**: `隐私`, `数据泄露`, `密码`, `加密`, `合规`, `个人信息`, `监控`

---

## Cron Privacy Digest — Recommended Output Format

Based on the June 2026 session, the following 5-item format works well:

```
🛡️ 隐私保护周刊 | YYYY年MM月DD日

1️⃣ [分类] 标题
简介（1-2句，中文）
📎 来源链接

2️⃣ ...

📌 来源：EFF / Krebs / WIRED | 搜索周期：MM月DD日-DD日
```
