# 大表格数据提取（替代 browser_snapshot 截断）

## 适用场景

-页面含大量行（如排行榜、资产列表），`browser_snapshot` 返回结果被截断（`... 2096 more lines truncated`）
- 需要获取完整表结构数据
- 页面是 JS 动态渲染，`urllib`拿不到数据

## 核心方法：browser_console + document.querySelectorAll

```javascript
// 提取表格所有行数据
const rows = document.querySelectorAll('table tbody tr');
const data = [];
rows.forEach(row => {
  const cells = row.querySelectorAll('td');
  if (cells.length >= 7) {
    data.push({
      rank: cells[1]?.textContent?.trim(),
      name: cells[2]?.querySelector('a')?.innerText?.trim() || cells[2]?.textContent?.trim(),
      marketCap: cells[4]?.textContent?.trim(),
      price: cells[5]?.textContent?.trim(),
      change24h: cells[6]?.textContent?.trim()
    });
  }
});
JSON.stringify(data);
```

`browser_console` 返回完整 JSON，不受截断限制。

## 实际操作流程（assetmarketcap.com 法币/公司列表）

1. `browser_navigate` 到目标分类页
2. 点击 Filters → 选择 Category → Apply（或用 URL 参数 `?category=Currency`）
3. `browser_console` 执行上面 JS，提取完整数据
4. 在 JSON 返回结果中解析（注意 cells 索引因页面结构可能略有偏差）

## 注意事项

- `cells[n]` 索引从0 开始，第 0 个通常是☆☆收藏按钮，实际数据从第 1 个开始
- 资产名可能在 `cells[x].querySelector('a')` 里（点击链接），也可能在 `cells[x].textContent` 里
- 如果表格有合并单元格（rowspan），某些行的 cell 数量会比其他行少，需要做 `cells.length >= N` 的防御检查
- 返回的 JSON 里 `\\n` 换行符需 `.replace(/\\s+/g, ' ')` 清理
- 如果表格用了自定义列排序，某些行的字段顺序可能不一致

## 替代方案：bb-browser eval

```bash
bb-browser eval "document.querySelectorAll('table tbody tr').length"
```

适合快速检查行数，但取完整数据还是用 `browser_console`。

## 已知成功案例

| 场景 | 站点 | 提取内容 |
|------|------|---------|
| 法币排行榜（112种货币） | assetmarketcap.com | 货币名称、市值、汇率、24h变化 |
| 上市公司排行榜 | assetmarketcap.com | 公司名、市值、股价、24h市值变化 |
| 加密货币排行榜 | assetmarketcap.com | 币种名、市值、价格、24h变化 |