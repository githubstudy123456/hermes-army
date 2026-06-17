# Web 爬虫工具验证记录（2026-06-04）

## agent-reach
- **结论**：不存在，PyPI 搜不到
- 原因：帖子可能引用的是 GitHub 项目名但未发布到 PyPI，或名称不同
- 建议：直接去 GitHub 搜索 `agent-reach` 或 `browser-use` 等关键字

## scrapling
- **状态**：✅ 可用，CLI 模式正常
- **安装**：`pip install scrapling browserforge`（browserforge 需单独装）
- **正确用法**：
  ```bash
  # 基础 GET 请求
  scrapling extract get https://httpbin.org/html /tmp/out.html

  # CSS 选择器提取（参数是 --css-selector，不是 --match）
  scrapling extract get https://example.com /tmp/out.html --css-selector 'h1, a.title'

  # 伪装浏览器
  scrapling extract get https://example.com /tmp/out.html --impersonate chrome

  # 加超时
  scrapling extract get https://example.com /tmp/out.html --timeout 60
  ```
- **已知限制**：
  - HackerNews 等强反爬站点会超时（默认30s）
  - 简单页面（httpbin.org）正常
  - 需要 browserforge 依赖（不装会报 `ModuleNotFoundError: No module named 'browserforge'`）

## browser-use
- **状态**：未测（需要 Node.js + Playwright，重量级）
- 适用场景：需要 AI 像人一样操作网页、填表、点击、多步任务
- GitHub：github.com/browser-use/browser-use

## web-access
- **状态**：未测
- 适用场景：全自动联网、接管日常 Chrome（天然带登录态）
- GitHub：github.com/eze-is/web-access

## Claude in Chrome
- **状态**：官方浏览器扩展，需在用户真实 Chrome 中运行
- 适用场景：复杂认证、需要盯着看操作
- 官网：claude.ai/chrome

## 测试优先级建议
1. 先用 scrapling（轻量，pip 装完即用）
2. 需要登录态 → browser-use 或 Playwright CDP
3. 复杂多步操作 → Claude in Chrome
4.全自动后台跑 → web-access