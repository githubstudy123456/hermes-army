# Japan 服务器运维手册

> 来源：`japan-server` skill（2026-06-03）— 已并入 `server-operations` umbrella

## 连接信息

| 项目 | 值 |
|------|-----|
| IP | `207.56.226.147` |
| SSH 密钥 | `~/.ssh/japan`（密码认证已禁用）|
| SSH 端口 | 22（有时被防火墙临时阻断，443 端口有 CloudFront HTTPS）|
| 用途 | 物理教学资料存储（PPT/练习/知识点/测试），LibreOffice 图片渲染 |

## SSH 连接方式

```bash
# 必须用密钥，密码 Yfwq3879267 已失效
ssh -i ~/.ssh/japan root@207.56.226.147
```

**注意**：有时端口 22 被临时阻断（Connection refused），重试即可恢复。443 端口有 CloudFront HTTPS 可用。

## 数据路径

```
/data/baidu-library/files/初中物理/
├── 第9章-压强/
│   ├── 知识点/  (.docx 知识清单，有学生版/教师版)
│   ├── PPT/     (.pptx 课件，含原卷版/解析版)
│   ├── 练习/    (.docx 习题，有学生版/教师版)
│   └── 测试/    (.docx 单元测试，有原卷版/解析版)
```

- 总计约 252 个文件，约 2.8GB
- SQLite 数据库：`/data/baidu-library/library.db`（182条材料记录）

## 常用操作

### 检查磁盘空间
```bash
ssh -i ~/.ssh/japan root@207.56.226.147 'df -h /data'
```

### 查找 PPTX 文件
```bash
ssh -i ~/.ssh/japan root@207.56.226.147 'find /data/baidu-library/files/ -name "*.pptx" | head -5'
```

### SSH 直测脚本（不经过 Flask）
```bash
# 测试 parse_pptx_b64.py 是否可用
b64path=$(python3 -c "import base64; print(base64.b64encode(b'/data/baidu-library/files/xxx.pptx').decode())")
ssh -i ~/.ssh/japan root@207.56.226.147 "python3 /tmp/hermes/parse_pptx_b64.py $b64path"
```

### pip 安装（Japan 默认无 pip）
```bash
ssh -i ~/.ssh/japan root@207.56.226.147 'curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py && python3 /tmp/get-pip.py'
ssh -i ~/.ssh/japan root@207.56.226.147 'python3 -m pip install python-pptx Pillow'
```

### LibreOffice 图片渲染（PPT → PNG）
```bash
ssh -i ~/.ssh/japan root@207.56.226.147 'libreoffice --headless --convert-to png --outdir /tmp/slides /path/to/file.pptx'
```

## 代理配置

Japan 上的 Xray 使用 VLESS + REALITY 协议：
- UUID: `b831381d-6324-4d53-ad4f-8cda48b30811`
- 伪装目标: `www.amazon.com:443`
- 本地代理端口：10808（SOCKS5）/ 10809（HTTP）

## 已知坑

1. **SSH 端口 22 有时被临时阻断**：重试即可恢复，不要立即判断服务器宕机
2. **Japan 默认无 pip**：需用 get-pip.py 安装
3. **PPTX 文件名含空格**：SSH 命令传参时需 base64 编码路径
4. **curl 测试可能不准**：始终用 Python urllib 测试 API（curl 和 urllib URL 编码行为不同）