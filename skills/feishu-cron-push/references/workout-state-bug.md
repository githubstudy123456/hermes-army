# 运动计划 Cron Bug 记录（2026-05-16）

## 问题现象

晚间气质体态运动计划 cron（job_id: 3623acc6233c）每次推送内容都是"第1周"，无论实际过了多少天。

## 根因

`evening-workout.py` 的状态持久化有两处串联 bug：

### Bug 1: save_state() 从未被调用

```python
# 错误的逻辑
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"start_date": str(date.today()), "week": 1, "phase": 1}
    # ← 默认值直接 return，文件从未创建
    # ← save_state() 从未被调用
```

`build_plan()` 计算了 `total_week` 但从未写回文件，每次重启后从第1周开始。

### Bug 2: 首次运行没有初始化文件

`load_state()` 返回默认值后直接丢弃，状态文件从未被创建。

## 正确写法

```python
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    # 首次运行，初始化并持久化
    s = {"start_date": str(date.today()), "week": 1, "phase": 1}
    save_state(s)          # ← 必须调用 save_state
    return s

def save_state(s):
    with open(STATE_FILE, 'w') as f:
        json.dump(s, f)
```

### 在 build_plan() 中推进状态

```python
def build_plan():
    s = load_state()
    phase_num, week_num, total_week = get_phase_and_week()
    new_week = total_week
    prev_phase = s.get("phase", 1)
    phase_changed = (prev_phase != phase_num)
    if s.get("week") != new_week:
        s["week"] = new_week
        s["phase"] = phase_num
        save_state(s)
    # ...
```

## 关键原则

Python 脚本的状态持久化：
1. **默认值必须立即持久化** — 不能只 return 不 save
2. **每次推进状态后必须 save_state()** — 计算了不等于写入了
3. **首次运行必须初始化文件** — 避免重启后从零开始

## 相关文件

- 脚本：`/home/ubuntu/.hermes/scripts/evening-workout.py`
- 状态文件：`~/.hermes/scripts/workout-state.json`