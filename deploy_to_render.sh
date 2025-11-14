#!/bin/bash

# Interactive Render Deployment Script
# This script will guide you through deploying to Render

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Meta Ads MCP - Render Deployment Assistant"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Check if we're in the right directory
if [ ! -f "render.yaml" ]; then
    echo -e "${RED}❌ Error: render.yaml not found${NC}"
    echo "Please run this script from the meta-ads-mcp-main directory"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found render.yaml"
echo ""

# Step 2: Check git status
echo -e "${BLUE}📋 Step 1: Checking Git Status${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d ".git" ]; then
    echo -e "${YELLOW}⚠ Git not initialized. Initializing...${NC}"
    git init
    git branch -m main
    git add .
    git commit -m "Initial commit with deployment configs"
    echo -e "${GREEN}✓${NC} Git initialized and files committed"
else
    echo -e "${GREEN}✓${NC} Git already initialized"
    
    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        echo -e "${YELLOW}⚠ Uncommitted changes found. Committing...${NC}"
        git add .
        git commit -m "Update deployment configs"
        echo -e "${GREEN}✓${NC} Changes committed"
    else
        echo -e "${GREEN}✓${NC} No uncommitted changes"
    fi
fi

echo ""

# Step 3: GitHub setup
echo -e "${BLUE}📋 Step 2: GitHub Repository Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To deploy to Render, your code needs to be on GitHub."
echo ""

# Check if remote already exists
if git remote get-url origin &>/dev/null; then
    REMOTE_URL=$(git remote get-url origin)
    echo -e "${GREEN}✓${NC} GitHub remote already configured:"
    echo "  $REMOTE_URL"
    echo ""
    read -p "Push to this repository? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Pushing to GitHub..."
        if git push -u origin main 2>/dev/null; then
            echo -e "${GREEN}✓${NC} Successfully pushed to GitHub"
        else
            echo -e "${YELLOW}⚠${NC} Trying force push (this is safe for new repos)..."
            git push -u origin main --force
            echo -e "${GREEN}✓${NC} Successfully pushed to GitHub"
        fi
    fi
else
    echo "You need to create a GitHub repository first."
    echo ""
    echo "📝 Please follow these steps:"
    echo ""
    echo "1. Go to: https://github.com/new"
    echo "2. Create a new repository named: meta-ads-mcp"
    echo "3. Do NOT initialize with README (we have code already)"
    echo "4. Copy the repository URL"
    echo ""
    read -p "Press Enter when you've created the repository..."
    echo ""
    read -p "Enter your GitHub repository URL (e.g., https://github.com/username/meta-ads-mcp.git): " GITHUB_URL
    
    if [ -z "$GITHUB_URL" ]; then
        echo -e "${RED}❌ Error: No URL provided${NC}"
        exit 1
    fi
    
    echo "Adding remote and pushing..."
    git remote add origin "$GITHUB_URL"
    
    if git push -u origin main 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Successfully pushed to GitHub"
    else
        echo -e "${YELLOW}⚠${NC} Trying force push (this is safe for new repos)..."
        git push -u origin main --force
        echo -e "${GREEN}✓${NC} Successfully pushed to GitHub"
    fi
fi

echo ""

# Step 4: Meta Developer App Credentials
echo -e "${BLUE}📋 Step 3: Meta Developer App Setup${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "You need Meta Developer App credentials for direct authentication."
echo ""
echo "📝 Follow these steps:"
echo "   1. Read SETUP_META_APP.md for detailed instructions"
echo "   2. Go to: https://developers.facebook.com/apps"
echo "   3. Create a new app (Business type)"
echo "   4. Add Marketing API product"
echo "   5. Get your App ID and App Secret from Settings → Basic"
echo ""
read -p "Press Enter when you have your App ID and Secret..."
echo ""
read -p "Enter your META_APP_ID: " META_APP_ID
echo ""
read -p "Enter your META_APP_SECRET: " -s META_APP_SECRET
echo ""

if [ -z "$META_APP_ID" ] || [ -z "$META_APP_SECRET" ]; then
    echo -e "${YELLOW}⚠${NC} Credentials not provided. You'll need to add them in Render dashboard later."
