# OpenClaw + Hermes 双系统架构：账号体系与群组路由

## 核心概念：三个系统，两套账号

| 系统 | appId | 连接群 | 路由方式 |
|------|-------|--------|----------|
| **Hermes commander**（⭐☚本体） | `cli_a9632857a4bc9bc4` | `oc_08f6cb`（Hermes军团） | 飞书 gateway 直连 |
| **OpenClaw default** | `cli_a954ec0730b85bc9` | `oc_8c4fa`（龙虾军团）+ `oc_c6883`（订阅群） | `groupAllowFrom` 白名单 |
| **OpenClaw lobster bots** | 复用 Hermes profiles 的 appId | `oc_8c4fa`（龙虾军团） | `groupAllowFrom` 白名单 |

**OpenClaw `default` 账号不是 Hermes。** 它是最初的 OpenClaw chat bot（appId `cli_a954ec`），当它被加入某个群时，那个群里的消息它也会响应。

## 关键发现：两个系统共享同一批 appId，绑定不同群组

**同一个 appId，被 OpenClaw 和 Hermes 两个系统复用：**

| appId | OpenClaw 账号 | Hermes profile | 绑 OpenClaw 群 | 绑 Hermes 群 |
|-------|-------------|----------------|---------------|-------------|
| `cli_a96b4b3f0d381bcf` | dev | lobster-dev | `oc_8c4fa`（龙虾军团） | `oc_08f6cb`（Hermes军团） |
| `cli_a96b4468633a9bda` | marketing | lobster-market | `oc_8c4fa`（龙虾军团） | `oc_08f6cb`（Hermes军团） |
| `cli_a96b4a83dd7c5bd6` | pm | lobster-product | `oc_8c4fa`（龙虾军团） | `oc_08f6cb`（Hermes军团） |
| `cli_a96b4b852ce31bde` | qa | lobster-test | `oc_8c4fa`（龙虾军团） | `oc_08f6cb`（Hermes军团） |

**同一个飞书 bot appId 在两个群里是"两个独立身份"** — 在龙虾军团群的消息只有 OpenClaw bot 能收到，在 Hermes军团的消息只有 Hermes profile 能收到。互不干扰。

### 有 appId 但 Hermes 侧无飞书配置的部门

这些部门在 OpenClaw 侧有配置，但 Hermes 侧无 `platforms.feishu`，无法通过飞书 @ 它们：

| appId | 部门 | OpenClaw 侧 | Hermes 侧 |
|-------|------|------------|----------|
| `cli_a96b530405785bde` | CEO | ✅ | ❌ |
| `cli_a96ec9e03af89bca` | CFO | ✅ | ❌ |
| `cli_a96b4be3c73a9bcf` | content | ✅ | ❌ |
| `cli_a96b44c8ae7adbd8` | fullstack | ✅ | ❌ |

## 路由机制：`groupAllowFrom` 白名单（OpenClaw）

OpenClaw 通过 `groupAllowFrom` 决定哪个账号能接收哪个群的消息。

```json
{
  "accounts": {
    "default": {
      "appId": "cli_a954ec0730b85bc9",
      "groupAllowFrom": [
        "oc_8c4fa359fd2f4278307a435ee3826dac",
        "oc_c6883cd907e4d226736d87ce9c6c6d79"
      ]
    },
    "ceo": {
      "appId": "cli_a96b530405785bde",
      "groupAllowFrom": [
        "oc_8c4fa359fd2f4278307a435ee3826dac"
      ]
    }
  }
}
```

**规则：** 账号只接收 `groupAllowFrom` 列表中群的消息。如果群不在列表里，账号收不到。

## 爱马仕军团 vs 龙虾军团

| 称呼 | 代号 | 说明 |
|------|------|------|
| 爱马仕军团 | 对主人公开的正式名称 | 原来的"龙虾军团"已更名，profile 代号仍用 `lobster-*` |
| 龙虾军团群 | `oc_8c4fa359fd2f4278307a435ee3826dac` | OpenClaw lobster bots 所在的飞书群 |
| Hermes军团群 | `oc_08f6cb45cf9c2132e7ee86fd6fb5dec9` | Hermes commander 和爱马仕军团 profiles 所在的群 |

