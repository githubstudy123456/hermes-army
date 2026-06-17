# 学科网(zxxk.com)结构参考文档
> 验证时间：2026-05-27
> 用途：物理教学平台改版参考

## 站点信息

- **正确域名**：`www.zxxk.com`（`xueke.cn` 不存在）
- **物理初中站**：`wl.zxxk.com/m/`
- **物理高中站**：`wl.zxxk.com/p/`
- **首页**：`https://www.zxxk.com`
- **技术栈**：Vue.js（`__VUE__` 全局变量）+ jQuery 1.10.2，多页应用（MPA）

## 全学科导航（首页顶部）

学科按学段分三条横栏：小学 / 初中 / 高中，每科独立子站：

```
语文 → yw.zxxk.com
数学 → sx.zxxk.com
英语 → yy.zxxk.com
物理 → wl.zxxk.com/m/ 或 /p/
化学 → hx.zxxk.com/m/
生物学 → sw.zxxk.com/m/
历史 → ls.zxxk.com/m/
地理 → dl.zxxk.com/m/
道德与法治 → zz.zxxk.com
科学 → kx.zxxk.com
信息科技 → xx.zxxk.com
音乐 → yinyue.zxxk.com
美术 → ms.zxxk.com
体育与健康 → ty.zxxk.com
```

## 页面结构（以初中物理移动站 wl.zxxk.com/m/ 为例）

### 左侧导航（年级 → 章节 → 知识点，4层）
当前OURS：人教版 → 年级 → 章节 → 知识点（共4层，嵌套太深）
目标：改为 年级（顶部切换）→ 章节 → 知识点（2层）

### 中间横向 Tab

| 主Tab | 子Tab | 内容 |
|-------|-------|------|
| 同步教学 | 新授课/单元复习/阶段检测/期中/期末/暑假/寒假 | 按教材章节顺序 |
| 中考备考 | 一轮复习/二轮专题/三轮冲刺/一模/二模/模拟预测 | 初中专属 |
| 知识点 | 力学/电和磁/欧姆定律/热学/光学/电功和电功率/实验/跨学科实践/物理模型 | 学科知识体系 |
| 作业 | — | 待补充 |
| 试卷 | — | 待补充 |
| 作文 | — | 待补充 |
| 精品 | — | 待补充 |
| 名校 | — | 待补充 |
| 教辅 | — | 待补充 |

### 知识内容详情（以「光的折射」为例）

每知识点下展示四类资源：
- **课件**：同步课件 PPT
- **教案**：教学设计
- **题型**：习题训练
- **模型**：3D可视化（这正是OURS已有的）

### URL Pattern

```
{学科}.zxxk.com/{学段}/{内容分类}
wl.zxxk.com/m/kpoints-kp13958（力学知识点）
wl.zxxk.com/m/review-ctzy/sce420301/（中考一轮复习）
```

## 对OURS平台的参考价值

OURS已有的数据正好可以填入学科网结构中的「模型」位置：

| 学科网分类 | OURS modelTemplates 对应 |
|-----------|--------------------------|
| 力学 | `force-vector`, `newton-friction`, `pressure-fluid`, `buoyancy`, `work-energy`, `pulley-system` |
| 光学 | `light-ray` |
| 热学 | `state-change`, `macro-micro`, `heat-engine` |
| 电和磁 | `circuit-basic`, `voltage-resistance`, `ohm-law`, `electric-power`, `home-electric` |
| 电磁学 | `electromagnetism`, `magnetic-induction` |
| 高中力学 | `kinematics-graph`, `projectile-motion`, `circular-gravity` |
| 高中电磁学 | `electrostatic-field`, `shm-wave` |

OURS curriculum3d.ts 中的 scenes 对应各知识点的具体模型。

## 关键踩坑

- 学科网是多页应用（非 SPA），每个学段/学科有独立 URL
- jQuery 1.10.2 + Vue.js 共存，jQuery 管传统脚本，Vue 管新功能
- 移动站和 PC 站 URL 不同（移动站有 `/m/` 后缀）