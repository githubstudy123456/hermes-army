# 高校招生网站 & PDF 解析实战笔记

> 来源：2026-05-26 扒取北体/北舞/上戏招生简章 + 上体附中/上戏附中培养方案

---

## 一、已验证可访问的来源（补遗）

| 学校 | 网址 | 内容 |
|------|------|------|
| 上海戏剧学院招生网 | `https://zs.sta.edu.cn/` | 2026艺术类校考简章（PDF直接链接） |
| 上戏 PDF 直接地址 | `https://zs.sta.edu.cn/_upload/article/files/65/e6/736a9e474865ac32e7ce334f3fb4/f164cf66-bc5a-4c51-b22c-79eca9fbd555.pdf` | 上戏2026艺术类招生简章 PDF |
| 北京舞蹈学院 | `http://www.bda.edu.cn/zsjy/bkzsxx/e2ac12fec980435b9a4db3e5a7a62b80.htm` | HTML版招生信息页 |
| 北京体育大学 | `https://zs.bsu.edu.cn/bkzsw/zszc/e0d72e82df07463cab06c7e490420e6c.htm` | HTML版2025招生章程 |

### 两所附中的信息源（官网 DNS 不通时备用）
| 学校 | 备用信息源 | 可获取内容 |
|------|---------|----------|
| 上海体育学院附属中学 | 百度百科词条 `baike.baidu.com/item/上海体育学院附属中学` | 基本信息、课程体系、办学定位 |
| 上海戏剧学院附属高级中学 | 百度百科词条 `baike.baidu.com/item/上海戏剧学院附属高级中学` | 基本信息、培养方向 |

### 已验证的附中域名（全部失败，记录以免重试）
| 域名 | 猜测学校 | 结果 |
|------|---------|------|
| susfz.edu.cn | 上体附中 | FAIL — DNS 无响应 |
| stafz.sh.edu.cn | 上体附中 | FAIL |
| stafz.edu.sh.cn | 上体附中 | FAIL |
| susfuzhong.edu.sh.cn | 上体附中 | FAIL |
| shanghaisusfz.edu.sh.cn | 上体附中 | FAIL |
| shxsfz.cn | 上戏附中 | FAIL |
| shxsfz.com.cn | 上戏附中 | FAIL |
| shxsfz.net | 上戏附中 | FAIL |
| shxsx.cn | 上戏附中 | FAIL |
| shanghaixifuzhong.cn/.com.cn | 上戏附中 | FAIL |
| xifuzhong.sh.cn | 上戏附中 | FAIL |
| www.shxfz.com | 上戏附中 | **误判** → 清远盛兴集团（广东，完全无关） |
| xsfz.edu.sh.cn | 上戏附中 | FAIL |

**结论**：两所附中均无公开可访问的官网，DNS 查询全挂。唯一可靠信息源：**百度百科词条**（urllib 直读，无验证码）。

---

## 二、PDF 抓取 & 解析实战

### 成功流程（推荐）

```
1. browser_navigate 访问高校招生列表页（找 PDF 链接）
2. urllib 直接下载 PDF（urllib.urlopen 配合 headers）
3. pypdf 终端提取文字（terminal 工具 + PYTHONPATH）
```

### 关键发现

**PDF URL 可直接 urllib 下载**：
```python
import urllib.request
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...'}
req = urllib.request.Request(pdf_url, headers=headers)
with urllib.request.urlopen(req, timeout=15) as r:
    content = r.read()
    print(f"size: {len(content)}, type: {r.info().get('Content-Type')}")
    with open('/tmp/output.pdf', 'wb') as f:
        f.write(content)
```

**browser_navigate 访问 PDF URL → 返回截断（~343 字节）**：
- 不要用 browser_navigate 打开 PDF 链接，会返回空/截断内容
- urllib 直连下载 PDF 是正确路径

**pypdf 在 execute_code 超时但 terminal 工具正常**：
- execute_code 中的 pypdf.Reader 操作超时（1行输出，无法提取）
- 改用 terminal 工具：`pip install --user pypdf && python3.10 ...`
- PYTHONPATH 必须指定：`PYTHONPATH=/home/ubuntu/.local/lib/python3.10/site-packages`

```bash
# 终端提取 PDF 文字（正确方式）
PYTHONPATH=/home/ubuntu/.local/lib/python3.10/site-packages python3.10 -c "
import pypdf
reader = pypdf.PdfReader('/tmp/shta_2026.pdf')
print(f'Pages: {len(reader.pages)}')
for i, page in enumerate(reader.pages[:15]):
    t = page.extract_text()
    if t:
        print(f'--- Page {i+1} ---')
        print(t[:3000])
"
```

---

## 三、搜索附中信息的备用策略

当目标中学官网 DNS 不通时：

