# Setting Up Your Meta Developer App

Since you're not using Pipeboard authentication, you need to create your own Meta Developer App. This gives you direct control over your Meta API credentials.

## 📋 Prerequisites

- Facebook account with access to Meta Business Suite
- Admin access to the Facebook Pages/Ad Accounts you want to manage

---

## Step 1: Create a Meta Developer App (5 minutes)

### 1.1 Go to Meta for Developers

1. Visit: [developers.facebook.com/apps](https://developers.facebook.com/apps)
2. Click **"Create App"**

### 1.2 Choose App Type

Select: **"Business"** (for managing ads and business data)

### 1.3 Fill in App Details

- **App Name**: `My Meta Ads MCP` (or any name you prefer)
- **App Contact Email**: Your email
- **Business Account**: Select your business account (or create one)

Click **"Create App"**

---

## Step 2: Configure Your App

### 2.1 Add Marketing API Product

1. In your app dashboard, find **"Add Products"** section
2. Click **"Set Up"** on **"Marketing API"**
3. Accept the terms if prompted

### 2.2 Get Your Credentials

1. Go to **Settings** → **Basic** in the left sidebar
2. You'll see:
   - **App ID** - Copy this (you'll need it as `META_APP_ID`)
   - **App Secret** - Click "Show" and copy it (you'll need it as `META_APP_SECRET`)

⚠️ **Keep your App Secret secure!** Never commit it to Git or share it publicly.

### 2.3 Add Redirect URI

1. Still in **Settings** → **Basic**
2. Scroll down to **"App Domains"**
3. Add your Render domain: `your-app.onrender.com`
4. Scroll to **"Website"** section
5. Add: `https://your-app.onrender.com`

### 2.4 Configure OAuth Settings

1. In left sidebar, go to **"Use Cases"**
2. Click on **"Customize"** under Business Use Cases
3. Enable permissions:
   - `business_management`
   - `public_profile`
   - `pages_show_list`
   - `pages_read_engagement`
   - `ads_management`
   - `ads_read`

---

## Step 3: Get Your Access Token (2 options)

### Option A: Graph API Explorer (Quick Testing)

1. Go to: [developers.facebook.com/tools/explorer](https://developers.facebook.com/tools/explorer)
2. Select your app from the dropdown
3. Click **"Generate Access Token"**
4. Select permissions:
   - `business_management`
   - `ads_management`
   - `ads_read`
   - `pages_show_list`
   - `pages_read_engagement`
5. Copy the generated token (you can use this as `META_ACCESS_TOKEN`)

⚠️ **This token expires!** For production, use Option B.

### Option B: OAuth Flow (Production - Recommended)

The MCP server will handle the OAuth flow automatically when users connect. You just need the App ID and App Secret.

---

## Step 4: Deploy with Your Credentials

### Environment Variables for Render

When deploying to Render, set these environment variables:

| Variable | Value | Required |
|----------|-------|----------|
| `META_APP_ID` | Your App ID from Step 2.2 | ✅ Required |
| `META_APP_SECRET` | Your App Secret from Step 2.2 | ✅ Required |
| `META_ACCESS_TOKEN` | Token from Step 3 | ⚠️ Optional (for quick testing) |

**Don't set `PIPEBOARD_API_TOKEN`** - the server will automatically use direct Meta authentication when this is missing.

---

## Step 5: Test Your Setup

Once deployed, test your authentication:

```bash
# Test if app credentials work
curl -X POST https://your-app.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer YOUR_META_ACCESS_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
      "name": "get_ad_accounts",
      "arguments": {"limit": 5}
    }
  }'
```

---

## 🔒 Security Best Practices

1. **Never commit secrets to Git**
   - Add to `.gitignore`: `.env`, `*.secret`
   - Use platform environment variables only

2. **Rotate tokens regularly**
   - Generate new access tokens periodically
   - Update in your deployment platform

3. **Use App Review for production**
   - For public apps, submit for Meta App Review
   - Get "Advanced Access" for full permissions

4. **Monitor API usage**
   - Check your app's dashboard for usage limits
   - Meta has rate limits on API calls

---

## 🆘 Troubleshooting

### "Invalid App ID"
- Check that META_APP_ID matches your app exactly
- Verify the app is active (not in development mode blocked)

### "Invalid OAuth Redirect URI"
- Add your Render URL to App Domains
- Must use HTTPS (not HTTP) in production

### "Insufficient Permissions"
- Ensure all required permissions are added in Use Cases
- May need App Review for advanced permissions

### "Token Expired"
- Generate a new access token
- Consider using long-lived tokens (60 days)

---

## 📚 Additional Resources

- [Meta Marketing API Documentation](https://developers.facebook.com/docs/marketing-apis)
- [App Dashboard](https://developers.facebook.com/apps)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
- [Meta Business Help Center](https://www.facebook.com/business/help)

---

## ✅ Quick Checklist

- [ ] Created Meta Developer App
- [ ] Added Marketing API product
- [ ] Got App ID and App Secret
- [ ] Configured OAuth permissions
- [ ] Generated access token (optional for testing)
- [ ] Added credentials to deployment platform
- [ ] Tested authentication

Once complete, proceed with deployment! 🚀

