# Cron 多任务数据管道模式

## 适用场景

多个 cron job 串联工作：各自收集数据 → 汇总到共享文件 → 最后一个 job 读取并推送。

## 文件命名规范

```
/tmp/cron_<任务标识>_<日期}.txt          # 单任务报告
/tmp/cron_daily_summary_{日期}.txt       # 汇总累加文件
```

## 流水线路径

```
Job1 (03:00) 收集AI论文  → 写 /tmp/cron_ai_frontier_2026-05-11.txt
                           追加 "AI前沿: 摘要" 到 /tmp/cron_daily_summary_2026-05-11.txt

Job2 (04:00) 收集Skills → 写 /tmp/cron_skill_hunter_2026-05-11.txt
                           追加 "SKILL: 摘要" 到 /tmp/cron_daily_summary_2026-05-11.txt

Job3 (05:00) 摸鱼娱乐   → 写 /tmp/cron_entertainment_2026-05-11.txt
                           追加 "娱乐: 摘要" 到 /tmp/cron_daily_summary_2026-05-11.txt

Job4 (06:00) 汇总推送   → 读取 cron_daily_summary_*
                           生成简报 → send_message 或 feishu 推送
```

## Cron Job 创建命令

```bash
# Job1 - 收集任务（deliver: local，不推送）
hermes cron create "0 3 * * *" \
  --name "AI前沿猎手（03:00）" \
  --skill arxiv,web-browse \
  --deliver local \
  --prompt "你是AI前沿猎手。今天是 {{ date }}。任务：搜索arXiv论文，写入 /tmp/cron_ai_frontier_{{ date }}.txt，然后 echo \"AI前沿: ...\" >> /tmp/cron_daily_summary_{{ date }}.txt"

# Job4 - 汇总任务（deliver: origin，推送给主人）
hermes cron create "0 6 * * *" \
  --name "早间汇总推送（06:00）" \
  --skill feishu-messaging \
  --deliver origin \
  --prompt "你是汇总员。今天是 {{ date }}。读取 /tmp/cron_daily_summary_{{ date }}.txt，生成简报，通过 send_message 发给 origin"
```

## 关键实现细节

### 日期格式处理
```bash
# cron 任务中用 date +%Y-%m-%d 获取当天日期
DATE=$(date +%Y-%m-%d)
echo "AI前沿: 摘要" >> /tmp/cron_daily_summary_${DATE}.txt
```

### 汇总任务读取逻辑
```bash
# 优先读带日期的版本，fallback 到通用版本
if [ -f /tmp/cron_daily_summary_${DATE}.txt ]; then
  cat /tmp/cron_daily_summary_${DATE}.txt
elif [ -f /tmp/cron_daily_summary.txt ]; then
  cat /tmp/cron_daily_summary.txt
else
  echo "NO_DATA"
fi
```

### 飞书推送
使用 `send_message` 工具，`target` 设为 `origin`（推送给主人）或 `feishu:<chat_id>`（推送到特定群）。

## 已知限制

- `deliver: local` 的 job 产出在 `~/.hermes/cron/output/<job_id>/`，不直接推送给用户
- 任务间依赖时间错开（至少间隔 5 分钟），防止写文件冲突
- 共享文件用 `>>` 追加模式，不用 `>` 覆盖
