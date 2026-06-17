---
name: japan-server
description: Japan 服务器 (207.56.226.147) 操作手册 — PPTX处理、知识树API、SSH subprocess编码问题
trigger: 当需要在 Japan 服务器上做文件操作、API开发、或调用 find_json.py 时
trigger: SSH subprocess 调用传中文参数时报错或无输出
trigger: 需要操作 /data/baidu-library/ 目录
---

# Japan 服务器操作手册

**SSH：** `ssh -i ~/.ssh/japan root@207.56.226.147`
**关键路径：**
- PPTX源文件：`/tmp/hermes/pptx/`
- JSON转换后：`/data/baidu-library/files/`
- 课件脚本：`/tmp/hermes/find_json.py`（Python 3，依赖 pptx + json）

---

## 已知问题：SSH subprocess 编码

**问题描述：**
通过 Python `subprocess` 执行远程 SSH 命令时，中文参数会失败（无输出，rc=1）。
直接在终端执行 SSH 命令是正常的。

**触发条件：**
```python
subprocess.run([
    '/usr/bin/ssh', '-i', '/home/ubuntu/.ssh/japan', '-o', 'StrictHostKeyChecking=no',
    'root@207.56.226.147',
    'python3', '/tmp/hermes/find_json.py', '第一章+机械运动（单元复习课件）.json'
], capture_output=True, text=True)
# rc=1, stdout='', stderr=''
```

**Workaround — 直接cat+grep（推荐）：**
```python
cmd = [
    '/usr/bin/ssh', '-i', '/home/ubuntu/.ssh/japan',
    'root@207.56.226.147',
    "grep -rl '机械运动' /data/baidu-library/files/ 2>/dev/null | head -5"
]
r = subprocess.run(cmd, capture_output=True, text=True)
```

**Workaround — 文件名搜索用grep不用脚本：**
```bash
ssh -i ~/.ssh/japan root@207.56.226.147 \
  'cd /data/baidu-library/files && grep -rl "机械运动" . 2>/dev/null | head'
```

**find_json.py 直接用时的正确方式：**
SSH到服务器后，本地执行：
```bash
ssh -i /home/ubuntu/.ssh/japan root@207.56.226.147 \
  'python3 /tmp/hermes/find_json.py "第一章 机械运动"'
```
不要通过 subprocess 从 Python 调用这个脚本。

---

## 工作流程

### PPTX → JSON 批量转换
```
源目录: /tmp/hermes/pptx/
目标目录: /data/baidu-library/files/
```
转换脚本参考 `teaching-platform` 的 `ppteach/` 模块。
完成后删除原PPTX（需确认）。

### 知识树 API
Flask端读 `/data/baidu-library/files/` 下的JSON，聚合为：
```
GET /api/knowledge-tree?subject=物理
→ {subject, grades: [{grade, chapters: [{title, knowledge_points: [{name, star, desc}]}]}]}
```

### Japan 服务器 Flask 服务
端口 5001，`nohup python3 app.py &`
日志：`journalctl -u flask -f`

---

## 验证命令
```bash
# 检查JSON文件数量
ssh -i ~/.ssh/japan root@207.56.226.147 'ls /data/baidu-library/files/ | wc -l'

# 检查Flask是否在跑
ssh -i ~/.ssh/japan root@207.56.226.147 'curl -s localhost:5001/api/knowledge-tree?subject=物理 | head -c 200'

# 检查磁盘
ssh -i ~/.ssh/japan root@207.56.226.147 'df -h /data'
```