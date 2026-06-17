#!/usr/bin/env python3
"""
每周生活用品优惠精选推送
数据源：什么值得买（smzdm.com）好价排行
品类：日常消耗品 + 零食饮料
推送：直接通过飞书 API 发送，不走文件落地
"""

import re
import json
import sys
import tempfile
import os
import subprocess
from datetime import datetime
from pathlib import Path

# ── 配置 ──────────────────────────────────────────
PLAYWRIGHT_BIN = "/home/ubuntu/.hermes/hermes-agent/venv/bin/python3"
FEISHU_CHAT    = "oc_c6883cd907e4d226736d87ce9c6c6d79"

import urllib.request

# 匹配日常消耗品的关键词（放宽）
DAILY_KEYWORDS = [
    # 纸品
    "抽纸", "卷纸", "纸巾", "卫生纸", "厨房纸", "湿巾", "湿厕纸",
    # 清洁
    "洗衣液", "洗衣粉", "洗衣凝珠", "柔顺剂", "洗洁精", "洗碗液", "洗手液", "洗菜",
    # 粮油调味
    "食用油", "花生油", "调和油", "菜籽油", "橄榄油", "猪油",
    "大米", "稻花香", "五常", "东北大米", "泰国香米", "香米", "粥", "米糊",
    "面粉", "面条", "挂面", "方便面", "粉丝", "酱油", "醋", "盐", "糖",
    "鸡精", "味精", "番茄酱", "沙拉酱", "孜然", "辣椒", "花椒", "八角", "桂皮",
    "火锅底料", "麻辣烫", "蘸料", "番茄酱", "沙拉酱",
    # 口腔护理
    "牙膏", "牙刷", "漱口水", "牙线", "牙贴",
    # 洗护
    "洗发水", "护发素", "发膜", "护发精油",
    "沐浴露", "香皂", "洗手液", "身体乳",
    "洗面奶", "面霜", "护肤", "卸妆", "防晒",
    # 女士/婴儿护理
    "卫生巾", "护垫", "安心裤", "安睡裤", "纸尿裤",
    # 家居
    "垃圾袋", "保鲜袋", "保鲜膜", "铝箔纸", "厨房纸",
    # ===== 食品饮料 全覆盖 =====

    # 饮料类
    "牛奶", "酸奶", "纯牛奶", "鲜奶", "早餐奶", "儿童奶", "高钙奶",
    "饮料", "可乐", "雪碧", "矿泉水", "纯净水", "苏打水", "气泡水",
    "果汁", "橙汁", "苹果汁", "葡萄汁", "柠檬汁", "NFC果汁",
    "奶茶", "柠檬茶", "果茶", "冰红茶", "绿茶", "红茶", "乌龙茶",
    "咖啡", "速溶", "咖啡粉", "拿铁", "摩卡",
    "豆浆", "米糊", "麦片", "藕粉", "芝麻糊", "核桃粉",
    "蜂蜜", "红糖", "冰糖", "柚子茶", "柠檬片",

    # 零食/饼干/糕点
    "饼干", "曲奇", "威化", "苏打饼干", "消化饼干", "夹心饼干",
    "面包", "吐司", "全麦面包", "蛋糕", "蛋黄酥", "凤梨酥", "月饼", "青团",
    "薯片", "薯条", "虾条", "薯片", "锅巴", "爆米花",
    "坚果", "瓜子", "花生", "核桃", "板栗", "腰果", "杏仁", "开心果", "夏威夷果", "碧根果", "松子", "榛子",
    "巧克力", "巧克力棒", "巧克力豆", "麦丽素",
    "糖果", "软糖", "硬糖", "QQ糖", "润喉糖", "薄荷糖", "口香糖", "木糖醇",
    "布丁", "果冻", "龟苓膏", "凉粉", "烧仙草",
    "海苔", "紫菜", "海带", "小鱼仔", "鱿鱼丝",
    "肉干", "牛肉干", "猪肉脯", "肉松", "腊肉", "腊肠", "烤肠",
    "零食", "小吃", "特产", "卤味", "鸭脖", "鸭锁骨", "鸡爪", "鸡腿", "鸡翅", "豆干", "素肉", "魔芋", "海蜇",
    "蛋卷", "沙琪玛", "麻花", "麻糖", "酥糖", "花生糖", "米果", "糙米卷",

    # 方便速食
    "泡面", "方便面", "干脆面", "火鸡面", "拉面", "挂面", "意面",
    "螺蛳粉", "酸辣粉", "桂林米粉", "过桥米线", "土豆粉", "麻辣粉", "朝鲜冷面",
    "自热", "自热饭", "自热火锅", "自热米饭", "煲仔饭",
    "罐头", "午餐肉", "金枪鱼罐头", "豆豉罐头", "水果罐头",
    "八宝粥", "绿豆粥", "红豆粥", "小米粥", "早餐粥",
    "麦片", "即食麦片", "水果麦片", "坚果麦片", "燕麦片",

    # 速冻食品
    "水饺", "饺子", "包子", "蒸饺", "小笼包", "灌汤包",
    "汤圆", "元宵",
    "粽子",
    "馄饨", "云吞",
    "手抓饼", "葱油饼", "馅饼", "烧饼",
    "馒头", "花卷", "发糕",
    "披萨", "蛋挞", "鸡块", "鸡柳", "薯条", "洋葱圈",
    "牛排", "鸡排", "猪排", "肉丸", "鱼丸", "虾滑",

    # 乳制品/冰品
    "酸奶", "牛奶", "奶酪", "芝士", "黄油", "淡奶油",
    "冰淇淋", "冰激凌", "雪糕", "冰棍", "冰棒", "雪泥",
    "冻粽子", "冻汤圆",

    # 粮油/干货/调味
    "食用油", "花生油", "调和油", "菜籽油", "橄榄油", "猪油", "牛油", "椰子油", "稻米油",
    "酱油", "老抽", "生抽", "味极鲜", "蚝油", "蒸鱼豉油",
    "醋", "白醋", "陈醋", "香醋", "米醋",
    "盐", "白糖", "红糖", "冰糖", "木糖醇", "代糖",
    "鸡精", "味精", "鸡粉", "太太乐",
    "豆瓣酱", "辣椒酱", "老干妈", "拌饭酱", "下饭酱",
    "番茄酱", "沙拉酱", "蛋黄酱", "芥末酱",
    "火锅底料", "麻辣烫底料", "串串底料", "关东煮",
    "花椒", "八角", "桂皮", "香叶", "草果", "白芷", "孜然", "辣椒干", "胡椒", "五香粉", "十三香",
    "榨菜", "萝卜干", "酸菜", "泡菜", "梅干菜", "雪菜", "腐乳",
    "木耳", "银耳", "香菇", "榛蘑", "茶树菇", "猴头菇", "虫草花",
    "紫菜", "海带", "海苔", "虾皮", "虾米", "干贝", "海参", "银鱼",
    "红枣", "枸杞", "桂圆", "莲子", "百合", "芡实", "薏米", "黑豆", "红豆", "绿豆", "黄豆",
    "腐竹", "豆皮", "豆棍", "千张", "素鸡", "豆芽",
    "粉丝", "粉条", "宽粉", "细粉", "土豆粉", "红薯粉", "魔芋粉",

    # 日化
    "拖鞋", "收纳", "衣架", "挂钩", "抹布", "刷子",
]

