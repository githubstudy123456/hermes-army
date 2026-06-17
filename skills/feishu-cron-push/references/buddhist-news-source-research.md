# 佛学内容推送数据源调研（2026-05-17）

## 调研结论

**暂不建立佛学推送 cron** — 用户先要看质量再决定。

---

## 可用数据源

### ✅ 凤凰佛教 — fo.ifeng.com

| 维度 | 评分 |
|------|------|
| 内容深度 | ⭐⭐⭐⭐ |
| 时效性 | ⭐⭐⭐⭐ |
| 内容广度 | ⭐⭐⭐⭐（学术/新闻/高僧故事/禅文化） |
| 稳定性 | ⭐⭐⭐⭐ |
| 维护成本 | 需 Playwright（无有效 RSS） |

**特点：** 中文原生、内容多元质量高、有时效性，适合做新闻/故事/学术类推送。

**代表性标题：**
- 释本性：中国历代高僧从严治教事迹——为人师表
- 面对AI浪潮，佛教该害怕还是拥抱？宽运法师：不神化不排斥
- 心游宝峰思马祖！千年禅庭风骨，藏在江西这座没有被"污染"的山里
- 加拿大多伦多大学三一学院人间佛教研究院揭牌

**抓取方式：** Playwright headless Chrome，CSS 选择器 `h4 a, a[href*="/internation/"][href*=".shtml"]`

---

### ⚠️ Buddha Weekly — buddhaweekly.com/feed

| 维度 | 评分 |
|------|------|
| 内容深度 | ⭐⭐⭐ |
| 时效性 | ⭐⭐ |
| 内容广度 | ⭐⭐（偏密法/咒语/禅修仪轨） |
| 稳定性 | ⭐⭐⭐⭐ |
| 维护成本 | 需翻译（走代理） |

**特点：** 英文，实修导向（咒语、禅修、藏传佛教），内容高度同质化，大量"会员专属视频"。

**代表性标题：**
- Dharma Mandala Meditation – Sleep Secrets of the Buddhist Yogis
- Palden Lhamo Glorious Goddess SriDevi of Protection
- 6 Gates Dharani – Chant 3x Morning and Night Purifies Karma

**适合：** 每日一咒/禅修引导类推送，不适合做新闻类。

---

## 不可用来源（2026-05实测）

| 来源 | 状态 |
|------|------|
| 法鼓山 RSS | 404 |
| 佛光山 RSS | 解析失败（返回错误页） |
| 凤凰佛教 /rss.xml | 404 |
| BBC Religion 佛教关键词 | 过滤后 0 条/天 |
| SuttaCentral | 可访问但非新闻类 |

---

## 用户决策

用户选择：先不做 cron，改为**按需抓取**。

触发方式：用户说"要"→ 手动抓取凤凰佛教首页 → 直接推送内容。

如果未来建立佛学 cron，优先选择**凤凰佛教**（需 Playwright）而非 Buddha Weekly（内容同质化太严重）。