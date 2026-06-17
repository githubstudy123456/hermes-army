# 中国教材电子课本资源导航

## 核心网站：电子课本网 (dzkbw.com)

### 网站结构
```
http://www.dzkbw.com/
├── /city/                    # 按城市查找教材版本
│   └── /guangdong_guangzhoushi/chuzhong.htm   # 广州初中教材版本
│   └── /jiangsu_nanjingshi/chuzhong.htm        # 南京初中教材版本
│   └── /shanghai_shanghaishi/chuzhong.htm     # 上海初中教材版本
├── /books/<version>/         # 按版本找课本
│   ├── /rjb/     # 人教版
│   ├── /sjb/     # 苏教版
│   ├── /yilin/   # 译林版（牛津版）
│   ├── /hjb/     # 沪教版
│   └── /waiyan/  # 外研版
└── /books/<version>/yingyu/<grade>/   # 具体科目年级
```

### 版本速查
| 版本 | 出版社 | 适用城市/地区 |
|------|--------|--------------|
| 译林版 (yilin) | 译林出版社（牛津大学出版社授权） | 南京等江苏城市 |
| 沪教版 (hjb) | 上海教育出版社 | 上海、广州、深圳 |
| 人教版 (rjb) | 人民教育出版社 | 全国通用 |
| 外研版 (waiyan) | 外语教学与研究出版社 | 全国 |
| 北师大版 (bsd) | 北京师范大学出版社 | 全国 |

**关键发现：用户说"牛津版"教材 → 实际对应的是"译林版"（译林出版社 = Oxford University Press 中国授权）**

### 译林版英语七年级上册（2024秋版）路径
```
URL: http://www.dzkbw.com/books/yilin/yingyu/7s_2024/
Unit列表:
  001.htm → Unit 1 This is me!
  002.htm → Unit 2 Hobbies
  003.htm → Unit 3 Welcome to our school
  004.htm → Unit 4 School day
  005.htm → Unit 5 A healthy lifestyle
  006.htm → Unit 6 My clothes, my style
  007.htm → Unit 7 Be wise with money
  008.htm → Unit 8 Let's celebrate!
```

### 踩坑记录
- dzkbw.com/books/ 目录页返回 403 → 只能通过具体城市或版本路径访问
- 点击 Unit 页面会跳转到第三方（加密混淆跳转），无法直接抓取内容
- 该站**只有导航，没有实际 PDF 文件**，内容在第三方平台（国家智慧教育平台）
- dzkbw.com/books/yilin/yingyu/7s_2024/00N.htm 直接访问返回 404

### 备选：国家中小学智慧教育平台
- 主站：https://www.smartedu.cn
- 教材频道：https://v3.bsszjc.com/#/szjcView （需登录）
- 基础教育教材网：https://www.100875.com.cn （北京师范大学出版集团）

## 其他教材资源站

| 网站 | 特点 | 限制 |
|------|------|------|
| dzkbw.com | 版本最全，导航索引完整 | 无 PDF，只有跳转链接 |
| 123pan.com | 常有用户分享 PDF | 链接易失效 |
| 各省教育考试院 | 权威信息 | 非电子教材 |
| 各出版社官网 | 原版内容 | 多需登录或付费 |

## 搜索关键词技巧

- "牛津版七年级上册英语" → 应搜 "译林版七年级上册英语" 或 "译林版 7A"
- "电子课本 pdf 下载" → 常搭配 "pan.baidu" "阿里云盘" "123云盘"
- 避免用 "Oxford 7年级" （搜索引擎会匹配成牛津大学相关内容）
- 百度搜索会被验证码拦截，用 Bing 或直接 URL 导航更可靠
