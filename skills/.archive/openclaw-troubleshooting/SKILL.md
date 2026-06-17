---
name: openclaw-troubleshooting
description: OpenClaw 启动、飞书连接故障排查、gateway 管理指南
triggers:
  - "openclaw 连不上"
  - "openclaw 启动"
  - "飞书 openclaw"
  - "openclaw gateway"
category: system
---

# OpenClaw 故障排查指南

## 启动 OpenClaw Gateway

### 正确重启 / 清理残留进程（完整流程）

**场景：想彻底重启或清理 openclaw（如内存占用过高、多个 ghost 进程残留）**

```bash
# 步骤 1：停止并禁用 systemd 服务（防止自动拉起）
systemctl --user stop openclaw-gateway.service
systemctl --user disable openclaw-gateway.service

# 步骤 2：分析进程树（确认谁在拉谁）
ps -ef | grep openclaw | grep -v grep
# 示例输出：
# 2969633 2396056 bash       (bash wrapper，openclaw 的父进程)
# 2969643 2969633 openclaw  (supervisor，自动拉起 gateway)
# 2969651 2969643 openclaw-gateway  (实际 gateway)
# 2972462 10064    openclaw-gateway  (另一个 ghost gateway，被 systemd 拉起)

# 步骤 3：杀掉所有残留 gateway 和 supervisor
# 先杀所有 gateway 子进程
for pid in $(pgrep openclaw-gateway); do kill $pid 2>/dev/null; done
# 再杀 supervisor
kill $(pgrep -f '^openclaw$' | grep -v grep) 2>/dev/null
# 如果还有残留，强制杀
kill -9 $(pgrep openclaw) 2>/dev/null
# 杀掉 bash wrapper（父进程）
kill -9 $(pgrep -f 'openclaw gateway run' | grep -v grep) 2>/dev/null

# 步骤 4：确认干净
ps aux | grep openclaw | grep -v grep
# 应只剩 bash（npm run dev 等无关进程）

# 步骤 5：确认端口释放
ss -tlnp | grep 18789  # 应无输出

# 步骤 6：重新启动（清除 proxy 环境变量）
env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY \
  openclaw gateway run &
# 或用 systemd（推荐，自动干净环境）
systemctl --user enable openclaw-gateway.service
systemctl --user start openclaw-gateway.service
```

**⚠️ 关键陷阱：**
- 直接 `kill <gateway_pid>` 会触发 systemd auto-restart 拉起新实例，看起来"杀不掉"。必须先停服务层。
- 如果有多个月 bash wrapper 同时存在（每次手动启动累积），旧的 wrapper 会继续拉起 supervisor，形成 zombie 进程链。用 `kill -9` 清理所有 wrapper。
- **不要用 `pkill -g`** 杀整个进程组，可能误杀其他进程。
- 启动时如果继承 proxy 环境变量，所有飞书 channel 会报 400 "plain HTTP request" 错误。必须 `env -u http_proxy ...` 清除后再启动。

### 正确启动方式
```bash
# ★ 必须用 systemd 管理，不要用 nohup
systemctl --user start openclaw-gateway    # 启动
systemctl --user stop openclaw-gateway     # 停止
systemctl --user restart openclaw-gateway  # 重启
systemctl --user status openclaw-gateway   # 状态
journalctl --user -u openclaw-gateway -f  # 实时日志
```

**为什么不用 nohup**：nohup 继承父 shell 的环境变量，如果 shell 里设置了 `HTTP_PROXY`/`HTTPS_PROXY`（如 v2ray 代理），Node.js/Axios 会把 HTTPS 请求发成明文 HTTP 格式，代理返回 400 "The plain HTTP request was sent to HTTPS port"，导致所有飞书 bot 连接全部失败。systemd 默认有干净环境，不会继承代理变量。

如果一定要手动启动，必须先清空代理环境：
```bash
unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy
nohup openclaw gateway > /tmp/oc_gw.log 2>&1 &
```

### 检查进程状态
```bash
ps aux | grep openclaw | grep -v grep
```

### 检查端口监听
```bash
ss -tlnp | grep 18789
```

---

## 飞书连接状态排查

### 查看 channel 状态
```bash
openclaw channels status
```

输出示例（正常）：
```
Feishu default: enabled, configured, running
```

### 查看详细健康状态
```bash
openclaw health
```

### 常见错误

