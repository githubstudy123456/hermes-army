---
name: daily-market-scripts
description: Daily US stock and crypto price fetching scripts for lobster-cfo reports. Crypto via Binance works; Yahoo Finance is rate-limited on this server.
category: devops
---

# Daily Market Data Scripts

Fetch daily US stock and crypto prices for the lobster army CFO reports.

## Background

Deployed on `~/scripts/` — cron-run by lobster-cfo or lobster-ceo each morning.
Crypto via Binance works reliably. Yahoo Finance is permanently rate-limited on this server IP.

## Scripts

### `~/scripts/daily-crypto.sh`
**Status: Working**

```bash
#!/bin/bash
echo "=== 加密货币 ==="
for sym in BTCUSDT ETHUSDT BNBUSDT SOLUSDT ADAUSDT; do
  data=$(curl -s --max-time 10 "https://api.binance.com/api/v3/ticker/24hr?symbol=$sym")
  price=$(echo $data | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['lastPrice'], d['priceChangePercent'])")
  name=$(echo $sym | sed 's/USDT//')
  echo "$name: \$$price"
done
```

### `~/scripts/daily-us-stock.sh`
**Status: BROKEN — Yahoo Finance rate-limits this server IP**

Yahoo blocks after concurrent/multi-symbol testing. All symbols return "获取失败".
Workarounds in order of preference:

1. **Alpha Vantage** (recommended — free tier: 25 req/day):
   ```bash
   curl -s "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey=YOUR_KEY"
   ```
   Get key at: https://www.alphavantage.co/support/#api-key

2. **Twelve Data** (free tier: 800 req/day):
   ```bash
   curl -s "https://api.twelvedata.com/quote?symbol=AAPL&apikey=YOUR_KEY"
   ```

3. **Finnhub** (free tier: 60 req/min):
   ```bash
   curl -s "https://finnhub.io/api/v1/quote?symbol=AAPL&token=YOUR_KEY"
   ```

4. **Wait for Yahoo IP unblock** — could be hours to days. Test with:
   ```bash
   curl -s --max-time 10 -H "User-Agent: Mozilla/5.0" "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?interval=1d&range=5d"
   ```

5. **Use a proxy with different exit IP** — v2ray proxy with different outbound node

### `~/scripts/daily-cn-stock.sh`
**Status: Not yet created**

For Chinese stocks (A-share), use:
```bash
curl -s "http://hq.sinajs.cn/list=sh600519"  # Kweichow Moutai example
```
Or Eastmoney:
```bash
curl -s "https://push2.eastmoney.com/api/qt/stock/get?secid=1.600519&fields=f43,f44,f45,f46,f47,f48,f57,f58"
```

## Trial Log

| Source | Result | Notes |
|--------|--------|-------|
| Yahoo Finance (query1) | ❌ BLOCKED | IP permanently rate-limited after concurrent testing |
| Binance ticker API | ✅ WORKS | Crypto only, no rate limit issues |
| Financial Modeling Prep demo | ❌ FAILS | `Invalid API KEY` even for demo |
| Alpha Vantage demo key | ❌ FAILS | Requires real API key |
| Direct Yahoo through proxy | ❌ STILL BLOCKED | Rate limit follows the request, not just IP |
