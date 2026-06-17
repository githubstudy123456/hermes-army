# Japan Server — Baidu Library 数据库

**服务器**: 207.56.226.147  
**数据库**: `/data/baidu-library/library.db` (SQLite)

## 连接方式

```bash
ssh -i ~/.ssh/japan root@207.56.226.147
```

## 快速查询

```python
# 查所有表
import sqlite3
conn = sqlite3.connect('/data/baidu-library/library.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print([r[0] for r in cur.fetchall()])
conn.close()
```

## materials 表结构

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| subject | TEXT | 学科（如"初中物理"） |
| grade | TEXT | 年级 |
| volume | TEXT | 册次 |
| chapter | TEXT | 章节 |
| material_type | TEXT | 材料类型 |
| title | TEXT | 标题 |
| original_name | TEXT | 原始文件名 |
| file_path | TEXT | 源文件路径 |
| size_bytes | INTEGER | 大小 |
| sha256 | TEXT | 校验码 |
| source | TEXT | 来源 |
| notes | TEXT | 备注 |
| created_at | TEXT | 创建时间 |
| updated_at | TEXT | 更新时间 |

## 材料统计（截至2026-05-30）

- **PPT**: 60 个
- **教案**: 28 份
- **知识点**: 34 份
- **测试**: 36 份
- **练习**: 24 份
- **合计**: 182 条

## 源文件目录结构

```
/data/baidu-library/files/初中物理/八年级/上册/第2章-声现象/
├── PPT/
│   ├── 第1节 声音的产生与传播.pptx
│   └── 第2节 声音的特性.pptx
├── 知识点/
│   ├── 第2章 声现象【速记清单】（原卷版）.docx
│   └── ...
├── 教案/
│   ├── 第1节 声音的产生与传播.docx
│   └── ...
└── 测试/ / 练习/
```

## 典型查询

```python
# 查某章节 PPT
cur.execute('SELECT title, file_path FROM materials WHERE material_type = "PPT" AND chapter LIKE "%声现象%"')

# 查教案列表
cur.execute('SELECT title, file_path FROM materials WHERE material_type = "教案"')

# 查知识点
cur.execute('SELECT title, file_path FROM materials WHERE material_type = "知识点"')
```

## 待办

- [ ] 在日本服务器部署 Flask API 提供知识点数据 + PPT 下载
- [ ] 本地通过 SSH 隧道访问 API
- [ ] 或将数据库内容同步到 teaching-platform 本地 data/ 目录