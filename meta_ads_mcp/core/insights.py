"""Insights and Reporting functionality for Meta Ads API."""

import json
from typing import Optional, Union, Dict
from .api import meta_api_tool, make_api_request
from .utils import download_image, try_multiple_download_methods, ad_creative_images, create_resource_from_image
from .server import mcp_server
import base64
import datetime


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





 