# Physics Platform UI Patterns

## Project Location
`/home/ubuntu/physics-visual-platform/`

## Data Flow
```
curriculum.json / physicsContent.ts
    ↓
App.tsx (chapters[], point state)
    ↓
components/ (PhysicsModel, AnimationPlayer, etc.)
```

## Data Structures

### curriculum.json fields
```json
{
  "books": [{
    "chapters": [{
      "id": "ch1",
      "title": "第一章 机械运动",
      "points": [{
        "id": "kp1-1",
        "title": "1.1 长度和时间的测量",
        "has_model": false,
        "model_type": "cart",
        "narrations": [{ "step": 1, "title": "...", "content": "..." }]
      }]
    }]
  }]
}
```

### physicsContent.ts KnowledgePoint fields
```typescript
type KnowledgePoint = {
  id: string
  title: string
  section: string
  pptImage: string
  guidingQuestion: string
  objective: string
  explanation: string
  method: string[]
  examples: string[]
  mistakes: string[]
  questionPatterns: QuestionPattern[]
  practice: string
  model: ModelKind | 'none'
  resources: MaterialResource[]
}
```

## UI Layout Structure

### Drawer: Two-Level (Chapter → Points)
- **Grade selector** at top (八年级上册/下册 toggle)
- **Chapter list** below — click to expand points
- **Points list** collapsible under each chapter
- Year level shown once at top, NOT repeated per chapter
- File: `App.tsx` drawer section (line ~194-245)

### Primary Card: Knowledge-First Layout
Right 55% area, content order:
1. Section kicker + title
2. Learning objective box
3. Explanation content block
4. Method breakdown
5. Knowledge list (from `method[]`)
6. Question patterns
7. Examples
8. Mistakes
9. Practice strip
10. **Model entry button** (bottom, only if `point.model !== 'none'`)

### Model Card: Hidden by Default
Right 45% area, hidden until model entry button clicked:
- `isModelExpanded` state (default `false`)
- Conditional render: `{isModelExpanded && <div className="model-card">...}`
- Close button (`×`) top-right of header
- SlideDown animation on expand

## Content Sources

### Uploaded teaching materials
```
uploads/
  初中物理八年级上册第一章_机械运动.zip  ← future uploads land here
```

### Already-extracted text (OCR done)
```
docs/materials/8a-physics/extracted-text/
  1.1+长度和时间的测量（导学案）【教师版】.txt
  1.2+运动的描述（导学案）【教师版】.txt
  1.3+运动的快慢（教学设计）.txt
  1.4+速度的测量（导学案）【学生版】.txt
  第1章+机械运动【速记清单】（解析版）.txt
```

Format from 导学案:
- 【学习目标】→ `objective`
- 【学习重点】→ `keyPoint`
- 【学习难点】→ `difficulty`
- 【合作探究】content → `explanation` / `method[]`
- 例题 → `examples[]`
- 练习 → `practice`

## Key Implementation Details

### State for model expansion
```typescript
const [isModelExpanded, setModelExpanded] = useState(false)
const handleEnterModel = useCallback(() => setModelExpanded(true), [])
```

### Model entry button (in primary card)
```tsx
{point.model !== 'none' && modelOptions.length > 0 && (
  <button className="model-entry-btn" onClick={handleEnterModel}>
    🔷 进入模型演示 →
  </button>
)}
```

### Model card conditional render
```tsx
{isModelExpanded && (
  <div className="model-card">
    {/* model content */}
    <button className="model-close-btn" onClick={() => setModelExpanded(false)}>×</button>
  </div>
)}
```

## Build & Dev Commands
```bash
cd /home/ubuntu/physics-visual-platform
npm run build    # verify compilation
npm start        # dev server on localhost:3000
pkill -f "next-server" && npm start  # restart
```