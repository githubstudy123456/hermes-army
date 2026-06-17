# Feishu 飞书调试参考

## 排查飞书消息问题时的正确日志路径

### Gateway 日志（Hermes 飞书消息）

**正确路径：** `~/.hermes/logs/gateway.log`

这条日志记录的是 Hermes 自己的飞书连接、收到的消息和回复状态。

```
grep -a "feishu\|DM from\|dispatch\|streaming\|Closed streaming" ~/.hermes/logs/gateway.log | tail -50
```

### Gateway 状态文件

`~/.hermes/profiles/commander/gateway_state.json` 包含连接状态：

```bash
cat ~/.hermes/profiles/commander/gateway_state.json | python3 -m json.tool
```

重点字段：
- `platforms.feishu.state` — `connected` = 正常
- `platforms.weixin.state` — 微信连接状态

### ❌ 错误路径：OpenClaw 日志

`~/.openclaw/logs/openclaw.log` 是 **OpenClaw**（另一个 bot 框架）的日志，不是 Hermes 的。如果你在这些日志里找飞书消息，会找到 lobster agents 的会话记录（OpenClaw 自己的 DM/群消息）。

两者区别：

| 日志 | 内容 |
|------|------|
| `~/.hermes/logs/gateway.log` | Hermes 飞书 DM/群消息、dispatch 记录 |
| `~/.openclaw/logs/openclaw.log` | OpenClaw 的消息（另一个 bot，与 Hermes 无关） |

## 群消息被动监控：权限机制详解

**问题：Hermes 能不能主动监听群消息（不被 @ 也能收到）？**

答案取决于飞书开放平台的权限配置，不是 OpenClaw 的路由规则。

### 两个缺一不可的前提

**1. 飞书开放平台 — 应用权限配置**

在飞书开放平台 → 应用功能 → 事件订阅：
- 必须开启「接收消息」权限（事件类型选「接收消息」）
- 有此权限的 bot 可以开启「静默监听」模式，收取群里所有消息
- 普通 bot 必须被 @ 才收得到

**2. Hermes SOUL.md — 主动介入规则**

Hermes 收到消息后由 `~/.hermes/SOUL.md` 里的规则决定要不要主动发言。

参考格式（龙虾 CEO 的实现）：
```markdown
## 主动监控规则
**不必被 @ 也能介入。** 在以下情况主动发言：
1. 主人情绪：语气异常、表达不满、提出表扬
2. 内容质量：报告方向偏差、明显错误、数据不实
3. 任务状态：定时任务失败、推送未送达
```

### OpenClaw vs Hermes：两个独立的飞书连接

这是两个独立的 bot 系统：

| | Hermes（⭐☁️） | OpenClaw（lobster 军团） |
|--|--------|----------|
| 飞书应用 | Hermes 自己的 appId（cli_a954ec0730b85bc9） | lobster 各自的 appId（ceo/dev/pm...） |
| SOUL.md | `~/.hermes/SOUL.md` | `~/.openclaw/workspace-*/SOUL.md` |
| 群消息路由 | Hermes gateway | OpenClaw binding 配置 |
| 日志 | `~/.hermes/logs/gateway.log` | `~/.openclaw/logs/openclaw.log` |

**关键澄清**：龙虾军团的 lobster agents 运行在 OpenClaw 上，有自己的 SOUL.md 和飞书连接。Hermes 走 `~/.hermes/logs/gateway.log`。两者互不干扰。

### 排查流程

1. **确认 Hermes 收到了群消息**：
   ```
   grep "oc_605cb68\|group.*received" ~/.hermes/logs/gateway.log | tail -20
   ```
   有记录 = Hermes 收到了群消息

2. **看 OpenClaw 日志确认 lobster 消息**：
   ```
   grep "oc_8c4fa\|dispatch" ~/.openclaw/logs/openclaw.log | tail -20
   ```

3. **确认飞书开放平台的权限**：
   登录飞书开放平台 → 找到对应的应用 → 检查「事件订阅」是否开启了「接收消息」

### 当前状态（2026-06-16）

- Hermes app（cli_a954ec0730b85bc9）：groupAllowFrom 包含日报群 + 周报群
- 飞书开放平台的「消息事件订阅」权限状态待确认（需要用户去飞书控制台检查）
- OpenClaw lobster 群（oc_8c4fa359fd2f4278307a435ee3826dac）：lobster 各自的 app 已授权，能被动监控

## 快速诊断流程

1. 检查 gateway 是否在跑：
   ```bash
   ps aux | grep hermes | grep gateway
   ```

2. 检查飞书连接状态：
   ```bash
   cat ~/.hermes/profiles/commander/gateway_state.json
   ```

3. 查看 Hermes gateway 日志（飞书消息在这里）：
   ```bash
   tail -100 ~/.hermes/logs/gateway.log | grep -i feishu
   ```

4. 查看飞书收到的消息（`DM from` = 私信）：
   ```bash
   grep "DM from" ~/.hermes/logs/gateway.log | tail -20
   ```

5. `dispatch complete` = Hermes 已回复；`dispatching to agent` = 正在处理

## 常见状态码含义

| 日志关键词 | 含义 |
|-----------|------|
| `DM from ou_XXX` | 收到私信（p2p） |
| `received message in oc_XXX (group)` | 收到群消息 |
| `dispatching to agent` | 正在路由到 AI 处理 |
| `dispatch complete` | 处理完成 |
| `Started streaming` / `Closed streaming` | 卡片消息发送中/完成 |
| `stuck session` | 会话卡住（处理超时） |

## DM vs 群消息

- DM（私信）：日志显示 `DM from ou_XXX`
- 群消息：日志显示 `received message in oc_XXX (group)`

如果你在订阅群发消息没有回复，检查 Bot 是否被移出群，或 `FEISHU_GROUP_POLICY` 是否设为 `open`。
