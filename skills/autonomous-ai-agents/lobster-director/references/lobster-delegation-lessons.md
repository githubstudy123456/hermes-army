# 龙虾军团实战教训
> 整理时间：2026-05-26 | 来源：物理教学平台 Phase 2 开发 + 体态院校爬取

---

## 哪些任务适合派给 lobster-director（delegate_task）

✅ **适合派发的任务**：
- 市场调研报告（web-browse 搜索整理）
- 文档生成（PRD、设计文档、测试报告）
- UI 改版（设计师主导，lobster-product/lobster-test 执行）
- 爬虫脚本编写（blogwatcher、web-browse）
- 信息检索+汇总（高校招生信息、竞品分析）
- 界面美化（深色主题重构、动效添加）

❌ **不适合派发的任务**：
- TypeScript 类型修复（需 commander 逐行核对编译器报错）
- 多文件同步修改（物理模型绑定映射、import 语句统一）
- 精准的模型绑定关系配置（kp1-1 → optics-demo 这类精确映射）
- 需要读取多个交叉文件核对的精确修改
- **信息扒取类任务**：多次验证 delegate_task 只返回工具调用计划，不实际执行结果

---

## delegate_task 执行结果陷阱（重要！）

**发现时间**：2026-05-26
**现象**：lobster军团 content 部门接收 delegate_task 后，只返回"工具调用计划"，不返回实际执行结果。多次派发任务扒取高校招生信息均如此。
**用户原文**："你一个一个来不就行了"，"不要一口气吃成大胖子"

**根本原因**：delegate_task 是异步调度，子 agent 的 subprocess 读取的是全局 SOUL.md，commander 只收到工具规划而非执行结果。

**解法**（按优先级）：
1. **Commander 直接执行**：信息抓取类任务（高校招生、PDF 解析、网站访问），commander 自己动手最有效
2. **goal 参数注入角色**：在 delegate_task 的 `goal` 中直接写清楚最终交付物要求，而非让子 agent 自行规划
3. **避免派给 content 部门**：lobster-content 的 delegate_task 多次只返回计划不执行，扒数据类任务优先用 browser_navigate + urllib + pypdf 自己来

**本 session 教训**：扒5所体态相关院校招生+培养信息，派了3轮 delegate_task 给 content 部门全部无效，最后 commander 自己动手，browser_navigate + urllib 下载 + pypdf 终端提取，完成4所（3完整+1简略）。

---

## 体态院校爬取任务记录（2026-05-26）

| 学校 | 执行方式 | 结果 |
|------|---------|------|
| 北京体育大学 | browser_navigate 招生网 + 浏览器视觉识别 | ✅ 完整 HTML 版招生章程 |
| 北京舞蹈学院 | urllib 下载 PDF + terminal pypdf 提取 | ✅ PDF 7页全部文字提取 |
| 上海戏剧学院 | browser_navigate 招生网 + urllib 下载 PDF + terminal pypdf | ✅ PDF 7页舞蹈方向招生简章 |
| 上体附中 | browser_navigate + Bing 搜索 + 百度百科 | ⚠️ 简略（官网DNS不通） |
| 上戏附中 | Bing 搜索 + 百度百科 | ⚠️ 简略（官网DNS不通） |

**关键技术**：
- PDF URL 可直接 urllib 下载，但不要用 browser_navigate 打开 PDF（返回截断空内容）
- pypdf 在 execute_code 超时 → 用 terminal 工具 + PYTHONPATH 指定
- 上戏/上体附中官网域名均无响应（shxsfz.edu.sh.cn / susfz.edu.cn 等 DNS 不通）
  → 换用百度百科词条获取基本信息
- Bing 搜索比百度更可靠（百度有验证码墙）

---

## 百度网盘课件处理 SOP

```
1. 检查上传目录：
   ls /home/ubuntu/physics-visual-platform/uploads/
2. 分析 zip 内容：
   unzip -l xxx.zip
   # 如中文乱码，用：
   unzip -O GBK -l xxx.zip

3. 对比现有数据（physicsContent.ts 的 ch1）：
   - kp1-1：长度和时间的测量（已有讲解脚本）
   - kp1-2：运动的描述
   - kp1-3：运动的快慢
   - kp1-4：测量平均速度

4. 判断：
   - 如 zip 内容与 platform 已有数据重叠 → rm xxx.zip（释放空间）
   - 如 zip 有 platform 缺少的独家内容 → 解压集成

5. 清理：
   rm /path/to/xxx.zip
```

---

## 精准代码修改场景的判断原则
当用户说"把 X 集成进去"时，先判断：
1. X 是否有 duplicates？（platform 是否已有类似内容）
2. X 是否需要精确的多文件同步修改？
3. X 是否涉及类型系统/编译错误？
如果任意一个为"是"，优先 commander 直接执行，而非派给 sub-agent。