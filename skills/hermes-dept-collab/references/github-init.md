# GitHub 仓库初始化流程

## 关键前提

SSH 私钥 ≠ GitHub API Token。

| 能力 | SSH 私钥 | GitHub PAT |
|------|---------|-----------|
| git clone / push | ✅ | ✅ |
| 创建仓库（API） | ❌ | ✅ |
| 管理 repo settings | ❌ | ✅ |

**创建 GitHub 仓库必须用 Personal Access Token（PAT）**，SSH 私钥只能做 git 传输层操作。

---

## 初始化流程

### Step 1: 配置 SSH 私钥

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
cp /path/to/id_ed25519 ~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_ed25519

# 验证私钥
ssh-keygen -y -f ~/.ssh/id_ed25519
# 输出：ssh-ed25519 AAAA... user@email.com → 私钥有效

# 测试 GitHub 连接
ssh -T -o StrictHostKeyChecking=no git@github.com
# 成功输出：Hi username! You've successfully authenticated...
```

### Step 2: 获取 GitHub PAT

**方式 A：用 gh CLI（如果已安装）**
```bash
gh auth login
gh auth token
```

**方式 B：手动获取**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. 生成新 token，勾选 `repo` 范围
3. 保存 token（格式：`ghp_xxxxxxxx`）

### Step 3: 创建仓库（API）

```bash
GITHUB_TOKEN="ghp_xxxxxxxx"

# 创建公开仓库
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.github.com/user/repos \
  -d '{
    "name": "hermes-config",
    "description": "Hermes Army configuration backup",
    "public": true,
    "auto_init": false
  }'
```

### Step 4: 初始化本地 git 并推送

```bash
cd /home/ubuntu/.hermes

git init
git remote add origin git@github.com:username/hermes-config.git

# 追加 .gitignore（排除敏感文件）
cat >> .gitignore << 'EOF'
# 排除
cache/
logs/
sessions/
state.db*
auth.json
secrets/
gateway.pid
gateway.lock
EOF

# 追踪的文件
git add profiles/ skills/ scripts/ cron/output/ \
        knowledge_base.md projects/ config.yaml \
        SOUL.md army-architecture.txt

git commit -m "Initial commit"
git branch -M main
git push -u origin main
```

---

## 纳入 git 管理的目录

| 目录 | 建议 | 说明 |
|------|------|------|
| `profiles/` | ✅ | Agent 配置、SOUL.md |
| `skills/` | ✅ | 所有 skill 定义 |
| `scripts/` | ✅ | Python/Shell 脚本 |
| `cron/output/` | ✅ | 生成的报告存档 |
| `knowledge_base.md` | ✅ | 知识库 |
| `projects/` | ✅ | 主人待处理项目 |
| `config.yaml` | ✅ | 主配置 |
| `SOUL.md` | ✅ | 根配置 |
| `army-architecture.*` | ✅ | 架构文档 |
| `cache/` `logs/` `sessions/` | ❌ | 临时文件 |
| `state.db*` `auth.json` | ❌ | 运行时状态 |
| `secrets/` | ❌ | 密钥凭据 |

---

## 当前环境状态（2026-06-17）

- SSH 私钥：`~/.ssh/id_ed25519`（已配置）
- GitHub 账号：`githubstudy123456`（SSH 验证通过）
- PAT 状态：**未配置** — 需要主人提供 GitHub PAT 才能创建仓库

---

## 常用 GitHub API 端点

```bash
# 查看用户信息
curl -s -H "Authorization: token $TOKEN" https://api.github.com/user

# 查看现有仓库
curl -s -H "Authorization: token $TOKEN" https://api.github.com/user/repos

# 删除仓库（慎用）
curl -s -X DELETE \
  -H "Authorization: token $TOKEN" \
  https://api.github.com/repos/username/repo-name
```
