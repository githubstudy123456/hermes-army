#!/usr/bin/env python3
"""
⭐☁️ Hermes Agent 每周自我报告
生成我的状态、技能、近期动态，发送到飞书群
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

HERMES_HOME = Path.home() / ".hermes"
OUTPUT_DIR = HERMES_HOME / "cron" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FEISHU_APP_ID = "cli_a95612fc9ebddbc8"
FEISHU_GROUP_CHAT_ID = "oc_c6883cd907e4d226736d87ce9c6c6d79"


def curl_post(url, headers=None, data=None, form_data=None):
    cmd = ["curl", "-s", "-X", "POST", url]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    if data:
        cmd += ["-d", data]
    if form_data:
        for item in form_data:
            cmd += ["-F", item]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.stdout


def get_feishu_creds():
    """从 ~/.hermes/.env 文件直接读取飞书凭证"""
    env_file = HERMES_HOME / ".env"
    if not env_file.exists():
        raise Exception("~/.hermes/.env 文件不存在")
    app_secret = None
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line.startswith("FEISHU_APP_SECRET="):
            app_secret = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    if not app_secret:
        raise Exception("FEISHU_APP_SECRET 未在 .env 中找到")
    return FEISHU_APP_ID, app_secret


def get_token():
    app_id, app_secret = get_feishu_creds()
    r = curl_post(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"app_id": app_id, "app_secret": app_secret})
    )
    return json.loads(r)["tenant_access_token"]


def upload_file(token, file_path):
    r = curl_post(
        "https://open.feishu.cn/open-apis/im/v1/files",
        headers={"Authorization": f"Bearer {token}"},
        form_data=[
            "file_type=stream",
            f"file_name={file_path.name}",
            f"file=@{file_path};type=text/markdown"
        ]
    )
    resp = json.loads(r)
    if resp.get("code") != 0:
        raise Exception(f"上传失败: {resp}")
    return resp["data"]["file_key"]


def send_file_to_group(token, file_key, file_name):
    """发送文件到飞书群（大姐姐群）"""
    payload = json.dumps({
        "receive_id": FEISHU_GROUP_CHAT_ID,
        "msg_type": "file",
        "content": json.dumps({"file_key": file_key})
    })
    r = curl_post(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        data=payload
    )
    resp = json.loads(r)
    if resp.get("code") != 0:
        raise Exception(f"发送失败: {resp}")
    return resp["data"]["message_id"]


def get_memory_summary():
    """读取 MEMORY.md 关键信息"""
    mem_file = HERMES_HOME / "memory" / "MEMORY.md"
    if not mem_file.exists():
        return {}
    content = mem_file.read_text()
    info = {}
    in_section = None
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("## "):
            in_section = line[3:].strip()
        elif in_section == "👤 主人信息" and ": " in line:
            key, _, val = line.partition(": ")
            if val:
                info[key.strip()] = val.strip()
        elif in_section and line.startswith("## "):
            in_section = None
    return info


def get_skills_summary():
    """按分类统计 Skills"""
    skills_dir = HERMES_HOME / "skills"
    by_cat = {}
    cat_names = {
        "autonomous-ai-agents": "🤖 子Agent派遣",
        "software-development": "📦 研发流程",
        "devops": "🛠️ 运维&部署",
        "github": "🔨 GitHub",
        "messaging": "💬 消息通讯",
        "productivity": "📊 效率工具",
        "mlops": "🧠 AI/ML",
        "media": "🎨 媒体生成",
        "creative": "✨ 创意工具",
        "data-science": "📈 数据科学",
        "research": "🔬 学术研究",
        "smart-home": "🏠 智能家居",
        "social-media": "🌐 社交媒体",
        "gaming": "🎮 游戏",
        "email": "📧 邮件",
        "note-taking": "📝 笔记",
        "system": "⚙️ 系统",
        "openclaw-imports": "🅾️ OpenClaw导入",
        "leisure": "☕ 生活",
        "red-teaming": "🔴 安全测试",
        "dogfood": "🧪 Dogfood测试",
    }
    if skills_dir.exists():
        for item in sorted(skills_dir.iterdir()):
            if item.is_dir():
                cat = item.name
                label = cat_names.get(cat, cat)
                skills = sorted([p.name for p in item.iterdir() if p.is_dir()])
                if skills:
                    by_cat[label] = skills
    return by_cat


def get_proxy_nodes():
    """读取代理节点配置"""
    proxy_file = HERMES_HOME / "proxy_nodes.json"
    if not proxy_file.exists():
        return []
    nodes = json.loads(proxy_file.read_text())
    return nodes.get("nodes", [])[:5]


def get_projects():
    """读取项目库，只返回进行中的项目"""
    proj_file = HERMES_HOME / "projects.json"
    if not proj_file.exists():
        return []
    try:
        data = json.loads(proj_file.read_text())
        active = [p for p in data.get("projects", []) if p.get("status") != "已完成"]
        return active
    except Exception:
        return []


def generate_report():
    now = datetime.now()
    date_str = now.strftime("%Y年%m月%d日 %H:%M")
    week_ago_str = (now - timedelta(days=7)).strftime("%m月%d日")

    memory = get_memory_summary()
    skills_by_cat = get_skills_summary()
    total_skills = sum(len(v) for v in skills_by_cat.values())
    proxy_nodes = get_proxy_nodes()

    owner_name = memory.get("称呼", "主人")
    owner_ai = memory.get("AI名字", "⭐☁️")
    owner_interests = memory.get("感兴趣的", "")
    owner_network = memory.get("网络限制", "")

    projects = get_projects()

    skills_lines = []
    for cat, items in sorted(skills_by_cat.items()):
        skills_lines.append(f"- **{cat}**（{len(items)}）：`" + "`、`".join(items) + "`")

    proxy_lines = []
    for n in proxy_nodes:
        proxy_lines.append(f"- **{n['name']}**：{n['server']}:{n['port']}")

    cron_file = HERMES_HOME / "cron" / "jobs.json"
    cron_count = 0
    if cron_file.exists():
        jobs = json.loads(cron_file.read_text())
        cron_count = len(jobs.get("jobs", []))

    report = f"""# ⭐☁️ Hermite 每周状态报告

