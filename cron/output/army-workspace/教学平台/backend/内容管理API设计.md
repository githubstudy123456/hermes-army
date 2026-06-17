# 内容管理API设计

## 1. API设计原则

### 1.1 设计规范
- RESTful风格API
- 统一响应格式
- JWT认证
- 版本控制(v1)

### 1.2 基础URL
```
生产环境: https://api.teaching-platform.com/api/v1
测试环境: https://api-test.teaching-platform.com/api/v1
```

## 2. 统一响应格式

### 2.1 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 2.2 错误响应
```json
{
  "code": 400,
  "message": "参数错误",
  "error": "详细的错误信息"
}
```

## 3. 学科管理API

### 3.1 获取学科列表
```
GET /api/v1/subjects

Response:
{
  "code": 200,
  "data": [
    { "id": "1", "name": "物理", "code": "physics", "icon": "physics.png" },
    { "id": "2", "name": "化学", "code": "chemistry", "icon": "chemistry.png" }
  ]
}
```

### 3.2 获取学科详情
```
GET /api/v1/subjects/:id

Response:
{
  "code": 200,
  "data": {
    "id": "1",
    "name": "物理",
    "code": "physics",
    "chapters": [
      { "id": "1-1", "name": "力学", "sections": [...] },
      { "id": "1-2", "name": "热学", "sections": [...] }
    ]
  }
}
```

## 4. 知识点管理API

### 4.1 获取知识点列表
```
GET /api/v1/knowledge-points
Query: subject_id, chapter, section, page, size

Response:
{
  "code": 200,
  "data": {
    "list": [...],
    "total": 100,
    "page": 1,
    "size": 20
  }
}
```

### 4.2 获取知识点详情
```
GET /api/v1/knowledge-points/:id

Response:
{
  "code": 200,
  "data": {
    "id": "kp-001",
    "title": "牛顿第一定律",
    "content": "...",
    "formulas": ["F=ma"],
    "relatedPoints": ["kp-002", "kp-003"],
    "videos": ["video-001"],
    "exercises": ["ex-001"]
  }
}
```

### 4.3 创建知识点
```
POST /api/v1/knowledge-points
Body: { subject_id, chapter, section, title, content, ... }

Response:
{
  "code": 201,
  "data": { "id": "kp-xxx" }
}
```

### 4.4 更新知识点
```
PUT /api/v1/knowledge-points/:id
Body: { title, content, ... }

Response:
{
  "code": 200,
  "message": "更新成功"
}
```

### 4.5 删除知识点
```
DELETE /api/v1/knowledge-points/:id

Response:
{
  "code": 200,
  "message": "删除成功"
}
```

## 5. 视频内容管理API

### 5.1 上传视频
```
POST /api/v1/videos/upload
Content-Type: multipart/form-data
Body: file, subject_id, knowledge_point_ids, title

Response:
{
  "code": 201,
  "data": {
    "id": "video-xxx",
    "url": "https://oss.../video.mp4",
    "duration": 1800
  }
}
```

### 5.2 获取视频列表
```
GET /api/v1/videos
Query: subject_id, page, size

Response:
{
  "code": 200,
  "data": { "list": [...], "total": 50 }
}
```

### 5.3 获取视频详情
```
GET /api/v1/videos/:id

Response:
{
  "code": 200,
  "data": {
    "id": "video-001",
    "title": "牛顿定律讲解",
    "url": "...",
    "transcript": "...",
    "relatedPoints": [...]
  }
}
```

## 6. 习题管理API

### 6.1 获取习题列表
```
GET /api/v1/exercises
Query: subject_id, type, difficulty, page, size

Response:
{
  "code": 200,
  "data": {
    "list": [
      {
        "id": "ex-001",
        "type": "choice",
        "difficulty": 2,
        "stem": "以下关于牛顿定律的说法正确的是...",
        "options": ["A", "B", "C", "D"]
      }
    ]
  }
}
```

### 6.2 提交习题答案
```
POST /api/v1/exercises/submit
Body: { exercise_id, answer, user_id }

Response:
{
  "code": 200,
  "data": {
    "correct": true,
    "analysis": "正确答案是A，因为..."
  }
}
```

## 7. 学习进度API

### 7.1 更新学习进度
```
POST /api/v1/learning/progress
Body: { user_id, subject_id, knowledge_point_id, status }

Response:
{
  "code": 200,
  "data": { "progress": 75 }
}
```

### 7.2 获取学习报告
```
GET /api/v1/learning/report
Query: user_id, subject_id

Response:
{
  "code": 200,
  "data": {
    "totalPoints": 100,
    "completedPoints": 45,
    "accuracy": 78,
    "weakPoints": ["力学", "电磁学"],
    "studyTime": 3600
  }
}
```

## 8. 搜索API

### 8.1 全局搜索
```
GET /api/v1/search
Query: keyword, subject, type, page, size

Response:
{
  "code": 200,
  "data": {
    "knowledgePoints": [...],
    "videos": [...],
    "exercises": [...]
  }
}
```

## 9. 文件上传API

### 9.1 图片上传
```
POST /api/v1/upload/image
Content-Type: multipart/form-data
Body: file

Response:
{
  "code": 201,
  "data": { "url": "https://oss.../image.jpg" }
}
```

### 9.2 3D模型上传
```
POST /api/v1/upload/model
Content-Type: multipart/form-data
Body: file (gLB/glTF format)

Response:
{
  "code": 201,
  "data": {
    "id": "model-xxx",
    "url": "https://oss.../model.glb",
    "thumbnail": "https://oss.../thumb.jpg"
  }
}
```

## 10. 错误码定义

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

---
文档版本：v1.0
创建时间：2026-05-28
负责部门：lobster-dev-backend