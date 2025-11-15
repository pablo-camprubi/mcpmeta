# 🔐 OAuth Setup Guide for Multiple Users

## Overview

Your MCP server now supports **full OAuth authentication** for multiple users! Users can authenticate via their Facebook account directly from your chatbot interface—no more manual token pasting. 🎉

## Architecture

```
User's Browser → Chatbot App → MCP Server → Facebook OAuth → User Authorizes → Access Token
```

Your chatbot already has the OAuth **client** built in. This guide shows how to configure the OAuth **provider** we just added to your MCP server.

---

## 1. Configure Facebook App

### Step 1: Go to Facebook Developer Console

1. Visit [Facebook Developers](https://developers.facebook.com/)
2. Select your app (App ID: `1600502367599734`)
3. Go to **Settings** → **Basic**

### Step 2: Add OAuth Redirect URI

1. In the left sidebar, click **Facebook Login** → **Settings**
2. Under **Valid OAuth Redirect URIs**, add:
   ```
   https://meta-ads-mcp-rike.onrender.com/oauth/facebook/callback
   ```
3. Click **Save Changes**

### Step 3: Request Permissions (if not already done)

1. Go to **App Review** → **Permissions and Features**
2. Request these permissions:
   - `ads_read` - Read ad account data
   - `ads_management` - Manage ads
   - `business_management` - Manage business assets

---

## 2. Environment Variables (Already Configured!)

These are already set in your `render.yaml`:

```yaml
META_APP_ID: "1600502367599734"
META_APP_SECRET: "6cafab7d8c8a0f14317be3d6d2507fa3"
PUBLIC_URL: "https://meta-ads-mcp-rike.onrender.com"
```

✅ No changes needed!

---

## 3. Deploy to Render

The OAuth provider is now integrated into your server. Just deploy:

```bash
git add .
git commit -m "Add OAuth provider for multiple users"
git push origin main
```

Render will automatically deploy the changes.

---

## 4. Test OAuth Flow

### From Your Chatbot:

1. **Remove manual token** from MCP configuration
2. **Open chatbot** → Go to MCP dashboard
3. **Click "Authorize"** on the Meta Ads MCP card
4. **Login popup opens** → User logs into Facebook
5. **User grants permissions** → Redirects back
6. **Token stored** → User can now use the MCP tools!

### Manual Test (Optional):

Test the OAuth endpoints directly:

```bash
# 1. Test OAuth discovery
curl https://meta-ads-mcp-rike.onrender.com/.well-known/oauth-authorization-server

# 2. Initiate authorization (opens in browser)
# Visit: https://meta-ads-mcp-rike.onrender.com/oauth/authorize?response_type=code&state=test123&redirect_uri=https://your-chatbot.com/callback&code_challenge=test&code_challenge_method=S256
```

---

## 5. OAuth Endpoints

Your MCP server now exposes these endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/.well-known/oauth-authorization-server` | GET | OAuth discovery (metadata) |
| `/oauth/authorize` | POST/GET | Start OAuth flow |
| `/oauth/facebook/callback` | GET | Facebook callback handler |
| `/oauth/token` | POST | Exchange code for token |

---

## 6. Security Features

✅ **PKCE** - Code challenge/verifier for security  
✅ **State parameter** - CSRF protection  
✅ **Session expiry** - Auto-cleanup after 10 minutes  
✅ **HTTPS only** - Secure communication  
✅ **Token expiry** - Facebook tokens expire after 60 days  

---

## 7. Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  User clicks "Authorize" in chatbot                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Chatbot → POST /oauth/authorize                             │
│  Params: state, redirect_uri, code_challenge                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  MCP Server → Redirects to Facebook OAuth                    │
│  URL: facebook.com/dialog/oauth                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  User logs into Facebook & grants permissions                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Facebook → /oauth/facebook/callback                         │
│  Params: code, state                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  MCP Server → Exchanges Facebook code for access token       │
│  Generates authorization code                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  MCP Server → Redirects to chatbot callback                  │
│  URL: chatbot.com/api/mcp/oauth/callback                   │
│  Params: code, state                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Chatbot → POST /oauth/token                                 │
│  Params: code, code_verifier                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  MCP Server → Returns access token                           │
│  Response: { access_token, token_type, expires_in }        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Chatbot → Stores token in database                          │
│  User can now use MCP tools!                                │
└─────────────────────────────────────────────────────────────┘
```

---

## 8. Chatbot Configuration

Your chatbot should already have this, but here's the MCP config format:

```json
{
  "mcpServers": {
    "meta-ads": {
      "url": "https://meta-ads-mcp-rike.onrender.com/mcp",
      "oauth": {
        "authorizationEndpoint": "https://meta-ads-mcp-rike.onrender.com/oauth/authorize",
        "tokenEndpoint": "https://meta-ads-mcp-rike.onrender.com/oauth/token",
        "clientId": "optional",
        "scopes": ["mcp:tools"]
      }
    }
  }
}
```

**Remove this** if it exists:
```json
"headers": {
  "Authorization": "Bearer <token>"
}
```

---

## 9. Production Considerations

### For High Traffic:

Currently, OAuth sessions are stored **in-memory**. For production with many users:

1. **Upgrade to Redis**:
   ```python
   import redis
   redis_client = redis.Redis.from_url(os.environ['REDIS_URL'])
   ```

2. **Add session persistence**:
   - Store sessions in Redis with TTL
   - Handle server restarts gracefully

3. **Add rate limiting**:
   - Limit OAuth attempts per IP
   - Prevent abuse

### For Long-lived Tokens:

Facebook tokens expire after 60 days. To extend:

1. Use **System User Access Tokens** (never expire)
2. Implement **token refresh** before expiry
3. Store token expiry in database

---

## 10. Troubleshooting

### "OAuth redirect URI not registered"
- Go to Facebook App → Facebook Login → Settings
- Add: `https://meta-ads-mcp-rike.onrender.com/oauth/facebook/callback`

### "Session expired or invalid"
- Sessions expire after 10 minutes of inactivity
- User needs to restart OAuth flow

### "Server not configured for OAuth"
- Check `META_APP_ID` and `META_APP_SECRET` are set on Render
- Check `PUBLIC_URL` is correct

### "PKCE verification failed"
- Ensure chatbot is sending `code_challenge` and `code_verifier`
- Check challenge method is `S256`

---

## 11. Logs

Check Render logs for OAuth flow:

```bash
# Authorization started
OAuth authorization initiated for state: abc123

# Facebook callback received
Facebook callback received for state: abc123

# Token exchange successful
Successfully obtained Facebook access token
Token exchange successful
```

---

## 🎉 You're Done!

Your MCP server now supports **OAuth authentication** for multiple users!

**Next Steps**:
1. ✅ Deploy to Render (push to GitHub)
2. ✅ Add redirect URI to Facebook App
3. ✅ Test from your chatbot
4. ✅ Users can now authenticate with one click!

No more manual token management! 🚀