#### tenant_access_token 错误
```
Feishu: failed (unknown) - Cannot destructure property 'tenant_access_token' 
of '(intermediate value)' as it is undefined.
```
**原因**：飞书应用的凭证（appId/appSecret）过期或无效  
**解决**：需要更新飞书凭证，重新配置 channels login

#### 400 "The plain HTTP request was sent to HTTPS port"
```
[error]: [ '[ws]', 'Request failed with status code 400' ]
[error]: [ '[ws]', 'connect failed' ]
```
**症状**：所有飞书 channel（8个 bot）全部 `stopped`，WebSocket 重连全失败，每个都报 400 + CONNECT failed

**原因**：Node.js 进程继承了 `HTTP_PROXY`/`HTTPS_PROXY` 环境变量（来自 shell 父进程或 nohup），Node.js/Axios 把 `POST https://open.feishu.cn/...` 发成了明文 HTTP 请求 `POST http://open.feishu.cn/...`，飞书服务器返回 400

**验证**：
```bash
# 在运行 openclaw 的进程环境里检查
cat /proc/$(pgrep openclaw-gateway | head -1)/environ | tr '\0' '\n' | grep -i proxy
# 有输出 = 继承了代理环境变量
```

**解决**：用 systemd 重启（干净环境）：
```bash
systemctl --user restart openclaw-gateway
```
不要用 nohup 启动，如果必须用 nohup，先 `unset HTTP_PROXY HTTPS_PROXY http_proxy https_proxy`

#### 配置命令
```bash
# 重新登录飞书
openclaw channels login --channel feishu
```

---

## 查看日志

```bash
# systemd journal 日志（最全）
journalctl --user -u openclaw-gateway --since "today" --no-pager

# 自定义日志文件
cat ~/.openclaw/logs/config-health.json
cat /tmp/oc_gw.log
```

### 关键排查：消息收到但没回复

gateway 进程在跑、飞书显示 connected，但用户没收到回复？

优先查 systemd journal：

```bash
journalctl --user -u openclaw-gateway --since "today" --no-pager | grep -E "pairing|dispatch|ERROR"
```

**`pairing request` = 访问被拒**：发消息的人不在允许列表，触发配对请求但没有后续回复。这是 **workspace 访问控制**问题，不是 gateway 挂了。

```log
pairing request sender=ou_xxxxxxxx  # ← 陌生人访问 lobster-* workspace 被拒
dispatch complete (queuedFinal=true, replies=N)  # ← 正常回复
```

**有 `received message` 无 `dispatch` = 消息收到但分发失败**：可能是 agent 处理异常或 session 问题。

**有 `dispatch` 但无 `dispatch complete` = agent 处理超时**：检查 agent 是否卡住、API 是否过载。

---

## 关键端口

| 端口 | 协议 | 说明 |
|------|------|------|
| 18789 | HTTP/WebSocket | Gateway 主端口 |
| 18791 | HTTP | 次要端口 |
| 36453 | HTTP | 内部端口 |

---

## 配置文件位置

- 主配置：`~/.openclaw/openclaw.json`
- 飞书配置：`~/.openclaw/openclaw.json` → `channels.feishu`
- Agent 配置：`~/.openclaw/agents/`
- Session：`~/.openclaw/agents/main/sessions/sessions.json`

### 查看飞书配置
```bash
cat ~/.openclaw/openclaw.json | python3 -c "
import json, sys
c = json.load(sys.stdin)
ch = c.get('channels', {}).get('feishu', {})
print('appId:', ch.get('appId'))
print('connectionMode:', ch.get('connectionMode'))
"
```

---

## 故障排查流程

```
1. 检查进程：ps aux | grep openclaw | grep -v grep
2. 检查端口：ss -tlnp | grep 18789
3. 查看channel状态：openclaw channels status
4. 查看health：openclaw health
5. 查看日志：journalctl --user -u openclaw-gateway --since "today" --no-pager
6. 检查代理环境：cat /proc/$(pgrep openclaw-gateway | head -1)/environ | tr '\0' '\n' | grep -i proxy
   → 有输出说明继承了代理环境变量，是 400 错误的根因，用 systemd 重启即可
```

---

## 多账号飞书配置（7 机器人架构）

