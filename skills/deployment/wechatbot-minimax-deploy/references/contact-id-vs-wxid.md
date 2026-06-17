# room_invites.json contact ID vs wxid

微信联系人有两套独立 ID 体系：

| 格式 | 示例 | 用途 |
|------|------|------|
| wxid | `hxz18318498340` | 微信分配的全局唯一 ID，纯数字 |
| contact ID | `@2bf964db6d375f3ae29ad80bc8e3435192e85f64dc3622fb6bfbc9f717383e6a` | wechat4u/puppet 中存储的用户标识，带 `@` 前缀 |

**wechat4u 在 `room_invites.json` 里存的是 contact ID**，而 `POO_SUPER_ADMIN` 环境变量和 `permissions.yaml` SUPER_ADMINS 字段填的是 wxid。两者直接比对永远不相等。

**判断方法**：以 `@` 开头且长度 > 20 的是 contact ID；纯数字字符串是 wxid。

当前 `is_room_allowed()` 修复方案：直接 `return True`，权限走 SUPER_ADMINS/TRUSTED_USERS（认 wxid）。