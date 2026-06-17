# Chrome/bb-browser 资源泄漏分析（2026-06-15）

## 问题现象

- 服务器 Load Avg 飙到 83（4核系统，正常应 < 4）
- 内存使用率 80%，可用仅 152MB
- kswapd 运行 17 天 6 小时，连续高 CPU 占用
- Chrome 52 个进程占用 ~1.8GB RSS

## 根因

**只装了一个 Chrome 实例，但渲染器进程从未回收。**

```
Chrome 主进程 (PID 1682975)  ← bb-browser daemon (PID 1780296) 通过 CDP 启动
├── Crashpad Handler × 2
├── Zygote 进程 (PID 1682990)  ← 渲染器孵化器（fork 后等待）
│   ├── Renderer × 33  ← 每个 browser 操作开一个 tab，关闭后进程不回收
│   ├── Utility (PID 1683014)
│   ├── GPU (PID 1683011)
│   └── Network (PID 1683013)
└── Bash 启动器 (PID 1682964)
```

**关键发现：**
- 所有 Hermès profile（共 26 个）的 browser tool 共享同一个 Chrome 实例
- 每个 profile 调用 browser 时在 Chrome 里开 tab
- Tab 关闭后渲染器进程成为僵尸（RSS 不释放）
- 从 04:03 持续到 15:20，越积越多

## 另一层根因：无 Swap

```bash
# 当前 Swap 状态
$ cat /proc/swaps
Filename    Type    Size    Used    Priority
（空）      无Swap分区
```

无 Swap + 80% 内存占用 = 内存压力直接传导给 kswapd，kswapd 没有可换出的页面，只能反复扫描 Page Cache 产生 I/O wait，Load 被拉高。

## 诊断命令

```bash
# 1. 确认 Chrome 渲染器数量（正常值: < 10，泄漏时: 30+）
ps aux | grep 'type=renderer' | grep -v grep | wc -l

# 2. 确认 Chrome 实例数（正常值: 1，泄漏时: 多个独立进程）
ps aux | grep chrome | grep -v grep | awk '{print $2, $11}' | sort -k2

# 3. 确认 Swap 状态
swapon --show
cat /proc/swaps

# 4. 确认 kswapd CPU 占用（持续 > 1% = 异常）
ps -p 105 -o %cpu,etime=

# 5. Chrome 进程树（确认是否同实例）
pstree -p 1682975 | head -60

# 6. 渲染器 RSS 汇总
ps aux | grep chrome | grep -v grep | awk '{rss+=$6} END {print "Chrome 总 RSS:", rss/1024, "MB"}'
```

## 解决方案

### 方案 A：加 Swap（治本）
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
# 永久化
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 方案 B：重启 Chrome 实例（治标）
```bash
# 杀掉所有 Chrome 进程（bb-browser daemon 会自动重建）
killall chrome chrome_crashpad_handler
pkill -f "bb-browser"

# 验证
ps aux | grep chrome | grep -v grep | wc -l  # 应返回 0
sleep 2
ps aux | grep bb-browser | grep -v grep      # daemon 应自动重启
```

### 方案 C：限制 Chrome 子进程数（防复发）
给 bb-browser 加 `--disable-features=ProcessPerSite` 或限制 max renderer count。

## 经验阈值

| 指标 | 正常值 | 危险值 | 说明 |
|------|--------|--------|------|
| Chrome 渲染器数 | < 5 | > 15 | 泄漏信号 |
| kswapd CPU | < 0.5% | > 1% | 无 Swap + 内存压力 |
| Load Avg | < 4 | > 10 | 受 kswapd 影响 |
| 可用内存 | > 500MB | < 200MB | 告警阈值 |
| Swap | 存在 | 无 | 内存压力缓冲 |

## 当前状态（2026-06-15 22:37）

Load 已回落到 0.07，内存仍紧张（111MB free / 301MB available）。主人决定先观察，暂不执行清理。