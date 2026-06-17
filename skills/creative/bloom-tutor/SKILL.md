---
name: bloom-tutor
description: Bloom 2-Sigma AI Tutor — 部署、使用、二次开发。Benjamin Bloom 的 2σ 效应 + AI Agent 实现一对一苏格拉底式导师。
tags: [ai-tutor, bloom, fastapi, react, docker, learning]
trigger: 当用户想用 Bloom 项目学习某个主题、或要部署/维护/扩展这个 AI 导师系统时加载
---

# Bloom AI Tutor

## 核心定位

基于 [Li-Evan/Bloom](https://github.com/Li-Evan/Bloom) 的 AI 一对一导师系统。Benjamin Bloom 1984年提出"2 Sigma Problem"：一对一导师能让学生成绩从平均提升到前2%（+2σ）。本系统用 AI Agent 复现这个效果。

## 项目结构

```
bloom-tutor/
├── backend/          # FastAPI + Python 3.11, JWT认证, SQLite
├── frontend/         # React 19 (TypeScript)
├── docker-compose.yml
├── .env             # LLM API 配置
├── CLAUDE.zh.md     # 交互协议（中文导师规则）
└── GUIDE.zh.md      # 用户指南
```

## 部署步骤

### 1. 环境准备

Docker 和 docker-compose 必须先安装：

```bash
# Ubuntu 22.04，用 apt（get.docker.com 被代理屏蔽时）
sudo apt-get update
sudo apt-get install -y docker.io docker-compose --allow-unauthenticated
sudo systemctl enable docker
sudo systemctl start docker
docker --version
```

### 2. Clone 项目

```bash
git clone https://github.com/Li-Evan/Bloom.git /home/ubuntu/bloom-tutor
```

> ⚠️ GitHub 直连可能超时（代理问题），先验证：`curl -s --connect-timeout 5 https://github.com` 不通就走代理。

### 3. 配置 .env

```bash
cp /home/ubuntu/bloom-tutor/.env.example /home/ubuntu/bloom-tutor/.env
```

必填项：
```env
LLM_API_KEY=你的key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1  # 阿里云DashScope（通义千问）
LLM_MODEL=qwen-plus
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
DATABASE_URL=sqlite:///./bloom.db
```

也可切换为 OpenRouter（免费额度）：
```env
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_API_KEY=sk-or-...
LLM_MODEL=mistralai/mistral-7b-instruct
```

### 4. docker-compose 端口修复

backend 默认不暴露端口，需手动加入（否则前端调用不到）：
```yaml
services:
  backend:
    ports:
      - "8000:8000"   # 加这行
```

### 5. 启动

```bash
cd /home/ubuntu/bloom-tutor
docker-compose up -d --build
# 验证
curl http://localhost:8000/api/health
# 前端访问：http://服务器IP:3000
```

### 6. 关闭

```bash
docker-compose down        # 停止
docker-compose down -v     # 停止+删除数据
```

---

## 导师交互协议（来自 CLAUDE.zh.md）

### 铁律：同一轮交互内完成 syllabus.md + 01.md

用户说"帮我学习 [主题]"，同一轮必须生成完整课程大纲 + 首节内容，不得拆分两轮。

### syllabus.md 格式规范

- 核心哲学：**学习目标固定，学习路径弹性**
- 每条目标是可验证的行为（能解释/能推导/能应用/能判断），禁止"了解X"
- 2-5个知识模块，总条目 8-15 条
- 有 checkbox，学完可勾选

### 学习流程

1. 用户给课题 → 生成 `syllabus.md` + `01.md`（同轮）
2. 用户学完 01.md 后在反馈区给理解情况
3. 基于反馈调整下一个文档（苏格拉底追问+讲解）
4. 循环直到 syllabus 全部掌握项勾满

---

## 扩展方向

- 接中文模型（通义千问/DeepSeek，修改 LLM_MODEL）
- 接 Whisper 实现语音输入/播报
- 接入飞书：定时推送学习进度报告
- 多课题并行：不同文件夹管理不同学科

---

## 已知坑

1. **docker-compose backend 不暴露 8000 端口**：默认只有 frontend:3000，API 调用全挂。必须手动在 docker-compose.yml 里加 `ports: "8000:8000"`
2. **get.docker.com 被代理屏蔽**：apt 装 docker.io，走腾讯镜像源
3. **GitHub clone 超时**：先测连通性，不通先开代理
