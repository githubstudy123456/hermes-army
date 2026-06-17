# 物理教学平台 — 物料处理工作流

## 上传目录
`/home/ubuntu/physics-visual-platform/uploads/`

文件名格式：`{年级}-{教材名}-{章节}.zip`
示例：`8上-初中物理人教版-第1章-机械运动.zip`

## ZIP 结构
```
{教材名}/
├── manifest.json          ← 目录索引（含 panPath → localPath 映射）
├── 02 课件/               ← PPT 文件
│   ├── 第1节 xxx/
│   │   ├── 第1课时 xxx.pptx
│   │   └── 课件衔接说课稿.docx
│   └── ...
├── 06 单元测试/
├── 07 知识清单/           ← docx 格式
├── 10 试题试卷/
└── ...
```

## 正确读取中文文件名 ZIP 的方式

**❌ 错误**：用 `unzip -l`，中文文件名显示乱码
**✅ 正确**：Python zipfile 自动处理编码
```python
import zipfile
zf = zipfile.ZipFile('/path/to/file.zip', 'r')
for info in zf.infolist()[:10]:
    print(info.filename)  # 自动正确解码

# 读 manifest.json
content = zf.read('教材名/manifest.json').decode('utf-8')
import json
manifest = json.loads(content)
print(manifest['chapter'])  # {'book', 'no', 'title', 'name'}
```

## 已有 extracted-text 的路径
`/home/ubuntu/physics-visual-platform/docs/materials/8a-physics/extracted-text/`
包含：
- 各节导学案（教师版/学生版）`.txt`
- 各节教学设计 `.txt`
- 第1章速记清单（解析版/原卷版）`.txt`

这些是已提取好的纯文本，可直接用于填充知识点内容。

## PPTX 解析（用于提取课件文字）
PPTX 本质是 ZIP，XML 在 `ppt/slides/` 目录下：
```python
import zipfile
zf = zipfile.ZipFile('课件.pptx', 'r')
# 读第1页
content = zf.read('ppt/slides/slide1.xml').decode('utf-8')
# 用 re 提取 <a:t> 标签内的文字
import re
texts = re.findall(r'<a:t[^>]*>([^<]+)</a:t>', content)
```

## curriculum.json 当前结构
位置：`/home/ubuntu/physics-visual-platform/src/data/curriculum.json`
章节数据在 `chapters[].points[]`，知识点字段：
- `id`, `title`, `section`
- `narrations[step/title/narration]` — 讲解内容
- `model` — 模型类型（'none'|'average-speed'|'relative-motion'|...）
- `model_type` — 'cart'|'optics'|'wave'|'spring'|'none'

需要填充的字段（来自教学资料）：
- `objective` — 学习目标
- `explanation` — 讲解主线
- `method[]` — 原理/方法列表
- `examples[]` — 典型例题
- `mistakes[]` — 易错点
- `practice` — 练习题目

## 当前 UI 状态（2026-05-26）
- 右侧知识点精讲（标题/目标/原理/例子/易错/练习）
- 无统一格式强迫症：不需要模型的章节干净展示，不加多余按钮
- 模型折叠已移除（model-entry-btn 已删除）
- 配色：深蓝星空风（#00d4ff 青蓝 + #0d1b2a 渐变背景）
- Three.js 星空粒子背景组件：`src/components/ThreeBackground.tsx`
- Build 通过