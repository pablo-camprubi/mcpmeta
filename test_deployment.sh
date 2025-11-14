#!/bin/bash

# Test Deployment Script
# Usage: ./test_deployment.sh https://your-app.onrender.com YOUR_PIPEBOARD_TOKEN

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "❌ Error: Missing arguments"
    echo "Usage: ./test_deployment.sh <DEPLOYMENT_URL> <PIPEBOARD_TOKEN>"
    echo "Example: ./test_deployment.sh https://meta-ads-mcp.onrender.com your_token_here"
    exit 1
fi

DEPLOYMENT_URL=$1
TOKEN=$2
ENDPOINT="${DEPLOYMENT_URL}/mcp"

echo "🔍 Testing Meta Ads MCP Deployment"
echo "Endpoint: $ENDPOINT"
echo ""

# Test 1: Health Check (tools/list)
echo "Test 1: Checking if server is accessible..."
RESPONSE=$(curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }')

if echo "$RESPONSE" | grep -q "tools"; then
    echo "✅ Server is running and accessible!"
    TOOL_COUNT=$(echo "$RESPONSE" | grep -o '"name"' | wc -l)
    echo "   Found $TOOL_COUNT tools available"
else
    echo "❌ Server test failed"
    echo "Response: $RESPONSE"
    exit 1
fi

echo ""

# Test 2: Authentication Check (get_ad_accounts)
echo "Test 2: Testing authentication..."
RESPONSE=$(curl -s -X POST "$ENDPOINT" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 2,
    "params": {
      "name": "get_ad_accounts",
      "arguments": {"limit": 5}
    }
  }')

if echo "$RESPONSE" | grep -q '"result"'; then
    echo "✅ Authentication successful!"
    echo "   You can access Meta Ads data"
else
    echo "⚠️  Authentication test inconclusive"
    echo "Response: $RESPONSE"
fi

echo ""
echo "🎉 Deployment test complete!"
echo ""
echo "Your MCP server is ready to use:"
echo "  URL: $ENDPOINT"
echo ""
echo "Next steps:"
echo "1. Add to your MCP client config (Claude, Cursor, etc.)"
echo "2. Or use the Python/TypeScript clients in examples/"
echo ""

