# MCP 服务器配置

## 已接入 MCP

| MCP | 用途 | 配置位置 | 状态 |
|-----|------|---------|------|
| Google Calendar | 日历管理 | config.yaml → `gcalendar` | ✅ 运行中 |
| 天眼查 | 企业工商查询 | config.yaml → `tyc-mcp` | ✅ 运行中 |
| 魔搭（ModelScope） | 酒店搜索 | config.yaml → `rollinggo-mcp` | ⚠️ 仅酒店查询 |
| 高德地图 | 地图/POI/导航 | config.yaml → `amap-mcp` | ✅ 运行中 |
| fetch-mcp | 网页抓取 | config.yaml → `fetch-mcp` | ✅ 运行中 |

---

## 详细配置

### gcalendar
```yaml
mcp_servers:
  gcalendar:
    command: npx
    args: ['-y', '@cocal/google-calendar-mcp']
    env:
      GOOGLE_OAUTH_CREDENTIALS: /home/ubuntu/.hermes/secrets/gcp-oauth.keys.json
    timeout: 120
```

### 天眼查
```yaml
mcp_servers:
  tyc-mcp:
    url: https://mcp.tianyancha.com/v1
    headers:
      Authorization: Bearer <TYC_API_KEY>
    timeout: 120
```
Key 存储于：`~/.hermes/secrets/tyc-api-key.txt`

### 高德地图
```yaml
mcp_servers:
  amap-mcp:
    url: https://mcp.amap.com/mcp?key=<AMAP_KEY>
    timeout: 120
```

### fetch-mcp
```yaml
mcp_servers:
  fetch-mcp:
    command: uvx
    args: ['mcp-server-fetch']
    timeout: 120
```

---

## 待接入

暂无

---

*最后更新：2026-06-23*
