# Deploy to Render WITHOUT Pipeboard

Complete guide to deploy your Meta Ads MCP server using **direct Meta authentication** (no Pipeboard required).

---

## 🎯 What You'll Need

1. **GitHub Account** (free) - To host your code
2. **Render Account** (free) - To deploy your server
3. **Meta Developer App** - Your own Meta app credentials

---

## Step 1: Create Your Meta Developer App (5 minutes)

### Quick Setup

1. Go to: [developers.facebook.com/apps](https://developers.facebook.com/apps)
2. Click **"Create App"** → Select **"Business"**
3. Fill in:
   - Name: `My Meta Ads MCP`
   - Email: Your email
4. Click **"Create App"**

### Get Your Credentials

1. Go to **Settings** → **Basic**
2. Copy your **App ID** (save this as `META_APP_ID`)
3. Click **"Show"** next to **App Secret** and copy it (save as `META_APP_SECRET`)

### Add Marketing API

1. Find **"Add Products"** section
2. Click **"Set Up"** on **"Marketing API"**

### Configure Permissions

1. Go to **"Use Cases"** in left sidebar
2. Click **"Customize"** under Business Use Cases
3. Enable these permissions:
   - `business_management`
   - `ads_management`
   - `ads_read`
   - `pages_show_list`
   - `pages_read_engagement`

📚 **Detailed instructions:** See [SETUP_META_APP.md](SETUP_META_APP.md)

---

## Step 2: Push Code to GitHub (2 minutes)

### If you don't have a GitHub repo yet:

```bash
# 1. Create repo at https://github.com/new
#    Name: meta-ads-mcp
#    Don't initialize with README

# 2. Push your code
cd /Users/p.camprubi/Desktop/meta-ads-mcp-main
git remote add origin https://github.com/YOUR_USERNAME/meta-ads-mcp.git
git push -u origin main
```

### If you already have a repo:

```bash
cd /Users/p.camprubi/Desktop/meta-ads-mcp-main
git add .
git commit -m "Configure for direct Meta authentication"
git push
```

---

## Step 3: Deploy to Render (3 minutes)

### Option A: Using Blueprint (Recommended)

1. Go to: [dashboard.render.com/blueprints](https://dashboard.render.com/blueprints)
2. Click **"New Blueprint Instance"**
3. Connect your GitHub repo: `meta-ads-mcp`
4. When prompted for environment variables, enter:

| Variable | Value | Where to Get It |
|----------|-------|-----------------|
| `META_APP_ID` | Your App ID | From Step 1 - Settings → Basic |
| `META_APP_SECRET` | Your App Secret | From Step 1 - Settings → Basic (click "Show") |
| `META_ACCESS_TOKEN` | *(Optional)* | From Graph API Explorer (see below) |

5. Click **"Apply"**
6. Wait 2-3 minutes for deployment

### Option B: Manual Setup

1. Go to: [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repo
4. Configure:
   - **Name**: `meta-ads-mcp`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m meta_ads_mcp --transport streamable-http --host 0.0.0.0 --port $PORT`
5. Add Environment Variables (same as above)
6. Click **"Create Web Service"**

---

## Step 4: Get Access Token (Optional but Recommended)

For easier testing, generate an access token:

1. Go to: [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer)
2. Select your app from dropdown
3. Click **"Generate Access Token"**
4. Select permissions:
   - `business_management`
   - `ads_management`
   - `ads_read`
   - `pages_show_list`
   - `pages_read_engagement`
5. Copy the token
6. Add to Render: Dashboard → Your Service → Environment → Add `META_ACCESS_TOKEN`

⚠️ **Note:** This token expires in ~2 hours. For production, the OAuth flow will generate long-lived tokens automatically.

---

## Step 5: Test Your Deployment

### Get Your Deployment URL

From Render dashboard: `https://meta-ads-mcp.onrender.com`

Your MCP endpoint: `https://meta-ads-mcp.onrender.com/mcp`

### Test with curl

```bash
curl -X POST https://meta-ads-mcp.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer YOUR_META_ACCESS_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'
```

### Test with the script

```bash
cd /Users/p.camprubi/Desktop/meta-ads-mcp-main
./test_deployment.sh https://meta-ads-mcp.onrender.com YOUR_META_ACCESS_TOKEN
```

---

## Step 6: Connect to Your AnalyticsAds Repo

### Option 1: MCP Client (Cursor/Claude)

Create or update `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "meta-ads-deployed": {
      "url": "https://meta-ads-mcp.onrender.com/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_META_ACCESS_TOKEN"
      }
    }
  }
}
```

Restart Cursor, and the MCP server will be available!

### Option 2: Python Client

Copy `examples/analyticsads_integration.py` to your analyticsads repo:

```python
from meta_ads_mcp_client import MetaAdsMCPClient

client = MetaAdsMCPClient(
    base_url="https://meta-ads-mcp.onrender.com",
    token="YOUR_META_ACCESS_TOKEN"
)

# Get ad accounts
accounts = client.get_ad_accounts()
print(accounts)

# Get insights
insights = client.get_insights(
    object_id="act_123456789",
    time_range="last_30d",
    level="campaign"
)
print(insights)
```

### Option 3: TypeScript Client

Copy `examples/analyticsads_integration.ts` to your analyticsads repo:

```typescript
import { MetaAdsMCPClient } from './metaAdsMcpClient';

const client = new MetaAdsMCPClient(
  "https://meta-ads-mcp.onrender.com",
  process.env.META_ACCESS_TOKEN!
);

const accounts = await client.getAdAccounts();
const insights = await client.getInsights({
  object_id: "act_123456789",
  time_range: "last_30d",
  level: "campaign"
});
```

---

## 🔒 Security Notes

1. **Never commit secrets to Git**
   - Your META_APP_SECRET
   - Your META_ACCESS_TOKEN
   - Use environment variables only

2. **Keep App Secret secure**
   - Store in Render environment variables
   - Never share or expose publicly

3. **Rotate tokens regularly**
   - Generate new access tokens periodically
   - Update in Render dashboard

---

## 🆘 Troubleshooting

### Build Fails on Render
- Check `requirements.txt` is complete
- View build logs in Render dashboard
- Ensure Python version is 3.10+

### "Invalid App ID" Error
- Verify META_APP_ID matches your app exactly
- Check spelling and no extra spaces

### "OAuth Redirect URI mismatch"
- Add your Render URL to app domains
- Settings → Basic → App Domains → Add `your-app.onrender.com`

### "Insufficient Permissions"
- Check Use Cases in your Meta app
- Ensure all required permissions are enabled
- May need App Review for production

### Token Expired
- Generate new token in Graph API Explorer
- Update META_ACCESS_TOKEN in Render
- Consider implementing OAuth refresh flow

---

## 📚 Additional Resources

- **[SETUP_META_APP.md](SETUP_META_APP.md)** - Detailed Meta app setup
- **[examples/README_ANALYTICSADS_INTEGRATION.md](examples/README_ANALYTICSADS_INTEGRATION.md)** - Integration examples
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - General deployment guide

---

## ✅ Quick Checklist

- [ ] Created Meta Developer App
- [ ] Got App ID and App Secret
- [ ] Added Marketing API product
- [ ] Configured permissions
- [ ] Pushed code to GitHub
- [ ] Deployed to Render with environment variables
- [ ] Generated access token
- [ ] Tested deployment
- [ ] Connected to analyticsads repo

---

## 🎉 You're Done!

Your Meta Ads MCP server is now deployed without Pipeboard! 

Access it from anywhere:
- **MCP clients** (Cursor, Claude)
- **Python/TypeScript** directly from your code
- **Any HTTP client** that supports JSON-RPC

Need help? Open an issue on GitHub or check the troubleshooting section above.