### 关键：accounts 是 dict 不是 array
```json
"channels": {
  "feishu": {
    "accounts": {
      "ceo":         {"appId": "cli_...", "appSecret": "...", "name": "lobster-ceo", "groupAllowFrom": ["oc_群ID"]},
      "dev":         {"appId": "cli_...", "appSecret": "...", "name": "lobster-dev", "groupAllowFrom": ["oc_群ID"]}
    }
  }
}
```

**每个账号都要单独配 `groupAllowFrom`**（见踩坑记录第 8 条）。

### 批量检查 per-account groupAllowFrom
```bash
python3 -c "
import json
c = json.load(open('~/.openclaw/openclaw.json'))
for name, acc in c['channels']['feishu']['accounts'].items():
    ga = acc.get('groupAllowFrom', 'NOT SET')
    print(f'  {name}: {ga}')
"

### 绑定：type "route" vs "acp" 的区别

**`type: "acp"`** — 需要 `match.peer.id`（群/私聊的具体 conversation ID），不能通配。用于一对一持久会话。
```
❌ ACP bindings require match.peer.id to target a concrete conversation.
```
**原因**：`AcpBindingSchema` 有 superRefine 强制检查 `peer.id` 必须有值。

**`type: "route"`** — `peer` 可选，可以只按 `accountId` 路由。用于多 bot 通过 account 区分的场景。
```json
"bindings": [
  {"type": "route", "agentId": "lobster-ceo", "match": {"channel": "feishu", "accountId": "lobster-ceo"}},
  {"type": "route", "agentId": "lobster-dev", "match": {"channel": "feishu", "accountId": "lobster-dev"}}
]
```

### 群聊白名单：groupPolicy=allowlist
```json
"channels": {
  "feishu": {
    "groupPolicy": "allowlist",
    "groupAllowFrom": ["oc_8c4fa359fd2f4278307a435ee3826dac"]
  }
}
```
没有这个 → 群里消息全部被拒绝：`not in groupAllowFrom (groupPolicy=allowlist)`

### 完整 7 账号配置结构
```json
{
  "agents": {
    "list": [
      {"id": "main"},
      {"id": "lobster-ceo",     "workspace": "/home/ubuntu/.openclaw/workspace-lobster-ceo/"},
      {"id": "lobster-dev",     "workspace": "/home/ubuntu/.openclaw/workspace-lobster-dev/"},
      ...
    ]
  },
  "channels": {
    "feishu": {
      "enabled": true,
      "connectionMode": "websocket",
      "groupPolicy": "allowlist",
      "groupAllowFrom": ["oc_群ID"],
      "accounts": {
        "lobster-ceo":     {"appId": "cli_...", "appSecret": "...", "name": "lobster-ceo"},
        "lobster-dev":     {"appId": "cli_...", "appSecret": "...", "name": "lobster-dev"},
        ...
      }
    }
  },
  "bindings": [
    {"type": "route", "agentId": "lobster-ceo",     "match": {"channel": "feishu", "accountId": "lobster-ceo"}},
    {"type": "route", "agentId": "lobster-dev",     "match": {"channel": "feishu", "accountId": "lobster-dev"}},
    ...
  ]
}
```

### 验证配置
```bash
openclaw config validate
```

### 日志看绑定路由结果
```bash
journalctl --user -u openclaw-gateway --no-pager | grep -E "received message|not in groupAllow|dispatch"
```

## 多账号飞书配置识别

openclaw.json 中 `channels.feishu.accounts` 字典里有多个 bot：

| bot 名称 | appId | 用途 |
|----------|-------|------|
| `feishu[default]` | `cli_a96b4a83dd7c5bd6` | PM bot |
| `feishu[ceo]` | `cli_a96b530405785bde` | CEO bot |
| `feishu[dev]` | `cli_a96b4b3f0d381bcf` | 开发 bot |
| `feishu[qa]` | `cli_a96b4b852ce31bde` | 测试 bot |
| `feishu[content]` | `cli_a96b4be3c73a9bcf` | 内容 bot |
| `feishu[marketing]` | `cli_a96b4468633a9bda` | 市场 bot |
| `feishu[fullstack]` | `cli_a96b44c8ae7adbd8` | 全栈 bot |
| `feishu[chat]` | `cli_a954ec0730b85bc9` | chat bot（绑定 main agent，用于连接龙虾军团群） |

**注意**：config 里 account 字典的 key 是短名字（如 `ceo`、`dev`、`pm`），不是 `lobster-ceo`、`lobster-dev`。binding 里的 `accountId` 也用短名字。

**按 appId 查日志**：
```bash
# 查特定 bot 的消息
journalctl --user -u openclaw-gateway --since "HH:MM" --no-pager | grep "feishu\[default\]"

