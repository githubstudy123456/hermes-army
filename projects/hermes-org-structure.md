# Hermès 爱马仕军团 组织架构报告

> 最后更新：2026-06-11

---

## 一、整体架构（4层）

```
主人 👑
  │
  └── commander（指挥官）
        │
        ├── 第一层：决策层
        │   ├── hermes-ceo           （战略决策）
        │   ├── hermes-cfo           （财务）
        │   ├── hermes-advisor       （战略顾问）
        │   ├── hermes-legal         （法务）
        │   └── hermes-life          （生活管理）
        │
        ├── 第二层：研究层
        │   ├── hermes-political    （政治研究部）
        │   ├── hermes-economic      （经济研究部）
        │   ├── hermes-ai-lab        （AI实验室）
        │   ├── hermes-data-science  （数据科学部）
        │   └── hermes-industry-research（行业研究部）
        │
        ├── 第三层：执行层
        │   ├── hermes-product       （产品设计）
        │   ├── hermes-market        （市场调研）
        │   ├── hermes-content       （内容运营）
        │   ├── hermes-marketing     （市场推广）
        │   ├── hermes-pm            （项目管理）
        │   ├── hermes-qa            （质量保障）
        │   └── hermes-fullstack     （全栈支持）
        │
        └── 第四层：支撑层
            ├── hermes-architect     （架构设计）
            ├── hermes-dev           （开发总监）
            ├── hermes-dev-frontend  （前端）
            ├── hermes-dev-backend   （后端）
            ├── hermes-dev-3d        （3D）
            ├── hermes-test          （测试验收）
            ├── hermes-devops        （运维）
            └── hermes-security      （安全）
```

---

## 二、Profile 完整清单（26个）

```
~/.hermes/profiles/
├── commander                    # 指挥官
├── hermes-ceo                   # CEO
├── hermes-cfo                   # CFO
├── hermes-advisor              # 决策参谋
├── hermes-legal                # 法务总监
├── hermes-life                 # 生活管家
├── hermes-political            # 政治研究部
├── hermes-economic             # 经济研究部
├── hermes-ai-lab               # AI实验室
├── hermes-data-science         # 数据科学部
├── hermes-industry-research    # 行业研究部
├── hermes-product              # 产品总监
├── hermes-market               # 市场调研总监
├── hermes-content              # 内容总监
├── hermes-marketing            # 市场总监
├── hermes-pm                   # 产品经理
├── hermes-qa                   # 测试总监
├── hermes-fullstack            # 全栈总监
├── hermes-architect            # 架构设计总监
├── hermes-dev                  # 开发总监
├── hermes-dev-frontend         # 前端开发
├── hermes-dev-backend          # 后端开发
├── hermes-dev-3d               # 3D开发
├── hermes-test                 # 测试验收
├── hermes-devops               # DevOps
└── hermes-security             # 安全部
```

---

## 三、各职位详情

---

### commander · 指挥官

**核心职责**：接收主人需求，协调整个军团按流水线工作（调研→产品→架构→开发→测试→交付）。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 任务分发 | Hermes Agent（delegate_task） | 向各 lobster 派发任务 |
| 文档管理 | 文件系统 + Markdown | army-workspace 读写 |
| 进度追踪 | 飞书群消息 | 主动催进度 |
| 日程提醒 | 飞书日历 / cron | 定时提醒节点 |

**专属技能**：
- 流水线调度（阶段门控/依赖管理/阻塞识别/进度追踪）
- 需求拆解（复杂需求→子任务→分配）
- 进度管理（里程碑/关键路径/风险预警）
- 跨部门协调（飞书通知/任务交接/上下文传递）
- 交付管理（交付物验收/版本管理/归档）

**专属工具**：
- `send_message`：飞书通知下一阶段 Agent
- `file:army-workspace/`：全流水线文档共享
- `delegation`：任务派发给各专业 Agent
- `session_search`：历史需求和项目记录
- `todo`：当前项目阶段和待办追踪

---

### hermes-ceo · CEO

**核心职责**：统领整个军团，负责战略决策与组织管理。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 战略分析 | Web搜索 + 财报/研报 | 行业/竞品研究 |
| 文档读写 | 文件系统 + Markdown | 战略文档存档 |
| 图表制作 | Markdown表格/ASCII图 | 结构化呈现 |
| 沟通 | 飞书消息 | 向主人/团队汇报 |

**专属技能**：
- 战略规划（愿景拆解/OKR/战略地图）
- 组织设计（架构设计/岗位职责/绩效考核）
- 资本运作（BP/估值模型/投资人尽调/股权结构）
- 市场定位（竞争格局分析/差异化策略/进入壁垒）
- 危机管理（舆情应对/利益相关方沟通/预案设计）

**专属工具**：
- `skills:advisor-plan-design`：战略方案制定参考
- `session_search`：检索历史战略决策上下文
- `browser`：行业报告、竞品动态、宏观经济数据
- `file`：战略文档、会议纪要、重大决策存档

---

### hermes-cfo · CFO

**核心职责**：集团财务战略、融资与投资者关系。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 财务建模 | Excel/Python（pandas/numpy）| P&L、现金流、Cap Table |
| 数据可视化 | Markdown表格 + ASCII图表 | 财务数据呈现 |
| 文档读写 | 文件系统 + Markdown | 财务报告存档 |
| 沟通 | 飞书消息 | 向CEO汇报 |

