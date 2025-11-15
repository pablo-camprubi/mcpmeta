"""
OAuth Provider for Meta Ads MCP Server

This module implements OAuth 2.0 provider endpoints that proxy authentication
to Facebook, allowing users to authenticate via their chatbot interface.
"""

import os
import json
import hashlib
import secrets
from typing import Dict, Optional
from datetime import datetime, timedelta
from urllib.parse import urlencode, parse_qs
from starlette.applications import Starlette
from starlette.responses import JSONResponse, RedirectResponse
from starlette.requests import Request
from starlette.routing import Route
import httpx
from .utils import logger


# In-memory session storage (upgrade to Redis for production)
oauth_sessions: Dict[str, Dict] = {}
authorization_codes: Dict[str, Dict] = {}


def cleanup_expired_sessions():
    """Remove expired sessions and codes"""
    now = datetime.now()
    
    # Cleanup sessions older than 10 minutes
    expired_sessions = [
        state for state, data in oauth_sessions.items()
        if (now - data.get('created_at', now)).total_seconds() > 600
    ]
    for state in expired_sessions:
        del oauth_sessions[state]
    
    # Cleanup codes older than 5 minutes
    expired_codes = [
        code for code, data in authorization_codes.items()
        if (now - data.get('created_at', now)).total_seconds() > 300
    ]
    for code in expired_codes:
        del authorization_codes[code]


async def oauth_discovery(request: Request):
    """OAuth 2.0 Discovery endpoint
    
    Returns OAuth server metadata per RFC 8414
    """
    base_url = os.environ.get('PUBLIC_URL', 'https://meta-ads-mcp-rike.onrender.com')
    
    metadata = {
        "issuer": base_url,
        "authorization_endpoint": f"{base_url}/oauth/authorize",
        "token_endpoint": f"{base_url}/oauth/token",
        "registration_endpoint": f"{base_url}/oauth/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["none"],
        "scopes_supported": ["mcp:tools", "ads_read", "ads_management", "business_management"]
    }
    
    logger.info("OAuth discovery endpoint called")
    return JSONResponse(metadata)


async def oauth_authorize(request: Request):
    """OAuth 2.0 Authorization endpoint
    
    Initiates the authorization flow by redirecting to Facebook OAuth
    """
    try:
        # Parse query parameters
        params = dict(request.query_params)
        
        state = params.get('state')
        redirect_uri = params.get('redirect_uri')
        code_challenge = params.get('code_challenge')
        code_challenge_method = params.get('code_challenge_method', 'S256')
        response_type = params.get('response_type', 'code')
        
        if not state or not redirect_uri:
            logger.error("Missing required parameters: state or redirect_uri")
            return JSONResponse({
                "error": "invalid_request",
                "error_description": "Missing required parameters"
            }, status_code=400)
        
        if response_type != 'code':
            logger.error(f"Unsupported response_type: {response_type}")
            return JSONResponse({
                "error": "unsupported_response_type",
                "error_description": "Only 'code' response type is supported"
            }, status_code=400)
        
        # Store authorization request
        oauth_sessions[state] = {
            'redirect_uri': redirect_uri,
            'code_challenge': code_challenge,
            'code_challenge_method': code_challenge_method,
            'created_at': datetime.now()
        }
        
        logger.info(f"OAuth authorization initiated for state: {state}")
        logger.debug(f"Stored session: redirect_uri={redirect_uri}, code_challenge present={bool(code_challenge)}")
        
        # Cleanup old sessions
        cleanup_expired_sessions()
        
        # Get Facebook app credentials
        fb_app_id = os.environ.get('META_APP_ID') or os.environ.get('FACEBOOK_APP_ID')
        if not fb_app_id:
            logger.error("META_APP_ID not configured")
            return JSONResponse({
                "error": "server_error",
                "error_description": "Server is not configured for OAuth"
            }, status_code=500)
        
        # Build Facebook OAuth URL
        base_url = os.environ.get('PUBLIC_URL', 'https://meta-ads-mcp-rike.onrender.com')
        fb_redirect_uri = f"{base_url}/oauth/facebook/callback"
        
        fb_auth_params = {
            'client_id': fb_app_id,
            'redirect_uri': fb_redirect_uri,
            'state': state,
            'scope': 'ads_read,ads_management,business_management',
            'response_type': 'code'
        }
        
        fb_auth_url = f"https://www.facebook.com/v21.0/dialog/oauth?{urlencode(fb_auth_params)}"
        
        logger.info(f"Redirecting to Facebook OAuth: {fb_auth_url}")
        return RedirectResponse(fb_auth_url, status_code=302)
        
    except Exception as e:
        logger.error(f"Error in oauth_authorize: {e}", exc_info=True)
        return JSONResponse({
            "error": "server_error",
            "error_description": str(e)
        }, status_code=500)


