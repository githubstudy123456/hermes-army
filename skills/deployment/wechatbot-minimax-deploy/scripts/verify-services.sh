#!/bin/bash
# 验证 wechatbot + AI 服务存活状态
set -e

echo "=== 微信机器人进程 ==="
pgrep -f "node main.js" && echo "✅ node main.js 运行中" || echo "❌ node main.js 未运行"

echo ""
echo "=== AI 服务健康检查 ==="
curl -s http://localhost:8080/health && echo " ✅ AI 服务 (:8080) 正常" || echo " ❌ AI 服务 (:8080) 异常"

echo ""
echo "=== 最近日志 ==="
tail -5 /tmp/wechatbot.log 2>/dev/null || echo "（无日志）"
tail -5 /tmp/ai_service.log 2>/dev/null || echo "（无日志）"