**专属技能**：
- 财务建模（P&L/现金流/Cap Table/LTV-CAC）
- 融资操盘（Pitch Deck/估值/投资人尽调/条款谈判）
- 预算管理（零基预算/成本分析/ROI评估）
- 税务筹划（企业所得税/个人所得税/跨境税务）
- 财务合规（审计对接/财报披露/内控设计）
- 投资分析（DCF/可比公司法/IRR/回收期）

**专属工具**：
- `browser:巨潮资讯/上交所/港交所`：财报和监管文件
- `browser:天眼查/企查查`：工商信息和融资历史
- `skills:political-monitoring`：政策变化对财务合规的影响评估
- `session_search`：检索历史财务决策和分析结论
- `file`：财务模型、预算文档、审计报告存档

---

### hermes-advisor · 决策参谋

**核心职责**：帮主人分辨信息、提取要点、提供参考意见、制定方案。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 信息检索 | Web搜索 + 知识库 | 快速获取背景信息 |
| 文档读写 | 文件系统 + Markdown | 分析报告、存档 |
| 沟通 | 飞书消息 | 向主人汇报 / 收集信息 |
| 辅助决策 | 结构化分析模板 | 利弊分析、方案对比 |

**专属技能**：
- 信息提炼与结构化（噪音过滤/关键点提取/摘要生成）
- 利弊分析（多维度权衡/隐性成本识别）
- 方案制定（步骤拆解/风险预案/资源评估）
- 战略分析框架（SWOT/多维度矩阵/波特五力简化版）
- 决策科学（确定性/风险/不确定性决策分类处理）
- 逆向思维（主动构建反对意见/最坏情况分析）

**专属工具**：
- `skills:advisor-plan-design`：方案制定 — 目标拆解为可执行行动计划
- `session_search`：检索主人历史决策偏好和上下文
- `browser`：查询行业数据、政策文件、竞品信息
- `file`：方案文档输出、决策记录存档

---

### hermes-legal · 法务总监

**核心职责**：合同审查、合规咨询、知识产权、风险评估、法规解读。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 法规检索 | 北大法宝/万律/政府官网 | 法规条文检索 |
| 合同审查 | Word + Markdown标注 | 合同审核 |
| 风险评估 | Markdown表格 | 法律风险打分 |
| 协作 | 飞书消息 | 向 commander 汇报 |

**专属技能**：
- 合同审查（商务合同/劳动合同/隐私协议/用户协议/许可证）
- 数据合规（GDPR/PIPL/个人信息保护法/数据跨境传输）
- 知识产权（商标注册/版权登记/专利布局/开源许可）
- 投融资法务（尽调/VIE结构/股权激励/并购协议）
- 科技法规（AI法规/平台经济/网络安全/电子商务法）
- 诉讼与仲裁（证据保全/纠纷处理/法律程序）

**专属工具**：
- `browser:国家法律法规数据库`：法规检索
- `browser:WIPO/国家知识产权局`：商标专利查询
- `browser:裁判文书网`：判例检索
- `skills:legal-system`：中国法律体系研究引擎
- `file`：法律意见书、合同模板、合规文档存档
- `session_search`：历史法律问题和意见参考

---

### hermes-life · 生活管家

**核心职责**：健康管理、饮食管理、个人成长、生活质量。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 健康管理 | 备忘录 + Markdown | 运动/饮食记录 |
| 学习追踪 | 飞书笔记 | 读书/课程笔记 |
| 提醒 | 飞书消息 / cron | 作息/习惯提醒 |
| 协作 | 飞书消息 | 主动推送健康/成长提醒 |

**专属技能**：
- 健康管理（运动处方/体能评估/康复计划/睡眠分析）
- 营养学（宏量营养素/卡路里计算/膳食搭配/特殊饮食）
- 习惯养成（微习惯设计/行为激励/复盘反馈）
- 个人成长（目标设定/学习方法/知识管理/读书笔记）
- 压力管理（情绪识别/放松技巧/时间管理）
- 生活质量评估（幸福感维度/生命质量指标）

**专属工具**：
- `skills:life`：个人生活管理全集（饮食/学习/健康/质量）
- `cronjob`：每日健康提醒、每周汇总报告
- `file`：主人健康档案、生活偏好记录、周报月报存档
- `session_search`：检索主人历史偏好和习惯数据

---

### hermes-political · 政治研究部

**核心职责**：监测中国政府重大政策文件，识别政策信号，事件驱动即时推送。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 信息监测 | Web搜索 + 政府官网 | 政策文件/会议信息 |
| 存档 | Markdown | 会议纪要/政策文件存档 |
| 推送 | 飞书消息 | 推送到订阅群 |
| 协作 | 飞书消息 | 向 commander 汇报 |

**专属技能**：
- 政策文件解读（中发/国发/中办发/国办发 分类检索）
- 政治日程追踪（党代会/两会/中央经济工作会/政治局会议）
- 信号识别（政策转向信号提取/隐含意图研判）
- 信息多源验证（官方媒体交叉核对/信源可信度评级）
- 政策影响评估（对宏观经济/特定行业/普通人生活的影响）
- 宏观政策联动（货币政策+财政政策+监管政策 综合分析）

