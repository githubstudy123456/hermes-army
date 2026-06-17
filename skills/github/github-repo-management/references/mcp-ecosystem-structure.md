# MCP (Model Context Protocol) Ecosystem Structure

## MCP Official GitHub Organization

`https://github.com/modelcontextprotocol`

### Key Repos

| Repo | Stars | Purpose |
|---|---|---|
| `servers` | 87k | **Main servers** — 7 active servers (src/ + package.json workspaces) |
| `servers-archived` | 277 | **Archived servers** — 14 additional servers moved to archive |
| `registry` | 7k | Community MCP server registry (app store for MCP servers) |
| `python-sdk` | 23k | Python SDK |
| `typescript-sdk` | 13k | TypeScript SDK |
| `inspector` | 10k | MCP protocol debugging inspector |
| `ext-apps` | 2k | MCP Apps protocol (UIs embedded AI chatbots) |

### Active Servers (servers/src/)

```
src/
  everything/          TS  @modelcontextprotocol/server-everything
  filesystem/          TS  @modelcontextprotocol/server-filesystem
  memory/              TS  @modelcontextprotocol/server-memory
  sequentialthinking/  TS  @modelcontextprotocol/server-sequential-thinking
  fetch/               Py  mcp-server-fetch
  git/                 Py  mcp-server-git
  time/                Py  mcp-server-time
```

### Archived Servers (servers-archived/src/)

```
src/
  aws-kb-retrieval-server/  AWS Bedrock Knowledge Base RAG
  brave-search/              Brave Search (web + local)
  everart/                   Image generation
  gdrive/                    Google Drive
  github/                    GitHub API
  gitlab/                    GitLab API
  google-maps/               Maps geocoding
  postgres/                  PostgreSQL read-only
  puppeteer/                 Browser automation
  redis/                     Redis KV
  sentry/                     Sentry error tracking
  slack/                      Slack API (channels/post/reaction)
  sqlite/                     SQLite + BI
  git/                        Git repo ops
```

### Research Workflow for MCP Org Repos

When researching `modelcontextprotocol` org repos:

```bash
# 1. Active servers
curl -s "https://api.github.com/repos/modelcontextprotocol/servers/contents/src"

# 2. Archived servers (EASY TO MISS — must check explicitly)
curl -s "https://api.github.com/repos/modelcontextprotocol/servers-archived/contents/src"

# 3. Org repo list (all repos)
curl -s "https://api.github.com/orgs/modelcontextprotocol/repos?per_page=100&sort=updated"
```

**Pitfall**: `servers-archived` does not appear in normal org repo listings sorted by stars or name — it only shows up when you list all repos or query it directly.

### MCP Server Registry

Registry API: `https://registry.modelcontextprotocol.io/docs`
Status: v0.1 API freeze (stable for integrators)

Community servers can be published to the registry at `https://github.com/modelcontextprotocol/registry`