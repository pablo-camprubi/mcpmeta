"""Insights and Reporting functionality for Meta Ads API."""

import json
from typing import Optional, Union, Dict
from .api import meta_api_tool, make_api_request
from .utils import download_image, try_multiple_download_methods, ad_creative_images, create_resource_from_image
from .server import mcp_server
import base64
import datetime


def _convert_cents_to_currency(value) -> float:
    """
    Convert Meta API monetary values from cents to major currency unit.
    Facebook Ads API returns monetary values in cents to avoid floating-point precision issues.
    
    Args:
        value: String or numeric value in cents (e.g., "11051" = 110.51 CHF)
    
    Returns:
        Float value in major currency unit (e.g., 110.51)
    """
    try:
        return round(float(value) / 100, 2)
    except (ValueError, TypeError):
        return 0.0


def _convert_monetary_fields(data: dict) -> dict:
    """
    Convert all monetary fields in Meta API response from cents to major currency unit.
    
    Handles:
    - spend, cpc, cpm: Direct monetary values
    - cost_per_action_type: Array of action costs
    - action_values: Array of action values (revenue)
    
    Args:
        data: API response data dictionary
    
    Returns:
        Modified dictionary with converted monetary values
    """
    if not isinstance(data, dict):
        return data
    
    # Convert top-level monetary fields
    monetary_fields = ["spend", "cpc", "cpm"]
    for field in monetary_fields:
        if field in data and data[field]:
            data[field] = _convert_cents_to_currency(data[field])
    
    # Convert cost_per_action_type array
    if "cost_per_action_type" in data and isinstance(data["cost_per_action_type"], list):
        for action in data["cost_per_action_type"]:
            if isinstance(action, dict) and "value" in action:
                action["value"] = _convert_cents_to_currency(action["value"])
    
    # Convert action_values array (revenue)
    if "action_values" in data and isinstance(data["action_values"], list):
        for action in data["action_values"]:
            if isinstance(action, dict) and "value" in action:
                action["value"] = _convert_cents_to_currency(action["value"])
    
    return data


# Shared helper function for all insights tools
async def _get_insights_data(object_id: str, fields: str, access_token: Optional[str] = None,
                             time_range: Union[str, Dict[str, str]] = "last_30d", 
                             breakdown: str = "", level: str = "ad", 
                             limit: int = 25, after: str = "") -> str:
    """
    Internal helper to fetch insights data with specific fields.
    """
    if not object_id:
        return json.dumps({"error": "No object ID provided"}, indent=2)
        
    endpoint = f"{object_id}/insights"
    params = {
        "fields": fields,
        "level": level,
        "limit": limit
    }
    
    # Handle time range based on type
    if isinstance(time_range, dict):
        # Use custom date range with since/until parameters
        if "since" in time_range and "until" in time_range:
            params["time_range"] = json.dumps(time_range)
        else:
            return json.dumps({"error": "Custom time_range must contain both 'since' and 'until' keys in YYYY-MM-DD format"}, indent=2)
    else:
        # Map user-friendly date presets to Meta API valid values
        date_preset_mapping = {
            "this_week": "this_week_mon_today",
            "last_week": "last_week_mon_sun",
        }
        mapped_preset = date_preset_mapping.get(time_range, time_range)
        params["date_preset"] = mapped_preset
    
    if breakdown:
        params["breakdowns"] = breakdown
    
    if after:
        params["after"] = after
    
    data = await make_api_request(endpoint, access_token, params)
    
    # Convert monetary values from cents to major currency unit
    if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        for item in data["data"]:
            _convert_monetary_fields(item)
    
    return json.dumps(data, indent=2)


BREAKDOWN_DOCS = """Optional breakdown dimension. Valid values include:
                   Demographic: age, gender, country, region, dma
                   Platform/Device: device_platform, platform_position, publisher_platform, impression_device
                   Creative Assets: ad_format_asset, body_asset, call_to_action_asset, description_asset, 
                                  image_asset, link_url_asset, title_asset, video_asset, media_type
                   Time-based: hourly_stats_aggregated_by_advertiser_time_zone, 
                              hourly_stats_aggregated_by_audience_time_zone, frequency_value
                   Other: breakdown_ad_objective, app_id, product_id, conversion_destination"""

TIME_RANGE_DOCS = """Either a preset time range string or a dictionary with "since" and "until" dates in YYYY-MM-DD format.
                   Preset options: today, yesterday, this_month, last_month, this_quarter, maximum, data_maximum, 
                   last_3d, last_7d, last_14d, last_28d, last_30d, last_90d, this_week, last_week, last_quarter, 
                   last_year, this_year
                   Dictionary example: {"since":"2023-01-01","until":"2023-01-31"}"""