# 同时看所有 bot 的消息接收情况
journalctl --user -u openclaw-gateway --since "today" --no-pager | grep "received message"
```

## 踩坑记录

1. **只运行 openclaw 不够**：必须用 `openclaw gateway` 子命令才能启动 WebSocket gateway
2. **openclaw 会自动 fork**：运行 `openclaw gateway` 后会 fork 出多个进程，这是正常的
3. **飞书 running 不代表正常**：`channels status` 显示 running 但 `health` 可能仍失败（token 问题）
4. **进程消失**：gateway 进程可能意外退出，需要 nohup 后台运行或 systemd 服务化
5. **用户没收到回复但进程在跑**：优先查 `journalctl` 中的 `pairing request` — 很可能是 workspace 访问控制拒绝了发消息的人，不是 gateway 故障
6. **Config hot reload 导致消息丢失**：gateway 重启时会触发 `feishu[xxx]` channel restart，如果发过来的消息在此时到达，会直接丢弃。症状：日志里最后一条 `received message` 时间点之后用户发的消息全部消失。**原因**：飞书事件订阅 URL 没变，但 gateway 重启期间的消息队列丢失。
7. **消息没到 gateway = 飞书事件订阅断了**：如果 `journalctl` 里某个 bot 的 `received message` 在某个时间点之后完全消失，但飞书应用显示"已连接"，说明**事件推送没到**，不是 gateway 处理问题。需要去飞书开放平台 → 应用功能 → 事件订阅，检查订阅的 URL 是否指向正确的 gateway 公网地址。
8. **Bot 在群里被 groupPolicy 拦，但 channel-level groupAllowFrom 看起来正确** — 如果 bot 在群里收到 "not in groupAllowFrom (groupPolicy=allowlist)"，但 channel-level `groupAllowFrom` 配置里确实有这个群 ID，说明 **per-account groupAllowFrom 覆盖了 channel-level 配置**。OpenClaw 优先级：**per-account groupAllowFrom > channel-level groupAllowFrom**。当 per-account 没配时，fallback 逻辑是 `account.groupAllowFrom ?? (configuredAllowFrom.length > 0 ? configuredAllowFrom : void 0)` — 如果 channel-level 是空数组 `[]`（length=0），fallback 变成 `void 0`，导致 groupPolicy 完全失效。**解决**：在**每个 account** 里单独配 `groupAllowFrom`，不只是 channel level。

```
# 每个 lobster 账号都要单独配：
"accounts": {
  "ceo": {
    "appId": "cli_...",
    "groupAllowFrom": ["oc_8c4fa359fd2f4278307a435ee3826dac"]
  },
  "dev": {
    "appId": "cli_...",
    "groupAllowFrom": ["oc_8c4fa359fd2f4278307a435ee3826dac"]
  }
}
```

9. **修改 per-account 配置（如 groupAllowFrom）会触发 config hot reload 但不会重启 channel** — 这是好事，7 个 bot 的 WebSocket 连接不会中断，消息处理不受影响。修改 channel-level 配置才会导致 channel restart。

10. **Pairing 需要每个 bot 单独 approve** — 不同 bot 账号对应不同的飞书 user ID，发消息给不同 bot 会触发不同的 pairing request。需要分别 `openclaw pairing approve feishu <code>`。

10. **多 bot 群里消息路由** — 当多个 bot 在同一个群里时，每个 bot 只能收到 @它 的消息（飞书平台行为）。没被 @的 bot 收不到群消息，不会触发 groupPolicy。

龙虾军团群（oc_8c4fa359fd2f4278307a435ee3826dac）：
- 7 个 lobster bot 全部 pairing 完毕（ceo/dev/pm/qa/content/marketing/fullstack）
- chat bot（appId: cli_a954ec0730b85bc9）已配对，绑定 main agent，用于连接龙虾军团群
- 最后一个问题：CEO bot 在龙虾军团群里仍被 groupPolicy 拦（not in groupAllowFrom），已对所有账号单独加 groupAllowFrom 配置待验证
- 下次会话优先检查：龙虾军团群里 @任意 lobster bot 是否有响应

12. **图片分析**：execute_code 里的 hermes_tools 不支持 PIL。vision_analyze 可以分析本地图片，但需要通过文件 URI 格式（`file:///绝对路径`），不接受相对路径。