else
    echo -e "${GREEN}✓${NC} Credentials received"
    echo "   App ID: $META_APP_ID"
    echo "   Secret: ${META_APP_SECRET:0:8}... (hidden)"
fi

echo ""
echo "Optional: If you already have a Meta Access Token:"
read -p "Enter your META_ACCESS_TOKEN (or press Enter to skip): " -s META_ACCESS_TOKEN
echo ""
if [ ! -z "$META_ACCESS_TOKEN" ]; then
    echo -e "${GREEN}✓${NC} Access token received (${#META_ACCESS_TOKEN} characters)"
fi

echo ""

# Step 5: Render Deployment
echo -e "${BLUE}📋 Step 4: Deploy to Render${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Now let's deploy to Render!"
echo ""
echo "📝 Please follow these steps:"
echo ""
echo "1. Go to: https://dashboard.render.com/blueprints"
echo "   (Sign up for free if you haven't already)"
echo ""
echo "2. Click 'New Blueprint Instance'"
echo ""
echo "3. Connect your GitHub account if not connected"
echo ""
echo "4. Select your 'meta-ads-mcp' repository"
echo ""
echo "5. Render will detect render.yaml automatically!"
echo ""
echo "6. When prompted for environment variables:"
echo "   - PIPEBOARD_API_TOKEN: [paste your token]"
echo ""
echo "7. Click 'Apply' to deploy"
echo ""
echo "8. Wait 2-3 minutes for deployment to complete"
echo ""
read -p "Press Enter once deployment is complete..."
echo ""

# Step 6: Get deployment URL
echo -e "${BLUE}📋 Step 5: Test Your Deployment${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
read -p "Enter your Render deployment URL (e.g., https://meta-ads-mcp.onrender.com): " RENDER_URL

if [ ! -z "$RENDER_URL" ] && [ ! -z "$META_ACCESS_TOKEN" ]; then
    echo ""
    echo "Testing deployment..."
    ENDPOINT="${RENDER_URL}/mcp"
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$ENDPOINT" \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -H "Authorization: Bearer $META_ACCESS_TOKEN" \
      -d '{"jsonrpc":"2.0","method":"tools/list","id":1}')
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓${NC} Server is responding!"
        
        if echo "$BODY" | grep -q "tools"; then
            TOOL_COUNT=$(echo "$BODY" | grep -o '"name"' | wc -l | tr -d ' ')
            echo -e "${GREEN}✓${NC} Found $TOOL_COUNT MCP tools available"
            echo ""
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
            echo -e "${GREEN}🎉 DEPLOYMENT SUCCESSFUL!${NC}"
            echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        else
            echo -e "${YELLOW}⚠${NC} Server responded but tools not found"
            echo "Response: $BODY"
        fi
    else
        echo -e "${RED}❌ Server test failed (HTTP $HTTP_CODE)${NC}"
        echo "Response: $BODY"
        echo ""
        echo "Check Render dashboard logs for errors"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Deployment Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your MCP Server Details:"
echo "  URL: ${RENDER_URL}/mcp"
echo ""
echo "Next Steps:"
echo ""
echo "1️⃣  Add to Claude Desktop:"
echo "   File: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "   {\"
echo "     \"mcpServers\": {"
echo "       \"meta-ads\": {"
echo "         \"url\": \"${RENDER_URL}/mcp\","
echo "         \"headers\": {"
echo "           \"Authorization\": \"Bearer YOUR_META_ACCESS_TOKEN\""
echo "         }"
echo "       }"
echo "     }"
echo "   }"
echo ""
echo "2️⃣  Add to Cursor:"
echo "   File: ~/.cursor/mcp.json (same format as above)"
echo ""
echo "3️⃣  Use Python Client:"
echo "   See: examples/analyticsads_integration.py"
echo ""
echo "4️⃣  Use TypeScript Client:"
echo "   See: examples/analyticsads_integration.ts"
echo ""
echo "📚 Full documentation:"
echo "   - DEPLOYMENT.md"
echo "   - examples/README_ANALYTICSADS_INTEGRATION.md"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