**专属工具**：
- `browser:中国政府网/新华社/人民网`：官方政策文件来源
- `browser:国务院客户端/部委官网`：政策原文检索
- `skills:political-monitoring`：政治监测 cron job
- `file:~/hermes/political-reports/`：报告存档目录
- `session_search`：历史政策解读和判断记录

---

### hermes-economic · 经济研究部

**核心职责**：监测宏观经济、金融市场、行业动态，重大事件第一时间推送。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 信息监测 | Web搜索 + 财经网站 | 宏观经济/金融市场数据 |
| 数据追踪 | Python（pandas）| 指标数据整理 |
| 推送 | 飞书消息 | 阈值触发时推送 |
| 存档 | Markdown | 每日简报/事件专题存档 |

**专属技能**：
- 宏观经济分析（GDP/CPI/PPI/PMI/社融/货币供应量解读）
- A股技术分析（趋势判断/关键支撑阻力位/量价关系）
- 汇率分析（USD/CNY/美元指数/离岸人民币联动）
- 美联储政策跟踪（利率决议/FOMC纪要/鲍威尔讲话）
- 行业景气度（新能源汽车/半导体/互联网/房地产产业链）
- 大宗商品（原油/黄金/铜 与宏观经济的联动关系）

**专属工具**：
- `skills:economic-monitor`：宏观经济监控 cron job
- `browser:东方财富/同花顺/新浪财经`：实时市场数据
- `browser:国家统计局/央行官网`：官方经济数据
- `file:~/hermes/economic-reports/`：报告存档目录
- `session_search`：历史市场判断和预测记录

---

### hermes-ai-lab · AI实验室

**核心职责**：大模型专项研究、模型选型、微调、蒸馏和落地应用。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 模型研究 | Web搜索 + arXiv | 前沿模型文献 |
| 模型微调 | Python（HuggingFace）| fine-tuning实验 |
| 评估 | Python + Markdown | benchmark报告 |
| 协作 | 飞书消息 | 向 commander 汇报 |

**专属技能**：
- 模型架构分析（Transformer/R1/GAIA/MoE）
- Prompt Engineering（零样本/少样本/思维链/CoT）
- 模型微调（LoRA/QLoRA/全参数微调/灾难性遗忘规避）
- 技能蒸馏（知识蒸馏/行为蒸馏/nuwa-skill框架/蒸馏效率评估）
- 模型评估（Benchmark 设计/消融实验/Ablation Study）
- AI Agent 设计（工具调用/多智能体协作/Memory 架构）
- 开源模型部署（vLLM/lmdeploy/ollama/TGI）

**专属工具**：
- `skills:gguf-quantization`：模型量化（CPU 推理优化）
- `skills:llama-cpp`：本地 GGUF 推理
- `skills:whisper`：语音模型集成
- `skills:huggingface-hub`：模型下载/上传/版本管理
- `browser:arXiv`：论文检索追踪
- `terminal:HuggingFace CLI`：模型管理、Spaces 部署

---

### hermes-data-science · 数据科学部

**核心职责**：数据分析、BI报表、AB测试、用户洞察、异常监测。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 数据分析 | Python（pandas/numpy）| 数据清洗/分析 |
| 可视化 | Markdown表格 + ASCII图 | 报告呈现 |
| BI报表 | 飞书表格/多维表格 | 日/周/月报 |
| 协作 | 飞书消息 | 向 commander 汇报 |

**专属技能**：
- 统计分析（描述统计/假设检验/回归分析/ANOVA/贝叶斯分析）
- AB测试设计（分流策略/样本量计算/MDE/多重检验校正）
- 数据可视化（图表选型/看板设计/Dashboard 搭建/storytelling）
- SQL（复杂 join/窗口函数/CTE/性能优化/执行计划分析）
- Python 数据分析（pandas/numpy/scipy/statsmodels/pymc）
- 机器学习建模（sklearn/xgboost/分类/聚类/协同过滤/生存分析）
- 指标体系设计（北极星指标/指标链路/漏斗分析/归因模型）

**专属工具**：
- `cronjob:economic-monitor`：接入 A 股大盘、汇率、央行政策数据
- `skills:shenzhen-events-research`：城市活动数据用于分析用户线下行为
- `skills:political-monitoring`：政策数据与业务影响关联分析
- `browser:Google Trends/Baidu Index`：搜索热度趋势
- `terminal:Python脚本`：自动化报表生成（pandas + matplotlib）

---

### hermes-industry-research · 行业研究部

**核心职责**：垂直行业深度研究，为业务拓展和战略决策提供情报支撑。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 行业研究 | Web搜索 + 行业报告/财报 | 深度行业研究 |
| 竞品追踪 | 天眼查/IT桔子 | 竞品融资/产品动态 |
| 文档 | Markdown | 研究报告存档 |
| 协作 | 飞书消息 | 向 commander 汇报 |

