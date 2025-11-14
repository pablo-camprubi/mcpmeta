# 🚀 Deploy to Render NOW - Just Run One Command!

## The Easiest Way to Deploy

I've created an interactive script that will guide you through the entire deployment process step-by-step.

## Just Run This:

```bash
cd /Users/p.camprubi/Desktop/meta-ads-mcp-main
./deploy_to_render.sh
```

That's it! The script will:

1. ✅ Set up Git (if needed)
2. ✅ Guide you to create a GitHub repo
3. ✅ Push your code automatically
4. ✅ Help you get your Pipeboard token
5. ✅ Guide you through Render deployment
6. ✅ Test your deployment
7. ✅ Give you the configuration for your analyticsads repo

---

## What You'll Need (The Script Will Tell You)

1. **GitHub Account** (free) - [github.com](https://github.com)
2. **Render Account** (free) - [render.com](https://render.com)
3. **Pipeboard Token** (free) - [pipeboard.co/api-tokens](https://pipeboard.co/api-tokens)

The script will walk you through getting each of these!

---

## Manual Steps (If You Prefer)

If you prefer to do it manually, here's the quick version:

### 1. Create GitHub Repo
```bash
# Go to: https://github.com/new
# Create repo: meta-ads-mcp
# Then:
cd /Users/p.camprubi/Desktop/meta-ads-mcp-main
git remote add origin https://github.com/YOUR_USERNAME/meta-ads-mcp.git
git push -u origin main
```

### 2. Deploy to Render
- Go to: https://dashboard.render.com/blueprints
- Click "New Blueprint Instance"
- Select your GitHub repo
- Add `PIPEBOARD_API_TOKEN` environment variable
- Click "Apply"

### 3. Done!
Your URL will be: `https://meta-ads-mcp.onrender.com/mcp`

---

## After Deployment

### For Your AnalyticsAds Repo

**Option 1: Add to Cursor/Claude**

Create or update `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "meta-ads-deployed": {
      "url": "https://YOUR-APP.onrender.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_PIPEBOARD_TOKEN"
      }
    }
  }
}
```

**Option 2: Python Client**

Copy `examples/analyticsads_integration.py` to your analyticsads repo:

```python
from meta_ads_mcp_client import MetaAdsMCPClient

client = MetaAdsMCPClient(
    base_url="https://YOUR-APP.onrender.com",
    token="YOUR_PIPEBOARD_TOKEN"
)

accounts = client.get_ad_accounts()
```

**Option 3: TypeScript Client**

Copy `examples/analyticsads_integration.ts` to your analyticsads repo:

```typescript
import { MetaAdsMCPClient } from './metaAdsMcpClient';

const client = new MetaAdsMCPClient(
  "https://YOUR-APP.onrender.com",
  process.env.PIPEBOARD_API_TOKEN!
);

const accounts = await client.getAdAccounts();
```

---

## Need Help?

The interactive script will guide you, but if you get stuck:

1. **Check Render Logs**: dashboard.render.com → your service → Logs
2. **Verify Token**: Make sure PIPEBOARD_API_TOKEN is set correctly
3. **Discord**: [discord.gg/YzMwQ8zrjr](https://discord.gg/YzMwQ8zrjr)
4. **Email**: info@pipeboard.co

---

## Ready?

```bash
cd /Users/p.camprubi/Desktop/meta-ads-mcp-main
./deploy_to_render.sh
```

The script will do the rest! 🚀