async def facebook_callback(request: Request):
    """Facebook OAuth callback handler
    
    Exchanges Facebook authorization code for access token,
    then redirects back to the chatbot with our authorization code
    """
    try:
        # Parse query parameters
        params = dict(request.query_params)
        
        fb_code = params.get('code')
        state = params.get('state')
        fb_error = params.get('error')
        
        if fb_error:
            logger.error(f"Facebook OAuth error: {fb_error}")
            error_description = params.get('error_description', 'Unknown error')
            
            # Get original redirect URI
            session = oauth_sessions.get(state, {})
            redirect_uri = session.get('redirect_uri', 'about:blank')
            
            # Redirect back to chatbot with error
            error_params = urlencode({
                'error': fb_error,
                'error_description': error_description,
                'state': state
            })
            return RedirectResponse(f"{redirect_uri}?{error_params}", status_code=302)
        
        if not fb_code or not state:
            logger.error("Missing code or state from Facebook callback")
            return JSONResponse({
                "error": "invalid_request",
                "error_description": "Missing code or state"
            }, status_code=400)
        
        # Get session data
        session = oauth_sessions.get(state)
        if not session:
            logger.error(f"Session not found for state: {state}")
            return JSONResponse({
                "error": "invalid_state",
                "error_description": "Session expired or invalid"
            }, status_code=400)
        
        logger.info(f"Facebook callback received for state: {state}")
        
        # Exchange Facebook code for access token
        fb_app_id = os.environ.get('META_APP_ID') or os.environ.get('FACEBOOK_APP_ID')
        fb_app_secret = os.environ.get('META_APP_SECRET') or os.environ.get('FACEBOOK_APP_SECRET')
        
        if not fb_app_id or not fb_app_secret:
            logger.error("Facebook app credentials not configured")
            return JSONResponse({
                "error": "server_error",
                "error_description": "Server not properly configured"
            }, status_code=500)
        
        base_url = os.environ.get('PUBLIC_URL', 'https://meta-ads-mcp-rike.onrender.com')
        fb_redirect_uri = f"{base_url}/oauth/facebook/callback"
        
        token_url = "https://graph.facebook.com/v21.0/oauth/access_token"
        token_params = {
            'client_id': fb_app_id,
            'client_secret': fb_app_secret,
            'redirect_uri': fb_redirect_uri,
            'code': fb_code
        }
        
        logger.info("Exchanging Facebook code for access token")
        
        async with httpx.AsyncClient() as client:
            token_response = await client.get(token_url, params=token_params)
            
            if token_response.status_code != 200:
                logger.error(f"Facebook token exchange failed: {token_response.text}")
                return JSONResponse({
                    "error": "server_error",
                    "error_description": "Failed to exchange authorization code"
                }, status_code=500)
            
            fb_tokens = token_response.json()
        
        logger.info("Successfully obtained Facebook access token")
        
        # Generate our authorization code for the chatbot
        auth_code = secrets.token_urlsafe(32)
        
        # Store tokens associated with auth code
        authorization_codes[auth_code] = {
            'access_token': fb_tokens.get('access_token'),
            'token_type': fb_tokens.get('token_type', 'Bearer'),
            'expires_in': fb_tokens.get('expires_in', 5184000),  # Default 60 days
            'state': state,
            'created_at': datetime.now()
        }
        
        logger.info(f"Generated authorization code: {auth_code[:10]}...")
        
        # Get original redirect URI from session
        redirect_uri = session.get('redirect_uri')
        
        # Redirect back to chatbot with our authorization code
        callback_params = urlencode({
            'code': auth_code,
            'state': state
        })
        
        callback_url = f"{redirect_uri}?{callback_params}"
        logger.info(f"Redirecting back to chatbot: {redirect_uri}")
        
        return RedirectResponse(callback_url, status_code=302)
        
    except Exception as e:
        logger.error(f"Error in facebook_callback: {e}", exc_info=True)
        return JSONResponse({
            "error": "server_error",
            "error_description": str(e)
        }, status_code=500)


async def oauth_register(request: Request):
    """OAuth 2.0 Dynamic Client Registration endpoint (RFC 7591)
    
    For PKCE flows, this returns static client credentials without actual registration.
    The client_id is deterministic based on the client_name for consistency.
    """
    try:
        # Parse request body
        body = await request.body()
        client_metadata = json.loads(body)
        
        logger.info(f"Client registration requested: {client_metadata.get('client_name', 'unknown')}")
        
        # Generate deterministic client_id based on client_name for consistency across restarts
        client_name = client_metadata.get('client_name', 'mcp-client')
        client_id = hashlib.sha256(client_name.encode('utf-8')).hexdigest()[:16]
        
        # For PKCE, we don't need a client_secret (token_endpoint_auth_method: "none")
        # Return the client metadata with a generated client_id
        response_data = {
            "client_id": client_id,
            "client_id_issued_at": int(datetime.now().timestamp()),
            **client_metadata  # Return all provided metadata
        }
        
        logger.info(f"Client registration successful: {client_id}")
        return JSONResponse(response_data, status_code=201)
        
    except Exception as e:
        logger.error(f"Error in oauth_register: {e}", exc_info=True)
        return JSONResponse({
            "error": "invalid_request",
            "error_description": str(e)
        }, status_code=400)


