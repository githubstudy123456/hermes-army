# Physics Visual Platform — systematic.ts 结构参考

## 文件位置
```
/home/ubuntu/.hermes/army-workspace/04-开发实现/physics-visual-platform/src/data/systematic.ts
```

## 核心结构

```typescript
// 第86行左右
export const chapterLectures: ChapterLecture[] = [
  // 38个章节，id如 '8a-1', '8b-7', '9-13' 等
  // 每个章节有 knowledgePoints 子数组（目前大部分为空）
]

// 第110行左右
export const knowledgePoints: KnowledgePointDetail[] = [
  // 当前已填充32个知识点（覆盖8a-1/8a-2/8a-3/8a-4/8a-6/8b-7/8b-8/8b-9）
  // 剩余13章待填充：8b-10~8b-12, 9-13~9-22
]

// 第1010行左右
function exercise(
  id: string,
  title: string,
  tier: ExerciseTask['tier'],
  source: string,
  pageOrRange: string,
  target: string,
  requirement: string,
  passScore?: number,
  excellentScore?: number
): ExerciseTask
```

## KnowledgePointDetail 格式

```typescript
{
  id: string,           // 格式：'{chapterId}-{section-slug}' 如 '8a3-temperature'
  chapterId: string,    // 如 '8a-3'
  lessonTitle: string,  // 如 '物态变化'
  title: string,        // 知识点标题
  definition: string,   // 定义/概念
  why: string,          // 为什么学这个
  howToUse: string,     // 如何使用
  unit?: string,        // 单位（如 kg/m³）
  needsModel: boolean,
  modelIds?: string[],  // 如 ['balance-scale', 'spring-oscillator', 'wave-equation', 'optics-demo']
  specialCases?: string,
  mistakes?: string,
  example?: string,
  patterns: [
    {
      title: string,    // 匹配 curriculum.ts 的 sectionTitle
      type: '基础' | '提高' | '真题类型',
      method?: string,
      variation?: string
    }
  ],
  exercises: ExerciseTask[]  // 使用 exercise() helper
}
```

## 章节 ID 命名规范
- 8年级上：8a-1~8a-8
- 8年级下：8b-7~8b-12（8b-7力, 8b-8运动和力, 8b-9压强, 8b-10浮力, 8b-11功和机械能, 8b-12简单机械）
- 9年级：9-13~9-22（功和机械能/简单机械/功和机械效率/热学综合/电学基础/电功率/电磁现象/信息能源...）

## curriculum.ts 参考
- 位置：`/home/ubuntu/.hermes/army-workspace/04-开发实现/physics-visual-platform/src/data/curriculum.ts`
- 788行，包含38章完整定义（sectionNo/sectionTitle/theme/difficulty/knowledge/modelIds/homework/summary）
- 是 systematic.ts 章节的权威数据源

## 当前进度（2026-05-28）
- ✅ 已完成：8a-1(5点)/8a-2(4点)/8a-3(4点)/8a-4(5点)/8a-6(4点)/8b-7(3点)/8b-8(3点)/8b-9(4点) = 32点
- ⏳ 待填充：8b-10浮力~9-22能源，共约13章44个知识点
- 每章约3-5个知识点，每个知识点需定义+why+howToUse+patterns+exercises

## 常见陷阱
1. **大 patch 后语法错误**：11k char 的 patch 可能引入格式问题，patch 后用 `grep -n "];\s*$"` 验证数组关闭
2. **重复 id**：并行 agent 写同一文件需协调，本模式是各写不同章节行区域所以无冲突
3. **exercise() helper**：所有练习必须用 `exercise()` 函数，不用直接写对象