## 实际操作清单

### 查账号绑定状态
```bash
cat ~/.openclaw/openclaw.json | python3 -c "
import sys, json
d = json.load(sys.stdin)
feishu = d['channels']['feishu']
for name, acc in feishu['accounts'].items():
    print(f\"{name}: appId={acc['appId']}, groups={acc['groupAllowFrom']}\")
"
```

### 查 Hermes profile 的飞书配置
```bash
for dir in ~/.hermes/profiles/lobster-*; do
  name=$(basename $dir)
  feishu=$(python3 -c "
import sys, yaml
try:
    with open('$dir/config.yaml') as f:
        d = yaml.safe_load(f)
    p = d.get('platforms', {})
    if p.get('feishu'):
        feishu = p['feishu']
        app_id = feishu.get('extra', {}).get('app_id', 'N/A')
        group = feishu.get('extra', {}).get('group_chat_id', 'N/A')
        print(f'app_id={app_id[:20]}..., group={group}')
    else:
        print('no feishu config')
except: print('err')
" 2>/dev/null)
  echo "$name | $feishu"
done
```

### appId 交叉对比脚本
```python
import yaml, json, os

with open('/home/ubuntu/.openclaw/openclaw.json') as f:
    openclaw = json.load(f)
openclaw_accounts = {k: v['appId'] for k, v in openclaw['channels']['feishu']['accounts'].items()}

profiles_dir = '/home/ubuntu/.hermes/profiles'
hermes_profiles = {}
for name in os.listdir(profiles_dir):
    cfg_path = os.path.join(profiles_dir, name, 'config.yaml')
    if os.path.exists(cfg_path):
        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)
        app_id = cfg.get('platforms', {}).get('feishu', {}).get('extra', {}).get('app_id', None)
        if app_id:
            hermes_profiles[name] = app_id

print("=== CROSS-CHECK ===")
for profile, hermes_app in hermes_profiles.items():
    for oc_name, oc_app in openclaw_accounts.items():
        if hermes_app == oc_app:
            match = "✅ SAME" if hermes_app == oc_app else "❌"
            print(f"  {profile} ↔ {oc_name}: {hermes_app[:20]}... {match}")
```

### 从龙虾军团群移除 default（避免重复响应）
修改 `~/.openclaw/openclaw.json`，从 `default.groupAllowFrom` 中删除 `oc_8c4fa...`：
```json
"default": {
  "appId": "cli_a954ec0730b85bc9",
  "groupAllowFrom": ["oc_c6883cd907e4d226736d87ce9c6c6d79"]
}
```
然后重启 gateway：`systemctl --user restart openclaw-gateway`

### 添加新 lobster bot 到群
1. 在飞书开放平台创建应用，获得 appId + appSecret
2. 在 `~/.openclaw/openclaw.json` 的 `accounts` 下添加新账号
3. 在 `agents.list` 添加新 agent（id=代号，workspace=`~/.openclaw/workspace-{代号}/`）
4. 重启 gateway

## 已知群ID速查

| 名称 | 群ID | 用途 |
|------|------|------|
| 龙虾军团群 | `oc_8c4fa359fd2f4278307a435ee3826dac` | OpenClaw lobster bots |
| 订阅日报群 | `oc_c6883cd907e4d226736d87ce9c6c6d79` | 每日资讯推送 |
| Hermes军团群 | `oc_08f6cb45cf9c2132e7ee86fd6fb5dec9` | Hermes commander + 爱马仕军团 profiles |

## OpenClaw 配置结构速查

```
~/.openclaw/openclaw.json
├── agents.list[]           # agent 定义（id, name, workspace, tools）
├── bindings[]             # agent → accountId → peer 精确路由（当前已填写）
├── channels.feishu.accounts{}  # 飞书账号（appId, groupAllowFrom）
└── channels.feishu.defaultAccount  # 默认账号

~/.hermes/profiles/<name>/
├── config.yaml            # Hermes profile 配置（toolsets, platforms.feishu）
├── SOUL.md                # Agent 角色定义
└── workspace/            # 独立工作区
```