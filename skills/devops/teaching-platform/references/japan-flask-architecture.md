# Japan 服务器角色

**角色：** 文件数据库 + PPTX 解析引擎（远端）

**地址：** Japan（服务器名）
**PPTX 文件路径模式：** `初中物理/八年级/上册/第1章-机械运动/PPT/第1课时  长度的单位和测量.pptx`

---

## 本地 Flask API 网关

**监听：** `localhost:5001`
**路由：** `GET /api/japan/pptx?path=<url编码的路径>`
**行为：**
1. 接收请求，构造 Japan 服务器上的命令
2. 通过 SSH 在 Japan 上执行 PPTX 解析脚本
3. 返回 JSON：`{"slides": [{"texts": [...]}, ...], ...}`
4. 超时：65秒

**验证命令：**
```python
import urllib.request, urllib.parse, json
path = '初中物理/八年级/上册/第1章-机械运动/PPT/第1课时  长度的单位和测量.pptx'
url = f'http://localhost:5001/api/japan/pptx?path={urllib.parse.quote(path)}'
resp = urllib.request.urlopen(url, timeout=65)
data = json.loads(resp.read())
slides = data.get('slides', [])
print(f'共 {len(slides)} 页')
```

**已知返回结构：** 27页演示文稿，第1页含"第一章    机械运动"，第16页含"长度的单位和测量"

---

## 架构图

```
用户点击章节
    ↓
前端请求 GET /api/japan/pptx?path=...
    ↓
本地Flask (port 5001)
    ↓ SSH
Japan服务器（文件存储 + PPTX解析）
    ↓
返回JSON {slides: [{texts: [...]}, ...]}
    ↓
前端渲染幻灯片
```

---

## 备注

- Japan 与本地 Flask 之间通过 SSH 密钥互信
- 该 endpoint 仅处理 PPTX 解析，不处理 Word/Excel
- 前端尚未接入此接口（用户说"要做吗？还是先把架构稳定下来？"）