# 🚀 OAuth Quick Start (2 Minutes)

## What Was Added?

Your MCP server now has **OAuth provider endpoints** so users can authenticate with Facebook instead of pasting tokens manually.

---

## Setup Steps

### 1. Add Facebook Redirect URI (1 minute)

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Select your app → **Facebook Login** → **Settings**
3. Add this URL to **Valid OAuth Redirect URIs**:
   ```
   https://meta-ads-mcp-rike.onrender.com/oauth/facebook/callback
   ```
4. Click **Save Changes**

### 2. Deploy (1 minute)

```bash
cd /Users/p.camprubi/Desktop/meta-ads-mcp-main
git add .
git commit -m "Add OAuth provider for multiple users"
git push origin main
```

Render will auto-deploy in ~2-3 minutes.

### 3. Test (30 seconds)

From your chatbot:
1. Remove manual token from config (if any)
2. Click **"Authorize"** on Meta Ads MCP card
3. Login with Facebook → Done! ✅

---

## What Changed?

### Files Added:
- `meta_ads_mcp/core/oauth_provider.py` - OAuth provider implementation
- `OAUTH_SETUP.md` - Full documentation
- `OAUTH_QUICK_START.md` - This file

### Files Modified:
- `meta_ads_mcp/core/http_auth_integration.py` - Added OAuth routes
- `render.yaml` - Added `PUBLIC_URL` environment variable

### Environment Variables:
Already configured in `render.yaml`:
- ✅ `META_APP_ID`
- ✅ `META_APP_SECRET`
- ✅ `PUBLIC_URL`

---

## OAuth Endpoints

Your server now has:

| Endpoint | Purpose |
|----------|---------|
| `/.well-known/oauth-authorization-server` | OAuth metadata |
| `/oauth/authorize` | Start OAuth flow |
| `/oauth/facebook/callback` | Facebook callback |
| `/oauth/token` | Exchange code for token |

---

## How It Works

```
User clicks "Authorize" 
  → MCP server redirects to Facebook
  → User logs in & grants permissions
  → Facebook redirects back with code
  → MCP server exchanges code for token
  → Token stored in chatbot database
  → User can use MCP tools! ✅
```

---

## Security

✅ PKCE - Code challenge/verifier  
✅ State parameter - CSRF protection  
✅ HTTPS only  
✅ Session auto-expiry (10 minutes)  

---

## Need Help?

- **Full documentation**: See `OAUTH_SETUP.md`
- **Troubleshooting**: Check Render logs
- **Test endpoints**: `curl https://meta-ads-mcp-rike.onrender.com/.well-known/oauth-authorization-server`

---

## That's It!

OAuth is now enabled. Deploy and test from your chatbot! 🎉