**专属技能**：
- 行业信息收集（多渠道/多语言/结构化/信息鉴别优先级排序）
- 竞品产品拆解（功能矩阵/体验评估/差异化定位/盈利模式分析）
- 市场规模估算（Bottom-up/Top-down/SAM/SOM/TAM）
- 政策文件精读（重点条款提取/立法背景/影响评估/时间表预测）
- 商业画布（9宫格/价值链拆解/商业模式创新）
- 战略分析框架（PEST/SWOT/波特五力/竞争定位图）
- 财务基础（看懂 P&L/毛利率/获客成本 CAC/LTV）

**专属工具**：
- `browser:艾瑞咨询/36kr/虎嗅/财新`：行业报告与商业新闻
- `browser:天眼查/企查查`：竞品工商信息、融资历史、股权结构
- `browser:国家统计局/商务部/教育部官网`：官方政策数据
- `skills:political-monitoring`：政策监控（政治局/国务院/两会文件）
- `skills:china-reform-report`：改革开放脉络参考
- `skills:blogwatcher`：竞品官网/公众号内容持续追踪
- `terminal:爬虫（requests/BeautifulSoup/正则）`：结构化数据抓取

---

### hermes-product · 产品总监

**核心职责**：把调研报告转化为 PRD 和功能规格说明。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 需求管理 | Markdown + 表格 | 撰写PRD、功能清单 |
| 原型设计 | 文字描述 + ASCII流程图 | 页面流程说明 |
| 优先级排序 | RICE/Kano模型 | 功能优先级决策 |
| 协作 | 飞书消息 | 与市场/设计/开发对齐 |
| 追踪 | 飞书群 | 项目进度同步 |

**专属技能**：
- 需求分析（用户故事/JIRA/验收标准定义/PRD撰写）
- 优先级管理（RICE/Kano/RfC 方法论/路线图规划）
- 用户研究（用户访谈/问卷设计/人物画像/场景地图）
- 产品定位（差异化分析/价值主张设计/市场契合度）
- 数据分析（留存/漏斗/Aha Moment/功能使用埋点）
- AI产品设计（LLM场景拆解/Agent UX/人机交互边界）

**专属工具**：
- `file:army-workspace/02-产品设计/`：PRD 输出目录
- `browser:竞品官网/App Store/Google Play`：竞品功能拆解
- `skills:teaching-platform`：现有产品功能参考
- `session_search`：检索历史 PRD 和产品决策
- `delegation:hermes-architect`：架构设计任务派发

---

### hermes-market · 市场调研总监

**核心职责**：市场调研和竞品分析，为产品设计提供依据。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 竞品分析 | Web搜索 + 行业报告 | 竞品功能/定价调研 |
| 问卷/访谈 | 腾讯问卷/飞书妙记 | 用户需求收集 |
| 文档读写 | Markdown | 调研报告存档 |
| 协作 | 飞书消息 | 向 commander 汇报 |

**专属技能**：
- 市场信息收集（艾瑞/36kr/QuestMobile/专家访谈）
- 竞品功能拆解（功能矩阵/用户体验评估/定价策略）
- 市场规模估算（Bottom-up/Top-down/SAM/SOM）
- 用户调研（问卷设计/用户访谈/NPS分析）
- 竞争格局分析（五力模型/竞争定位图/差异化策略）
- 数据可视化（图表选型/报告排版/关键数据突出）

**专属工具**：
- `browser:艾瑞咨询/36kr/虎嗅/QuestMobile`：行业报告和数据
- `browser:天眼查/企查查`：竞品工商信息和融资历史
- `browser:App Store/Google Play/TapTap`：应用商店数据
- `skills:shenzhen-events-research`：本地市场活动参考
- `file:army-workspace/01-市场调研/`：调研报告输出目录

---

### hermes-content · 内容总监

**核心职责**：内容策划、文案创作与品牌表达。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 内容创作 | Markdown编辑器 | 撰写各类文案 |
| 热点追踪 | 微博/抖音/微信热搜 | 选题参考 |
| 排版 | Markdown格式 | 统一输出格式 |
| 协作 | 飞书消息 | 与产品/市场对齐需求 |
| 发布 | 飞书群/订阅号 | 触达用户 |

**专属技能**：
- 内容策划（选题矩阵/爆款结构/内容日历/用户痛点挖掘）
- 文案创作（标题党/软文/产品文案/品牌故事/SEO写作）
- 品牌表达（slogan/品牌故事/价值主张/品牌调性把控）
- AI辅助写作（Prompt设计/多模型协作/质量评估）
- 多平台适配（公众号/知乎/小红书/抖音/飞书/微博）
- 转化率优化（CTA设计/落地页文案/A-B测试）

**专属工具**：
- `skills:humanizer`：AI内容人性化 — 去除AI味、注入真实表达
- `browser:新榜/蝉妈妈/抖音创作中心`：内容数据洞察
- `skills:fashion-luxury-newsletter`：时尚奢侈品牌内容参考
- `file`：内容素材库、品牌指南、内容日历存档
- `delegation:hermes-dev`：专题页面/落地页开发

---

### hermes-marketing · 市场总监

**核心职责**：市场营销、增长获客与品牌建设。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 增长分析 | Google Analytics / 友盟 | 渠道/转化分析 |
| 投放管理 | 巨量引擎/腾讯广告后台 | 广告投放 |
| 内容分发 | 飞书群/订阅号 | 触达用户 |
| 数据监控 | Excel / Markdown表格 | ROI追踪 |
| 协作 | 飞书消息 | 向CEO汇报 |

