---
name: hermes-skill-audit
description: Browse, inspect, and evaluate Hermes Skills Hub registry entries before installation — risk triage, security review, and structured recommendation.
category: software-development
---

# hermes-skill-audit

Browse, inspect, and evaluate Hermes Skills Hub registry entries before installation.

## Trigger

- When the user asks to find, review, or evaluate new Hermes skills from the Skills Hub
- When browsing available skills (`hermes skills browse`) before deciding what to install
- When the user wants a curated list of high-value skills with risk assessments

## Steps

### Step 1: Browse Available Skills

```bash
hermes skills browse
```

For more pages: `hermes skills browse --page N`

### Step 2: Read the Skills Index Cache

The canonical registry lives at:
`~/.hermes/skills/.hub/index-cache/hermes-index.json`

```bash
python3 -c "
import json
with open('/home/ubuntu/.hermes/skills/.hub/index-cache/hermes-index.json') as f:
    data = json.load(f)
skills = data if isinstance(data, list) else data.get('skills', data.get('data', []))
for s in skills:
    print(s.get('name','?'), '|', s.get('description','')[:80])
"
```

### Step 3: Inspect Individual Skills

For each candidate, run:

```bash
hermes skills inspect <identifier>
```

e.g. `hermes skills inspect official/instructor`

Inspecting reveals the full SKILL.md content. Look for:
- **trigger conditions** — when does this skill activate?
- **steps/scripts** — exact commands, subprocess calls, file writes
- **API key requirements** — are any external keys needed?
- **subprocess/terminal calls** — any external commands executed?
- **file write operations** — does it modify local files?
- **network calls** — does it make outbound HTTP requests?
- **MCP tool usage** — does it register MCP servers/tools?

### Step 4: Risk Triage

Classify each skill into three tiers:

**✅ Recommended** — Pure local operations, no external calls, no API keys, well-established libraries (e.g. instructor, qmd)

**⚠️ Caution** — Requires API keys, makes external subprocess calls, or needs significant disk/RAM. Proceed if the use case is legitimate and the registry is trusted.

**❌ Skip** — Involves anti-bot/Cloudflare bypass, supply chain risk (cloning arbitrary repos), high-severity secrets management, or ethically questionable operations.

### Known High-Value Skills (Audited)

These have been reviewed and are safe to recommend:

| Skill | Tier | Why |
|-------|------|-----|
| `instructor` | ✅ | LLM structured output via Pydantic, GitHub 15k stars, pure Python lib |
| `qmd` | ✅ | Local RAG (BM25+vector), fully offline, privacy-friendly |
| `meme-generation` | ✅ | Local image gen, creative/marketing use |
| `agentmail` | ⚠️ | Needs API key, email sending — confirm legitimate use case |
| `1password` | ⚠️ | Direct secret access, OP_SERVICE_ACCOUNT_TOKEN leak risk |
| `scrapling` | ❌ | Explicitly supports Cloudflare bypass — legal/ethical risk |
| `gitnexus-explorer` | ⚠️ | Clones external repos + npm build (supply chain), Cloudflare tunnel exposure |

### External Sources — Network Limitations

When auditing from GitHub, HuggingFace, or skills.sh:

- **HuggingFace** (huggingface.co) is **directly unreachable** from this server — times out
- The proxy (`http://127.0.0.1:10809`) works for some sites via CONNECT tunnel but **fails with SSL EOF errors** for huggingface.co, api.github.com, and www.skills.sh
- HuggingFace Skills Marketplace (`hf skills add <name>`) — same SSL EOF issue, not accessible
- **Workaround**: Use `hermes skills browse` (local index cache) + `hermes skills inspect` as the primary research path

### GitHub Search Workaround (Direct Connection)

GitHub.com is **directly reachable** (no proxy needed). Use the GitHub API to find and evaluate high-star Hermes-related repos:

```bash
# Search Hermes agent skills repos by stars
curl -s "https://api.github.com/search/repositories?q=hermes+agent+skill&sort=stars&per_page=15&type=public"

# Get README content for a specific repo
curl -s "https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
```

GitHub API gives you: stars, forks, description, topics, language — enough for first-pass triage. Then `curl` the README for detailed evaluation.

**Known high-star GitHub repos for Hermes skills** (pre-researched):

| Repo | Stars | Description |
|------|-------|-------------|
| `NousResearch/hermes-agent-self-evolution` | 2605 | DSPy+GEPA auto-optimization of skills/prompts |
| `outsourc-e/hermes-workspace` | 2574 | Web workspace (chat/terminal/memory/skills) |
| `0xNyk/awesome-hermes-agent` | 2086 | Awesome list of Hermes ecosystem |
| `codejunkie99/agentic-stack` | 1766 | Portable .agent/ folder across agent tools |
| `jnMetaCode/superpowers-zh` | 1746 | superpowers Chinese version (159k⭐ original) |
| `conorbronsdon/avoid-ai-writing` | 1270 | Remove AI writing patterns, 36 feature categories |
| `AMAP-ML/SkillClaw` | 1086 | Collective skill evolution across agents |
| `prompt-security/clawsec` | 964 | Security suite (prompt injection, drift detection) |
| `Agents365-ai/drawio-skill` | 820 | Natural language → draw.io diagrams |

For any of these, `curl` the README for full evaluation steps, risks, and installation instructions.

### HF CLI (`hf skills`) — Not Accessible

HF CLI (`hf models list`, `hf skills add`) fails due to SSL EOF issue via httpx/httpcore even with proxy. The HuggingFace skills marketplace cannot be browsed from this server until the proxy SSL issue is resolved.

### Step 5: Structured Output for User Review

Present each candidate as:

```
**Skill Name** `official/X`
- **干嘛的**: One sentence description
- **为什么高星/有价值**: Why it stands out (stars, GitHub reputation, unique capability)
- **触发条件**: When to use this skill
- **风险评估**: Tier + specific concerns
- **安装建议**: ✅推荐 / ⚠️可选 / ❌跳过
```

## Pitfalls

- Do NOT trust a skill's description alone — always `hermes skills inspect` to see actual steps/scripts
- Skills with `onSubmit` event handlers in Next.js are NOT a skill-audit concern — that's a frontend bug (fix: add `"use client"` to the component)
- Community skills (from skills.sh) have lower trust thresholds than official ones
- The hermes-index.json may not contain star counts — those come from external registries (GitHub stars, skills.sh community ratings)
- For skills requiring API keys, warn the user before installation and confirm where keys will be stored
- When browsing Hermes Skills Hub, the local index cache (`hermes-index.json`) has no star counts — star ratings come from external registries which may be unreachable (see Network Limitations above)
