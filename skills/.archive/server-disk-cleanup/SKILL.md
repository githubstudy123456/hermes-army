---
name: server-disk-cleanup
description: Server disk space analysis and cleanup on Linux — find large files, identify junk, clean caches/temp/old backups.
triggers:
  - "check server space"
  - "服务器空间"
  - "磁盘满了"
  - "clean up server"
  - "清理服务器"
  - "清理磁盘"
  - "find large files on server"
  - "找大文件"
  - "clean cache"
  - "清理缓存"
  - "清理临时文件"
when: When the user asks to check or free disk space on the cloud server.
---

# Server Disk Cleanup

## Step 1: Check Disk Usage

```bash
df -h /
du -sh /* 2>/dev/null | sort -hr | head -20
```

## Step 2: Find Large Directories

```bash
du -sh /home/* ~/.cache ~/.tmp 2>/dev/null | sort -hr
du -sh ~/.openclaw/* ~/.hermes/* 2>/dev/null | sort -hr | head -20
du -sh ~/.openclaw/workspace* 2>/dev/null | sort -hr
```

## Step 3: Find Large Files

```bash
# Files > 100MB
find ~ -type f -size +100M 2>/dev/null | head -20

# Old files (>90 days not accessed), skip logs
find ~ -type f -atime +90 2>/dev/null | grep -v -E '\.(log|jsonl)$' | head -30
```

## Step 4: Common Junk Targets

| Path | Size | What | Cleanup |
|------|------|------|---------|
| `/var/log/journal/` | 1G+ | systemd logs | `sudo journalctl --vacuum-size=100M` |
| `~/.cache/go-build/` | 300M+ | Go build cache | `go clean -cache` |
| `~/.cache/pip/` | 200M+ | pip cache | `pip cache purge` |
| `/tmp/` | varies | temp files | `rm -rf /tmp/pw-browsers /tmp/yf /tmp/ffmpeg* /tmp/chrome.deb /tmp/node-compile-cache /tmp/skills-* /tmp/hermes.tar.gz` |
| `~/.cache/ms-playwright/` | 500M+ | Playwright browsers | `rm -rf ~/.cache/ms-playwright/` |
| `~/.openclaw/agents/*/sessions/` | varies | session JSONL | Check before deleting |
| `~/.openclaw/workspace-lobster-dev/` | 750M | old project | Delete if unused |
| `~/.openclaw/workspace/` | varies | old HTML/demos | Delete old demos |
| `~/.openclaw/media/inbound/` | varies | received files | Check for junk |
| `~/.openclaw/*.clobbered*` | 500K+ | old backups | `find ~/.openclaw -name "*.clobbered*" -delete` |
| `~/.openclaw/openclaw.json.bak*` | ~200K | old backups | Keep only latest |

## Step 5: OpenClaw Specific

```bash
# OpenClaw workspace sizes
du -sh ~/.openclaw/workspace* ~/.openclaw/agents/*/sessions 2>/dev/null | sort -hr

# Check for junk media files
ls ~/.openclaw/media/inbound/ | head -20
du -sh ~/.openclaw/media/inbound/* | sort -hr

# Check for unknown skills (empty dirs)
du -sh ~/.openclaw/skills/skills/* 2>/dev/null

# Clean old session files (>30 days)
find ~/.openclaw/agents -name "*.jsonl" -mtime +30 -ls 2>/dev/null
```

## Important Notes

- **Never `rm -rf /tmp/*`** — some processes rely on their own subdirs in /tmp
- **`node-compile-cache`** may need `sudo rm -rf /tmp/node-compile-cache`
- Check `/snap/` sizes — `lxd` snap can be 600M+
- After cleanup: run `df -h /` to verify space recovered
