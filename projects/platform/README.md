# 平台配置记录

记录主人配置的第三方平台 API Key 和接入配置。

---

## 平台清单

| 平台 | 用途 | Key 环境变量 | 状态 | 配置日期 |
|------|------|------------|------|---------|
| MiniMax-CN | 大模型（主力） | `MINIMAX_CN_API_KEY` | ✅ 已配置 | — |
| 飞书 | 消息推送 | `FEISHU_APP_SECRET` | ✅ 已配置 | — |
| 微信 | 消息推送 | `WEIXIN_TOKEN` | ✅ 已配置 | — |
| Google Calendar | 日历管理 | `GOOGLE_OAUTH_CREDENTIALS` | ✅ 已配置 | — |
| 天眼查 | 企业查询 | `TYC_API_KEY` | ✅ 已配置 | — |
| 高德地图 | 地图/POI | `AMAP_KEY` | ✅ 已配置 | — |
| GitHub | 代码/skill 安装 | `GITHUB_TOKEN` | 🔍 待配置 | — |
| OpenRouter | 备援模型 | `OPENROUTER_API_KEY` | 🔍 待配置 | — |

---

## 待接入

### 1. GitHub Token
- 用途：解除 skill 安装的 rate limit（60次/小时 → 5000次/小时）
- 地址：https://github.com/settings/tokens
- 权限：`repo` + `read:user`
- 状态：🔍 待配置

### 2. OpenRouter 备援模型
- 用途：MiniMax 限额时自动切换备援模型
- 地址：https://openrouter.ai/keys
- 额度：注册送 $5 免费 credits
- 备援模型：`deepseek-ai/DeepSeek-V3-0324`
- 状态：🔍 待配置

---

## MCP 服务器（见 `../mcp/`）

---

*最后更新：2026-06-23*
