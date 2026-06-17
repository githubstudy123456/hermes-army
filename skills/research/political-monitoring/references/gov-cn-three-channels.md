# gov.cn 三通道扫描法（2026-06-11 实测总结）

## 三条独立通道

| 通道 | URL pattern | 主要内容 | 时效规律 |
|------|------------|---------|---------|
| **lianbo/** | `/lianbo/YYYYMM/content_\d+.htm` | 各部委政策意见、联合发文、专项行动 | 最快，部委文件首发通道 |
| **yaowen/liebiao/** | `/yaowen/liebiao/YYYYMM/content_\d+.htm` | 领导人外事活动、会议报道、仪式性报道 | 有1-2小时延迟 |
| **zhengce/content/** | `/zhengce/content/YYYYMM/content_\d+.htm` | 国发/国办发正式文件（国令/国函） | 最慢，需等正式签发 |

## 扫描优先级（2026-06-11 实测结论）

**lianbo/ > yaowen/liebiao/ > zhengce/**

1. **lianbo/** — 优先扫描。工信部"人工智能+信息通信"意见（2026-06-11 08:11）在 yaowen/liebiao 出现之前，已先通过 lianbo/ 通道发布。多部委联合发文也优先从 lianbo/ 发现。
2. **yaowen/liebiao/** — 次要扫描。覆盖领导人外事访问（习近平访朝）、宪法宣誓仪式等政治仪式报道。
3. **zhengce/** — 验证扫描。正式政策文件编号（国发/国办发）在 lianbo/ 报道后才会出现在 zhengce/ 列表页。

## 为什么 lianbo/ 最快

gov.cn/lianbo/ 是"政务联播"频道，报道各部委日常动态（政策吹风会、意见征询、联合发文、地方政务），内容发布比领导人活动的 yaowen/liebiao 更及时。

**典型案例（2026-06-11）**：
- 工信部《"人工智能+信息通信"创新发展实施意见》→ 来源：人民日报，lianbo/ 首发（08:11）
- "三北工程西部阻击战片区现场推进会"→ yaowen/liebiao（6月9日20:26）
- 城市更新十五五规划政策吹风会→ zhengce/jiedu/（6月8日）

## 十五五规划文件发现路径

| 文件 | 发布通道 | 评级 | 发现路径 |
|------|---------|------|---------|
| 现代化应急体系建设十五五规划 | zhengce/index.htm | P2 | 国发文件，正规通道 |
| 加快农业农村现代化十五五规划 | zhengce/index.htm | P2 | 国发文件，正规通道 |
| 城市更新十五五规划 | zhengce/jiedu/ | P3 | 政策吹风会解读页 |
| 人工智能+信息通信创新发展实施意见 | lianbo/ | P2 | 部委意见，lianbo首发 |

## Content ID 去重法

gov.cn URL 中的 `content_\d{7,}` 是每篇政策的唯一标识，与标题无关。同一政策从不同通道进入URL签名相同。

```python
import re, glob, os
from datetime import datetime

def extract_content_ids(text):
    return set(re.findall(r'content_(\d{7,})', text))

reports_dir = os.path.expanduser("~/.hermes/political-reports")
today = datetime.now().strftime("%Y-%m-%d")

pushed_ids = set()
for fname in glob.glob(f"{reports_dir}/2026-06-11*"):
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()
        pushed_ids |= extract_content_ids(content)
    except:
        pass

# 候选URL列表
candidate_urls = [...]  # 从三通道提取的URL列表
candidate_ids = extract_content_ids(' '.join(candidate_urls))
new_ids = candidate_ids - pushed_ids
```

## 今日扫描结果记录（2026-06-11 17:42）

通过 gov.cn 首页 browser_navigate 快照发现以下条目，已去过重：

**P2 通过推送**：
1. 工信部"人工智能+信息通信"创新发展实施意见（2026-06-11，lianbo/通道）
2. 张国清出席"全球趋同促增长峰会"（2026-06-11，yaowen/liebiao通道）
3. "三北"工程西部阻击战片区现场推进会（2026-06-09，yaowen/liebiao通道）
4. 四部门解读《城市更新"十五五"规划》（2026-06-08，zhengce/jiedu通道）

**P3/P4 归入次日日报**：
- 国务院宪法宣誓仪式、李强讲话（6月9日）
- 丁薛祥出席三峡水运新通道开工仪式
- 谌贻琴出席国际劳工大会
- 教育部高校毕业生就业"百日冲刺"行动
- 人形机器人与具身智能实景实训专项行动
- 5月份消费市场运行总体平稳

**新浪财经 lid=2517**扫描结果：20条全部为财经/国际新闻（茅台规划、林清轩股价、美伊交火、SpaceX等），0条国内政策，国内政策监测价值全天均有限。