#!/usr/bin/env python3
"""
session_cleanup.py — 自动清理超长的 commander 会话文件
防止 context 溢出导致 gateway 卡死。

阈值：超过 150 条消息的 session 文件归档为 _archived_*.jsonl
"""

import json, os, shutil, time
from pathlib import Path

HERMES_HOME = Path(os.environ.get("HERMES_HOME", "/home/ubuntu/.hermes/profiles/commander"))
SESSIONS_DIR = HERMES_HOME / "sessions"
MAX_MESSAGES = 150


def count_messages(path: Path) -> int:
    """统计 JSONL 文件中的消息条数（非空有效行）"""
    try:
        with open(path) as f:
            return sum(1 for line in f if line.strip() and json.loads(line))
    except Exception:
        return 0


def main():
    if not SESSIONS_DIR.exists():
        print("[session_cleanup] sessions 目录不存在")
        return

    removed = []
    for f in SESSIONS_DIR.glob("*.jsonl"):
        if f.stat().st_size == 0:
            continue
        count = count_messages(f)
        if count > MAX_MESSAGES:
            archive = f.with_name(f.stem + f"_archived_{int(time.time())}.jsonl")
            shutil.move(str(f), str(archive))
            removed.append((f.name, count))

    if removed:
        print(f"[session_cleanup] 清理了 {len(removed)} 个超长会话:")
        for name, count in removed:
            print(f"  - {name} ({count} 条消息) → 已归档")
    else:
        max_count = max((count_messages(f) for f in SESSIONS_DIR.glob("*.jsonl")), default=0)
        print(f"[session_cleanup] 无需清理，当前最大会话条数: {max_count}")


if __name__ == "__main__":
    main()
