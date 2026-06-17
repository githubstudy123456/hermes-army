# WeChat Bot QR Login URL Format

## Token Login URL

When running `node main.js -r`, the bot outputs:
```
Or Access the URL to login: http://localhost:3002/login?token=<TOKEN>
```

The token is read from `process.env.globalLoginToken` which is set from `LOCAL_LOGIN_API_TOKEN` or `LOGIN_API_TOKEN` in `.env`.

**Note:** `LOCAL_LOGIN_API_TOKEN` in `.env shows as `***` when read via `cat /home/ubuntu/wechatbot/.env` (Hermes credential masking). The actual token value is still valid at runtime — the masking only affects display.

## Accessing the Login Page

The login URL is served on port `3002` (from `PORT=3002` in `.env`), not `3001`. The bot listens on whatever `PORT` env var is set.

To login from external network, need nginx reverse proxy for port `3002`.

## QR Code in Terminal

When running in a real TTY (not script/cat redirected), the QR code is printed as ASCII art directly in the terminal. The `-r` flag forces re-login regardless of saved session.