13. **nohup 继承代理导致 400 所有 channel 全挂**：当 shell 里设置了 `HTTP_PROXY`/`HTTPS_PROXY`（如 v2ray HTTP 代理），用 nohup 启动 openclaw 时这些变量会被子进程继承。Node.js/Axios 把 HTTPS URL 发成明文 HTTP 格式，请求被代理拒绝（400 Bad Request）。症状：所有 feishu channel 同时 `stopped`，每个都报 `Request failed with status code 400` + `connect failed`。**解决**：永远用 `systemctl --user restart openclaw-gateway`，不要用 nohup。验证：`journalctl --user -u openclaw-gateway --since "today" | grep "plain HTTP request"`

15. **`contentDedupeCache.get is not a function`（OpenClaw 2026.4.14 bug）**：飞书 channel 在群里收到 @mention 时，`inbound debounce flush` 阶段崩溃，错误为 `TypeError: contentDedupeCache.get is not a function`。影响：CEO bot 和 default bot 在龙虾军团群里被 @ 时静默无响应（消息收到但无法 dispatch）。**解决**：升级到 2026.4.15。
    ```bash
    npm update -g openclaw
    openclaw --version  # 确认 2026.4.15
    systemctl --user restart openclaw-gateway
    ```
    **验证**：`journalctl --user -u openclaw-gateway --since "today" | grep contentDedupeCache`，无输出说明 bug 已修。

17. **dispatch complete(replies=1) 但飞书无回复 — delivery recovery 卡住**：gateway 重启后，旧的 delivery 条目卡在 pending 状态，agent 返回的回复被路由到这些 stale delivery 任务但实际投递失败。日志特征：
    ```
    [delivery-recovery] Found N pending delivery entries — starting recovery
    [delivery-recovery] Retry failed for delivery <uuid>: Feishu account "chat" not configured
    [delivery-recovery] Recovered delivery <uuid> on feishu  ← 重启后有这条说明上次有卡住的
    ```
    日志里看到 `dispatch complete (queuedFinal=true, replies=1)` 证明 agent 已回复，但飞书用户没收到。**解决**：重启 gateway 清理 delivery 队列：
    ```bash
    systemctl --user restart openclaw-gateway
    ```

16. **Bot 回复"👍"而不是正经内容 — 口水过滤规则**：如果用 `openclaw agent` 手动触发 lobster-dev 等 bot，它们回复"👍"不搭理你，这是**正常行为**不是故障。

    **根因**：每个 lobster 的 AGENTS.md 里配置了"口水过滤规则"——短消息（≤10字）且不含动作词（帮我、查、写、做、整理、分析等）会被判定为"口水"，直接回 👍。

    **日志验证**：
    ```bash
    openclaw logs --limit 50 --json 2>&1 | grep -E '"message":"👍"'
    # 会看到 lobster-dev 输出 "👍"
    ```

    **解决**：发消息时带动作词或超过 10 字，例如：
    ```
    # 触发口水过滤（回👍）
    "你好，测试通讯"
    # 触发完整处理（正常回复）
    "开发总监，介绍一下你自己"
    ```

    **注意**：在飞书群里被 @ 不会触发这个规则（群消息走完整 dispatch 流程），只有 `openclaw agent` 手动触发时才生效。

## `openclaw agent` 命令行发消息（踩坑）

**目的**：想通过命令行给 lobster bot 发消息，验证它们是否响应。

### `--deliver` 超时 60 秒

```bash
timeout 60 openclaw agent --agent lobster-ceo --channel feishu --session-id oc_8c4fa... --message "测试" --deliver
# 返回：Command timed out after 60s
```

**原因**：`openclaw agent --deliver` 底层走 WebSocket 协议和 gateway 通信，不是 REST API。gateway 处理慢或 session 状态不对时会卡住 60 秒后超时。这是 expected behavior，不是 gateway 挂了。

### REST API 不支持发消息

```bash
curl http://127.0.0.1:18789/api/agent        # → 404 Not Found
curl http://127.0.0.1:18789/api/v1/status    # → 404 Not Found
curl http://127.0.0.1:18789/                 # → 返回 OpenClaw Control UI HTML
```

