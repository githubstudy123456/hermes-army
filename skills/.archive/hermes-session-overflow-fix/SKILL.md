---
name: hermes-session-overflow-fix
description: 修复 Hermes Agent / OpenClaw commander gateway 会话溢出卡死问题——诊断、重启、归档、自动清理全流程
version: 1.0.0
date_created: 2026-04-24
tags: [hermes, openclaw, session, gateway, troubleshooting, commander]
---

# Hermes / OpenClaw Session 溢出修复与自动清理

## 症状

commander 在飞书群里收到消息后没有响应，日志显示消息已 flush 但 `response ready` 从未出现。gateway 进程看似正常，但模型卡死在处理历史上下文。

## 根因

活跃会话 `.jsonl` 文件消息条数超过阈值（常见 >150 条），context 溢出导致模型无法生成响应。

## 诊断步骤

### 1. 查看 gateway 日志
```bash
tail -30 ~/.hermes/profiles/commander/logs/agent.log
```
卡死特征：最后一条是 `Flushing text batch` 但没有 `response ready`。

### 2. 查看 session 文件行数
```bash
wc -l ~/.hermes/profiles/commander/sessions/*.jsonl | sort -n | tail
```
超过 150 条的 .jsonl 即为危险会话。

### 3. 检查进程是否存活
```bash
ps aux | grep hermes | grep -v grep
```

## 修复流程

### 步骤1：归档卡死会话
```bash
cd ~/.hermes/profiles/commander/sessions/
mv 20260423_190903_e62d29.jsonl 20260423_190903_e62d29_STUCK_archived.jsonl
```

### 步骤2：重启 gateway
```bash
# 找到旧进程 PID
ps aux | grep "hermes.*gateway" | grep -v grep

# SIGTERM 优雅停止
kill <PID>
sleep 2

# 重启
cd /home/ubuntu && HERMES_HOME=/home/ubuntu/.hermes/profiles/commander \
  /home/ubuntu/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace &
```

## 自动清理（预防）

### 清理脚本
写入 `~/.hermes/scripts/session_cleanup.py`：
```python
import json, os, shutil, time
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "/home/ubuntu/.hermes/profiles/commander"))
SESSIONS_DIR = HERMES_HOME / "sessions"
MAX_MESSAGES = 150

def count_messages(path: Path) -> int:
    try:
        with open(path) as f:
            return sum(1 for line in f if line.strip() and json.loads(line))
    except Exception:
        return 0

def main():
    for f in SESSIONS_DIR.glob("*.jsonl"):
        if f.stat().st_size == 0:
            continue
        count = count_messages(f)
        if count > MAX_MESSAGES:
            archive = f.with_name(f.stem + f"_archived_{int(time.time())}.jsonl")
            shutil.move(str(f), str(archive))
            print(f"归档: {f.name} ({count} 条)")
    print("清理完成")
```

### 配置 session_reset.max_messages
在 `~/.hermes/profiles/commander/config.yaml` 的 `session_reset` 下加一行：
```yaml
session_reset:
  mode: both
  idle_minutes: 1440
  at_hour: 4
  max_messages: 80
```

### 创建每小时 Cron 任务
```
hermes cron create \
  --name commander-session-cleanup \
  --prompt "python3 ~/.hermes/scripts/session_cleanup.py" \
  --schedule "0 * * * *" \
  --script session_cleanup.py
```
会在每整点自动检查并归档超长会话，下次清理时间可在 `hermes cron list` 查看。

### 验证清理脚本
```bash
python3 ~/.hermes/scripts/session_cleanup.py
```
输出示例：`清理了 18 个超长会话: - 20260415_015228_7c5b2e.jsonl (314 条消息) → 已归档`

## 关键文件路径

### Hermes Commander
| 文件 | 作用 |
|------|------|
| `~/.hermes/profiles/commander/logs/agent.log` | gateway 主日志 |
| `~/.hermes/profiles/commander/sessions/*.jsonl` | 会话消息历史 |
| `~/.hermes/profiles/commander/state.db-wal` | SQLite WAL 日志 |
| `~/.hermes/scripts/session_cleanup.py` | 自动清理脚本 |
| `~/.hermes/profiles/commander/config.yaml` | gateway 配置 |

### OpenClaw Lobster Army
| 文件 | 作用 |
|------|------|
| `~/.openclaw/agents/*/sessions/*.jsonl` | 普通会话消息 |
| `~/.openclaw/agents/*/sessions/*.trajectory.jsonl` | **内存大户**，每个 20-30MB，积累最快 |
| `~/.openclaw/agents/*/sessions/*.trajectory-path.json` | trajectory 路径文件 |
| `~/.openclaw/agents/*/sessions/*.reset.*` | 重置备份，可删除 |
| `~/.openclaw/openclaw.json` | openclaw 主配置 |
| `~/.openclaw/tasks/runs.sqlite` | openclaw 任务数据库 |

## OpenClaw Session 清理（扩展）

OpenClaw lobster army 的 session 路径分布在各 agent workspace 下，主要清理对象是 `.trajectory.jsonl` 和过大的 `.jsonl` 文件。

### 诊断
```bash
# 查看所有 lobster agent session 大小
du -sh ~/.openclaw/agents/*/sessions

# 找最大的 trajectory 文件
find ~/.openclaw/agents -name "*.trajectory.jsonl" -exec ls -lh {} \; | sort -k5 -hr | head -10

# 查看会话文件行数
wc -l ~/.openclaw/agents/main/sessions/*.jsonl | sort -n | tail
```

### 清理策略
- `.trajectory.jsonl`：积累最快，优先清理
- `.jsonl.reset.*`：历史备份，可直接删除
- 活跃 `.jsonl`：根据 `max_messages` 配置决定是否归档

### OpenClaw 清理脚本
```python
import json, os, shutil, time
from pathlib import Path

OPENCLAW_SESSIONS = Path("/home/ubuntu/.openclaw/agents")
MAX_MESSAGES = 150

def count_messages(path: Path) -> int:
    try:
        with open(path) as f:
            return sum(1 for line in f if line.strip() and json.loads(line))
    except Exception:
        return 0

def main():
    total_freed = 0
    for agent_dir in OPENCLAW_SESSIONS.iterdir():
        sessions = agent_dir / "sessions"
        if not sessions.is_dir():
            continue
        for f in sessions.glob("*.trajectory.jsonl"):
            sz = f.stat().st_size / (1024*1024)
            archive = f.with_name(f.stem + f"_archived_{int(time.time())}.jsonl")
            shutil.move(str(f), str(archive))
            print(f"归档 {agent_dir.name}/{f.name} ({sz:.1f}MB)")
            total_freed += sz
        for f in sessions.glob("*.reset.*"):
            sz = f.stat().st_size / (1024*1024)
            f.unlink()
            print(f"删除 {agent_dir.name}/{f.name} ({sz:.1f}MB)")
            total_freed += sz
        for f in sessions.glob("*.jsonl"):
            if count_messages(f) > MAX_MESSAGES:
                archive = f.with_name(f.stem + f"_archived_{int(time.time())}.jsonl")
                shutil.move(str(f), str(archive))
                print(f"归档超长会话 {agent_dir.name}/{f.name}")
    print(f"共释放约 {total_freed:.1f}MB")
```

## 预防建议

- commander 作为任务中枢，频繁派发任务，最容易积累长会话
- `max_messages: 80` 配合 `idle_minutes: 1440`（24小时空闲重置）双重保护
- 每次重启后观察日志确认 gateway 提示 `Previous gateway exited cleanly`
