#!/usr/bin/env python3
"""
Weixin QR Login 脚本（2026-06-11 验证通过）

用法：
  cd ~/.hermes/hermes-agent && venv/bin/python /home/ubuntu/weixin_qr_login6.py > /tmp/weixin_qr6.log 2>&1 &
  sleep 4 && cat /tmp/weixin_qr6.log

关键细节：
  - qr_login(hermes_home) 接受一个位置参数（hermes_home 目录路径）
  - 返回 dict（登录成功）或 None（超时/失败）
  - 不是 async generator，不要 await迭代
  - 必须在导入前 os.chdir 到 hermes-agent 目录
  - signal(SIGTERM) 处理用于优雅退出
"""
import asyncio, sys, os, signal

sys.path.insert(0, os.path.expanduser('~/.hermes/hermes-agent'))
os.chdir(os.path.expanduser('~/.hermes/hermes-agent'))

from gateway.platforms.weixin import qr_login

HERMES_HOME = os.path.expanduser('~/.hermes')

def handle_term(signum, frame):
    print("收到退出信号")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_term)

async def main():
    print("生成微信登录二维码，请扫码...")
    result = await qr_login(HERMES_HOME)
    if result:
        print(f"登录成功: account_id={result.get('account_id','')[:20]}...")
        return 0
    else:
        print("登录失败或超时")
        return 1

if __name__ == '__main__':
    sys.exit(asyncio.run(main()))