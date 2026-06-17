---
name: mmx-vision
description: 使用 MiniMax mmx CLI 识别图片内容。支持本地图片文件路径或网络图片 URL。
triggers:
  - "识别图片"
  - "看看这张图"
  - "描述这张图片"
  - "图片里有什么"
  - "analyze image"
  - "describe image"
  - "vision"
---

# MMX Vision — MiniMax 图片识别

使用 `mmx vision` 命令调用 MiniMax 多模态模型识别图片内容。

## 使用方式

### 命令格式
```
mmx vision <file_path_or_url>
mmx vision describe --image <file_or_url> --prompt "<question>"
```

### 识别本地图片
```bash
mmx vision /path/to/image.png
```

### 识别网络图片
```bash
mmx vision https://example.com/image.jpg
```

### 带提示词识别
```bash
mmx vision describe --image /path/to/image.png --prompt "这张图里有什么？"
```

## 注意事项

- `mmx` 已配置使用 CN 平台 (`api.minimaxi.com`)，使用 `MINIMAX_CN_API_KEY` 认证
- 图片文件需可读，网络 URL 需服务器可访问（国内可直接访问 `file.cdn.minimax.io` 等）
- 如果图片较大，识别可能需要稍等几秒
