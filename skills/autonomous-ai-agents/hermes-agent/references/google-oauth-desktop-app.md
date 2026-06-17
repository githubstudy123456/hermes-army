# Google OAuth Desktop App — 避坑指南

## 核心问题

`@cocal/google-calendar-mcp` 只接受 `installed` 类型的 OAuth JSON，但 Google Cloud Console 默认创建的是 `web` 类型客户端。

**症状：** 打开授权 URL 报错「禁止访问：此应用的请求无效」

## 解决方案：创建桌面应用类型

1. Google Cloud Console → **凭据** → **创建凭据** → **OAuth 客户端 ID**
2. **应用类型选「桌面应用」**（不是 Web 应用）
3. 创建后直接显示 Client ID + Client Secret，重定向 URI 已预填 `http://localhost`
4. 下载 JSON 文件，直接可用（格式已是 `installed`）

**不要选「Web 应用」**，除非你想手动改 JSON 把 `web` 改成 `installed`。

## 关键字段（installed 格式）

```json
{
  "installed": {
    "client_id": "...",
    "client_secret": "...",
    "redirect_uris": ["http://localhost"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token"
  }
}
```

## 授权流程

1. 用 `google-auth-library` 的 `OAuth2Client.generateAuthUrl()` 生成授权 URL
2. 用户在浏览器打开，登录 Google 账号点允许
3. 授权后跳转到 `http://localhost?code=XXXXX`
4. 地址栏完整 URL 复制给程序，换取 token

## 凭据存放路径

```
~/.hermes/secrets/gcp-oauth.keys.json          # 主文件
~/.npm-global/lib/node_modules/@cocal/google-calendar-mcp/gcp-oauth.keys.json   # MCP 包内副本
/home/ubuntu/.config/google-calendar-mcp/tokens.json   # 授权后 token 存放位置
```

## Node.js ESM 模块踩坑

`@cocal/google-calendar-mcp` 是 ESM 包（`"type": "module"`），在其目录内运行脚本：
- 用 `.mjs` 扩展名，或
- 用 `import` 而非 `require`
- `google-auth-library` 是 CJS 模块，用默认导入：`import pkg from 'google-auth-library'; const {OAuth2Client} = pkg;`

## MCP 包导出

该包的导出是 `runAuthServer` 和 `main`，不是类直接导出。如果想手动触发 auth，用 `npx @cocal/google-calendar-mcp auth`（需手动复制 keys 文件到包根目录）。
