# wechatbot-webhook 消息格式详解

## multipart/form-data 上报字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `source` | JSON字符串 | 消息来源上下文（room/from/to结构） |
| `type` | string | `text`/`file`/`urlLink`/`friendship`/系统事件 |
| `content` | string | 消息文本内容 |
| `isMentioned` | `0`/`1` | 是否有人@机器人 |
| `isMsgFromSelf` | `0`/`1` | 是否机器人自己发的 |
| `isSystemEvent` | `0`/`1` | 是否系统事件 |

## source JSON 结构

```js
{
  "room": {           // 群消息时有
    "id": "@@xxx",
    "topic": "群名",
    "payload": {
      "id": "@@xxx",
      "adminIdList": [],
      "memberList": [
        {"id": "@xxxx", "name": "昵称", "alias": "备注名"}
      ]
    }
  },
  "from": {            // 发送者
    "id": "@xxx",
    "payload": {
      "id": "@xxx",
      "name": "昵称",
      "city": "城市",
      "province": "省份",
      "avatar": "http://..."
    }
  },
  "to": {              // 接收方（机器人自身）
    "id": "@xxx",
    "payload": {...}
  }
}
```

**关键字段读取方式：**
- 微信ID: `source.from.id`
- 昵称: `source.from.payload.name`
- 群名: `source.room.payload.topic`
- 群ID: `source.room.id`
- 被@的成员: 遍历 `source.room.payload.memberList` 匹配 `name`

## 过滤规则顺序

1. `isSystemEvent == "1"` → 直接返回 `{"success": true}`（静默跳过）
2. `isMsgFromSelf == "1"` → 跳过（不回自己的消息）
3. `type != "text"` → 跳过（目前只处理文字）
4. 群发言限制 → `is_room_allowed()` 检查
5. 空消息 → 跳过

## 消息类型 (type)

| type值 | 说明 |
|--------|------|
| `text` | 文字消息 |
| `image` | 图片 |
| `video` | 视频 |
| `audio` | 语音 |
| `file` | 文件 |
| `urlLink` | 链接 |
| `friendship` | 好友申请 |
| 系统事件 | 由 `legacySystemMsgStrMap` 映射 |