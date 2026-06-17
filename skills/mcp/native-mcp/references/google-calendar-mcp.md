# Google Calendar MCP Servers

Discovered via `npm search mcp calendar` (2026-06-16).

## Available Servers

### `@cocal/google-calendar-mcp`
- npm: `https://www.npmjs.com/package/@cocal/google-calendar-mcp`
- Version: 2.6.2 (updated 2026-06-01)
- Description: Google Calendar MCP Server with extensive support for calendar management
- Transport: stdio (npx or direct node)
- Auth: Google OAuth2

### `gogcli-mcp-calendar`
- npm: `https://www.npmjs.com/package/gogcli-mcp-calendar`
- Version: 2.8.0 (updated 2026-06-12)
- Description: Extended Google Calendar + Meet MCP server via gogcli — auth + Calendar events + Meet space management
- Transport: stdio (npx)
- Auth: Google OAuth2
- Note: Includes Google Meet integration; more feature-rich but heavier

## Config Pattern (Hermes native-mcp)

```yaml
mcp_servers:
  gcalendar:
    command: "npx"
    args: ["-y", "@cocal/google-calendar-mcp"]
    env:
      GOOGLE_CLIENT_ID: "your-client-id"
      GOOGLE_CLIENT_SECRET: "your-client-secret"
    timeout: 120
```

> **Note**: `@cocal/google-calendar-mcp` reads credentials from `gcp-oauth.keys.json` in its own root directory, not from env vars. The `env` approach above is an alternative if the package supports it. Confirm by checking `package.json` of the installed package for the exact mechanism.

Or with uvx (if pip package available):
```yaml
mcp_servers:
  gcalendar:
    command: "uvx"
    args: ["--from", "git+https://github.com/...", "gcalendar-mcp"]
    env:
      GOOGLE_CLIENT_ID: "your-client-id"
      GOOGLE_CLIENT_SECRET: "your-client-secret"
```

## Google OAuth2 Setup (User Must Do)

> ⚠️ **Critical distinction**: Google Cloud Console creates **two different JSON formats** for OAuth clients:
> - **"Desktop app"** → produces `installed` format (correct, works with MCP)
> - **"Web application"** → produces `web` format (incompatible, causes `invalid request` error)
>
> The `@cocal/google-calendar-mcp` package explicitly requires `installed` format. Always choose **"Desktop app"** even if "Web application" seems more logical.

1. Go to https://console.cloud.google.com/apis/credentials
2. Click **"Create Credentials" → "OAuth client ID"**
3. **Application type**: select **"Desktop app"** (this is the only way to get `installed` format)
4. Name it (e.g., `Hermes Calendar`) and create
5. Copy Client ID and Client Secret — JSON is auto-downloaded with `installed` root key
6. Share credentials with Hermes

### Auth URL Generation (Technical Detail)

The `@cocal/google-calendar-mcp` package is ES module-only (`"type": "module"` in package.json). Running auth scripts requires:
- Executing from **within the package directory** (node resolves `google-auth-library` from local `node_modules`)
- Using `.mjs` extension (CommonJS `require()` fails in ES module context)
- Using default import: `import pkg from 'google-auth-library'; const {OAuth2Client} = pkg;`

```bash
# Run from the MCP package directory
cd ~/.npm-global/lib/node_modules/@cocal/google-calendar-mcp
node gen-auth-url.mjs   # outputs the OAuth authorization URL
```

The auth URL uses `http://localhost` as redirect_uri. After user authorizes, the browser redirects to `http://localhost?...`. The full URL in the browser's address bar (including the `code=` parameter) must be captured — this is the authorization code exchangeable for tokens.

### Token Exchange (after user authorization)

Once the user returns the full `http://localhost?...` URL:
1. Extract the `code` query parameter from the URL
2. Exchange code for tokens via `google-auth-library`:

```javascript
// gen-token.mjs — run from MCP package directory
import pkg from 'google-auth-library';
const {OAuth2Client} = pkg;
import {readFileSync} from 'fs';

const keys = JSON.parse(readFileSync('/home/ubuntu/.hermes/secrets/gcp-oauth.keys.json', 'utf8')).installed;
const oauth2Client = new OAuth2Client(keys.client_id, keys.client_secret, 'http://localhost');

const code = 'USER_PROVIDED_CODE_FROM_REDIRECT_URL';
const {tokens} = await oauth2Client.getToken(code);

// Save tokens
const tokenDir = '/home/ubuntu/.config/google-calendar-mcp';
import {mkdirSync} from 'fs';
mkdirSync(tokenDir, {recursive: true});
import {writeFileSync} from 'fs';
writeFileSync(`${tokenDir}/tokens.json`, JSON.stringify(tokens, null, 2));
console.log('Tokens saved to', `${tokenDir}/tokens.json`);
```

Tokens are saved to `~/.config/google-calendar-mcp/tokens.json`. After this step, the MCP server can make Google Calendar API calls on behalf of the user.

## Use Case: Monthly/Annual Report → Calendar Events

After configuring, Hermes can:
- Read existing calendar events
- Create new events with title, description, time
- Write monthly report summaries as all-day events or detailed events
- Suggested event title pattern: `📊 月报 · 2026年6月`

## Related

- `native-mcp` SKILL.md — full MCP client docs
- User wants: cron output (月报/年报) → Google Calendar events automatically
