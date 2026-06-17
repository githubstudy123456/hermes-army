# Hermes Skill 注册机制（2026-06-14 实测）

## 核心结论

**本地 skills 放在 `~/.hermes/skills/<dir>/` 即可自动注册，无需手动添加到 profile config。**

profile config 的 `skills:` 字段只用于外部/hub skills 引用。

## 目录结构规范

```
~/.hermes/skills/
├── financial-analysis-comps/       # → skill name: financial-analysis-comps
│   ├── SKILL.md
│   └── config.yaml
├── financial-equity-research-earnings/  # → skill name: financial-equity-research-earnings
│   ├── SKILL.md
│   └── config.yaml
├── ip-legal/                       # → skill name: ip-renewal-watcher（去掉 ip-legal/ 前缀）
│   ├── ip-renewal-watcher/
│   │   ├── SKILL.md
│   │   └── config.yaml
│   └── trademark-watch/
│       ├── SKILL.md
│       └── config.yaml
```

注册后显示在 `hermes skills list` 的第一列，第二列显示 category（如 ip-legal、litigation-legal）。

## 验证命令

```bash
hermes skills list | grep -E "local.*enabled"   # 看已注册 skills
hermes skills list | grep "financial-"           # 验证金融类 skills
hermes skills list | grep "legal-"              # 验证法律类 skills
```

## config.yaml 格式

```yaml
name: skill-name                    # 必须是目录名（无路径前缀）
description: 一句话描述
toolsets:                           # 该 skill 需要的工具
  - web
  - terminal
category: domain-category           # 显示在 skills list 第二列
```

## 批量创建时的命名约定

金融部领域用 `financial-{domain}-{skill}`：
- `financial-equity-research-earnings`
- `financial-analysis-dcf`
- `financial-investment-banking-cim`

法律部领域用 `legal-{domain}-{skill}` 或 `{domain}-{legal}-{sub}`：
- `legal-commercial-nda-review`
- `ip-renewal-watcher`（ip-legal 子类）
- `litigation-legal-docket-watcher`

## 子目录注册规则

`~/.hermes/skills/some-subdir/skill-name/` 的 skill name 是 `skill-name`，不是 `some-subdir/skill-name`。