async def oauth_token(request: Request):
    """OAuth 2.0 Token endpoint
    
    Exchanges authorization code for access token with PKCE verification
    """
    try:
        # Parse form data
        body = await request.body()
        if request.headers.get('content-type', '').startswith('application/json'):
            params = json.loads(body)
        else:
            params = parse_qs(body.decode('utf-8'))
            # Flatten single-value lists
            params = {k: v[0] if isinstance(v, list) and len(v) == 1 else v 
                     for k, v in params.items()}
        
        grant_type = params.get('grant_type')
        code = params.get('code')
        code_verifier = params.get('code_verifier')
        redirect_uri = params.get('redirect_uri')
        
        logger.info(f"Token endpoint called with grant_type: {grant_type}")
        
        if grant_type == 'authorization_code':
            if not code:
                logger.error("Missing authorization code")
                return JSONResponse({
                    "error": "invalid_request",
                    "error_description": "Missing authorization code"
                }, status_code=400)
            
            # Get token data
            token_data = authorization_codes.get(code)
            if not token_data:
                logger.error(f"Invalid authorization code: {code[:10]}...")
                return JSONResponse({
                    "error": "invalid_grant",
                    "error_description": "Authorization code is invalid or expired"
                }, status_code=400)
            
            # Get session for PKCE verification
            state = token_data.get('state')
            session = oauth_sessions.get(state)
            
            if session and session.get('code_challenge'):
                # Verify PKCE
                if not code_verifier:
                    logger.error("Missing code_verifier for PKCE flow")
                    return JSONResponse({
                        "error": "invalid_request",
                        "error_description": "code_verifier required"
                    }, status_code=400)
                
                # Calculate challenge from verifier
                challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
                challenge = challenge.hex() if session.get('code_challenge_method') == 'plain' else \
                           hashlib.sha256(code_verifier.encode('utf-8')).hexdigest() if session.get('code_challenge_method') == 'S256' else \
                           None
                
                # For S256, we need base64url encoding
                if session.get('code_challenge_method') == 'S256':
                    import base64
                    challenge = base64.urlsafe_b64encode(
                        hashlib.sha256(code_verifier.encode('utf-8')).digest()
                    ).decode('utf-8').rstrip('=')
                
                if challenge != session.get('code_challenge'):
                    logger.error("PKCE verification failed")
                    return JSONResponse({
                        "error": "invalid_grant",
                        "error_description": "Code verifier does not match challenge"
                    }, status_code=400)
                
                logger.info("PKCE verification successful")
            
            # Clean up used code and session
            del authorization_codes[code]
            if state and state in oauth_sessions:
                del oauth_sessions[state]
            
            # Return Facebook access token to chatbot
            response_data = {
                "access_token": token_data.get('access_token'),
                "token_type": token_data.get('token_type', 'Bearer'),
                "expires_in": token_data.get('expires_in', 5184000)
            }
            
            logger.info("Token exchange successful")
            return JSONResponse(response_data)
        
        elif grant_type == 'refresh_token':
            # Refresh token flow (optional - Facebook doesn't support refresh tokens by default)
            logger.warning("Refresh token grant not implemented")
            return JSONResponse({
                "error": "unsupported_grant_type",
                "error_description": "Refresh token flow not implemented"
            }, status_code=400)
        
        else:
            logger.error(f"Unsupported grant_type: {grant_type}")
            return JSONResponse({
                "error": "unsupported_grant_type",
                "error_description": f"Grant type '{grant_type}' is not supported"
            }, status_code=400)
        
    except Exception as e:
        logger.error(f"Error in oauth_token: {e}", exc_info=True)
        return JSONResponse({
            "error": "server_error",
            "error_description": str(e)
        }, status_code=500)


# Define OAuth routes
oauth_routes = [
    Route('/.well-known/oauth-authorization-server', oauth_discovery, methods=['GET']),
    Route('/oauth/authorize', oauth_authorize, methods=['GET', 'POST']),
    Route('/oauth/register', oauth_register, methods=['POST']),
    Route('/oauth/facebook/callback', facebook_callback, methods=['GET']),
    Route('/oauth/token', oauth_token, methods=['POST']),
]


def add_oauth_routes_to_app(app: Starlette):
    """Add OAuth routes to the Starlette app
    
    Args:
        app: Starlette application instance
    """
    logger.info("Adding OAuth routes to Starlette app")
    
    # Add routes to the app's router
    for route in oauth_routes:
        app.router.routes.append(route)
    
    logger.info(f"Added {len(oauth_routes)} OAuth routes")
    logger.info("OAuth endpoints available:")
    logger.info("  - GET  /.well-known/oauth-authorization-server")
    logger.info("  - POST /oauth/authorize")
    logger.info("  - POST /oauth/register")
    logger.info("  - GET  /oauth/facebook/callback")
    logger.info("  - POST /oauth/token")

