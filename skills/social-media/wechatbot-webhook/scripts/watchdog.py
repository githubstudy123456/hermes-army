#!/usr/bin/env python3
"""
微信机器人 + AI 服务监控
检测服务存活状态，服务挂了则通过飞书通知主人

用法：
    python3 watchdog.py

Cron 配置（每分钟检查）：
    * * * * * cd /home/ubuntu/wechatbot && python3 watchdog.py >> /tmp/watchdog.log 2>&1
"""
import os
import sys
import time
import subprocess
import requests

# ============ 配置区 ============
FEISHU_WEBHOOK = "https://open.feishu.cn/open-apis/bot/v2/hook/oc_c6883cd907e4d226736d87ce9c6c6d79"
CHECK_INTERVAL = 60  # 每60秒检查一次

SERVICES = [
    {"name": "AI服务(Flask:8080)", "check": "health", "url": "http://localhost:8080/health"},
    {"name": "微信机器人(node)", "check": "process", "cmd": "pgrep -f 'node main.js'"},
]

COOLDOWN = 3600  # 同一服务挂了1小时后再通知
COOLDOWN_FILE = "/tmp/service_watchdog_cooldown"

# ============ 工具函数 ============
def check_process(cmd: str) -> bool:
    result = subprocess.run(cmd, shell=True, capture_output=True)
    return result.returncode == 0

def check_http(url: str) -> bool:
    try:
        resp = requests.get(url, timeout=5)
        return resp.status_code == 200
    except:
        return False

def check_service(svc: dict) -> bool:
    if svc["check"] == "process":
        return check_process(svc["cmd"])
    elif svc["check"] == "health":
        return check_http(svc["url"])
    return True

def load_cooldown() -> dict:
    data = {}
    if os.path.exists(COOLDOWN_FILE):
        try:
            import json
            with open(COOLDOWN_FILE, "r") as f:
                data = json.load(f)
        except:
            pass
    return data

def save_cooldown(data: dict):
    import json
    with open(COOLDOWN_FILE, "w") as f:
        json.dump(data, f)

def should_notify(svc_name: str) -> bool:
    data = load_cooldown()
    last = data.get(svc_name, 0)
    return time.time() - last >= COOLDOWN

def record_notify(svc_name: str):
    data = load_cooldown()
    data[svc_name] = time.time()
    save_cooldown(data)

def feishu_notify(message: str):
    try:
        payload = {"msg_type": "text", "content": {"text": message}}
        requests.post(FEISHU_WEBHOOK, json=payload, timeout=10)
    except Exception as e:
        print(f"[飞书通知失败] {e}", file=sys.stderr)

# ============ 主循环 ============
def main():
    print(f"🔍 服务监控启动，每{CHECK_INTERVAL}秒检查一次")

    dead_services = []
    for svc in SERVICES:
        alive = check_service(svc)
        print(f"[{'✅' if alive else '❌'}] {svc['name']}")
        if not alive:
            dead_services.append(svc["name"])

    if dead_services:
        msg = "⚠️ 微信机器人服务异常\n\n停止的服务：\n" + "\n".join("• " + s for s in dead_services)
        msg += "\n\n需要人工介入处理，请尽快检查！"

        for ds in dead_services:
            if should_notify(ds):
                feishu_notify("⚠️ " + ds + " 已停止，需要人工介入")
                record_notify(ds)
        print("📤 已发送飞书通知")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n监控已停止")
        sys.exit(0)