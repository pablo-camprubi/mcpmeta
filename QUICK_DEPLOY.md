# Quick Deploy Guide 🚀

Deploy your Meta Ads MCP server to the cloud in under 5 minutes!

## 🎯 Choose Your Platform

| Platform | Best For | Time | Cost |
|----------|----------|------|------|
| **[Railway](#railway-2-minutes)** ⭐ | Easiest setup | 2 min | ~$5/mo |
| **[Render](#render-3-minutes)** | Free tier | 3 min | Free |

---

## Railway (2 minutes) ⭐

### 1. Prerequisites
- [Railway account](https://railway.app) (free to sign up)
- [Pipeboard token](https://pipeboard.co/api-tokens) (free)

### 2. Deploy Now

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

Or manually:

```bash
# 1. Push to GitHub (if not already)
git remote add origin https://github.com/YOUR_USERNAME/meta-ads-mcp.git
git push -u origin main

# 2. Go to railway.app/new
# 3. Select your GitHub repo
# 4. Railway auto-deploys!
```

### 3. Set Environment Variables

In Railway dashboard → Variables:
```
PIPEBOARD_API_TOKEN=your_token_here
PORT=8080
```

### 4. Get Your URL
```
https://your-app.up.railway.app/mcp
```

**Done!** 🎉

---

## Render (3 minutes)

### 1. Prerequisites
- [Render account](https://render.com) (free to sign up)
- [Pipeboard token](https://pipeboard.co/api-tokens) (free)

### 2. Deploy from Blueprint

1. Push to GitHub
2. Go to [dashboard.render.com/blueprints](https://dashboard.render.com/blueprints)
3. Click "New Blueprint Instance"
4. Connect your repo
5. Render reads `render.yaml` automatically

### 3. Set Environment Variables

Render will prompt for:
```
PIPEBOARD_API_TOKEN=your_token_here
```

### 4. Get Your URL
```
https://meta-ads-mcp.onrender.com/mcp
```

**Done!** 🎉

---

## ✅ Test Your Deployment

```bash
curl -X POST https://YOUR-URL/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_PIPEBOARD_TOKEN" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

You should see a list of available tools!

---

## 🔗 Connect to Your AnalyticsAds Repo

### Option 1: MCP Client (Claude, Cursor)

Add to your MCP config:

```json
{
  "mcpServers": {
    "meta-ads-deployed": {
      "url": "https://YOUR-URL/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_PIPEBOARD_TOKEN"
      }
    }
  }
}
```

### Option 2: Direct HTTP (Python)

```python
from examples.analyticsads_integration import MetaAdsMCPClient

client = MetaAdsMCPClient(
    base_url="https://YOUR-URL",
    token="YOUR_PIPEBOARD_TOKEN"
)

accounts = client.get_ad_accounts()
print(accounts)
```

### Option 3: Direct HTTP (TypeScript)

```typescript
import { MetaAdsMCPClient } from './examples/analyticsads_integration';

const client = new MetaAdsMCPClient(
  "https://YOUR-URL",
  process.env.PIPEBOARD_API_TOKEN!
);

const accounts = await client.getAdAccounts();
console.log(accounts);
```

---

## 📚 Full Documentation

- **Detailed Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Integration Examples**: [examples/README_ANALYTICSADS_INTEGRATION.md](examples/README_ANALYTICSADS_INTEGRATION.md)
- **HTTP Transport Setup**: [STREAMABLE_HTTP_SETUP.md](STREAMABLE_HTTP_SETUP.md)

---

## 💡 Need Help?

- **Discord**: [discord.gg/YzMwQ8zrjr](https://discord.gg/YzMwQ8zrjr)
- **Email**: info@pipeboard.co
- **Issues**: [GitHub Issues](https://github.com/pipeboard-co/meta-ads-mcp/issues)

---

## 🎉 What's Next?

1. ✅ Server deployed
2. ✅ Test connection
3. 📊 Integrate with your analyticsads repo
4. 🚀 Start analyzing Meta Ads with AI!

**Happy deploying!** 🚀

