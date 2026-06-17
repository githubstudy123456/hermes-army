---
name: feishu-group-bot-communication
description: Bot-to-bot communication in Feishu groups — finding correct open_ids and using proper @ mention tags
triggers:
  - sending to a Feishu group to reach a specific bot
  - openclaw messaging in group chats
  - bot-to-bot @ mentions in Feishu
---

# Feishu Group Bot-to-Bot Communication

## Context
When two bots (e.g., Hermes and openclaw-chat) need to communicate in a Feishu group, direct messaging doesn't work — you must send to the **group** with the recipient's **open_id** as an `@mention` tag so Feishu's roller parses it correctly.

## Finding a Bot's open_id from Gateway Logs

The definitive source is the gateway's JSON log (`/tmp/openclaw/openclaw-YYYY-MM-DD.log`), not `send_message_tool` responses.

```bash
# Filter for received messages in the target group
grep "oc_c6883cd907e4d226736d87ce9c6c6d79" /tmp/openclaw/openclaw-2026-04-21.log \
  | grep "received message from" | tail -20
```

Each received message line contains:
- `received message from ou_XXXXXXXXXXXXXXXX in oc_GROUP_ID (group)`
- The message body text (may show `@mention` tags if present)

**Key insight**: If the message shows `<at user_id="ou_XXXX">BotName</at>` in the received log, that `ou_XXXX` IS the correct open_id for that bot.

**Important**: `ou_d035257cd57ea580c925e4f0b313cd37` often appears in logs — this is typically the openclaw gateway itself (not Hermes). The real target bot's open_id appears in the `sender:` or `from` field of received messages. When a bot posts with `@BotName` in the body, the `user_id` in the `<at>` tag IS that bot's open_id.

## Sending with Correct @ Mention Format

```python
from tools.send_message_tool import send_message_tool

result = send_message_tool({
    'action': 'send',
    'target': 'feishu:oc_c6883cd907e4d226736d87ce9c6c6d79',  # group chat ID
    'message': '<at user_id="ou_CORRECT_OPEN_ID">BotName</at>\n\nMessage text here'
}, task_id='unique-id')
```

## Diagnosing "Received but No Reply" Issues

If the log shows `dispatch complete (queuedFinal=true, replies=1)` but no message appears in the group:

- `dispatching to agent` → message reached the bot's agent
- `dispatch complete (queuedFinal=true, replies=1)` → agent produced a response
- **No message in group** → the response was delivered to a different conversation/session, OR the response was suppressed

**Actions**:
1. Check if the target bot is running in a **separate gateway/process** on a different machine
2. Check the bot's own session logs for the conversation with the group
3. Try sending directly via Feishu API to the bot's open_id (may fail with "Bot has NO availability")
4. Ask the user to copy the bot's actual reply from the group channel

**Note**: If the target bot runs on a **different server**, its agent processes messages independently — Hermes can send to the group but cannot retrieve that bot's responses from its own logs.

## Hermes Director Profile Toolsets — Critical Discovery

When a tool works in CLI but **silently disappears** from `hermes tools list` in a director profile (e.g., `send_message` missing from market-director), the root cause is almost always a **missing toolset in the profile's config.yaml**.

### How Hermes Tool Availability Works (Two-Layer Check)

Layer 1 — `check_fn` inside the tool file:
```python
# tools/send_message_tool.py
def _check_send_message() -> bool:
    return is_gateway_running()  # True if gateway is alive
```
This tells whether the tool CAN theoretically work.

Layer 2 — Profile's `toolsets:` list in `~/.hermes/profiles/<profile>/config.yaml`:
```yaml
toolsets:
  - hermes-cli       # slash commands only — does NOT include messaging
  - web
  - file
```
The toolset list is the **gate**. A tool only becomes visible when its parent toolset is listed here.

### The send_message Specific Case

`sendor_message` lives in the **`messaging`** toolset:
```python
# toolsets.py
elif category == "messaging":
    return ["send_message", "list_channels", ...]
```

If a director profile only has `hermes-cli` in toolsets, it gets zero messaging tools — even though the gateway is running and `_check_send_message()` returns `True`.

### Diagnosis Steps

1. Check if the tool's check_fn works:
```python
python3 -c "
import sys; sys.path.insert(0, '/home/ubuntu/.hermes/hermes-agent')
from tools.send_message_tool import _check_send_message
print('check_fn result:', _check_send_message())
"
# If True → the tool CAN work, the problem is toolsets

2. Check what toolsets are enabled in the profile:
hermes -p <profile> tools list 2>&1 | grep -i <tool-name>

3. Fix: Add the missing toolset to the profile's config.yaml:
```yaml
# ~/.hermes/profiles/<profile>/config.yaml
toolsets:
  - hermes-cli
  - messaging    # ← add this for send_message
  - web
  - file
```

Then restart the gateway: `kill <gateway-pid> && nohup hermes -p <profile> gateway run --replace > /tmp/<profile>.log 2>&1 &`

### Director Profile Recommended Toolsets

| Profile | Required Toolsets |
|---------|-------------------|
| commander | hermes-cli, messaging, delegation, terminal, file, web |
| market-director | hermes-cli, messaging, web, file |
| product-director | hermes-cli, messaging, web, file |
| architect-director | hermes-cli, messaging, file, terminal |
| dev-director | hermes-cli, messaging, delegation, terminal, file |
| test-director | hermes-cli, messaging, file, terminal |

## Common Pitfalls

1. **Wrong open_id**: `send_message_tool` returns `success: true` even with a wrong open_id — it just sends the message. Check logs to confirm the bot actually received it vs. the message being delivered but not triggering a response.
2. **Plain text mentions don't work**: Feishu requires the formal `<at user_id="...">...</at>` XML tag. Plain text like `@BotName` is ignored.
3. **Log locations**: The gateway logs at `/tmp/openclaw/` are the primary source of truth for debugging group message delivery.
4. **Toolsets gate is the real blocker**: A tool's `check_fn` returning True does NOT mean the tool is available in your session — always check the profile's `toolsets:` list first.

## Log Paths
- Active log: `/tmp/openclaw/openclaw-YYYY-MM-DD.log`
- Old log: `~/.openclaw/logs/openclaw.log`
- Dedup state: `~/.openclaw/feishu/dedup/default.json`
