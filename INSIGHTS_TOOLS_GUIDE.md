# 📊 Insights Tools Guide

## What Changed?

Instead of **one big `get_insights` tool** that returns ALL metrics, we now have **7 specific tools** that only return what's needed.

---

## 🎯 New Specific Tools

### 1. **`get_cpc`** - Cost Per Click
**When to use**: User asks about CPC, cost per click, or click efficiency  
**Returns**: `cpc`, `clicks`, `spend`

**Example Questions**:
- "What's the CPC for my campaigns?"
- "Show me cost per click for last month"
- "Which ads have the lowest CPC?"

---

### 2. **`get_ctr`** - Click-Through Rate
**When to use**: User asks about CTR, click rate, or engagement rate  
**Returns**: `ctr`, `impressions`, `clicks`

**Example Questions**:
- "What's my CTR?"
- "Show me click-through rates by age group"
- "Which ad has the best CTR?"

---

### 3. **`get_spend`** - Spend Analysis
**When to use**: User asks about budget, spending, or costs  
**Returns**: `spend`, `impressions`, `clicks`

**Example Questions**:
- "How much did I spend last week?"
- "Show me spend by campaign"
- "What's my total spend for Q1?"

---

### 4. **`get_conversions`** - Conversions
**When to use**: User asks about conversions, sales, leads, actions  
**Returns**: `conversions`, `actions`, `action_values`, `cost_per_action_type`, `spend`

**Example Questions**:
- "How many conversions did I get?"
- "What's my cost per conversion?"
- "Show me leads by campaign"

---

### 5. **`get_reach_frequency`** - Reach & Frequency
**When to use**: User asks about reach, unique users, or frequency  
**Returns**: `reach`, `frequency`, `impressions`

**Example Questions**:
- "How many people did I reach?"
- "What's my ad frequency?"
- "Show me reach by country"

---

### 6. **`get_cpm`** - Cost Per 1000 Impressions
**When to use**: User asks about CPM or impression costs  
**Returns**: `cpm`, `impressions`, `spend`

**Example Questions**:
- "What's my CPM?"
- "Show me cost per 1000 impressions"
- "Which ad has the lowest CPM?"

---

### 7. **`get_performance_overview`** - Quick Overview
**When to use**: User asks general performance questions  
**Returns**: `impressions`, `clicks`, `spend`, `cpc`, `ctr`, `cpm`

**Example Questions**:
- "How are my ads performing?"
- "Show me overall performance"
- "Give me a summary of last week's results"

---

## 💡 Key Benefits

### Before (Old Way)
```json
// User asks: "What's my CPC?"
// API returns: cpc, ctr, cpm, spend, impressions, clicks, reach, 
//              frequency, conversions, actions, action_values, etc.
// Result: 20+ metrics when you only need 3
```

### After (New Way)
```json
// User asks: "What's my CPC?"
// LLM picks: get_cpc tool
// API returns: cpc, clicks, spend
// Result: Only 3 relevant metrics ✅
```

---

## 🚀 How LLMs Will Use This

When a user asks:
- **"What's my CPC?"** → LLM calls `get_cpc`
- **"How much did I spend?"** → LLM calls `get_spend`
- **"Show me conversions"** → LLM calls `get_conversions`
- **"How are my ads doing?"** → LLM calls `get_performance_overview`

---

## 📝 All Tools Share Same Parameters

Every tool accepts:
- `object_id` - Campaign/AdSet/Ad/Account ID
- `time_range` - Date range (e.g., "last_30d", "this_month")
- `breakdown` - Segment by (e.g., "age", "gender", "device_platform")
- `level` - Aggregation level ("ad", "adset", "campaign", "account")
- `limit` - Results per page (default: 25)
- `after` - Pagination cursor

---

## 🔧 Technical Implementation

All tools share a common helper function:
```python
async def _get_insights_data(object_id, fields, access_token, 
                            time_range, breakdown, level, limit, after)
```

Each tool just specifies which **fields** it needs:
- `get_cpc` → `"cpc,clicks,spend"`
- `get_ctr` → `"ctr,impressions,clicks"`
- `get_conversions` → `"conversions,actions,action_values,cost_per_action_type,spend"`

---

## ✅ Testing

To test after deploying:

```bash
# Test get_cpc
curl -X POST https://meta-ads-mcp-rike.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "jsonrpc":"2.0",
    "method":"tools/call",
    "id":1,
    "params":{
      "name":"get_cpc",
      "arguments":{
        "object_id":"act_1372476760969411",
        "time_range":"last_7d",
        "level":"campaign"
      }
    }
  }'
```

---

## 🎉 Result

- **Faster responses** - Less data transferred
- **Better UX** - Only relevant metrics shown
- **Smarter LLM** - Picks the right tool for the job
- **Lower costs** - Smaller API responses = less bandwidth

---

This is exactly what you wanted! 🚀

