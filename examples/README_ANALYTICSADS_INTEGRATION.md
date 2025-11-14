# AnalyticsAds Integration Examples

This directory contains examples for integrating your deployed Meta Ads MCP server with your analyticsads repository on your desktop.

## Quick Start

1. **Deploy the MCP server** following [DEPLOYMENT.md](../DEPLOYMENT.md)
2. **Get your deployment URL** (e.g., `https://your-app.up.railway.app`)
3. **Get your Pipeboard token** from [pipeboard.co/api-tokens](https://pipeboard.co/api-tokens)
4. **Choose your integration method** below

---

## Option 1: MCP Client Integration (Recommended)

Use this if you want to access the MCP server through Claude Desktop, Cursor, or other MCP clients.

### For Claude Desktop

1. Open: `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)
2. Add configuration:

```json
{
  "mcpServers": {
    "meta-ads-deployed": {
      "url": "https://your-app.up.railway.app/mcp",
      "headers": {
        "Authorization": "Bearer your_pipeboard_token_here"
      }
    }
  }
}
```

3. Restart Claude Desktop
4. You can now ask Claude to use Meta Ads tools!

**Example prompts:**
- "Show me my Meta ad accounts"
- "Get performance insights for my campaigns in the last 30 days"
- "Create a new awareness campaign for my product"

### For Cursor

1. Open: `~/.cursor/mcp.json`
2. Add configuration (same as above)
3. Restart Cursor
4. The MCP server will be available in your Cursor AI agent

---

## Option 2: Direct HTTP Integration (Python)

Use this if you want to call the MCP server directly from Python code in your analyticsads repo.

### Installation

Copy `analyticsads_integration.py` to your analyticsads repo:

```bash
cp examples/analyticsads_integration.py /path/to/analyticsads/integrations/meta_ads_mcp_client.py
```

### Usage

```python
from integrations.meta_ads_mcp_client import MetaAdsMCPClient
import os

# Initialize client
client = MetaAdsMCPClient(
    base_url="https://your-app.up.railway.app",
    token=os.environ["PIPEBOARD_API_TOKEN"]
)

# Get ad accounts
accounts = client.get_ad_accounts(limit=10)
print(accounts)

# Get campaign insights
insights = client.get_insights(
    object_id="act_123456789",
    time_range="last_30d",
    level="campaign"
)
print(insights)

# Search interests
interests = client.search_interests("technology", limit=25)
print(interests)

# Create campaign
campaign = client.create_campaign(
    account_id="act_123456789",
    name="Q1 2025 Brand Awareness",
    objective="OUTCOME_AWARENESS",
    daily_budget=10000,  # $100 in cents
    status="PAUSED"
)
print(campaign)
```

### Environment Variables

Create a `.env` file in your analyticsads repo:

```bash
META_ADS_MCP_URL=https://your-app.up.railway.app
PIPEBOARD_API_TOKEN=your_token_here
```

---

## Option 3: Direct HTTP Integration (TypeScript/JavaScript)

Use this if you want to call the MCP server from TypeScript/JavaScript code.

### Installation

Copy `analyticsads_integration.ts` to your analyticsads repo:

```bash
cp examples/analyticsads_integration.ts /path/to/analyticsads/src/integrations/metaAdsMcpClient.ts
```

### Usage

```typescript
import { MetaAdsMCPClient } from './integrations/metaAdsMcpClient';

// Initialize client
const client = new MetaAdsMCPClient(
  process.env.META_ADS_MCP_URL!,
  process.env.PIPEBOARD_API_TOKEN!
);

// Get ad accounts
const accounts = await client.getAdAccounts({ limit: 10 });
console.log(accounts);

// Get campaign insights
const insights = await client.getInsights({
  object_id: 'act_123456789',
  time_range: 'last_30d',
  level: 'campaign'
});
console.log(insights);

// Search interests
const interests = await client.searchInterests('technology', 25);
console.log(interests);

// Create campaign
const campaign = await client.createCampaign({
  account_id: 'act_123456789',
  name: 'Q1 2025 Brand Awareness',
  objective: 'OUTCOME_AWARENESS',
  daily_budget: 10000,  // $100 in cents
  status: 'PAUSED'
});
console.log(campaign);
```

### Environment Variables

Create a `.env` file:

```bash
META_ADS_MCP_URL=https://your-app.up.railway.app
PIPEBOARD_API_TOKEN=your_token_here
```

---

## Example: Full Integration Workflow

Here's a complete example of using the MCP server in your analyticsads analytics pipeline:

### Python Example

```python
import os
from datetime import datetime, timedelta
from integrations.meta_ads_mcp_client import MetaAdsMCPClient
import pandas as pd

# Initialize
client = MetaAdsMCPClient(
    base_url=os.environ["META_ADS_MCP_URL"],
    token=os.environ["PIPEBOARD_API_TOKEN"]
)

# 1. Get all ad accounts
accounts = client.get_ad_accounts()
account_ids = [acc['id'] for acc in accounts.get('data', [])]

# 2. Get campaigns for each account
all_campaigns = []
for account_id in account_ids:
    campaigns = client.get_campaigns(account_id, limit=100)
    all_campaigns.extend(campaigns.get('data', []))

# 3. Get performance insights
insights_data = []
for campaign in all_campaigns:
    campaign_id = campaign['id']
    insights = client.get_insights(
        object_id=campaign_id,
        time_range='last_30d',
        level='campaign'
    )
    insights_data.append(insights)

# 4. Convert to DataFrame for analysis
df = pd.DataFrame([
    {
        'campaign_id': i['campaign_id'],
        'campaign_name': i['campaign_name'],
        'spend': float(i.get('spend', 0)),
        'impressions': int(i.get('impressions', 0)),
        'clicks': int(i.get('clicks', 0)),
        'ctr': float(i.get('ctr', 0))
    }
    for insight in insights_data
    for i in insight.get('data', [])
])

# 5. Analyze and create reports
print("Top 10 campaigns by spend:")
print(df.nlargest(10, 'spend'))

print("\nTop 10 campaigns by CTR:")
print(df.nlargest(10, 'ctr'))

# 6. Export to CSV for further analysis
df.to_csv('meta_ads_campaign_performance.csv', index=False)
print("\n✅ Campaign performance exported to meta_ads_campaign_performance.csv")
```

### TypeScript Example

```typescript
import { MetaAdsMCPClient } from './integrations/metaAdsMcpClient';
import * as fs from 'fs';

async function analyzeMetaAdsPerformance() {
  // Initialize
  const client = new MetaAdsMCPClient(
    process.env.META_ADS_MCP_URL!,
    process.env.PIPEBOARD_API_TOKEN!
  );

  // 1. Get all ad accounts
  const accounts = await client.getAdAccounts();
  const accountIds = accounts.data?.map((acc: any) => acc.id) || [];

  // 2. Get campaigns for each account
  const allCampaigns = [];
  for (const accountId of accountIds) {
    const campaigns = await client.getCampaigns({
      account_id: accountId,
      limit: 100
    });
    allCampaigns.push(...(campaigns.data || []));
  }

  // 3. Get performance insights
  const insightsData = [];
  for (const campaign of allCampaigns) {
    const insights = await client.getInsights({
      object_id: campaign.id,
      time_range: 'last_30d',
      level: 'campaign'
    });
    insightsData.push(...(insights.data || []));
  }

  // 4. Analyze data
  const performanceData = insightsData.map((insight: any) => ({
    campaign_id: insight.campaign_id,
    campaign_name: insight.campaign_name,
    spend: parseFloat(insight.spend || '0'),
    impressions: parseInt(insight.impressions || '0'),
    clicks: parseInt(insight.clicks || '0'),
    ctr: parseFloat(insight.ctr || '0')
  }));

  // 5. Sort by spend
  const topBySpend = performanceData
    .sort((a, b) => b.spend - a.spend)
    .slice(0, 10);

  console.log('Top 10 campaigns by spend:');
  console.table(topBySpend);

  // 6. Export to JSON
  fs.writeFileSync(
    'meta_ads_campaign_performance.json',
    JSON.stringify(performanceData, null, 2)
  );
  
  console.log('\n✅ Campaign performance exported to meta_ads_campaign_performance.json');
}

analyzeMetaAdsPerformance().catch(console.error);
```

---

## Testing Your Integration

### Test Script (Python)

```bash
# Set environment variables
export META_ADS_MCP_URL="https://your-app.up.railway.app"
export PIPEBOARD_API_TOKEN="your_token_here"

# Run the example
python examples/analyticsads_integration.py
```

### Test Script (TypeScript)

```bash
# Set environment variables
export META_ADS_MCP_URL="https://your-app.up.railway.app"
export PIPEBOARD_API_TOKEN="your_token_here"

# Compile and run
npx ts-node examples/analyticsads_integration.ts
```

---

## Available Tools Reference

Here are the most commonly used tools in the MCP server:

| Tool Name | Description | Common Use Case |
|-----------|-------------|-----------------|
| `get_ad_accounts` | Get all ad accounts | Initial setup, account discovery |
| `get_campaigns` | Get campaigns for an account | Campaign analysis |
| `get_insights` | Get performance metrics | Analytics, reporting |
| `search_interests` | Search targeting interests | Campaign planning |
| `create_campaign` | Create new campaign | Campaign automation |
| `update_campaign` | Update campaign settings | Campaign optimization |
| `get_adsets` | Get ad sets | Ad set analysis |
| `get_ads` | Get ads | Ad creative analysis |

For a complete list, call `client.list_tools()` or see the main [README.md](../README.md).

---

## Troubleshooting

### Connection Errors

```python
# Test basic connectivity
import requests

response = requests.post(
    "https://your-app.up.railway.app/mcp",
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer your_token"
    },
    json={
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }
)

print(response.status_code)
print(response.json())
```

### Authentication Errors

- Verify your token is valid at [pipeboard.co/api-tokens](https://pipeboard.co/api-tokens)
- Check the Authorization header format: `Bearer YOUR_TOKEN`
- Ensure the token hasn't expired

### Timeout Errors

- Increase timeout in your HTTP client
- Check if your deployment is running (check platform logs)
- Try a simpler request first (e.g., `tools/list`)

---

## Next Steps

1. ✅ Deploy your MCP server following [DEPLOYMENT.md](../DEPLOYMENT.md)
2. ✅ Test the connection using the examples above
3. ✅ Integrate into your analyticsads workflows
4. ✅ Monitor usage and scale as needed

Need help? Join our [Discord](https://discord.gg/YzMwQ8zrjr) or email [info@pipeboard.co](mailto:info@pipeboard.co).

