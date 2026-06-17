# 行业板块资金流向 — Sina newFLJK.php（2026-06-14 验证）

## API 端点

```
https://vip.stock.finance.sina.com.cn/q/view/newFLJK.php?page=1&num=50&sort=changepercent&asc=0&node=bk_hy&symbol=&_s_r_a=page
```

- 返回 84 个行业板块的涨跌幅数据
- `sort=changepercent&asc=0` → 按涨幅降序排列
- `num=50` → 返回前 50 条（可调大到 84 覆盖全量）
- 编码：GBK（`decode('gbk', errors='ignore')`）

## 响应格式

```javascript
var S_Finance_bankuai_ = {
  "hangye_ZA01": "hangye_ZA01,农业,15,7.9,0.14866666666667,1.9179496000688,622070107,3245174517,sz002041,6.357,8.700,0.520,登海种业",
  ...
};
```

每条字段（逗号分隔）：
```
0: hangye_XXX  (内部ID)
1: 板块名称
2: 成分股数量
3: 均价
4: 涨跌额
5: 涨跌幅(%)     ← 关键字段，第5个索引
6: 成交量(股)
7: 成交额(元)
8: 领涨股代码
9: 领涨股价格
10: 领涨股昨收
11: 领涨股涨跌幅
12: 领涨股名称
```

## 解析脚本

```python
import urllib.request, re, ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = 'https://vip.stock.finance.sina.com.cn/q/view/newFLJK.php?page=1&num=50&sort=changepercent&asc=0&node=bk_hy&symbol=&_s_r_a=page'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://finance.sina.com.cn'
})
with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
    content = r.read().decode('gbk', errors='ignore')

# 提取所有板块数据
matches = re.findall(r'"hangye_\w+":"([^"]+)"', content)
sectors = []
for match in matches:
    parts = match.split(',')
    if len(parts) >= 6:
        name = parts[1]
        try:
            change_pct = float(parts[5])
            sectors.append((name, change_pct))
        except:
            pass

sectors.sort(key=lambda x: x[1], reverse=True)
print("Top 10 gainers:")
for name, pct in sectors[:10]:
    print(f"  {name}: {pct:.2f}%")
print("\nTop 10 losers:")
for name, pct in sectors[-10:]:
    print(f"  {name}: {pct:.2f}%")
```

## 触发阈值应用

板块涨跌触发阈值：**±3%**

当日（2026-06-14 13:05）发现：
- 涨幅超3%：其他金融业 +6.88%、有色金属矿采选业 +5.26%、石油和天然气开采业 +4.97%、卫生 +4.43%、航空运输业 +4.20%
- 跌幅超3%：建筑安装业 -4.08%、综合 -3.46%、房屋建筑业 -3.08%

→ 触发条件4满足（单一板块涨跌超3%），推送板块资金集中简报

## 已知限制

- 该 API 仅返回涨跌幅和成交额，**不含净流入数据**（净流入需另查 East Money）
- 若需净流入/净占比数据，需用 East Money 板块资金流 API（`push2.eastmoney.com/api/qt/clist/get`），但该 API 在 execute_code 沙箱中 SSL 连接被 server 重置，改用 Playwright CDP 方案
- 领涨股字段（索引 8-12）可作为"板块内龙头股"参考

## 替代数据源

East Money 板块资金流 API（需 Playwright CDP）：
```
https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=20&po=1&np=1&fltt=2&invt=2&fid=f3&fs=m:90+t:2+f:!50&fields=f2,f3,f4,f5,f6,f7,f8,f10,f12,f14,f62
```
其中 `f62` = 主力净流入（元），`f3` = 涨跌幅，`f14` = 板块名称