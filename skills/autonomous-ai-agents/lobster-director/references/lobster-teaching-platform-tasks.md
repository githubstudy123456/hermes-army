# 教学平台开发任务（Phase 1）

> 更新：2026-05-28

## 项目目标
对标学科网，构建多科目在线教学平台。
9科已有框架（物理最完整），其他科目等资料上传。

## 当前状态
- 已有：index.html / data/subjects.json / data/taxonomy.json
- 物理：力学/热学/光学/电学/声学章节完整
- 其他科目：等待内容填充

## 本次任务分配（Phase 1）

| 部门 | 输出 | 负责人 |
|------|------|--------|
| lobster-product | 物理科目PRD.md | 产品需求审查 |
| lobster-architect | 系统架构设计.md | 多学科扩展方案 |
| lobster-dev-frontend | 物理页面UI优化.md | 前端开发 |
| lobster-dev-backend | 内容管理API设计.md | 后端开发 |
| lobster-dev-3d | 物理3D模型方案.md | 3D可视化 |
| lobster-test | 测试计划.md | 验收测试 |

**输出目录**：`~/.hermes/army-workspace/教学平台/`

## 关键约束
- UI层级：左侧抽屉从4层减为2层（章节→知识点，年级顶部显示一次）
- 没有模型的章节：干净展示知识点，不加多余按钮
- 有模型的章节：模型直接融入页面，无二次入口
- PM审查是强制步骤，不通过不交付