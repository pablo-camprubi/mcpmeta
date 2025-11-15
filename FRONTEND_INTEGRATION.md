# Frontend Integration Guide

Complete guide to connect your frontend application to the deployed Meta Ads MCP server.

**Server URL:** `https://meta-ads-mcp-rike.onrender.com/mcp`

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Vanilla JavaScript](#vanilla-javascript)
- [React Integration](#react-integration)
- [TypeScript Client](#typescript-client)
- [Next.js Integration](#nextjs-integration)
- [Vue.js Integration](#vuejs-integration)
- [Authentication](#authentication)
- [Error Handling](#error-handling)
- [Example Use Cases](#example-use-cases)

---

## Quick Start

### Basic Requirements

```javascript
// Your MCP server endpoint
const MCP_URL = 'https://meta-ads-mcp-rike.onrender.com/mcp';

// Your Meta access token (from Graph API Explorer or environment variable)
const ACCESS_TOKEN = 'YOUR_META_ACCESS_TOKEN';
```

### Required Headers

```javascript
const headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json, text/event-stream',
  'Authorization': `Bearer ${ACCESS_TOKEN}`
};
```

### Basic Request Format

```javascript
const request = {
  jsonrpc: '2.0',
  method: 'tools/call',
  id: 1,
  params: {
    name: 'tool_name',
    arguments: { /* tool arguments */ }
  }
};
```

---

## Vanilla JavaScript

### Simple Fetch Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Meta Ads MCP Client</title>
</head>
<body>
  <h1>Meta Ads Dashboard</h1>
  <button id="getAccounts">Get Ad Accounts</button>
  <pre id="results"></pre>

  <script>
    const MCP_URL = 'https://meta-ads-mcp-rike.onrender.com/mcp';
    const ACCESS_TOKEN = 'YOUR_META_ACCESS_TOKEN';

    // Helper function to call MCP tools
    async function callMCPTool(toolName, args = {}) {
      const response = await fetch(MCP_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json, text/event-stream',
          'Authorization': `Bearer ${ACCESS_TOKEN}`
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'tools/call',
          id: Date.now(),
          params: {
            name: toolName,
            arguments: args
          }
        })
      });

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error.message);
      }
      
      return data.result;
    }

    // Get ad accounts
    document.getElementById('getAccounts').addEventListener('click', async () => {
      try {
        const result = await callMCPTool('get_ad_accounts', { limit: 10 });
        document.getElementById('results').textContent = JSON.stringify(result, null, 2);
      } catch (error) {
        document.getElementById('results').textContent = `Error: ${error.message}`;
      }
    });
  </script>
</body>
</html>
```

### Complete JavaScript Client Class

```javascript
class MetaAdsMCPClient {
  constructor(serverUrl, accessToken) {
    this.serverUrl = serverUrl;
    this.accessToken = accessToken;
    this.requestId = 1;
  }

  async callTool(toolName, args = {}) {
    const response = await fetch(this.serverUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': `Bearer ${this.accessToken}`
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'tools/call',
        id: this.requestId++,
        params: {
          name: toolName,
          arguments: args
        }
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    
    if (data.error) {
      throw new Error(data.error.message);
    }
    
    return data.result;
  }

  async listTools() {
    const response = await fetch(this.serverUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': `Bearer ${this.accessToken}`
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'tools/list',
        id: this.requestId++
      })
    });

    const data = await response.json();
    return data.result.tools;
  }

  // High-level methods
  async getAdAccounts(limit = 10) {
    return this.callTool('get_ad_accounts', { user_id: 'me', limit });
  }

  async getCampaigns(accountId, limit = 10) {
    return this.callTool('get_campaigns', { account_id: accountId, limit });
  }

  async getInsights(objectId, timeRange = 'last_30d', level = 'campaign') {
    return this.callTool('get_insights', {
      object_id: objectId,
      time_range: timeRange,
      level
    });
  }

  async searchInterests(query, limit = 25) {
    return this.callTool('search_interests', { query, limit });
  }
}

// Usage
const client = new MetaAdsMCPClient(
  'https://meta-ads-mcp-rike.onrender.com/mcp',
  'YOUR_ACCESS_TOKEN'
);

// Get accounts
const accounts = await client.getAdAccounts();
console.log(accounts);
```

---

## React Integration

### React Hook

```javascript
// hooks/useMetaAdsMCP.js
import { useState, useCallback } from 'react';

const MCP_URL = 'https://meta-ads-mcp-rike.onrender.com/mcp';

export function useMetaAdsMCP(accessToken) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const callTool = useCallback(async (toolName, args = {}) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(MCP_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json, text/event-stream',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'tools/call',
          id: Date.now(),
          params: {
            name: toolName,
            arguments: args
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error.message);
      }
      
      return data.result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  return { callTool, loading, error };
}
```

### React Component Example

```javascript
// components/AdAccountsList.jsx
import React, { useState, useEffect } from 'react';
import { useMetaAdsMCP } from '../hooks/useMetaAdsMCP';

export function AdAccountsList() {
  const [accounts, setAccounts] = useState([]);
  const accessToken = process.env.REACT_APP_META_ACCESS_TOKEN;
  const { callTool, loading, error } = useMetaAdsMCP(accessToken);

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    try {
      const result = await callTool('get_ad_accounts', { limit: 10 });
      const parsed = JSON.parse(result.result);
      setAccounts(parsed.data || []);
    } catch (err) {
      console.error('Failed to load accounts:', err);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Ad Accounts</h2>
      <ul>
        {accounts.map(account => (
          <li key={account.id}>
            {account.name} ({account.id})
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### Complete React Dashboard

```javascript
// App.jsx
import React, { useState, useEffect } from 'react';
import { useMetaAdsMCP } from './hooks/useMetaAdsMCP';

function App() {
  const [accounts, setAccounts] = useState([]);
  const [selectedAccount, setSelectedAccount] = useState(null);
  const [campaigns, setCampaigns] = useState([]);
  const [insights, setInsights] = useState(null);
  
  const accessToken = process.env.REACT_APP_META_ACCESS_TOKEN;
  const { callTool, loading, error } = useMetaAdsMCP(accessToken);

  // Load accounts on mount
  useEffect(() => {
    loadAccounts();
  }, []);

  // Load campaigns when account is selected
  useEffect(() => {
    if (selectedAccount) {
      loadCampaigns(selectedAccount);
    }
  }, [selectedAccount]);

  const loadAccounts = async () => {
    const result = await callTool('get_ad_accounts', { limit: 10 });
    const parsed = JSON.parse(result.result);
    setAccounts(parsed.data || []);
  };

  const loadCampaigns = async (accountId) => {
    const result = await callTool('get_campaigns', { 
      account_id: accountId, 
      limit: 10 
    });
    const parsed = JSON.parse(result.result);
    setCampaigns(parsed.data || []);
  };

  const loadInsights = async (objectId) => {
    const result = await callTool('get_insights', {
      object_id: objectId,
      time_range: 'last_30d',
      level: 'campaign'
    });
    const parsed = JSON.parse(result.result);
    setInsights(parsed);
  };

  return (
    <div className="App">
      <h1>Meta Ads Dashboard</h1>
      
      {loading && <div>Loading...</div>}
      {error && <div>Error: {error}</div>}

      <section>
        <h2>Ad Accounts</h2>
        <select onChange={(e) => setSelectedAccount(e.target.value)}>
          <option value="">Select an account...</option>
          {accounts.map(account => (
            <option key={account.id} value={account.id}>
              {account.name}
            </option>
          ))}
        </select>
      </section>

      {selectedAccount && (
        <section>
          <h2>Campaigns</h2>
          <ul>
            {campaigns.map(campaign => (
              <li key={campaign.id}>
                {campaign.name}
                <button onClick={() => loadInsights(campaign.id)}>
                  View Insights
                </button>
              </li>
            ))}
          </ul>
        </section>
      )}

      {insights && (
        <section>
          <h2>Campaign Insights</h2>
          <pre>{JSON.stringify(insights, null, 2)}</pre>
        </section>
      )}
    </div>
  );
}

export default App;
```

---

## TypeScript Client

```typescript
// lib/metaAdsMCP.ts
interface MCPRequest {
  jsonrpc: string;
  method: string;
  id: number;
  params?: {
    name?: string;
    arguments?: Record<string, any>;
  };
}

interface MCPResponse {
  jsonrpc: string;
  id: number;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

export class MetaAdsMCPClient {
  private serverUrl: string;
  private accessToken: string;
  private requestId: number = 1;

  constructor(serverUrl: string, accessToken: string) {
    this.serverUrl = serverUrl;
    this.accessToken = accessToken;
  }

  private async request(method: string, params?: any): Promise<MCPResponse> {
    const request: MCPRequest = {
      jsonrpc: '2.0',
      method,
      id: this.requestId++,
      params
    };

    const response = await fetch(this.serverUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': `Bearer ${this.accessToken}`
      },
      body: JSON.stringify(request)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  async callTool(toolName: string, args: Record<string, any> = {}): Promise<any> {
    const response = await this.request('tools/call', {
      name: toolName,
      arguments: args
    });

    if (response.error) {
      throw new Error(response.error.message);
    }

    return response.result;
  }

  async listTools(): Promise<any[]> {
    const response = await this.request('tools/list');
    return response.result?.tools || [];
  }

  // High-level typed methods
  async getAdAccounts(limit: number = 10): Promise<any> {
    return this.callTool('get_ad_accounts', { user_id: 'me', limit });
  }

  async getCampaigns(accountId: string, limit: number = 10): Promise<any> {
    return this.callTool('get_campaigns', { account_id: accountId, limit });
  }

  async getInsights(
    objectId: string,
    timeRange: string = 'last_30d',
    level: string = 'campaign'
  ): Promise<any> {
    return this.callTool('get_insights', {
      object_id: objectId,
      time_range: timeRange,
      level
    });
  }

  async searchInterests(query: string, limit: number = 25): Promise<any> {
    return this.callTool('search_interests', { query, limit });
  }

  async createCampaign(params: {
    account_id: string;
    name: string;
    objective: string;
    status?: string;
    daily_budget?: number;
  }): Promise<any> {
    return this.callTool('create_campaign', params);
  }
}

// Usage
const client = new MetaAdsMCPClient(
  'https://meta-ads-mcp-rike.onrender.com/mcp',
  process.env.NEXT_PUBLIC_META_ACCESS_TOKEN!
);

export default client;
```

---

## Next.js Integration

### API Route (Server-Side)

```typescript
// pages/api/meta-ads/[...tool].ts
import type { NextApiRequest, NextApiResponse } from 'next';

const MCP_URL = 'https://meta-ads-mcp-rike.onrender.com/mcp';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { tool } = req.query;
  const args = req.body;
  const accessToken = req.headers.authorization?.replace('Bearer ', '');

  if (!accessToken) {
    return res.status(401).json({ error: 'No access token provided' });
  }

  try {
    const response = await fetch(MCP_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': `Bearer ${accessToken}`
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'tools/call',
        id: Date.now(),
        params: {
          name: tool,
          arguments: args
        }
      })
    });

    const data = await response.json();
    
    if (data.error) {
      return res.status(400).json(data.error);
    }
    
    res.status(200).json(data.result);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
}
```

### Client-Side Hook

```typescript
// hooks/useMetaAds.ts
import { useState, useCallback } from 'react';

export function useMetaAds() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const callTool = useCallback(async (toolName: string, args: any = {}) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/meta-ads/${toolName}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_META_ACCESS_TOKEN}`
        },
        body: JSON.stringify(args)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();
    } catch (err: any) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { callTool, loading, error };
}
```

### Next.js Page Component

```typescript
// pages/dashboard.tsx
import { useState, useEffect } from 'react';
import { useMetaAds } from '../hooks/useMetaAds';

export default function Dashboard() {
  const [accounts, setAccounts] = useState([]);
  const { callTool, loading, error } = useMetaAds();

  useEffect(() => {
    loadAccounts();
  }, []);

  const loadAccounts = async () => {
    const result = await callTool('get_ad_accounts', { limit: 10 });
    const parsed = JSON.parse(result.result);
    setAccounts(parsed.data || []);
  };

  return (
    <div>
      <h1>Meta Ads Dashboard</h1>
      {loading && <p>Loading...</p>}
      {error && <p>Error: {error}</p>}
      <ul>
        {accounts.map((account: any) => (
          <li key={account.id}>{account.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

---

## Vue.js Integration

### Vue Composable

```javascript
// composables/useMetaAdsMCP.js
import { ref } from 'vue';

const MCP_URL = 'https://meta-ads-mcp-rike.onrender.com/mcp';

export function useMetaAdsMCP(accessToken) {
  const loading = ref(false);
  const error = ref(null);

  const callTool = async (toolName, args = {}) => {
    loading.value = true;
    error.value = null;

    try {
      const response = await fetch(MCP_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json, text/event-stream',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({
          jsonrpc: '2.0',
          method: 'tools/call',
          id: Date.now(),
          params: {
            name: toolName,
            arguments: args
          }
        })
      });

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error.message);
      }
      
      return data.result;
    } catch (err) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return { callTool, loading, error };
}
```

### Vue Component

```vue
<!-- components/AdAccountsList.vue -->
<template>
  <div>
    <h2>Ad Accounts</h2>
    <div v-if="loading">Loading...</div>
    <div v-if="error">Error: {{ error }}</div>
    <ul v-if="accounts.length">
      <li v-for="account in accounts" :key="account.id">
        {{ account.name }} ({{ account.id }})
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useMetaAdsMCP } from '../composables/useMetaAdsMCP';

const accounts = ref([]);
const accessToken = import.meta.env.VITE_META_ACCESS_TOKEN;
const { callTool, loading, error } = useMetaAdsMCP(accessToken);

onMounted(async () => {
  const result = await callTool('get_ad_accounts', { limit: 10 });
  const parsed = JSON.parse(result.result);
  accounts.value = parsed.data || [];
});
</script>
```

---

## Authentication

### Environment Variables

Create a `.env` file:

```bash
# For React
REACT_APP_META_ACCESS_TOKEN=your_token_here

# For Next.js
NEXT_PUBLIC_META_ACCESS_TOKEN=your_token_here

# For Vue
VITE_META_ACCESS_TOKEN=your_token_here
```

### Security Best Practices

1. **Never expose tokens in frontend code**
2. **Use API routes** to proxy requests (Next.js example above)
3. **Store tokens in environment variables**
4. **Rotate tokens regularly**

### Secure Backend Proxy (Recommended)

```javascript
// backend/routes/meta-ads.js
const express = require('express');
const router = express.Router();

const MCP_URL = 'https://meta-ads-mcp-rike.onrender.com/mcp';
const ACCESS_TOKEN = process.env.META_ACCESS_TOKEN; // Server-side only!

router.post('/call-tool', async (req, res) => {
  const { toolName, args } = req.body;

  try {
    const response = await fetch(MCP_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Authorization': `Bearer ${ACCESS_TOKEN}`
      },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'tools/call',
        id: Date.now(),
        params: {
          name: toolName,
          arguments: args
        }
      })
    });

    const data = await response.json();
    res.json(data);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
```

---

## Error Handling

### Comprehensive Error Handler

```javascript
class MCPError extends Error {
  constructor(message, code, data) {
    super(message);
    this.name = 'MCPError';
    this.code = code;
    this.data = data;
  }
}

async function safeMCPCall(client, toolName, args) {
  try {
    return await client.callTool(toolName, args);
  } catch (error) {
    if (error instanceof MCPError) {
      // Handle MCP-specific errors
      switch (error.code) {
        case -32600:
          console.error('Invalid request:', error.message);
          break;
        case -32601:
          console.error('Method not found:', error.message);
          break;
        case -32602:
          console.error('Invalid params:', error.message);
          break;
        default:
          console.error('MCP error:', error.message);
      }
    } else {
      // Handle network or other errors
      console.error('Request failed:', error.message);
    }
    throw error;
  }
}
```

---

## Example Use Cases

### 1. Real-time Campaign Dashboard

```javascript
async function buildCampaignDashboard(accountId) {
  const client = new MetaAdsMCPClient(MCP_URL, ACCESS_TOKEN);
  
  // Get campaigns
  const campaigns = await client.getCampaigns(accountId, 50);
  
  // Get insights for each campaign
  const insights = await Promise.all(
    campaigns.data.map(campaign =>
      client.getInsights(campaign.id, 'last_7d', 'campaign')
    )
  );
  
  return {
    campaigns: campaigns.data,
    insights
  };
}
```

### 2. Interest Targeting Tool

```javascript
async function buildTargetingTool(searchQuery) {
  const client = new MetaAdsMCPClient(MCP_URL, ACCESS_TOKEN);
  
  // Search interests
  const interests = await client.searchInterests(searchQuery, 50);
  
  // Get audience estimate
  const estimate = await client.callTool('estimate_audience_size', {
    account_id: 'act_123456789',
    targeting: {
      geo_locations: { countries: ['US'] },
      age_min: 25,
      age_max: 65,
      flexible_spec: [
        { interests: interests.data.map(i => ({ id: i.id })) }
      ]
    }
  });
  
  return { interests, estimate };
}
```

### 3. Campaign Performance Report

```javascript
async function generatePerformanceReport(accountId, timeRange = 'last_30d') {
  const client = new MetaAdsMCPClient(MCP_URL, ACCESS_TOKEN);
  
  const insights = await client.getInsights(accountId, timeRange, 'campaign');
  const parsed = JSON.parse(insights.result);
  
  const report = parsed.data.map(campaign => ({
    name: campaign.campaign_name,
    spend: parseFloat(campaign.spend || 0),
    impressions: parseInt(campaign.impressions || 0),
    clicks: parseInt(campaign.clicks || 0),
    ctr: parseFloat(campaign.ctr || 0)
  }));
  
  return report.sort((a, b) => b.spend - a.spend);
}
```

---

## Testing Your Connection

```javascript
// test-connection.js
async function testConnection() {
  const client = new MetaAdsMCPClient(
    'https://meta-ads-mcp-rike.onrender.com/mcp',
    'YOUR_ACCESS_TOKEN'
  );

  console.log('Testing MCP connection...');
  
  try {
    // Test 1: List tools
    console.log('1. Listing available tools...');
    const tools = await client.listTools();
    console.log(`✅ Found ${tools.length} tools`);
    
    // Test 2: Get ad accounts
    console.log('2. Getting ad accounts...');
    const accounts = await client.getAdAccounts(5);
    const parsed = JSON.parse(accounts.result);
    console.log(`✅ Found ${parsed.data.length} accounts`);
    
    console.log('✅ All tests passed!');
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  }
}

testConnection();
```

---

## Quick Reference

### Common Tool Calls

```javascript
// Get ad accounts
await client.callTool('get_ad_accounts', { limit: 10 });

// Get campaigns
await client.callTool('get_campaigns', { 
  account_id: 'act_123', 
  limit: 10 
});

// Get insights
await client.callTool('get_insights', {
  object_id: 'act_123',
  time_range: 'last_30d',
  level: 'campaign'
});

// Search interests
await client.callTool('search_interests', { 
  query: 'technology', 
  limit: 25 
});

// Create campaign
await client.callTool('create_campaign', {
  account_id: 'act_123',
  name: 'My Campaign',
  objective: 'OUTCOME_TRAFFIC',
  status: 'PAUSED'
});
```

---

## Support

- **Server URL:** `https://meta-ads-mcp-rike.onrender.com/mcp`
- **Documentation:** Check `/Users/p.camprubi/Desktop/meta-ads-mcp-main/examples/`
- **GitHub:** [https://github.com/pablo-camprubi/mcpmeta](https://github.com/pablo-camprubi/mcpmeta)

---

**Ready to integrate!** 🚀 Use these examples to connect your frontend to your deployed Meta Ads MCP server.