# 排除关键词（明显不是生活品/食品）
EXCLUDE_KEYWORDS = [
    "洗衣机", "冰箱", "空调", "电视", "手机", "电脑", "平板", "耳机", "音箱", "相机",
    "无人机", "平衡车", "滑板车", "电动车", "自行车",
    "沙发", "床", "床垫", "桌椅", "柜子", "家居",
    "行车记录仪", "车衣", "机油", "轮胎",
    "男装", "女装", "童装", "男鞋", "女鞋", "运动鞋", "靴子", "裙子", "裤子", "外套",
    "玩具", "游戏", "手办", "乐高",
    "显卡", "主板", "CPU", "内存", "硬盘", "电源",
    "茅台", "五粮液", "泸州", "洋河",
]


def fetch_smzdm_feed(tab_path="0/3/"):
    """
    抓取 smzdm 好价排行榜内容（Playwright）
    tab: 0=全部 1=时尚运动 2=3C家电 3=食品家居 4=日百母婴 5=白菜 6=一键海淘 7=旅游汽车
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return []

    deals = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-setuid-sandbox"]
            )
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            url = f"https://www.smzdm.com/fanli/haojia/{tab_path}"
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(2000)

            # 滚动触发懒加载（smzdm 是无限滚动）
            for _ in range(6):
                page.evaluate("window.scrollBy(0, 700)")
                page.wait_for_timeout(1200)
            page.wait_for_timeout(3000)

            body_text = page.inner_text("body")
            browser.close()
    except Exception as e:
        print(f"[smzdm] Playwright error: {e}")
        return []

    lines = body_text.split("\n")
    for i, line in enumerate(lines):
        line = line.strip()
        if re.search(r"\d+\.\d+元", line) and i > 0:
            prev = lines[i - 1].strip() if i > 0 else ""
            if (
                prev
                and not re.search(r"^\d+\.?\d*元", prev)
                and len(prev) > 3
                and len(prev) < 80
                and not any(ex in prev for ex in EXCLUDE_KEYWORDS)
            ):
                deals.append({"name": prev, "price": line})
    return deals


def fetch_all_tabs():
    """抓取多个分类标签页"""
    # 并行抓取三个 tab
    all_deals = []
    tabs = [
        ("食品家居", "0/3/"),
        ("日百母婴", "0/4/"),
        ("白菜", "0/5/"),
        ("时尚运动", "0/1/"),   # 新增：运动零食、能量棒等
        ("数码家电", "0/2/"),   # 新增：咖啡机、饮水机等
    ]
    import concurrent.futures
    def fetch_tab(name, path):
        deals = fetch_smzdm_feed(path)
        print(f"  [{name}] 抓取到 {len(deals)} 条")
        return deals
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(fetch_tab, name, path): (name, path) for name, path in tabs}
        for future in concurrent.futures.as_completed(futures):
            all_deals.extend(future.result())
    return all_deals


def filter_deals(deals):
    """过滤出日常消耗品 + 零食饮料"""
    matched = []
    other = []
    for deal in deals:
        name = deal["name"]
        if any(kw in name for kw in DAILY_KEYWORDS):
            matched.append(deal)
        else:
            other.append(deal)
    return matched, other


def categorize(deals):
    """按品类分组"""
    groups = {
        "🥛 牛奶/饮料": [],
        "🍪 零食/饼干": [],
        "🍜 方便速食": [],
        "🫒 粮油/调味": [],
        "🧻 纸品/湿巾": [],
        "🧴 洗衣/清洁": [],
        "🪥 口腔护理": [],
        "🧴 洗护用品": [],
        "💧 女士护理": [],
        "🗑️ 家居日用": [],
        "🥜 其他食品": [],
    }
    keywords_map = {
        "🧻 纸品/湿巾": ["抽纸", "卷纸", "纸巾", "卫生纸", "厨房纸", "湿巾", "湿厕纸"],
        "🧴 洗衣/清洁": ["洗衣液", "洗衣粉", "洗衣凝珠", "柔顺剂", "洗洁精", "洗碗液", "洗手液"],
        "🫒 粮油/调味": ["油", "米", "面", "调料", "酱油", "醋", "糖", "盐", "鸡精", "味精", "芝麻", "孜然"],
        "🥛 牛奶/饮料": ["牛奶", "酸奶", "纯牛奶", "饮料", "可乐", "矿泉水", "果汁", "奶茶", "咖啡", "茶叶", "蜂蜜"],
        "🍪 零食/饼干": ["饼干", "面包", "蛋糕", "蛋黄酥", "薯片", "薯条", "坚果", "瓜子", "花生", "核桃", "巧克力", "糖果", "口香糖", "布丁", "果冻", "海苔", "肉干", "零食", "小吃"],
        "🍜 方便速食": ["方便面", "泡面", "螺蛳粉", "酸辣粉", "自热", "罐头", "八宝粥", "麦片", "藕粉", "芝麻糊"],
        "🪥 口腔护理": ["牙膏", "牙刷", "漱口水", "牙线"],
        "🧴 洗护用品": ["洗发水", "护发素", "沐浴露", "香皂", "身体乳", "洗面奶", "面霜"],
        "💧 女士护理": ["卫生巾", "护垫", "安心裤", "安睡裤", "纸尿裤"],
        "🗑️ 家居日用": ["垃圾袋", "保鲜袋", "保鲜膜", "拖鞋", "收纳", "衣架", "抹布"],
    }
    placed = set()
    for deal in deals:
        name = deal["name"]
        for cat, kws in keywords_map.items():
            if any(kw in name for kw in kws):
                groups[cat].append(deal)
                placed.add(name)
                break
    # 剩下的归入"其他食品"
    for deal in deals:
        if deal["name"] not in placed:
            groups["🥜 其他食品"].append(deal)
    return groups


def format_report(groups, daily_count, total_count):
    """生成报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    lines = []
    lines.append(f"🛒 本周生活用品优惠精选  {today}")
    lines.append(f"📡 来源：什么值得买 smzdm.com")
    lines.append("")

    for cat_name, cat_deals in groups.items():
        if not cat_deals:
            lines.append(f"【{cat_name}】")
            lines.append("  本周暂无")
            lines.append("")
            continue
        # 去重
        seen = set()
        unique = []
        for d in cat_deals:
            if d["name"] not in seen:
                seen.add(d["name"])
                unique.append(d)

        lines.append(f"【{cat_name}】")
        for deal in unique[:8]:
            name = deal["name"]
            price = deal["price"]
            lines.append(f"  {name}  {price}")
        lines.append("")

    lines.append("────────────────────────────────")
    lines.append(f"📊 共收录 {daily_count} 件优惠好物（共抓取 {total_count} 条）")
    lines.append("💡 价格随时变化，购买前请确认")
    lines.append("🔗 https://www.smzdm.com/fanli/haojia/")

    return "\n".join(lines)