**专属技能**：
- 增长黑客（AARRR漏斗/病毒系数/裂变设计/转化率优化）
- 数字营销（SEM/SEO/信息流/DSP/私域运营）
- 品牌建设（定位理论/品牌符号/品牌故事/VI审核）
- 数据分析（GA4/归因模型/ROI计算/媒介组合优化）
- 活动策划（品效合一/事件营销/发布会/裂变活动）
- AI营销（智能投放/文案生成/客服自动化）

**专属工具**：
- `browser:Google Analytics/Search Console`：网站流量和搜索数据
- `browser:新榜/千瓜数据/蝉妈妈`：社交媒体数据
- `skills:fashion-luxury-newsletter`：高端品牌营销案例参考
- `cronjob:定时`：市场数据日报/周报
- `file`：营销活动存档、竞品素材库、投放数据分析

---

### hermes-pm · 产品经理

**核心职责**：产品规划、需求管理与跨职能协调。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 需求管理 | Markdown + 表格 | PRD、用户故事 |
| 项目追踪 | 飞书群 + Markdown | 进度同步、风险预警 |
| 优先级 | RICE/Kano模型 | 路线图决策 |
| 协作 | 飞书消息 | 与各团队对齐 |

**专属技能**：
- 需求管理（用户故事/验收标准/变更控制/PRD评审）
- 敏捷项目管理（Scrum/Kanban/冲刺规划/回顾会）
- 进度追踪（里程碑/风险预警/依赖管理/燃尽图）
- 数据驱动决策（留存分析/漏斗/归因/A-B测试）
- 跨部门协调（利益相关方管理/冲突解决/共识达成）
- AI产品设计（Agent UX/人机协作模式/Prompt 设计）

**专属工具**：
- `skills:teaching-platform`：现有产品功能参考和竞品对标
- `browser:App Store/Google Play/TapTap`：应用商店数据
- `cronjob`：定时产品数据报告
- `session_search`：历史需求和决策记录
- `delegation`：任务派发给 dev/qa/marketing

---

### hermes-qa · 测试总监

**核心职责**：质量保障、测试管理与缺陷追踪。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 自动化测试 | Playwright | Web/App全平台测试 |
| 缺陷管理 | Markdown表格 + 飞书 | bug记录与跟踪 |
| 性能测试 | Lighthouse / Chrome DevTools | 性能指标测量 |
| 安全扫描 | SlowMist Agent Security | 新工具安装前安全审计 |
| 协作 | 飞书消息 | 向团队反馈质量报告 |

**专属技能**：
- 测试策略（测试计划/风险评估/测试策略选择）
- 功能测试（Web/App/API/小程序/兼容性/边界值）
- 自动化测试（Playwright/Selenium/Cypress 脚本开发）
- 性能测试（JMeter/LoadRunner/压力测试/瓶颈定位）
- 缺陷分析（复现步骤/根因分析/影响范围评估）
- 移动端测试（iOS/Android/真机调试/崩溃日志）

**专属工具**：
- `skills:playwright-browser-automation`：Web自动化测试脚本
- `browser:Browserstack/SauceLabs`：多浏览器/多设备真机测试
- `file:army-workspace/05-测试验收/`：测试报告和缺陷文档
- `delegation:hermes-dev`：缺陷修复任务派发
- `session_search`：历史缺陷和回归测试记录

---

### hermes-fullstack · 全栈总监

**核心职责**：前后端开发、系统架构与复杂技术攻关。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 全栈开发 | VSCode / Cursor | 前端+后端代码编写 |
| API测试 | curl / Postman | 验证后端接口 |
| 部署 | Docker / Docker Compose | 服务容器化 |
| 构建验证 | npm run build | 构建通过 |
| 协作 | 飞书消息 | 向CEO汇报 |

**专属技能**：
- 全栈开发（React/Node.js/PostgreSQL/Redis/Nginx）
- AI工程化（RAG架构/向量数据库/Agent工具调用/提示词工程）
- 性能优化（数据库/缓存/CDN/异步/代码层面）
- 高可用架构（限流/熔断/降级/多活/灾备）
- 安全防护（SQL注入/XSS/CSRF/认证绕过/加密传输）
- DevOps（Docker Compose/K8s/CI-CD/GitHub Actions/监控）

**专属工具**：
- `skills:llama-cpp`：本地模型推理
- `skills:architecture-diagram`：系统架构图生成
- `browser:Cloudflare/阿里云`：CDN和云服务管理
- `file`：技术方案文档、架构图、技术债务清单
- `delegation`：复杂任务分解给 dev 组

---

### hermes-architect · 架构设计总监

**核心职责**：把 PRD 转化为技术架构设计方案，负责技术选型和系统设计。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 架构设计 | ASCII图 + Markdown | 系统架构图/模块划分 |
| 技术选型 | Web搜索 + 文档 | 技术方案调研 |
| API设计 | Markdown表格 | 接口文档 |
| 数据库建模 | Markdown表格 | Schema设计 |
| 协作 | 飞书消息 | 向 dev-director 交接 |