@mcp_server.tool()
@meta_api_tool
async def get_cpc(object_id: str, access_token: Optional[str] = None,
                 time_range: Union[str, Dict[str, str]] = "last_30d", 
                 breakdown: str = "", level: str = "ad", 
                 limit: int = 25, after: str = "") -> str:
    """
    Get Cost Per Click (CPC) data for campaigns, ad sets, or ads.
    Returns: campaign/adset/ad names, CPC, clicks, and spend.
    
    Args:
        object_id: ID of the campaign, ad set, ad or account (e.g., 'act_123456')
        access_token: Meta API access token (optional - will use cached token if not provided)
        time_range: {TIME_RANGE_DOCS}
        breakdown: {BREAKDOWN_DOCS}
        level: Level of aggregation (ad, adset, campaign, account)
        limit: Maximum number of results per page (default: 25)
        after: Pagination cursor for next page
    """.format(TIME_RANGE_DOCS=TIME_RANGE_DOCS, BREAKDOWN_DOCS=BREAKDOWN_DOCS)
    
    fields = "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,cpc,clicks,spend"
    return await _get_insights_data(object_id, fields, access_token, time_range, breakdown, level, limit, after)


@mcp_server.tool()
@meta_api_tool
async def get_ctr(object_id: str, access_token: Optional[str] = None,
                 time_range: Union[str, Dict[str, str]] = "last_30d", 
                 breakdown: str = "", level: str = "ad", 
                 limit: int = 25, after: str = "") -> str:
    """
    Get Click-Through Rate (CTR) data for campaigns, ad sets, or ads.
    Returns: campaign/adset/ad names, CTR, impressions, and clicks.
    
    Args:
        object_id: ID of the campaign, ad set, ad or account (e.g., 'act_123456')
        access_token: Meta API access token (optional - will use cached token if not provided)
        time_range: {TIME_RANGE_DOCS}
        breakdown: {BREAKDOWN_DOCS}
        level: Level of aggregation (ad, adset, campaign, account)
        limit: Maximum number of results per page (default: 25)
        after: Pagination cursor for next page
    """.format(TIME_RANGE_DOCS=TIME_RANGE_DOCS, BREAKDOWN_DOCS=BREAKDOWN_DOCS)
    
    fields = "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,ctr,impressions,clicks"
    return await _get_insights_data(object_id, fields, access_token, time_range, breakdown, level, limit, after)


@mcp_server.tool()
@meta_api_tool
async def get_spend(object_id: str, access_token: Optional[str] = None,
                   time_range: Union[str, Dict[str, str]] = "last_30d", 
                   breakdown: str = "", level: str = "ad", 
                   limit: int = 25, after: str = "") -> str:
    """
    Get spend data for campaigns, ad sets, or ads.
    Returns: campaign/adset/ad names, total spend, impressions, and clicks.
    
    NOTE: All monetary values are automatically converted from cents to major currency unit
    (e.g., 11051 cents becomes 110.51 CHF/USD/EUR).
    
    Args:
        object_id: ID of the campaign, ad set, ad or account (e.g., 'act_123456')
        access_token: Meta API access token (optional - will use cached token if not provided)
        time_range: {TIME_RANGE_DOCS}
        breakdown: {BREAKDOWN_DOCS}
        level: Level of aggregation (ad, adset, campaign, account)
        limit: Maximum number of results per page (default: 25)
        after: Pagination cursor for next page
    """.format(TIME_RANGE_DOCS=TIME_RANGE_DOCS, BREAKDOWN_DOCS=BREAKDOWN_DOCS)
    
    fields = "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,spend,impressions,clicks"
    return await _get_insights_data(object_id, fields, access_token, time_range, breakdown, level, limit, after)


