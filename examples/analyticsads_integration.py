"""
Example: Integrating Meta Ads MCP Server with AnalyticsAds Repo

This example shows how to call the deployed MCP server from your analyticsads repo.
After deploying to Railway/Render/Fly.io, use this code to interact with your Meta Ads data.
"""

import os
import requests
from typing import Dict, Any, Optional, List
import json


class MetaAdsMCPClient:
    """
    Client for interacting with deployed Meta Ads MCP server
    
    Usage:
        # Initialize with your deployment URL
        client = MetaAdsMCPClient(
            base_url="https://your-app.up.railway.app",  # or .onrender.com, .fly.dev
            token=os.environ.get("PIPEBOARD_API_TOKEN")
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
    """
    
    def __init__(self, base_url: str, token: str):
        """
        Initialize the MCP client
        
        Args:
            base_url: Base URL of your deployed MCP server (without /mcp)
            token: Your Pipeboard API token from pipeboard.co/api-tokens
        """
        self.base_url = base_url.rstrip('/')
        self.endpoint = f"{self.base_url}/mcp"
        self.token = token
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        }
    
    def _call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Internal method to call an MCP tool
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Response from the MCP server
        """
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 1,
            "params": {
                "name": tool_name
            }
        }
        
        if arguments:
            payload["params"]["arguments"] = arguments
        
        try:
            response = requests.post(
                self.endpoint, 
                headers=self.headers, 
                json=payload,
                timeout=60  # 60 second timeout
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Check for JSON-RPC errors
            if "error" in result:
                raise Exception(f"MCP Error: {result['error']}")
            
            return result.get("result", {})
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"HTTP Request failed: {e}")
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 1
        }
        
        response = requests.post(self.endpoint, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json().get("result", {}).get("tools", [])
    
    # High-level methods for common operations
    
    def get_ad_accounts(self, limit: int = 200) -> Dict[str, Any]:
        """Get ad accounts accessible by the user"""
        return self._call_tool("get_ad_accounts", {
            "user_id": "me",
            "limit": limit
        })
    
    def get_account_info(self, account_id: str) -> Dict[str, Any]:
        """Get detailed info about a specific ad account"""
        return self._call_tool("get_account_info", {
            "account_id": account_id
        })
    
    def get_campaigns(
        self, 
        account_id: str, 
        limit: int = 10,
        status_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get campaigns for an account"""
        args = {
            "account_id": account_id,
            "limit": limit
        }
        if status_filter:
            args["status_filter"] = status_filter
        
        return self._call_tool("get_campaigns", args)
    
    def get_insights(
        self,
        object_id: str,
        time_range: str = "last_30d",
        level: str = "campaign",
        breakdown: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get performance insights for campaigns, adsets, or ads
        
        Args:
            object_id: ID of campaign, adset, ad, or account
            time_range: Time range (e.g., 'last_30d', 'last_7d', 'maximum')
            level: Aggregation level ('ad', 'adset', 'campaign', 'account')
            breakdown: Optional breakdown dimension (e.g., 'age', 'gender', 'country')
        """
        args = {
            "object_id": object_id,
            "time_range": time_range,
            "level": level
        }
        if breakdown:
            args["breakdown"] = breakdown
        
        return self._call_tool("get_insights", args)
    
    def search_interests(self, query: str, limit: int = 25) -> Dict[str, Any]:
        """Search for interest targeting options"""
        return self._call_tool("search_interests", {
            "query": query,
            "limit": limit
        })
    
    def create_campaign(
        self,
        account_id: str,
        name: str,
        objective: str,
        status: str = "PAUSED",
        daily_budget: Optional[int] = None,
        lifetime_budget: Optional[int] = None,
        bid_strategy: str = "LOWEST_COST_WITHOUT_CAP"
    ) -> Dict[str, Any]:
        """
        Create a new campaign
        
        Args:
            account_id: Meta Ads account ID (format: act_XXXXXXXXX)
            name: Campaign name
            objective: Campaign objective (use OUTCOME_* values like OUTCOME_TRAFFIC)
            status: Initial status (default: PAUSED)
            daily_budget: Daily budget in cents (e.g., 10000 = $100)
            lifetime_budget: Lifetime budget in cents
            bid_strategy: Bid strategy
        """
        args = {
            "account_id": account_id,
            "name": name,
            "objective": objective,
            "status": status,
            "bid_strategy": bid_strategy
        }
        
        if daily_budget:
            args["daily_budget"] = daily_budget
        if lifetime_budget:
            args["lifetime_budget"] = lifetime_budget
        
        return self._call_tool("create_campaign", args)


# Example usage
def main():
    """Example usage of the Meta Ads MCP Client"""
    
    # Initialize client with your deployment URL and token
    client = MetaAdsMCPClient(
        base_url=os.environ.get("META_ADS_MCP_URL", "https://your-app.up.railway.app"),
        token=os.environ.get("PIPEBOARD_API_TOKEN")
    )
    
    print("🔍 Testing Meta Ads MCP Connection...\n")
    
    # 1. List available tools
    print("1. Available Tools:")
    tools = client.list_tools()
    print(f"   Found {len(tools)} tools")
    print(f"   Tools: {[t.get('name', 'unknown') for t in tools[:5]]}...\n")
    
    # 2. Get ad accounts
    print("2. Getting Ad Accounts:")
    accounts = client.get_ad_accounts(limit=5)
    print(json.dumps(accounts, indent=2))
    print()
    
    # 3. Get campaigns for first account
    if accounts and len(accounts.get('data', [])) > 0:
        account_id = accounts['data'][0]['id']
        print(f"3. Getting Campaigns for account {account_id}:")
        campaigns = client.get_campaigns(account_id, limit=5)
        print(json.dumps(campaigns, indent=2))
        print()
        
        # 4. Get insights for first campaign
        if campaigns and len(campaigns.get('data', [])) > 0:
            campaign_id = campaigns['data'][0]['id']
            print(f"4. Getting Insights for campaign {campaign_id}:")
            insights = client.get_insights(
                object_id=account_id,
                time_range="last_30d",
                level="campaign"
            )
            print(json.dumps(insights, indent=2))
    
    print("\n✅ Integration test complete!")


if __name__ == "__main__":
    main()

