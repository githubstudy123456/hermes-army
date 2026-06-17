#!/bin/bash
# 检查今日推送中是否已有某标题关键词
# 用法: bash check_pushed.sh "关键词" [日期默认今天]
KEYWORD="${1?用法: check_pushed.sh \"关键词\" [日期]}"
DATE="${2:-$(date +%Y-%m-%d)}"
REPORTS_DIR="$HOME/.hermes/political-reports"

echo "=== 检查 '$KEYWORD' 是否已在 ${DATE} 推送 ==="
found=0
for f in "$REPORTS_DIR"/*"$DATE"*; do
  if [ -f "$f" ] && grep -l "$KEYWORD" "$f" > /dev/null 2>&1; then
    echo "  ✓ 已推送: $(basename "$f")"
    found=1
  fi
done
if [ $found -eq 0 ]; then
  echo "  ✗ 未推送，可继续"
fi