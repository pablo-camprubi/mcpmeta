# How to Get a Long-Lived Meta Access Token

Your access token expired. Here's how to get a new one that lasts **60 days**.

## Step 1: Get a Short-Lived Token

1. Go to [Meta Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app: **1600502367599734**
3. Click **"Get Token"** → **"Get User Access Token"**
4. Select these permissions:
   - ✅ `ads_management`
   - ✅ `ads_read`
   - ✅ `business_management`
5. Click **"Generate Access Token"** and copy it

## Step 2: Exchange for Long-Lived Token

Run this command (replace `SHORT_LIVED_TOKEN` with the token from Step 1):

```bash
curl -X GET "https://graph.facebook.com/v22.0/oauth/access_token?grant_type=fb_exchange_token&client_id=1600502367599734&client_secret=6cafab7d8c8a0f14317be3d6d2507fa3&fb_exchange_token=SHORT_LIVED_TOKEN"
```

You'll get a response like:

```json
{
  "access_token": "EAAWvpf8VPHYBOxxxxxxxx...",
  "token_type": "bearer",
  "expires_in": 5183944
}
```

The `access_token` will be valid for **60 days**.

## Step 3: Update Your MCP Configuration

Use the new long-lived token in your MCP config:

```json
{
  "url": "https://meta-ads-mcp-rike.onrender.com/mcp",
  "headers": {
    "Authorization": "Bearer YOUR_NEW_LONG_LIVED_TOKEN_HERE"
  }
}
```

## Step 4: Update Render Environment Variables (Optional)

If you want the server to use the new token by default:

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Find your `meta-ads-mcp` service
3. Go to **Environment** tab
4. Update `META_ACCESS_TOKEN` with the new token
5. Click **"Save Changes"** (will auto-redeploy)

## Alternative: Use System User Token (Never Expires)

For production, create a System User token that doesn't expire:

1. Go to [Meta Business Settings](https://business.facebook.com/settings/)
2. Click **"Users"** → **"System Users"**
3. Create a new System User
4. Assign it to your ad accounts
5. Generate a token with `ads_management` permissions
6. Select **"Never Expire"**

This is better for long-term deployments!

---

**Note**: Your current token expired because Meta user access tokens only last 1-2 hours by default. Long-lived tokens last 60 days, and System User tokens never expire.