> **生成时间：** {date_str}  
> **统计周期：** {week_ago_str} ～ 今天

---

## 一、身份信息

| 项目 | 内容 |
|------|------|
| AI 名称 | {owner_ai} |
| 主人称呼 | {owner_name} |
| 平台 | Android |
| 感兴趣的方向 | {owner_interests} |
| 网络限制 | {owner_network} |

---

## 二、技能统计（{total_skills} 个 Skills）

### 技能分类详情

{chr(10).join(skills_lines)}

---

## 三、代理节点配置（{len(proxy_nodes)} 个）

{chr(10).join(proxy_lines) if proxy_lines else "（无）"}

> 共 {len(proxy_nodes)} 个节点（完整配置在 `~/.hermes/proxy_nodes.json`）

---

## 四、任务调度（Cron Jobs）

| 项目 | 数值 |
|------|------|
| 活跃定时任务数 | {cron_count} |
| 下次执行 | 每周一 09:00 CST（两个报告同时触发） |

---

## 五、进行中项目

{chr(10).join([f"- **{p['name']}**（{p['client']}）：{p.get('description','')} [{p['status']}]" for p in projects]) if projects else "（无进行中项目）"}

---

## 六、长期记忆摘要

- **代理配置**：15 个节点，已配置 V2Ray/Trojan
- **龙虾军团**：9 个 Agent（main + 8 lobster），全部具有 exec 权限
- **飞书配置**：Hermes app `cli_a95612fc9ebddbc8`
- ** Skills 系统**：{total_skills} 个技能，覆盖研发/数据/媒体/运维等方向
- **网络**：访问外网需要代理（已配置）

---

_⭐☁️ Hermes 自我状态报告 · 每周一 09:00 CST 自动生成并推送_  
_脚本路径：`~/.hermes/scripts/hermes-weekly-report.py`_
"""
    return report


if __name__ == "__main__":
    report = generate_report()
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = OUTPUT_DIR / f"hermes-status-{today}.md"
    output_path.write_text(report)
    print(f"报告已生成：{output_path}", file=sys.stderr)

    # 发送到飞书群（用 Hermes 自己的身份）
    try:
        token = get_token()
        file_key = upload_file(token, output_path)
        msg_id = send_file_to_group(token, file_key, f"hermes-status-{today}.md")
        print(f"已发送到飞书群：message_id={msg_id}", file=sys.stderr)
    except Exception as e:
        print(f"飞书发送失败：{e}", file=sys.stderr)
        sys.exit(1)