gateway 18789 端口是 WebSocket/HTTP 服务器，提供 Control UI，不提供 agent 消息 REST API。

### 正确验证方式：直接在飞书群 @bot

在龙虾军团群（oc_8c4fa359fd2f4278307a435ee3826dac）里直接发：

```
<at user_id="ou_b8661dd85562f9d48558bd003bd4842a">总管龙虾</at> 报到
<at user_id="ou_07476257486c9dafd1cdb3df260c8bdc">开发龙虾</at> 报到
```

能收到回复 → OpenClaw 轨正常。收不到 → 按上面故障流程排查。

### `openclaw sessions list` 语法

```
openclaw sessions list              # ✓ 正确
openclaw sessions list --json       # ✓ 正确
openclaw sessions list --agent xxx  # ✗ "too many arguments"
openclaw sessions list --all-agents # ✗ "too many arguments"
```

`sessions` 是独立子命令，不接受 `sessions list` 这种带空格的子命令链。

## Session 溢出修复（Hermes / OpenClaw）

### 症状

commander 在飞书群里收到消息后没有响应，日志显示消息已 flush 但 `response ready` 从未出现。gateway 进程看似正常，但模型卡死在处理历史上下文。

### 根因

活跃会话 `.jsonl` 文件消息条数超过阈值（常见 >150 条），context 溢出导致模型无法生成响应。

### 诊断

```bash
# 查看 gateway 日志（卡死特征：最后一条是 "Flushing text batch" 但没有 "response ready"）
tail -30 ~/.hermes/profiles/commander/logs/agent.log

# 查看 session 文件行数（超过 150 条即为危险会话）
wc -l ~/.hermes/profiles/commander/sessions/*.jsonl | sort -n | tail

# 检查进程是否存活
ps aux | grep hermes | grep -v grep
```

### 修复步骤

1. **归档卡死会话**：
   ```bash
   cd ~/.hermes/profiles/commander/sessions/
   mv 20260423_190903_e62d29.jsonl 20260423_190903_e62d29_STUCK_archived.jsonl
   ```

2. **重启 gateway**：
   ```bash
   ps aux | grep "hermes.*gateway" | grep -v grep
   kill <PID>
   sleep 2
   cd /home/ubuntu && HERMES_HOME=/home/ubuntu/.hermes/profiles/commander \
     /home/ubuntu/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace &
   ```

### 预防：session_cleanup.py

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

if __name__ == "__main__":
    main()
```

保存到 `~/.hermes/scripts/session_cleanup.py`，每小时自动检查。

### 配置 max_messages

在 `~/.hermes/profiles/commander/config.yaml` 的 `session_reset` 下加：

```yaml
session_reset:
  mode: both
  idle_minutes: 1440
  at_hour: 4
  max_messages: 80
```

### OpenClaw Session 清理

OpenClaw session 主要清理对象是 `.trajectory.jsonl`（积累最快）和超长 `.jsonl`：

```bash
# 查看所有 lobster agent session 大小
du -sh ~/.openclaw/agents/*/sessions

# 找最大的 trajectory 文件
find ~/.openclaw/agents -name "*.trajectory.jsonl" -exec ls -lh {} \; | sort -k5 -hr | head -10

# 清理策略：
# - .trajectory.jsonl：积累最快，优先清理
# - .jsonl.reset.*：历史备份，可直接删除
# - 活跃 .jsonl：根据 max_messages 配置决定是否归档
```

---

## ClawHub Skills 查询与安装

clawhub.ai 浏览器访问成功率低，`npx clawhub explore` 经常返回 `No skills found`。

**正确方法**：用 `npx clawhub search <关键词>` 做向量搜索：

```bash
npx clawhub search "finance budget"     # 财务/CFO 相关
npx clawhub search "developer coding"   # 开发相关
npx clawhub search "marketing content"  # 市场/内容相关
npx clawhub search "product manager"    # PM 相关
npx clawhub search "qa testing"         # QA 相关
npx clawhub search "fullstack frontend" # 全栈相关
npx clawhub search "ceo executive"      # CEO/总管相关
```

**安装到 lobster workspace**：
```bash
npx clawhub install <slug> --workdir ~/.openclaw/workspace-lobster-<role> --dir skills
```

ClawHub CLI 无需全局安装，直接 `npx clawhub@latest` 即可。
