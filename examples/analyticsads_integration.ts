/**
 * Example: Integrating Meta Ads MCP Server with AnalyticsAds Repo (TypeScript)
 * 
 * This example shows how to call the deployed MCP server from your analyticsads repo.
 * After deploying to Railway/Render/Fly.io, use this code to interact with your Meta Ads data.
 */

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

interface ToolListResponse {
  tools: Array<{
    name: string;
    description?: string;
    inputSchema?: any;
  }>;
}

interface GetAccountsArgs {
  user_id?: string;
  limit?: number;
}

interface GetCampaignsArgs {
  account_id: string;
  limit?: number;
  status_filter?: string;
}

interface GetInsightsArgs {
  object_id: string;
  time_range?: string;
  level?: string;
  breakdown?: string;
}

interface CreateCampaignArgs {
  account_id: string;
  name: string;
  objective: string;
  status?: string;
  daily_budget?: number;
  lifetime_budget?: number;
  bid_strategy?: string;
}

/**
 * Client for interacting with deployed Meta Ads MCP server
 * 
 * Usage:
 * ```typescript
 * const client = new MetaAdsMCPClient(
 *   "https://your-app.up.railway.app",
 *   process.env.PIPEBOARD_API_TOKEN!
 * );
 * 
 * const accounts = await client.getAdAccounts({ limit: 10 });
 * console.log(accounts);
 * ```
 */
export class MetaAdsMCPClient {
  private endpoint: string;
  private headers: Record<string, string>;

  /**
   * Initialize the MCP client
   * 
   * @param baseUrl - Base URL of your deployed MCP server (without /mcp)
   * @param token - Your Pipeboard API token from pipeboard.co/api-tokens
   */
  constructor(baseUrl: string, token: string) {
    this.endpoint = `${baseUrl.replace(/\/$/, '')}/mcp`;
    this.headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  }

  /**
   * Internal method to call an MCP tool
   */
  private async callTool(toolName: string, args?: any): Promise<any> {
    const payload = {
      jsonrpc: '2.0',
      method: 'tools/call',
      id: 1,
      params: {
        name: toolName,
        ...(args && { arguments: args })
      }
    };

    try {
      const response = await fetch(this.endpoint, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result: MCPResponse = await response.json();

      if (result.error) {
        throw new Error(`MCP Error: ${result.error.message}`);
      }

      return result.result;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Request failed: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * List all available tools
   */
  async listTools(): Promise<ToolListResponse> {
    const payload = {
      jsonrpc: '2.0',
      method: 'tools/list',
      id: 1
    };

    const response = await fetch(this.endpoint, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify(payload)
    });

    const result: MCPResponse = await response.json();
    return result.result as ToolListResponse;
  }

  // High-level methods for common operations

  /**
   * Get ad accounts accessible by the user
   */
  async getAdAccounts(args?: GetAccountsArgs): Promise<any> {
    return this.callTool('get_ad_accounts', {
      user_id: 'me',
      limit: 200,
      ...args
    });
  }

  /**
   * Get detailed info about a specific ad account
   */
  async getAccountInfo(accountId: string): Promise<any> {
    return this.callTool('get_account_info', {
      account_id: accountId
    });
  }

  /**
   * Get campaigns for an account
   */
  async getCampaigns(args: GetCampaignsArgs): Promise<any> {
    return this.callTool('get_campaigns', args);
  }

  /**
   * Get performance insights for campaigns, adsets, or ads
   */
  async getInsights(args: GetInsightsArgs): Promise<any> {
    return this.callTool('get_insights', {
      time_range: 'last_30d',
      level: 'campaign',
      ...args
    });
  }

  /**
   * Search for interest targeting options
   */
  async searchInterests(query: string, limit: number = 25): Promise<any> {
    return this.callTool('search_interests', {
      query,
      limit
    });
  }

  /**
   * Create a new campaign
   */
  async createCampaign(args: CreateCampaignArgs): Promise<any> {
    return this.callTool('create_campaign', {
      status: 'PAUSED',
      bid_strategy: 'LOWEST_COST_WITHOUT_CAP',
      ...args
    });
  }

  /**
   * Update an existing campaign
   */
  async updateCampaign(
    campaignId: string,
    updates: { status?: string; name?: string; [key: string]: any }
  ): Promise<any> {
    return this.callTool('update_campaign', {
      campaign_id: campaignId,
      ...updates
    });
  }
}

// Example usage
async function main() {
  // Initialize client with your deployment URL and token
  const client = new MetaAdsMCPClient(
    process.env.META_ADS_MCP_URL || 'https://your-app.up.railway.app',
    process.env.PIPEBOARD_API_TOKEN!
  );

  console.log('🔍 Testing Meta Ads MCP Connection...\n');

  try {
    // 1. List available tools
    console.log('1. Available Tools:');
    const { tools } = await client.listTools();
    console.log(`   Found ${tools.length} tools`);
    console.log(`   Tools: ${tools.slice(0, 5).map(t => t.name).join(', ')}...\n`);

    // 2. Get ad accounts
    console.log('2. Getting Ad Accounts:');
    const accounts = await client.getAdAccounts({ limit: 5 });
    console.log(JSON.stringify(accounts, null, 2));
    console.log();

    // 3. Get campaigns for first account
    if (accounts?.data?.length > 0) {
      const accountId = accounts.data[0].id;
      console.log(`3. Getting Campaigns for account ${accountId}:`);
      const campaigns = await client.getCampaigns({
        account_id: accountId,
        limit: 5
      });
      console.log(JSON.stringify(campaigns, null, 2));
      console.log();

      // 4. Get insights for first campaign
      if (campaigns?.data?.length > 0) {
        console.log(`4. Getting Insights for account ${accountId}:`);
        const insights = await client.getInsights({
          object_id: accountId,
          time_range: 'last_30d',
          level: 'campaign'
        });
        console.log(JSON.stringify(insights, null, 2));
      }
    }

    console.log('\n✅ Integration test complete!');
  } catch (error) {
    console.error('❌ Error:', error);
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main();
}