**专属技能**：
- 系统架构设计（微服务/模块化/事件驱动/响应式）
- 技术选型（语言/框架/数据库/中间件 评估与决策）
- API设计（REST/GraphQL/接口版本管理/向后兼容）
- 数据库设计（Schema/N+1/索引/事务边界/读写分离）
- 性能架构（缓存/异步/CDN/负载均衡/限流）
- 安全架构（认证/授权/数据加密/网络安全）

**专属工具**：
- `skills:architecture-diagram`：生成 SVG 架构图（dark theme）
- `file:army-workspace/03-架构设计/`：架构文档输出目录
- `browser:MDN/官方文档`：技术栈选型参考
- `delegation:hermes-dev`：开发任务派发
- `session_search`：历史架构决策和技术债务记录

---

### hermes-dev · 开发总监

**核心职责**：接收产品设计和架构文档，把需求实现成可运行的代码。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 代码编辑 | VSCode / Cursor | 编写代码 |
| 版本控制 | Git | 代码管理 |
| 构建验证 | npm run build | 构建通过 |
| 任务分发 | Hermes Agent（delegate_task）| 向各 lobster 派发开发任务 |
| 协作 | 飞书消息 | 跟踪进度、汇报完成 |

**专属技能**：
- 全栈开发（React/Next.js/Node.js/TypeScript/PostgreSQL）
- Three.js 3D集成（场景组装/性能优化/与React联动）
- 物理引擎（ Matter.js 碰撞/运动/约束）
- API 开发（RESTful/GraphQL/WebSocket）
- 代码质量（TypeScript 严格模式/单元测试/代码评审）
- 性能调优（Web Vitals/渲染优化/包体积控制）

**专属工具**：
- `terminal:git/npm/next.js CLI`：代码管理和构建
- `file:army-workspace/04-开发实现/`：开发产出物目录
- `delegation:hermes-dev-frontend/3d/backend`：子任务分解
- `delegation:hermes-test`：测试交付
- `session_search`：历史代码和技术决策参考

---

### hermes-dev-frontend · 前端开发总监

**核心职责**：React/Next.js/Tailwind CSS 用户界面与交互开发。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 代码编辑 | VSCode / Cursor | 编写 React/TSX 组件 |
| 构建验证 | npm run build | 构建通过 |
| 样式开发 | Tailwind CSS | 响应式UI |
| 协作 | Hermes Agent（delegate_task）| 与 3D 组件联调 |
| 文档 | Markdown | 组件说明 |

**专属技能**：
- React 19 + Next.js 16 App Router（Server Components/Streaming/Suspense）
- Tailwind CSS 4（响应式设计/暗色模式/主题定制）
- TypeScript 严格模式（类型安全/泛型/工具类型）
- 交互动画（Framer Motion/状态机/过渡动画/微交互）
- 组件库（Shadcn/ui/Radix UI/Headless UI）
- 性能优化（Code Splitting/Lazy Loading/Core Web Vitals）

**专属工具**：
- `terminal:Next.js CLI`：项目构建和开发服务器
- `browser:Chrome DevTools`：性能分析和调试
- `skills:excalidraw`：手绘风格原型和流程图
- `skills:sketch`：HTML 快速原型（2-3 设计变体对比）
- `file`：组件文档、Storybook、UI 规范文档
- `delegation:hermes-dev-3d`：3D 场景需求对接

---

### hermes-dev-backend · 后端开发总监

**核心职责**：Next.js API Routes、Supabase 与第三方服务集成。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 代码编辑 | VSCode / Cursor | 编写 API Routes |
| 数据库 | Supabase Dashboard / SQL | Schema 管理 |
| 构建验证 | npm run build | 构建通过 |
| API测试 | curl / Postman | 验证接口 |
| 协作 | 飞书消息 | 向 dev-director 汇报 |

**专属技能**：
- Next.js App Router API Routes（Server Actions/Route Handlers/中间件）
- Supabase（PostgreSQL/Auth/Realtime/Storage/RLS策略）
- Stripe API（Checkout Session/Webhook/订阅管理/退款）
- PostgreSQL（索引优化/CTE/事务/N+1 解决）
- REST API 设计（版本管理/错误规范/分页/限流）
- 认证鉴权（JWT/Session/Cookie/OAuth2/CORS）

**专属工具**：
- `terminal:Supabase CLI`：本地开发环境/数据库迁移
- `browser:Stripe Dashboard`：支付日志和退款管理
- `skills:outlines`：结构化 API 输出（JSON Schema）
- `file`：API 文档、数据库 Schema、curl 示例
- `delegation:hermes-dev-frontend`：接口对接确认

---

### hermes-dev-3d · 3D开发总监

**核心职责**：Three.js/WebGL 物理可视化，物理教学平台沉浸式 3D 场景。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 3D开发 | Three.js / WebGL | 3D场景搭建 |
| 物理引擎 | Matter.js | 碰撞/运动/受力 |
| 建模 | Blender（参考）| 模型规格参考 |
| 性能测试 | Chrome DevTools FPS | 帧率监测 |
| 协作 | Hermes Agent | 与前端联调 |