def get_feishu_token() -> str:
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({
        "app_id": "cli_a95612fc9ebddbc8",
        "app_secret": "TBNvucvbHCHTeKqYtQ7PGfu1ANe0FSmb"
    }).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            return result.get("tenant_access_token", "")
    except Exception as e:
        print(f"获取token失败: {e}", file=sys.stderr)
        return ""

def feishu_send_text(text: str) -> bool:
    token = get_feishu_token()
    if not token:
        print("飞书token为空，推送失败", file=sys.stderr)
        return False
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    payload = json.dumps({
        "receive_id": FEISHU_CHAT,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            print(f"飞书推送结果: {result}")
            return result.get("code", 0) == 0
    except Exception as e:
        print(f"飞书推送失败: {e}", file=sys.stderr)
        return False


def main():
    print("正在抓取什么值得买好价数据（多标签页）...")

    all_deals = fetch_all_tabs()
    print(f"共抓取 {len(all_deals)} 条优惠信息")

    daily_deals, other = filter_deals(all_deals)
    groups = categorize(daily_deals)
    report = format_report(groups, len(daily_deals), len(all_deals))
    print("\n" + report)

    # 保存到文件（供本地备份）
    output_dir = Path.home() / ".hermes" / "cron" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    today_str = datetime.now().strftime("%Y-%m-%d")
    out_file = output_dir / f"weekly-deals-{today_str}.txt"
    out_file.write_text(report, encoding="utf-8")
    print(f"\n报告已保存：{out_file}")

    # 直接推送飞书（不走 cron 文件检测推送，避免格式被裹metadata）
    print("开始推送飞书...")
    ok = feishu_send_text(report)
    print(f"推送{'成功' if ok else '失败'}")


if __name__ == "__main__":
    main()
