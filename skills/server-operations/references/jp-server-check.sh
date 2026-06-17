#!/bin/bash
# 日本服务器 (207.56.226.147) 健康检查脚本
# 每两周运行一次（cron job: bcb87d7f3e19）

REPORT="/home/ubuntu/.hermes/cron/output/jp-server-health-$(date +%Y-%m-%d).md"

sshpass -p 'Yfwq3879267' ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 root@207.56.226.147 -p 22 << 'ENDSSH' 2>/dev/null > /tmp/jp-check.tmp
echo "=== SYSTEM ==="
uptime

echo "=== CPU / LOAD ==="
top -bn1 | head -5
cat /proc/loadavg

echo "=== MEMORY ==="
free -h

echo "=== DISK ==="
df -h | grep -E "^/dev"

echo "=== SERVICES ==="
systemctl is-active xray 2>/dev/null && echo "Xray: ACTIVE" || echo "Xray: INACTIVE"
systemctl is-active ssh 2>/dev/null && echo "SSH: ACTIVE" || echo "SSH: INACTIVE"
systemctl is-active docker 2>/dev/null && echo "Docker: ACTIVE" || echo "Docker: INACTIVE"
systemctl list-units --type=service --state=failed --no-pager 2>/dev/null | head -10

echo "=== XRAY STATUS ==="
xray api stats 2>/dev/null | head -10 || echo "xray api not available"
ss -tlnp 2>/dev/null | grep -E "443|22"

echo "=== NETWORK ==="
ss -s 2>/dev/null
netstat -i 2>/dev/null | head -10

echo "=== AUTH LOG (last 20 failed) ==="
grep -i "failed" /var/log/auth.log 2>/dev/null | tail -20 || journalctl -u ssh --since "24 hours ago" 2>/dev/null | grep -i fail | tail -20

echo "=== CRON LOG (recent) ==="
grep -i "cron" /var/log/syslog 2>/dev/null | tail -5 || echo "no cron log"

echo "=== LAST REBOOT ==="
who -b 2>/dev/null
ENDSSH

if [ $? -ne 0 ]; then
  echo "# 日本服务器检查 - $(date '+%Y-%m-%d %H:%M')\n\n❌ 连接失败，服务器可能离线或网络不通" > "$REPORT"
  exit 1
fi

# 生成 Markdown 报告
{
  echo "# 🇯🇵 日本服务器健康报告"
  echo ""
  echo "**检查时间:** $(date '+%Y-%m-%d %H:%M')"
  echo ""
  echo '```'
  cat /tmp/jp-check.tmp
  echo '```'
} > "$REPORT"

rm -f /tmp/jp-check.tmp
echo "报告已生成: $REPORT"