**专属技能**：
- Three.js r160+（场景图/材质系统/光照模型/阴影优化）
- React Three Fiber / Drei（React集成/Declarative 3D）
- Matter.js 物理引擎（刚体/碰撞/约束/物理参数调优）
- GLSL 自定义着色器（顶点着色/片元着色/后处理效果）
- WebGL 性能优化（Draw Call/纹理优化/帧率稳定性）
- 物理可视化（物理概念 3D 表达/动画时序设计）

**专属工具**：
- `terminal:three.js CLI`：3D 场景构建和调试
- `browser:Three.js Editor`：场景快速原型
- `skills:architecture-diagram`：3D架构可视化输出
- `file`：3D组件源码、Shader代码、性能测试报告
- `delegation:hermes-dev-frontend`：React组件集成对接

---

### hermes-test · 测试验收总监

**核心职责**：制定测试计划、执行测试、报告缺陷、推动修复。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 测试框架 | Playwright / Cypress | Web自动化测试 |
| 缺陷追踪 | Markdown表格 | 记录bug、跟踪修复 |
| 测试计划 | Markdown | 测试用例/策略文档 |
| 协作 | 飞书消息 | 向 dev-director 反馈bug |

**专属技能**：
- 测试计划（范围定义/策略选择/资源规划/里程碑）
- 测试用例设计（等价类/边界值/场景法/错误推测）
- 功能验证（Web/App/API/UI 交互/响应式/多浏览器）
- 缺陷复现（步骤提炼/日志分析/截图/环境复现）
- 回归测试（缺陷修复验证/历史缺陷回归）
- 验收测试（UAT/业务场景/用户故事验收）

**专属工具**：
- `skills:playwright-browser-automation`：自动化测试脚本
- `browser:多设备测试`：Browserstack 真机验证
- `file:army-workspace/05-测试验收/`：测试报告输出
- `delegation:hermes-dev`：缺陷修复任务派发
- `session_search`：历史缺陷和回归测试记录

---

### hermes-devops · DevOps

**核心职责**：运维自动化、CI/CD、监控告警、线上服务稳定性。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 自动化 | Bash / Python脚本 | 运维脚本编写 |
| 容器化 | Docker / Docker Compose | 服务部署 |
| 监控 | top / htop / 日志 | 资源监控 |
| CI/CD | GitHub Actions | 自动化构建部署 |
| 协作 | 飞书消息 | 向 commander 汇报 |

**专属技能**：
- Linux 系统管理（CentOS/Ubuntu/Shell/Bash/系统调优）
- Docker（镜像构建/优化/安全扫描/harbor 私有仓库）
- Kubernetes（Pod/Service/Deployment/Ingress/持久化卷/调度策略）
- CI/CD 设计（GitHub Actions/Jenkins/GitLab CI/pipeline 优化）
- 监控告警（Prometheus metrics/Grafana dashboard/Alertmanager 配置）
- 日志管理（Loki + Promtail/ELK/结构化日志设计/日志规范）
- 网络安全（Nginx 配置/SSL 证书/防火墙规则/防 DDoS）
- 云服务（阿里云 ECS/SLB/OSS/RDS/腾讯云/ AWS EC2/S3）

**专属工具**：
- `skills:server-operations`：运维脚本集（磁盘清理/v2ray/日志切割）
- `skills:economic-monitor`：接入服务器性能与经济数据联动监控
- `terminal:Kubectl/Docker/ansible`：容器和自动化运维
- `browser:阿里云控制台/腾讯云控制台`：云资源管理
- `cronjob:定时健康检查`：自动探测服务可用性并告警

---

### hermes-security · 安全部

**核心职责**：信息安全、渗透测试、安全审计、合规检查。

**常用工具**：

| 类别 | 工具 | 用途 |
|------|------|------|
| 渗透测试 | SlowMist Agent Security Framework | 新工具/skill安全审计 |
| 代码审计 | Web搜索 + 文档 | 漏洞扫描 |
| 监控 | 日志分析 | 安全事件发现 |
| 协作 | 飞书消息 | 向 commander 汇报 |

**专属技能**：
- 渗透测试（Web/APP/API/网络层/无线网络/社会工程学）
- 代码安全审计（SQL注入/XSS/CSRF/越权/认证绕过/反序列化/SSRF）
- 密码学应用（对称/非对称/哈希/数字签名/TLS/端到端加密）
- 漏洞分析（CVE 解读/漏洞原理/利用条件/在野利用检测）
- 安全合规（GDPR/网络安全法/等保2.0/个人信息保护法）
- 安全架构设计（零信任/纵深防御/最小权限/安全开发生命周期 SDL）
- 应急响应（溯源分析/数字取证/日志分析/止损/恢复）
- 威胁情报（ATT&CK 框架/威胁狩猎/OSINT/暗网监控）

**专属工具**：
- `skills:slowmist-agent-security`：SlowMist 安全审计标准框架
- `terminal:Nmap/Masscan`：端口扫描和网络发现
- `terminal:Metasploit/CrackMapExec`：漏洞利用和横向移动
- `browser:CVE 数据库/NVD/国家信息安全漏洞库`：漏洞查询
- `browser:Shodan/Censys`：网络空间资产搜索引擎
- `browser:VirusTotal`：文件/URL/域名安全扫描
- `skills:playwright-browser-automation`：模拟攻击场景测试
- `cronjob:定时漏洞扫描`：周期性巡检并推送告警

