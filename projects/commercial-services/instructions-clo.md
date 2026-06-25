# CLO 任务指令

> 来自：Hermès 指挥官 | 日期：2026-06-25 | 截止：2026-07-14

---

## 本次任务：完善商业化文档 — CLO 负责范围

---

### L1：标准服务协议模板

**文件：** `projects/commercial-services/legal-L1-service-agreement.md`（新建）

**需要覆盖的内容：**

1. **基本信息：** 甲乙双方、签订日期、服务期限
2. **服务范围：** 明确约定交付物（报告/咨询/内容）
3. **交付标准：** 对应 R5 输出的质量标准
4. **知识产权：** 交付内容版权归属
5. **保密条款：** 客户数据使用限制
6. **免责条款：** AI 辅助决策的免责声明
7. **退款条件：** 各产品对应的退款政策（与 pricing.md 一致）
8. **争议解决：** 适用法律、仲裁条款

---

### L2：各产品通用免责声明

**文件：** `projects/commercial-services/legal-L2-disclaimer.md`（新建）

**每个产品需要独立的免责声明段落：**

| 产品 | 特殊免责条款 |
|------|------------|
| PolicyGuard | 政策解读仅供参考，不构成法律意见 |
| DueDiligence | 仅基于公开信息，投资决策请自行承担风险 |
| ContractAI | AI 审查不替代律师法律意见 |
| EquityWatch | 报告仅供参考，不构成投资建议 |
| ContentStudio | 发布内容由客户提供，我们不承担内容合规责任 |
| TrainAI | 培训效果因人而异，不承诺就业结果 |
| GaokaoAdvisor | 录取结果由高校决定，我们提供参考建议 |

---

### L3：隐私政策

**文件：** `projects/commercial-services/legal-L3-privacy-policy.md`（新建）

**需要覆盖：**
- 客户数据收集范围（合同文本、联系方式、企业信息）
- 数据存储方式和期限
- 数据使用限制（只用于服务交付，不得用于他途）
- 客户数据删除机制

---

### L4：定价合规性确认

**文件：** `projects/commercial-services/legal-L4-compliance.md`（新建）

**需要确认：**
1. 财经内容（EquityWatch）是否需要相关资质？（证券咨询资质）
2. 教育咨询（GaokaoAdvisor）是否有监管要求？
3. 现有定价是否需要明码标价或备案？
4. 对公转账 / 微信收款是否涉及税务问题？

**结论格式：**
```
## 合规结论
- EquityWatch：✅ 无需资质 / ⚠️ 需要XXX资质，建议____
- GaokaoAdvisor：✅ 无需资质 / ⚠️ 需要XXX资质，建议____
- 收款合规：✅ 合规 / ⚠️ 需要____
```

---

## 提交要求

1. 所有文件写入 `projects/commercial-services/legal-*.md`
2. 完成后与 audit-report.md 中的免责声明逐条核对一致性
3. 截止日期：2026-07-14
