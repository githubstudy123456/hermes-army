---
name: agency-agents-sync
description: 同步 GitHub agency-agents 库至本地，并行安全审计，修复安全问题
triggers:
  - "帮我同步一下 agency-agents"
  - "agency-agents 有没有漏装"
  - "审阅一下 agency-agents"
  - "agency-agents 安全吗"
---

# agency-agents 同步与审计

同步 /home/ubuntu/agency-agents/ 至 GitHub 最新状态，并行安全审计。

## 使用场景
主人有 GitHub 上的 agency-agents 库，本地可能有缺漏或版本不一致。

## 标准流程

### Step 1 — 用 GitHub API 对比目录差异

```python
import json, subprocess

result = subprocess.run(
    ["curl", "-s", "https://api.github.com/repos/msitarzewski/agency-agents/contents/"],
    capture_output=True, text=True
)
github_dirs = [i["name"] for i in json.loads(result.stdout)
               if i["name"] not in [".git", "README.md", "CONTRIBUTING.md", "LICENSE"]
               and i["type"] == "dir"]
```

### Step 2 — 逐目录对比文件数量

```python
for dir in github_dirs:
    gh_count = subprocess.run(
        ["curl", "-s", f"https://api.github.com/repos/msitarzewski/agency-agents/contents/{dir}"],
        capture_output=True, text=True
    )
    github_files = set(i["name"] for i in json.loads(gh_count.stdout) if i["name"].endswith(".md"))
    local_files = set(__import__("os").listdir(f"/home/ubuntu/agency-agents/{dir}/"))
    missing = github_files - local_files
    if missing:
        print(f"⚠️  {dir} 缺: {sorted(missing)}")
```

### Step 3 — 并行下载缺失文件

```python
import concurrent.futures, subprocess

def download_file(dir, filename):
    url = f"https://raw.githubusercontent.com/msitarzewski/agency-agents/main/{dir}/{filename}"
    path = f"/home/ubuntu/agency-agents/{dir}/{filename}"
    subprocess.run(["curl", "-sL", url, "-o", path])
    print(f"✅ {dir}/{filename}")

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(download_file, d, f) for d, files in missing_by_dir.items() for f in files]
    concurrent.futures.wait(futures)
```

### Step 4 — 派发子任务并行审计（3个并发上限）

```python
delegate_task(
    tasks=[
        {"goal": "审计 finance/ (5文件) + specialized/ (10文件)", "toolsets": ["terminal","file"]},
        {"goal": "审计 engineering/ (8文件) + marketing/ + sales/ (4文件)", "toolsets": ["terminal","file"]},
        {"goal": "审计其余目录 (design/testing/support/product/PM/academic/strategy等，抽样8-10文件)", "toolsets": ["terminal","file"]},
    ],
    max_iterations=40
)
```

每个子任务审计内容：
1. 文件用途（一行）
2. 安全标志：eval/exec/未知curl目标/凭证获取/混淆/base64解码/外部脚本
3. 总结发现

### Step 5 — 修复安全问题

常见问题修复模式：

**eval() → ast.literal_eval()**
```python
# 替换 eval(fix['transformation'])
import ast
transform_fn = ast.literal_eval(fix['transformation'])
```

**env 空字符串默认值**
```javascript
// 替换 || '' 为 fail-fast 校验
const required = ['FEISHU_APP_ID', 'FEISHU_APP_SECRET'];
const missing = required.filter(k => !process.env[k]);
if (missing.length > 0) {
  throw new Error(`Missing required: ${missing.join(', ')}`);
}
```

## 验证
```bash
python3 -c "
import subprocess, json
for dir in ['finance','engineering','marketing','specialized']:
    gh = json.loads(subprocess.run(['curl','-s',f'https://api.github.com/repos/msitarzewski/agency-agents/contents/{dir}'], capture_output=True, text=True).stdout)
    github = sum(1 for i in gh if i['name'].endswith('.md'))
    local = len(__import__('os').listdir(f'/home/ubuntu/agency-agents/{dir}/'))
    print(f'✅ {dir}: {local}/{github}' if github==local else f'⚠️  {dir}: {local}/{github}')
"
```

## 相关文件
- /home/ubuntu/agency-agents/ — 专家知识库根目录
- 14个分类目录，157个agent定义文件