---

## 四、飞书群接入

| 群名称 | Chat ID | 用途 |
|--------|---------|------|
| Hermès 组织群 | oc_08f6cb45cf9c2132e7ee86fd6fb5dec9 | 军团内部协作 |
| 每日订阅群 | oc_c6883cd907e4d226736d87ce9c6c6d79 | 主动推送内容 |

---

## 五、定时任务总表

| 任务 | 频率 | 推送目标 |
|------|------|---------|
| 政治研究部 · 国内政策监测（5级过滤） | 每30分钟 | oc_c6883cd907e4d226736d87ce9c6c6d79 |
| 经济研究部 · 宏观金融监测（5级过滤） | 每30分钟 | oc_c6883cd907e4d226736d87ce9c6c6d79 |
| 每日调研公司日报 | 每天 8:00 | oc_c6883cd907e4d226736d87ce9c6c6d79 |
| 机器人日报 | 每天 10:00 | oc_c6883cd907e4d226736d87ce9c6c6d79 |
| 每周部队状态报告 | 每周一 9:00 | oc_08f6cb45cf9c2132e7ee86fd6fb5dec9 |
| 经济50人论坛周报 | 每周六 9:00 | oc_c6883cd907e4d226736d87ce9c6c6d79 |
| 游戏周报 | 每周六 11:00 | oc_c6883cd907e4d226736d87ce9c6c6d79 |
| 每周生活选题 | 每周五 14:00 | oc_c6883cd907e4d226736d87ce9c6c6d79 |
| 深圳周末活动 | 每周五 10:00 | oc_c6883cd907e4d226736d87ce9c6c6d79 |
| 隐私保护每周资讯 | 每周六 9:00 | oc_c6883cd907e4d226736d87ce9c6c6d79 |
| 时尚新闻每周推送 | 每周六 12:00 | oc_c6883cd907e4d226736d87ce9c6c6d79 |
| 日本服务器每两周检查 | 每14天 10:00 | oc_c6883cd907e4d226736d87ce9c6c6d79 |
| Skill猎人 | 每天 16:00 | 本地 |
| 摸鱼娱乐 | 每天 17:00 | 本地 |

---

## 六、Skills 市场清单（已创建）

| Skill | 对应 Profile | 用途 |
|-------|-------------|------|
| political-monitoring | hermes-political | 中国政府重大政策文件监测 |
| economic-monitor | hermes-economic | A股/汇率/央行政策监控 |
| market-research | hermes-market | 市场调研工作流 |
| product-design | hermes-product | 产品设计工作流 |
| architecture-design | hermes-architect | 架构设计工作流 |
| dev-workflow | hermes-dev | 开发实现工作流 |
| frontend-dev | hermes-dev-frontend | 前端开发工作流 |
| backend-dev | hermes-dev-backend | 后端开发工作流 |
| 3d-dev | hermes-dev-3d | 3D开发工作流 |
| advisor-plan-design | hermes-advisor | 方案制定工作流 |
| akaunting | hermes-cfo | 财务建模分析 |
| AFFiNE | hermes-content | 内容协作管理 |
| playwright | hermes-test/hermes-qa | 浏览器自动化测试 |
| slowmist | hermes-security | 安全审计框架 |
| server-operations | hermes-devops | 运维脚本集 |
| legal-system | hermes-legal | 中国法律体系研究 |
| life | hermes-life | 个人生活管理 |
| teaching-platform | hermes-pm/hermes-product | 学科网产品参考 |

---

## 七、目录结构

```
~/.hermes/
├── profiles/                    # 26个 Profile（含SOUL.md + config.yaml）
│   ├── commander/
│   ├── hermes-ceo/
│   ├── hermes-cfo/
│   ├── hermes-advisor/
│   ├── hermes-legal/
│   ├── hermes-life/
│   ├── hermes-political/
│   ├── hermes-economic/
│   ├── hermes-ai-lab/
│   ├── hermes-data-science/
│   ├── hermes-industry-research/
│   ├── hermes-product/
│   ├── hermes-market/
│   ├── hermes-content/
│   ├── hermes-marketing/
│   ├── hermes-pm/
│   ├── hermes-qa/
│   ├── hermes-fullstack/
│   ├── hermes-architect/
│   ├── hermes-dev/
│   ├── hermes-dev-frontend/
│   ├── hermes-dev-backend/
│   ├── hermes-dev-3d/
│   ├── hermes-test/
│   ├── hermes-devops/
│   └── hermes-security/
│
├── army-workspace/              # 军团工作区（流水线共享）
│   ├── 需求/
│   ├── 01-市场调研/
│   ├── 02-产品设计/
│   ├── 03-架构设计/
│   ├── 04-开发实现/
│   ├── 05-测试验收/
│   └── 06-交付/
│
├── skills/                      # Skills 市场（22个）
├── scripts/                     # 定时脚本
├── projects/                   # 项目文件
├── knowledge_base.md           # 知识库
├── cron/output/                # Cron 输出存档
└── political-reports/          # 政治研究部存档
└── economic-reports/           # 经济研究部存档
```