1. **Bing 中文搜索**：`site:baidu.com 上海体育学院附属中学`（不要用百度搜索，会触发验证码）
2. **Bing + edu.sh.cn 限定**：`上海体育学院附属中学 site:edu.sh.cn`
3. **百度百科移动版**：`https://baike.baidu.com/item/关键词`（无验证码，直接访问）
4. **尝试政府域名**：上海教育系统常用 `.edu.sh.cn`，但附中不一定在此域名下
5. **Bing 搜索 + 排除已知垃圾站**：用 `"上戏附中" "官网" -baidu -zhihu -tieba -youxi` 过滤百度系内容

### 可尝试的附中域名穷举模式
```
http://{关键词拼音}.edu.sh.cn/
http://{简称拼音}.edu.sh.cn/
http://www.{简称拼音}sh.cn/
```

---

## 四、已知踩坑（更新）

1. **browser_navigate 打开 PDF URL → 343 字节截断**  
   不要用 browser 访问 PDF 链接，改用 urllib 下载 + terminal pypdf 提取

2. **pypdf execute_code 超时**  
   execute_code 工具中 pypdf.Reader 操作超时；用 terminal 工具 + PYTHONPATH 指定 site-packages 路径

3. **上戏/上体附中官网 DNS 不通**  
   susfz.edu.cn / ssus.edu.cn / shxsfz.edu.sh.cn 等域名均无法解析  
   → 换用百度百科词条获取基本信息，Bing 搜索找其他来源

4. **urllib 直连高校官网 → 返回空内容**  
   北体/北舞/上戏官网 curl 访问返回空或 404  
   → browser_navigate 是正确工具，urllib 适合下载已知的 PDF URL

5. **delegate_task 子 agent 不实际执行**  
   commander lobster 军团 content 部门 delegate_task 只返回工具调用计划，不实际执行  
   → 自己动手用 browser/pypdf/urllib 直接执行

6. **www.shxfz.com 误判为上戏附中**  
   该域名实为广东清远盛兴集团，非上海戏剧学院附属中学，访问前先确认归属地

7. **urllib 中文字符 URL 编码**  
   URL 中含中文字符时必须用 `urllib.parse.quote` 编码整个 URL，否则报 `UnicodeEncodeError`  
   ```python
   url = "https://baike.baidu.com/item/" + urllib.parse.quote("上海体育学院附属中学")
   ```

8. **百度百科词条 urllib 直读 + 正则提取**（2026-05-26 验证）  
   ```python
   import urllib.request, urllib.parse, re
   url = "https://baike.baidu.com/item/" + urllib.parse.quote("上海体育学院附属中学")
   req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
   with urllib.request.urlopen(req, timeout=10) as r:
       content = r.read().decode('utf-8')
   # 按关键词提取上下文（前后150字符）
   for keyword in ['五环', '课程群', '博', '办学理念']:
       pattern = rf'.{{0,150}}{keyword}.{{0,150}}'
       for m in re.findall(pattern, content)[:2]:
           print(m.strip())
   ```
   成功率远高于页面渲染（browser_navigate），适合结构化提取词条正文。

9. **高校招生页面优先 HTML 版而非 PDF**  
   北舞官网同时有 PDF 版和 HTML 版招生信息：  
   - HTML 版 `http://www.bda.edu.cn/zsjy/bkzsxx/e2ac12fec980435b9a4db3e5a7a62b80.htm` → **browser_navigate + 正则直接提取成功**  
   - PDF 版需 urllib 下载 + pypdf 终端提取，超时风险高  
   → 遇到高校同时提供 HTML 和 PDF 时，优先抓 HTML，效率高出一个数量级。

## 五、百度百科词条提取标准流程（2026-05-26 实测）

当需要从百度百科提取学校/机构结构化信息时，按以下流程：

```python
import urllib.request, urllib.parse, re

def extract_baike(keyword, keywords=None):
    """从百度百科词条按关键词提取上下文"""
    url = "https://baike.baidu.com/item/" + urllib.parse.quote(keyword)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as r:
        content = r.read().decode('utf-8')
    if not keywords:
        return content  # 返回全文
    results = {}
    for kw in keywords:
        pattern = rf'.{{0,150}}{re.escape(kw)}.{{0,150}}'
        matches = re.findall(pattern, content)
        results[kw] = [m.strip() for m in matches[:3]]
    return results
```

**实操结果（2026-05-26）：**
- 上体附中词条（含"五环特色课程群"、"博·搏"校训、运动员占比三分之二等关键信息）→ 成功提取
- 上戏附中词条（含四门艺术课程、上戏教授参与教学、75%升学率等信息）→ 成功提取

**适用场景：** 学校/机构官网 DNS 不通、又无法通过政府/教育系统域名访问时，百度百科是唯一可稳定获取结构化文字信息的来源。