@mcp_server.tool()
@meta_api_tool
async def get_conversions(object_id: str, access_token: Optional[str] = None,
                         time_range: Union[str, Dict[str, str]] = "last_30d", 
                         breakdown: str = "", level: str = "ad", 
                         limit: int = 25, after: str = "") -> str:
    """
    Get conversion data for campaigns, ad sets, or ads.
    Returns: campaign/adset/ad names, conversions, actions, action values, cost per action, and spend.
    
    Args:
        object_id: ID of the campaign, ad set, ad or account (e.g., 'act_123456')
        access_token: Meta API access token (optional - will use cached token if not provided)
        time_range: {TIME_RANGE_DOCS}
        breakdown: {BREAKDOWN_DOCS}
        level: Level of aggregation (ad, adset, campaign, account)
        limit: Maximum number of results per page (default: 25)
        after: Pagination cursor for next page
    """.format(TIME_RANGE_DOCS=TIME_RANGE_DOCS, BREAKDOWN_DOCS=BREAKDOWN_DOCS)
    
    fields = "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,conversions,actions,action_values,cost_per_action_type,spend"
    return await _get_insights_data(object_id, fields, access_token, time_range, breakdown, level, limit, after)


@mcp_server.tool()
@meta_api_tool
async def get_reach_frequency(object_id: str, access_token: Optional[str] = None,
                              time_range: Union[str, Dict[str, str]] = "last_30d", 
                              breakdown: str = "", level: str = "ad", 
                              limit: int = 25, after: str = "") -> str:
    """
    Get reach and frequency data for campaigns, ad sets, or ads.
    Returns: campaign/adset/ad names, reach, frequency, impressions.
    
    Args:
        object_id: ID of the campaign, ad set, ad or account (e.g., 'act_123456')
        access_token: Meta API access token (optional - will use cached token if not provided)
        time_range: {TIME_RANGE_DOCS}
        breakdown: {BREAKDOWN_DOCS}
        level: Level of aggregation (ad, adset, campaign, account)
        limit: Maximum number of results per page (default: 25)
        after: Pagination cursor for next page
    """.format(TIME_RANGE_DOCS=TIME_RANGE_DOCS, BREAKDOWN_DOCS=BREAKDOWN_DOCS)
    
    fields = "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,reach,frequency,impressions"
    return await _get_insights_data(object_id, fields, access_token, time_range, breakdown, level, limit, after)


@mcp_server.tool()
@meta_api_tool
async def get_cpm(object_id: str, access_token: Optional[str] = None,
                 time_range: Union[str, Dict[str, str]] = "last_30d", 
                 breakdown: str = "", level: str = "ad", 
                 limit: int = 25, after: str = "") -> str:
    """
    Get Cost Per 1000 Impressions (CPM) data for campaigns, ad sets, or ads.
    Returns: campaign/adset/ad names, CPM, impressions, and spend.
    
    Args:
        object_id: ID of the campaign, ad set, ad or account (e.g., 'act_123456')
        access_token: Meta API access token (optional - will use cached token if not provided)
        time_range: {TIME_RANGE_DOCS}
        breakdown: {BREAKDOWN_DOCS}
        level: Level of aggregation (ad, adset, campaign, account)
        limit: Maximum number of results per page (default: 25)
        after: Pagination cursor for next page
    """.format(TIME_RANGE_DOCS=TIME_RANGE_DOCS, BREAKDOWN_DOCS=BREAKDOWN_DOCS)
    
    fields = "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,cpm,impressions,spend"
    return await _get_insights_data(object_id, fields, access_token, time_range, breakdown, level, limit, after)


@mcp_server.tool()
@meta_api_tool
async def get_roas(object_id: str, access_token: Optional[str] = None,
                  time_range: Union[str, Dict[str, str]] = "last_30d", 
                  breakdown: str = "", level: str = "ad", 
                  limit: int = 25, after: str = "") -> str:
    """
    Get ROAS (Return on Ad Spend) metrics for campaigns, ad sets, or ads.
    ROAS shows the revenue generated for every dollar spent on ads.
    Returns: spend, purchase_roas (if available), action_values (revenue), and calculated ROAS.
    
    Example: ROAS of 3.5 means you earned $3.50 for every $1.00 spent.
    
    NOTE: All monetary values (spend, revenue) are automatically converted from cents to 
    major currency unit (e.g., 11051 cents becomes 110.51 CHF/USD/EUR).
    
    Args:
        object_id: ID of the campaign, ad set, ad or account (e.g., 'act_123456')
        access_token: Meta API access token (optional - will use cached token if not provided)
        time_range: {TIME_RANGE_DOCS}
        breakdown: {BREAKDOWN_DOCS}
        level: Level of aggregation (ad, adset, campaign, account)
        limit: Maximum number of results per page (default: 25)
        after: Pagination cursor for next page
    """.format(TIME_RANGE_DOCS=TIME_RANGE_DOCS, BREAKDOWN_DOCS=BREAKDOWN_DOCS)
    
    fields = "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,spend,purchase_roas,action_values,actions"
    result = await _get_insights_data(object_id, fields, access_token, time_range, breakdown, level, limit, after)
    
    # Parse the result and add calculated ROAS if not present
    # Note: spend and action_values are already converted from cents to major currency unit
    try:
        data = json.loads(result)
        if "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                # If purchase_roas is not available, calculate it from action_values and spend
                if "purchase_roas" not in item or not item.get("purchase_roas"):
                    spend = float(item.get("spend", 0))
                    if spend > 0 and "action_values" in item:
                        # Find purchase value from action_values (already converted to major currency)
                        action_values = item.get("action_values", [])
                        purchase_value = 0
                        for action in action_values:
                            if action.get("action_type") in ["purchase", "omni_purchase"]:
                                purchase_value += float(action.get("value", 0))
                        
                        if purchase_value > 0:
                            calculated_roas = purchase_value / spend
                            item["calculated_roas"] = round(calculated_roas, 2)
                            item["calculated_revenue"] = round(purchase_value, 2)
        
        return json.dumps(data, indent=2)
    except Exception as e:
        # If parsing fails, return the original result
        return result


