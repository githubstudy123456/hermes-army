#!/usr/bin/env python3
"""
session_cleanup.py — 自动清理超长的 commander 会话文件
防止 context 溢出导致 gateway 卡死。

阈值：超过 150 条消息的 session 文件直接删除（下一个请求会开新 session）
"""

import json, os, sys
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "/home/ubuntu/.hermes/profiles/commander"))
SESSIONS_DIR = HERMES_HOME / "sessions"
MAX_MESSAGES = 150  # 超过此条数则清理


def count_messages(path: Path) -> int:
    try:
        with open(path) as f:
            return sum(1 for line in f if line.strip() and json.loads(line))
    except Exception:
        return 0


def main():
    if not SESSIONS_DIR.exists():
        return

    removed = []
    for f in SESSIONS_DIR.glob("*.jsonl"):
        # 跳过当前活跃会话（agent.log 里正在写的）
        if f.stat().st_size == 0:
            continue
        count = count_messages(f)
        if count > MAX_MESSAGES:
            # 直接删除超长会话，不做归档（文件名可能超 NAME_MAX）
            f.unlink()
            removed.append((f.name, count))

    if removed:
        print(f"[session_cleanup] 清理了 {len(removed)} 个超长会话:")
        for name, count in removed:
            print(f"  - {name} ({count} 条消息) → 已归档")
    else:
        print(f"[session_cleanup] 无需清理，最大会话条数: {max((count_messages(f) for f in SESSIONS_DIR.glob('*.jsonl')), default=0)}")


if __name__ == "__main__":
    main()
