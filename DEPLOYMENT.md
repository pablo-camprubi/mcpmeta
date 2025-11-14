# Deployment Guide: Meta Ads MCP Server

This guide shows you how to deploy the Meta Ads MCP server to cloud platforms so it can be accessed remotely from your analyticsads repo or any MCP client.

## 🚀 Quick Comparison

| Platform | Best For | Free Tier | Pricing | Setup Time |
|----------|----------|-----------|---------|------------|
| **Railway** | Easiest setup | $5 credit | ~$5-20/mo | 2 minutes |
| **Render** | Cost-effective | 750 hrs/mo free | $7+/mo | 3 minutes |
| **Fly.io** | Global deployment | Generous free tier | Pay as you go | 5 minutes |

---

## Option 1: Deploy to Railway (Recommended - Easiest) ⭐

### Step 1: Prerequisites
- GitHub account
- Railway account (sign up at [railway.app](https://railway.app))
- Pipeboard API token from [pipeboard.co/api-tokens](https://pipeboard.co/api-tokens)

### Step 2: Deploy

1. **Push your code to GitHub** (if not already):
```bash
cd /Users/p.camprubi/Desktop/meta-ads-mcp-main
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/meta-ads-mcp.git
git push -u origin main
```

2. **Deploy to Railway**:
   - Go to [railway.app/new](https://railway.app/new)
   - Click "Deploy from GitHub repo"
   - Select your `meta-ads-mcp` repository
   - Railway will auto-detect the Dockerfile and deploy

3. **Set Environment Variables**:
   - In Railway dashboard, go to your service
   - Click "Variables" tab
   - Add these variables:
     ```
     PIPEBOARD_API_TOKEN=your_pipeboard_token_here
     PORT=8080
     ```
   - Optional (if using custom Meta app):
     ```
     META_APP_ID=your_app_id
     META_APP_SECRET=your_app_secret
     ```

4. **Get Your Deployment URL**:
   - Railway will auto-generate a domain like: `meta-ads-mcp.up.railway.app`
   - Click "Settings" → "Generate Domain" if not auto-generated
   - Your MCP endpoint will be: `https://YOUR-APP.up.railway.app/mcp`

### Step 3: Test Your Deployment

```bash
curl -X POST https://YOUR-APP.up.railway.app/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer YOUR_PIPEBOARD_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

---

## Option 2: Deploy to Render

### Step 1: Prerequisites
- GitHub account
- Render account (sign up at [render.com](https://render.com))
- Pipeboard API token

### Step 2: Deploy

#### Method A: Using Blueprint (Easiest)

1. **Push code to GitHub** (if not already)

2. **Deploy via Render Blueprint**:
   - Go to [dashboard.render.com/blueprints](https://dashboard.render.com/blueprints)
   - Click "New Blueprint Instance"
   - Connect your GitHub repository
   - Render will read `render.yaml` and create the service

3. **Set Environment Variables**:
   - During setup, Render will prompt for:
     - `PIPEBOARD_API_TOKEN` (required)
     - `META_APP_ID` (optional)
     - `META_APP_SECRET` (optional)

#### Method B: Manual Setup

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: meta-ads-mcp
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m meta_ads_mcp --transport streamable-http --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   - `PIPEBOARD_API_TOKEN`
   - `PORT` (Render sets this automatically)
6. Click "Create Web Service"

### Step 3: Get Your URL
- Render will provide a URL like: `https://meta-ads-mcp.onrender.com`
- Your MCP endpoint: `https://meta-ads-mcp.onrender.com/mcp`

### Step 4: Test
```bash
curl -X POST https://meta-ads-mcp.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer YOUR_PIPEBOARD_TOKEN" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}'
```

---

## Option 3: Deploy to Fly.io

### Step 1: Install Fly CLI

```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

### Step 2: Login and Initialize

```bash
cd /Users/p.camprubi/Desktop/meta-ads-mcp-main

# Login to Fly.io
flyctl auth login

# Initialize app
flyctl launch --no-deploy
```

When prompted:
- Choose app name: `meta-ads-mcp` (or your preferred name)
- Choose region: Select closest to your users
- Would you like to set up a Postgresql database? **No**
- Would you like to deploy now? **No** (we'll set env vars first)

### Step 3: Set Environment Variables

```bash
flyctl secrets set PIPEBOARD_API_TOKEN="your_token_here"
# Optional:
flyctl secrets set META_APP_ID="your_app_id"
flyctl secrets set META_APP_SECRET="your_app_secret"
```

### Step 4: Deploy

```bash
flyctl deploy
```

### Step 5: Get Your URL
```bash
flyctl status
```

Your endpoint: `https://meta-ads-mcp.fly.dev/mcp`

---

## 🔗 Accessing from Your AnalyticsAds Repo

Once deployed, you can access your MCP server from your desktop analyticsads repo:

### For MCP Clients (Claude Desktop, Cursor, etc.)

Add to your MCP configuration file:

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):
```json
{
  "mcpServers": {
    "meta-ads-remote": {
      "url": "https://YOUR-DEPLOYMENT-URL.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_PIPEBOARD_TOKEN"
      }
    }
  }
}
```

**Cursor** (`~/.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "meta-ads-remote": {
      "url": "https://YOUR-DEPLOYMENT-URL.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_PIPEBOARD_TOKEN"
      }
    }
  }
}
```

### For HTTP Client Integration

```python
# In your analyticsads repo
import requests

class MetaAdsMCPClient:
    def __init__(self, base_url, token):
        self.endpoint = f"{base_url}/mcp"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
    
    def call_tool(self, tool_name, arguments=None):
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {"name": tool_name}
        }
        if arguments:
            payload["params"]["arguments"] = arguments
        
        response = requests.post(self.endpoint, headers=self.headers, json=payload)
        return response.json()

# Usage
client = MetaAdsMCPClient(
    base_url="https://YOUR-DEPLOYMENT-URL.com",
    token="YOUR_PIPEBOARD_TOKEN"
)

# Get ad accounts
result = client.call_tool("get_ad_accounts", {"limit": 10})
print(result)
```

### For JavaScript/TypeScript Integration

```typescript
// In your analyticsads repo
interface MCPClient {
  endpoint: string;
  headers: Record<string, string>;
}

class MetaAdsMCPClient implements MCPClient {
  endpoint: string;
  headers: Record<string, string>;

  constructor(baseUrl: string, token: string) {
    this.endpoint = `${baseUrl}/mcp`;
    this.headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  }

  async callTool(toolName: string, args?: any): Promise<any> {
    const payload = {
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: { name: toolName, arguments: args }
    };

    const response = await fetch(this.endpoint, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(payload)
    });

    return response.json();
  }
}

// Usage
const client = new MetaAdsMCPClient(
  'https://YOUR-DEPLOYMENT-URL.com',
  process.env.PIPEBOARD_API_TOKEN!
);

const result = await client.callTool('get_ad_accounts', { limit: 10 });
console.log(result);
```

---

## 🔒 Security Best Practices

1. **Never commit tokens to Git**:
   - Add `.env` to `.gitignore`
   - Use platform environment variables

2. **Use HTTPS only**:
   - All platforms provide free SSL certificates
   - Never use HTTP for production

3. **Rotate tokens regularly**:
   - Generate new Pipeboard tokens at [pipeboard.co/api-tokens](https://pipeboard.co/api-tokens)
   - Update environment variables in your deployment platform

4. **Monitor usage**:
   - Check platform logs regularly
   - Set up alerts for errors

---

## 📊 Monitoring and Logs

### Railway
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# View logs
railway logs
```

### Render
- View logs in dashboard: [dashboard.render.com](https://dashboard.render.com)
- Or use Render CLI: `render logs -s meta-ads-mcp`

### Fly.io
```bash
# View logs
flyctl logs

# View metrics
flyctl dashboard metrics
```

---

## 🔧 Troubleshooting

### Server won't start
- Check environment variables are set correctly
- Verify PIPEBOARD_API_TOKEN is valid
- Check platform logs for error messages

### Authentication errors
- Ensure Authorization header format: `Bearer YOUR_TOKEN`
- Verify token hasn't expired
- Check token has proper permissions at pipeboard.co

### Timeout errors
- Increase timeout settings in your platform
- For Railway: Add healthcheck timeout in `railway.toml`
- For Render: Adjust health check settings

### Port binding errors
- Make sure `PORT` environment variable is set
- Railway/Render set `$PORT` automatically
- Dockerfile should use `${PORT}` variable

---

## 💰 Cost Estimates

### Railway
- **Free**: $5 credit (enough for ~1 month testing)
- **Pro**: $20/month (includes $5 credit)
- **Estimated**: ~$5-10/month for low-medium traffic

### Render
- **Free**: 750 hours/month (one instance can run continuously)
- **Starter**: $7/month per service
- **Standard**: $25/month per service (for production)

### Fly.io
- **Free tier**: 3 shared-cpu-1x VMs with 256MB RAM
- **Estimated**: Free to ~$5/month for low traffic
- **Scale up**: ~$10-30/month for production

---

## 🎯 Next Steps

1. Choose your platform (Railway recommended for easiest setup)
2. Deploy following the steps above
3. Test your deployment with curl
4. Integrate into your analyticsads repo
5. Monitor and scale as needed

Need help? Join our [Discord](https://discord.gg/YzMwQ8zrjr) or email [info@pipeboard.co](mailto:info@pipeboard.co).