@mcp_server.tool()
@meta_api_tool
async def get_cpa(object_id: str, access_token: Optional[str] = None,
                 time_range: Union[str, Dict[str, str]] = "last_30d", 
                 breakdown: str = "", level: str = "ad", 
                 limit: int = 25, after: str = "") -> str:
    """
    Get CPA (Cost Per Action) and CPL (Cost Per Lead) metrics for campaigns, ad sets, or ads.
    Shows how much you're paying for each conversion action (purchases, leads, registrations, etc.).
    Returns: spend, actions, cost_per_action_type, and calculated CPA for each action type.
    
    Example: CPA of $5.50 means each conversion costs $5.50.
    
    NOTE: All monetary values (spend, CPA) are automatically converted from cents to 
    major currency unit (e.g., 11051 cents becomes 110.51 CHF/USD/EUR).
    
    Args:
        object_id: ID of the campaign, ad set, ad or account (e.g., 'act_123456')
        access_token: Meta API access token (optional - will use cached token if not provided)
        time_range: {TIME_RANGE_DOCS}
        breakdown: {BREAKDOWN_DOCS}
        level: Level of aggregation (ad, adset, campaign, account)
        limit: Maximum number of results per page (default: 25)
        after: Pagination cursor for next page
    """.format(TIME_RANGE_DOCS=TIME_RANGE_DOCS, BREAKDOWN_DOCS=BREAKDOWN_DOCS)
    
    fields = "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,spend,actions,cost_per_action_type"
    result = await _get_insights_data(object_id, fields, access_token, time_range, breakdown, level, limit, after)
    
    # Parse and enhance with calculated CPA for each action type
    # Note: spend is already converted from cents to major currency unit
    try:
        data = json.loads(result)
        if "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                spend = float(item.get("spend", 0))
                actions = item.get("actions", [])
                
                if spend > 0 and actions:
                    calculated_cpa = {}
                    for action in actions:
                        action_type = action.get("action_type", "unknown")
                        action_count = int(action.get("value", 0))
                        if action_count > 0:
                            cpa = spend / action_count
                            calculated_cpa[action_type] = round(cpa, 2)
                    
                    if calculated_cpa:
                        item["calculated_cpa"] = calculated_cpa
        
        return json.dumps(data, indent=2)
    except Exception as e:
        return result


