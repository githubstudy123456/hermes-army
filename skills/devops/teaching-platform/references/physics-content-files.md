# 物理教学平台文件清单与扫描脚本

## 文件命名规范

```
data/
└── 物理/
    ├── index.json          # 章节索引（id → name 映射）
    ├── stars.json          # 星级数据（按册次组织）
    ├── 1-1.json            # 第1章第1节内容
    ├── 1-2.json
    ├── ...
    └── 16-3.json
```

**文件命名**：不使用 curriculum.json，使用 `index.json`。

## 扫描缺失文件（Python）

```python
import json, os

data_dir = '/home/ubuntu/teaching-platform/data/物理/'

with open(data_dir + 'index.json') as f:
    index = json.load(f)

existing = set(f.replace('.json','') for f in os.listdir(data_dir) 
               if f.endswith('.json') and f not in ['index.json', 'stars.json'])

missing = []
for ch in index['章节']:
    for kp in ch['知识点']:
        kid = kp['id']
        if kid not in existing:
            missing.append((kid, kp['name']))

print(f"Missing: {missing}")
print(f"Total: {len(existing)}/{sum(len(ch['知识点']) for ch in index['章节'])}")
```

## 内容文件格式

### 旧格式（引入/知识点/小结/练习结构）

```json
{
  "id": "11-1",
  "name": "第一节 杠杆",
  "star": 4,
  "引入": { "类比说明": "...", "生活场景": [...] },
  "知识点": [
    { "title": "一、杠杆的定义", "讲解": "...", "关键公式": "...", "生活实例": [...], "小实验": {...} }
  ],
  "小结": { "要点": [...], "记忆口诀": "..." },
  "练习": [{ "type": "choice", "question": "...", "options": [...], "answer": 0, "analysis": "..." }]
}
```

⚠️ **注意**：旧格式文件中 `知识点[].讲解` 字段常为空（stub），需转换为新格式。

### 新格式（扁平知识点数组，2026-05迁移）

```json
[
  {
    "id": "12-2-1",
    "title": "电功率的定义与物理意义",
    "type": "knowledge",
    "modelKind": "none",
    "content": "详细知识点正文，200-400个中文字符，包含具体例子...",
    "summary": "一句话总结，30-60个中文字符"
  },
  {
    "id": "12-2-2",
    "title": "额定功率与实际功率",
    "type": "knowledge",
    "modelKind": "none",
    "content": "...",
    "summary": "..."
  }
]
```

**字段规范**：
- `id`: `{章节号}-{序号}`，如 `12-2-1`
- `type`: 固定 `"knowledge"`
- `modelKind`: `"none"` 或模型标识符（如 `"spring-oscillator"`）
- `content`: 200-400中文字符，含具体例子
- `summary`: 30-60中文字符

### JSON 转义陷阱 ⚠️

内容字段含 ASCII 双引号 `"` 会导致 JSON 解析失败：
```
JSONDecodeError: Expecting ',' delimiter: line 7 column 250 (char 353)
```

**解决**：用中文书名号 `「」` 替代，或对 `"` 做 `\` 转义。

```python
# 错误
"content": "标有"220V 60W"的灯泡"  # ❌

# 正确
"content": "标有「220V 60W」的灯泡"  # ✅
# 或
"content": "标有\\"220V 60W\\"的灯泡"  # ✅
```

## 当前物理内容文件列表（59+个）

```
章节: 1-1~1-4, 2-1~2-4, 3-1~3-4, 4-1~4-5, 5-1~5-3, 6-1~6-3,
      7-1~7-3, 8-1~8-4, 9-1~9-4, 10-1~10-4, 11-1~11-4,
      12-1~12-2 (已迁移新格式), 13-1~13-4, 14-1~14-5, 15-1~15-4, 16-1~16-3
```

**截至 2026-05-28**：11-4、12-1、12-2 已迁移至新格式。
**剩余待迁移**：56个旧格式stub需分批转换。
**缺失**：12-3（焦耳定律）待创建。