@mcp_server.tool()
@meta_api_tool
async def get_cac(object_id: str, access_token: Optional[str] = None,
                 time_range: Union[str, Dict[str, str]] = "last_30d", 
                 breakdown: str = "", level: str = "ad", 
                 limit: int = 25, after: str = "") -> str:
    """
    Get CAC (Customer Acquisition Cost) metrics for campaigns, ad sets, or ads.
    CAC specifically tracks the cost to acquire a new customer (purchase conversion).
    Returns: spend, purchase actions, and calculated CAC.
    
    Example: CAC of $25.00 means each new customer costs $25.00 to acquire.
    
    NOTE: All monetary values (spend, CAC) are automatically converted from cents to 
    major currency unit (e.g., 11051 cents becomes 110.51 CHF/USD/EUR).
    
    Args:
        object_id: ID of the campaign, ad set, ad or account (e.g., 'act_123456')
        access_token: Meta API access token (optional - will use cached token if not provided)
        time_range: {TIME_RANGE_DOCS}
        breakdown: {BREAKDOWN_DOCS}
        level: Level of aggregation (ad, adset, campaign, account)
        limit: Maximum number of results per page (default: 25)
        after: Pagination cursor for next page
    """.format(TIME_RANGE_DOCS=TIME_RANGE_DOCS, BREAKDOWN_DOCS=BREAKDOWN_DOCS)
    
    fields = "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,spend,actions,cost_per_action_type"
    result = await _get_insights_data(object_id, fields, access_token, time_range, breakdown, level, limit, after)
    
    # Parse and calculate CAC specifically for purchases
    # Note: spend is already converted from cents to major currency unit
    try:
        data = json.loads(result)
        if "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                spend = float(item.get("spend", 0))
                actions = item.get("actions", [])
                
                # Find purchase actions
                purchase_count = 0
                for action in actions:
                    if action.get("action_type") in ["purchase", "omni_purchase"]:
                        purchase_count += int(action.get("value", 0))
                
                if spend > 0 and purchase_count > 0:
                    cac = spend / purchase_count
                    item["customer_acquisition_cost"] = round(cac, 2)
                    item["customers_acquired"] = purchase_count
                elif purchase_count > 0:
                    item["customers_acquired"] = purchase_count
        
        return json.dumps(data, indent=2)
    except Exception as e:
        return result


@mcp_server.tool()
@meta_api_tool
async def get_conversion_rate(object_id: str, access_token: Optional[str] = None,
                              time_range: Union[str, Dict[str, str]] = "last_30d", 
                              breakdown: str = "", level: str = "ad", 
                              limit: int = 25, after: str = "") -> str:
    """
    Get CVR (Conversion Rate) metrics for campaigns, ad sets, or ads.
    Shows the percentage of clicks that result in conversions.
    Returns: clicks, conversions, and calculated conversion rate.
    
    Example: CVR of 2.5% means 2.5 out of every 100 clicks result in a conversion.
    
    Args:
        object_id: ID of the campaign, ad set, ad or account (e.g., 'act_123456')
        access_token: Meta API access token (optional - will use cached token if not provided)
        time_range: {TIME_RANGE_DOCS}
        breakdown: {BREAKDOWN_DOCS}
        level: Level of aggregation (ad, adset, campaign, account)
        limit: Maximum number of results per page (default: 25)
        after: Pagination cursor for next page
    """.format(TIME_RANGE_DOCS=TIME_RANGE_DOCS, BREAKDOWN_DOCS=BREAKDOWN_DOCS)
    
    fields = "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,clicks,actions,conversions"
    result = await _get_insights_data(object_id, fields, access_token, time_range, breakdown, level, limit, after)
    
    # Parse and calculate conversion rate
    try:
        data = json.loads(result)
        if "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                clicks = int(item.get("clicks", 0))
                
                # Get conversion count (Meta sometimes provides this directly)
                conversion_count = 0
                if "conversions" in item:
                    conversions = item.get("conversions", [])
                    for conv in conversions:
                        conversion_count += int(conv.get("value", 0))
                
                # If no conversions field, count from actions
                if conversion_count == 0 and "actions" in item:
                    actions = item.get("actions", [])
                    for action in actions:
                        # Count conversion actions (purchases, leads, etc.)
                        if action.get("action_type") in ["purchase", "omni_purchase", "lead", "complete_registration", "add_to_cart"]:
                            conversion_count += int(action.get("value", 0))
                
                # Calculate CVR
                if clicks > 0 and conversion_count > 0:
                    cvr = (conversion_count / clicks) * 100
                    item["conversion_rate_percent"] = round(cvr, 2)
                    item["total_conversions"] = conversion_count
                elif conversion_count > 0:
                    item["total_conversions"] = conversion_count
        
        return json.dumps(data, indent=2)
    except Exception as e:
        return result


@mcp_server.tool()
@meta_api_tool
async def get_revenue(object_id: str, access_token: Optional[str] = None,
                     time_range: Union[str, Dict[str, str]] = "last_30d", 
                     breakdown: str = "", level: str = "ad", 
                     limit: int = 25, after: str = "") -> str:
    """
    Get Revenue and Purchase Value metrics for campaigns, ad sets, or ads.
    Shows total revenue generated from purchase conversions.
    Returns: action_values (purchase value), spend, and calculated profit.
    
    Example: Revenue of $5,000 with spend of $1,000 = $4,000 profit.
    
    NOTE: All monetary values (spend, revenue, profit) are automatically converted from cents 
    to major currency unit (e.g., 11051 cents becomes 110.51 CHF/USD/EUR).
    
    Args:
        object_id: ID of the campaign, ad set, ad or account (e.g., 'act_123456')
        access_token: Meta API access token (optional - will use cached token if not provided)
        time_range: {TIME_RANGE_DOCS}
        breakdown: {BREAKDOWN_DOCS}
        level: Level of aggregation (ad, adset, campaign, account)
        limit: Maximum number of results per page (default: 25)
        after: Pagination cursor for next page
    """.format(TIME_RANGE_DOCS=TIME_RANGE_DOCS, BREAKDOWN_DOCS=BREAKDOWN_DOCS)
    
    fields = "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,spend,action_values,actions"
    result = await _get_insights_data(object_id, fields, access_token, time_range, breakdown, level, limit, after)
    
    # Parse and calculate revenue/profit
    # Note: spend and action_values are already converted from cents to major currency unit
    try:
        data = json.loads(result)
        if "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                spend = float(item.get("spend", 0))
                
                # Extract purchase revenue from action_values (already converted to major currency)
                revenue = 0
                purchase_count = 0
                
                if "action_values" in item:
                    action_values = item.get("action_values", [])
                    for action in action_values:
                        if action.get("action_type") in ["purchase", "omni_purchase"]:
                            revenue += float(action.get("value", 0))
                
                # Get purchase count
                if "actions" in item:
                    actions = item.get("actions", [])
                    for action in actions:
                        if action.get("action_type") in ["purchase", "omni_purchase"]:
                            purchase_count += int(action.get("value", 0))
                
                # Add calculated fields
                if revenue > 0:
                    item["total_revenue"] = round(revenue, 2)
                    item["profit"] = round(revenue - spend, 2)
                    item["profit_margin_percent"] = round(((revenue - spend) / revenue) * 100, 2) if revenue > 0 else 0
                    
                    if purchase_count > 0:
                        item["average_order_value"] = round(revenue / purchase_count, 2)
                        item["purchase_count"] = purchase_count
        
        return json.dumps(data, indent=2)
    except Exception as e:
        return result


@mcp_server.tool()
@meta_api_tool
async def get_performance_overview(object_id: str, access_token: Optional[str] = None,
                                  time_range: Union[str, Dict[str, str]] = "last_30d", 
                                  breakdown: str = "", level: str = "ad", 
                                  limit: int = 25, after: str = "") -> str:
    """
    Get a quick performance overview for campaigns, ad sets, or ads.
    Returns: campaign/adset/ad names, impressions, clicks, spend, CPC, CTR, CPM.
    Use this for general performance questions.
    
    Args:
        object_id: ID of the campaign, ad set, ad or account (e.g., 'act_123456')
        access_token: Meta API access token (optional - will use cached token if not provided)
        time_range: {TIME_RANGE_DOCS}
        breakdown: {BREAKDOWN_DOCS}
        level: Level of aggregation (ad, adset, campaign, account)
        limit: Maximum number of results per page (default: 25)
        after: Pagination cursor for next page
    """.format(TIME_RANGE_DOCS=TIME_RANGE_DOCS, BREAKDOWN_DOCS=BREAKDOWN_DOCS)
    
    fields = "campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,impressions,clicks,spend,cpc,ctr,cpm"
    return await _get_insights_data(object_id, fields, access_token, time_range, breakdown, level, limit, after)


# Backward compatibility: keep get_insights for existing tests/integrations
async def get_insights(object_id: str, access_token: Optional[str] = None, 
                      time_range: Union[str, Dict[str, str]] = "maximum", breakdown: str = "", 
                      level: str = "ad", limit: int = 25, after: str = "") -> str:
    """
    Get performance insights for a campaign, ad set, ad or account.
    
    DEPRECATED: This function is kept for backward compatibility. 
    For new code, use specific tools like get_cpc, get_ctr, get_conversions, etc.
    
    Args:
        object_id: ID of the campaign, ad set, ad or account
        access_token: Meta API access token (optional - will use cached token if not provided)
        time_range: Either a preset time range string or a dictionary with "since" and "until" dates
        breakdown: Optional breakdown dimension
        level: Level of aggregation (ad, adset, campaign, account)
        limit: Maximum number of results to return per page (default: 25)
        after: Pagination cursor to get the next set of results
    """
    # Return all fields for backward compatibility
    fields = "account_id,account_name,campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,impressions,clicks,spend,cpc,cpm,ctr,reach,frequency,actions,action_values,conversions,unique_clicks,cost_per_action_type"
    return await _get_insights_data(object_id, fields, access_token, time_range, breakdown, level, limit, after)





 