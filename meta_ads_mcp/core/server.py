"""MCP server configuration for Meta Ads API."""

from mcp.server.fastmcp import FastMCP
import argparse
import os
import sys
import webbrowser
import json
from typing import Dict, Any, Optional
from .auth import login as login_auth
from .resources import list_resources, get_resource
from .utils import logger
from .pipeboard_auth import pipeboard_auth_manager
import time

# Initialize FastMCP server
mcp_server = FastMCP("meta-ads")

# Register resource URIs
mcp_server.resource(uri="meta-ads://resources")(list_resources)
mcp_server.resource(uri="meta-ads://images/{resource_id}")(get_resource)


class StreamableHTTPHandler:
    """Handles stateless Streamable HTTP requests for Meta Ads MCP"""
    
    def __init__(self):
        """Initialize handler with no session storage - all auth per request"""
        logger.debug("StreamableHTTPHandler initialized for stateless operation")
        
    def handle_request(self, request_headers: Dict[str, str], request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle individual request with authentication
        
        Args:
            request_headers: HTTP request headers
            request_body: JSON-RPC request body
            
        Returns:
            JSON response with auth status and any tool results
        """
        try:
            # Extract authentication configuration from headers
            auth_config = self.get_auth_config_from_headers(request_headers)
            logger.debug(f"Auth method detected: {auth_config['auth_method']}")
            
            # Handle based on auth method
            if auth_config['auth_method'] == 'bearer':
                return self.handle_bearer_request(auth_config, request_body)
            elif auth_config['auth_method'] == 'custom_meta_app':
                return self.handle_custom_app_request(auth_config, request_body)
            else:
                return self.handle_unauthenticated_request(request_body)
                
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32603,
                    'message': 'Internal error',
                    'data': str(e)
                },
                'id': request_body.get('id')
            }
    
    def get_auth_config_from_headers(self, request_headers: Dict[str, str]) -> Dict[str, Any]:
        """Extract authentication configuration from HTTP headers
        
        Args:
            request_headers: HTTP request headers
            
        Returns:
            Dictionary with auth method and relevant credentials
        """
        # Security validation - only allow safe headers
        ALLOWED_VIA_HEADERS = {
            'pipeboard_api_token': True,   # ✅ Primary method - simple and secure
            'meta_app_id': True,           # ✅ Fallback only - triggers OAuth complexity
            'meta_app_secret': False,      # ❌ Server environment only
            'meta_access_token': False,    # ❌ Use proper auth flows instead
        }
        
        # PRIMARY: Check for Bearer token in Authorization header (handles 90%+ of cases)
        auth_header = request_headers.get('Authorization') or request_headers.get('authorization')
        if auth_header and auth_header.lower().startswith('bearer '):
            token = auth_header[7:].strip()
            logger.info("Bearer authentication detected (primary path)")
            return {
                'auth_method': 'bearer',
                'bearer_token': token,
                'requires_oauth': False  # Simple token-based auth
            }
        
        # FALLBACK: Custom Meta app (minority of users)
        meta_app_id = request_headers.get('X-META-APP-ID') or request_headers.get('x-meta-app-id')
        if meta_app_id:
            logger.debug("Custom Meta app authentication detected (fallback path)")
            return {
                'auth_method': 'custom_meta_app',
                'meta_app_id': meta_app_id,
                'requires_oauth': True  # Complex OAuth flow required
            }
        
        # No authentication provided
        logger.warning("No authentication method detected in headers")
        return {
            'auth_method': 'none',
            'requires_oauth': False
        }
    
    def handle_bearer_request(self, auth_config: Dict[str, Any], request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request with Bearer token (primary path)
        
        Args:
            auth_config: Authentication configuration from headers
            request_body: JSON-RPC request body
            
        Returns:
            JSON response ready for tool execution
        """
        logger.debug("Processing Bearer authenticated request")
        token = auth_config['bearer_token']
        
        # Token is ready to use immediately for API calls
        # TODO: In next phases, this will execute the actual tool call
        return {
            'jsonrpc': '2.0',
            'result': {
                'status': 'ready',
                'auth_method': 'bearer',
                'message': 'Authentication successful with Bearer token',
                'token_source': 'bearer_header'
            },
            'id': request_body.get('id')
        }
    
    def handle_custom_app_request(self, auth_config: Dict[str, Any], request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request with custom Meta app (fallback path)
        
        Args:
            auth_config: Authentication configuration from headers
            request_body: JSON-RPC request body
            
        Returns:
            JSON response indicating OAuth flow is required
        """
        logger.debug("Processing custom Meta app request (OAuth required)")
        
        # This may require OAuth flow initiation
        # Each request is independent - no session state
        return {
            'jsonrpc': '2.0',
            'result': {
                'status': 'oauth_required',
                'auth_method': 'custom_meta_app',
                'meta_app_id': auth_config['meta_app_id'],
                'message': 'OAuth flow required for custom Meta app authentication',
                'next_steps': 'Use get_login_link tool to initiate OAuth flow'
            },
            'id': request_body.get('id')
        }
    
    def handle_unauthenticated_request(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request with no authentication
        
        Args:
            request_body: JSON-RPC request body
            
        Returns:
            JSON error response requesting authentication
        """
        logger.warning("Unauthenticated request received")
        
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': -32600,
                'message': 'Authentication required',
                'data': {
                    'supported_methods': [
                        'Authorization: Bearer <token> (recommended)',
                        'X-META-APP-ID: Custom Meta app OAuth (advanced users)'
                    ],
                    'documentation': 'https://github.com/pipeboard-co/meta-ads-mcp'
                }
            },
            'id': request_body.get('id')
        }


def login_cli():
    """
    Command-line function to authenticate with Meta
    """
    logger.info("Starting Meta Ads CLI authentication flow")
    print("Starting Meta Ads CLI authentication flow...")
    
    # Call the common login function
    login_auth()


def main():
    """Main entry point for the package"""
    # Log startup information
    logger.info("Meta Ads MCP server starting")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Args: {sys.argv}")
    
    # Initialize argument parser
    parser = argparse.ArgumentParser(
        description="Meta Ads MCP Server - Model Context Protocol server for Meta Ads API",
        epilog="For more information, see https://github.com/pipeboard-co/meta-ads-mcp"
    )
    parser.add_argument("--login", action="store_true", help="Authenticate with Meta and store the token")
    parser.add_argument("--app-id", type=str, help="Meta App ID (Client ID) for authentication")
    parser.add_argument("--version", action="store_true", help="Show the version of the package")
    
    # Transport configuration arguments
    parser.add_argument("--transport", type=str, choices=["stdio", "streamable-http"], 
                       default="stdio", 
                       help="Transport method: 'stdio' for MCP clients (default), 'streamable-http' for HTTP API access")
    parser.add_argument("--port", type=int, default=8080, 
                       help="Port for Streamable HTTP transport (default: 8080, only used with --transport streamable-http)")
    parser.add_argument("--host", type=str, default="localhost", 
                       help="Host for Streamable HTTP transport (default: localhost, only used with --transport streamable-http)")
    parser.add_argument("--sse-response", action="store_true", 
                       help="Use SSE response format instead of JSON (default: JSON, only used with --transport streamable-http)")
    
    args = parser.parse_args()
    logger.debug(f"Parsed args: login={args.login}, app_id={args.app_id}, version={args.version}")
    logger.debug(f"Transport args: transport={args.transport}, port={args.port}, host={args.host}, sse_response={args.sse_response}")
    
    # Validate CLI argument combinations
    if args.transport == "stdio" and (args.port != 8080 or args.host != "localhost" or args.sse_response):
        logger.warning("HTTP transport arguments (--port, --host, --sse-response) are ignored when using stdio transport")
        print("Warning: HTTP transport arguments are ignored when using stdio transport")
    
    # Update app ID if provided as environment variable or command line arg
    from .auth import auth_manager, meta_config
    
    # Check environment variable first (early init)
    env_app_id = os.environ.get("META_APP_ID")
    if env_app_id:
        logger.debug(f"Found META_APP_ID in environment: {env_app_id}")
    else:
        logger.warning("META_APP_ID not found in environment variables")
    
    # Command line takes precedence
    if args.app_id:
        logger.info(f"Setting app_id from command line: {args.app_id}")
        auth_manager.app_id = args.app_id
        meta_config.set_app_id(args.app_id)
    elif env_app_id:
        logger.info(f"Setting app_id from environment: {env_app_id}")
        auth_manager.app_id = env_app_id
        meta_config.set_app_id(env_app_id)
    
    # Log the final app ID that will be used
    logger.info(f"Final app_id from meta_config: {meta_config.get_app_id()}")
    logger.info(f"Final app_id from auth_manager: {auth_manager.app_id}")
    logger.info(f"ENV META_APP_ID: {os.environ.get('META_APP_ID')}")
    
    # Show version if requested
    if args.version:
        from meta_ads_mcp import __version__
        logger.info(f"Displaying version: {__version__}")
        print(f"Meta Ads MCP v{__version__}")
        return 0
    
    # Handle login command
    if args.login:
        login_cli()
        return 0
    
    # Check for Pipeboard authentication and token
    pipeboard_api_token = os.environ.get("PIPEBOARD_API_TOKEN")
    if pipeboard_api_token:
        logger.info("Using Pipeboard authentication")
        print("✅ Pipeboard authentication enabled")
        print(f"   API token: {pipeboard_api_token[:8]}...{pipeboard_api_token[-4:]}")
        # Check for existing token
        token = pipeboard_auth_manager.get_access_token()
        if not token:
            logger.info("No valid Pipeboard token found. Initiating browser-based authentication flow.")
            print("No valid Meta token found. Opening browser for authentication...")
            try:
                # Initialize the auth flow and get the login URL
                auth_data = pipeboard_auth_manager.initiate_auth_flow()
                login_url = auth_data.get('loginUrl')
                if login_url:
                    logger.info(f"Opening browser with login URL: {login_url}")
                    webbrowser.open(login_url)
                    print("Please authorize the application in your browser.")
                    print("After authorization, the token will be automatically retrieved.")
                    print("Waiting for authentication to complete...")
                    
                    # Poll for token completion
                    max_attempts = 30  # Try for 30 * 2 = 60 seconds
                    for attempt in range(max_attempts):
                        print(f"Waiting for authentication... ({attempt+1}/{max_attempts})")
                        # Try to get the token again
                        token = pipeboard_auth_manager.get_access_token(force_refresh=True)
                        if token:
                            print("Authentication successful!")
                            break
                        time.sleep(2)  # Wait 2 seconds between attempts
                    
                    if not token:
                        print("Authentication timed out. Starting server anyway.")
                        print("You may need to restart the server after completing authentication.")
                else:
                    logger.error("No login URL received from Pipeboard API")
                    print("Error: Could not get authentication URL. Check your API token.")
            except Exception as e:
                logger.error(f"Error initiating browser-based authentication: {e}")
                print(f"Error: Could not start authentication: {e}")
        else:
            print(f"✅ Valid Pipeboard access token found")
            print(f"   Token preview: {token[:10]}...{token[-5:]}")
    
    # Transport-specific server initialization and startup
    if args.transport == "streamable-http":
        logger.info(f"Starting MCP server with Streamable HTTP transport on {args.host}:{args.port}")
        logger.info("Mode: Stateless (no session persistence)")
        logger.info(f"Response format: {'SSE' if args.sse_response else 'JSON'}")
        logger.info("Primary auth method: Bearer Token (recommended)")
        logger.info("Fallback auth method: Custom Meta App OAuth (complex setup)")
        
        print(f"Starting Meta Ads MCP server with Streamable HTTP transport")
        print(f"Server will listen on {args.host}:{args.port}")
        print(f"Response format: {'SSE' if args.sse_response else 'JSON'}")
        print("Primary authentication: Bearer Token (via Authorization: Bearer <token> header)")
        print("Fallback authentication: Custom Meta App OAuth (via X-META-APP-ID header)")
        
        # Configure the existing server with streamable HTTP settings
        mcp_server.settings.host = args.host
        mcp_server.settings.port = args.port
        mcp_server.settings.stateless_http = True
        mcp_server.settings.json_response = not args.sse_response
        
        # Import all tool modules to ensure they are registered
        logger.info("Ensuring all tools are registered for HTTP transport")
        from . import accounts, campaigns, adsets, ads, insights, authentication
        from . import ads_library, budget_schedules, reports, openai_deep_research
        
        # ✅ NEW: Setup HTTP authentication middleware
        logger.info("Setting up HTTP authentication middleware")
        try:
            from .http_auth_integration import setup_fastmcp_http_auth
            
            # Setup the FastMCP HTTP auth integration
            setup_fastmcp_http_auth(mcp_server)
            logger.info("FastMCP HTTP authentication integration setup successful")
            print("✅ FastMCP HTTP authentication integration enabled")
            print("   - Bearer tokens via Authorization: Bearer <token> header")
            print("   - Direct Meta tokens via X-META-ACCESS-TOKEN header")
            
        except Exception as e:
            logger.error(f"Failed to setup FastMCP HTTP authentication integration: {e}")
            print(f"⚠️  FastMCP HTTP authentication integration setup failed: {e}")
            print("   Server will still start but may not support header-based auth")
        
        # Log final server configuration
        logger.info(f"FastMCP server configured with:")
        logger.info(f"  - Host: {mcp_server.settings.host}")
        logger.info(f"  - Port: {mcp_server.settings.port}")
        logger.info(f"  - Stateless HTTP: {mcp_server.settings.stateless_http}")
        logger.info(f"  - JSON Response: {mcp_server.settings.json_response}")
        logger.info(f"  - Streamable HTTP Path: {mcp_server.settings.streamable_http_path}")
        
        # Start the FastMCP server with Streamable HTTP transport
        try:
            logger.info("Starting FastMCP server with Streamable HTTP transport")
            print(f"✅ Server configured successfully")
            print(f"   URL: http://{args.host}:{args.port}{mcp_server.settings.streamable_http_path}/")
            print(f"   Mode: {'Stateless' if mcp_server.settings.stateless_http else 'Stateful'}")
            print(f"   Format: {'JSON' if mcp_server.settings.json_response else 'SSE'}")
            
            # Add OAuth routes before starting the server
            logger.info("Adding OAuth routes to FastMCP server")
            try:
                from .oauth_provider import oauth_routes
                
                # Patch run method to add OAuth routes after app creation
                original_run = mcp_server.run
                
                def patched_run(transport="stdio", **kwargs):
                    if transport == "streamable-http":
                        # Add OAuth routes by patching the app creation
                        logger.info("Patching app creation to inject OAuth routes")
                        
                        # Store original app methods
                        if mcp_server.settings.json_response:
                            original_app_method = mcp_server.streamable_http_app
                            method_name = "streamable_http_app"
                        else:
                            original_app_method = mcp_server.sse_app
                            method_name = "sse_app"
                        
                        def patched_app_method():
                            # Get the original app
                            app = original_app_method()
                            
                            if app:
                                logger.info(f"Patching {method_name} to add OAuth routes")
                                # Add OAuth routes to this app
                                for route in oauth_routes:
                                    # Check if route already exists to avoid duplicates
                                    if not any(r.path == route.path for r in app.router.routes):
                                        app.router.routes.insert(0, route)  # Insert at start for priority
                                        logger.info(f"Added OAuth route: {route.path}")
                                
                                print(f"✅ OAuth routes added ({len(oauth_routes)} endpoints)")
                            else:
                                logger.error(f"Could not get app from {method_name}")
                            
                            return app
                        
                        # Replace the app method temporarily
                        if mcp_server.settings.json_response:
                            mcp_server.streamable_http_app = patched_app_method
                        else:
                            mcp_server.sse_app = patched_app_method
                        
                        # Now call the original run - it will use our patched app method
                        return original_run(transport=transport, **kwargs)
                    else:
                        # For non-HTTP transports, use original run
                        return original_run(transport=transport, **kwargs)
                
                mcp_server.run = patched_run
                logger.info("OAuth route patching complete")
                print("✅ OAuth provider configured")
                
            except Exception as e:
                logger.error(f"Failed to setup OAuth routes: {e}", exc_info=True)
                print(f"⚠️  OAuth setup failed: {e}")
                print("   Server will start without OAuth support")
            
            # Run FastMCP on localhost:10001 (backend, not public)
            # Run OAuth proxy on 0.0.0.0:10000 (public-facing with auth enforcement)
            
            import threading
            from .auth_proxy import run_proxy
            
            # Override FastMCP to use localhost:10001
            original_port = args.port
            mcp_backend_port = original_port + 1  # 10001 if original is 10000
            
            logger.info(f"Starting FastMCP backend on localhost:{mcp_backend_port}")
            logger.info(f"Starting OAuth proxy on {args.host}:{original_port}")
            print(f"\n{'='*80}")
            print(f"🔒 OAUTH PROXY ARCHITECTURE")
            print(f"{'='*80}")
            print(f"   Backend MCP Server: http://127.0.0.1:{mcp_backend_port}/mcp (private)")
            print(f"   OAuth Proxy:        http://{args.host}:{original_port}/mcp (public)")
            print(f"   ✅ All requests to {args.host}:{original_port} REQUIRE Bearer token")
            print(f"{'='*80}\n")
            
            # Start FastMCP backend in a separate thread on localhost:10001
            def run_mcp_backend():
                """Run FastMCP backend on localhost with custom port"""
                import uvicorn
                from mcp.server.fastmcp import FastMCP
                
                print(f"\n🔧 BACKEND THREAD: Starting FastMCP backend...")
                print(f"   Target: 127.0.0.1:{mcp_backend_port}")
                print(f"   Auth: NONE (proxy handles all auth)")
                
                # Create a fresh FastMCP instance without any auth middleware
                # The proxy handles all authentication
                backend_mcp = FastMCP("meta-ads-backend")
                
                # Copy all tools from the main mcp_server
                backend_mcp._tools = mcp_server._tools
                backend_mcp._resources = mcp_server._resources
                backend_mcp._prompts = mcp_server._prompts
                
                # Get clean app without auth middleware
                backend_app = backend_mcp.streamable_http_app()
                print(f"   App type: Clean Streamable HTTP app (no auth middleware)")
                
                logger.info(f"Starting FastMCP backend on 127.0.0.1:{mcp_backend_port}")
                print(f"🚀 Calling uvicorn.run() with host=127.0.0.1, port={mcp_backend_port}\n")
                
                # Run uvicorn on the backend port (localhost only)
                uvicorn.run(
                    backend_app,
                    host="127.0.0.1",
                    port=mcp_backend_port,
                    log_level="info"
                )
            
            print(f"🔧 Creating backend thread...")
            mcp_thread = threading.Thread(target=run_mcp_backend, daemon=True, name="FastMCP-Backend")
            mcp_thread.start()
            print(f"✅ Backend thread started (thread name: {mcp_thread.name})")
            
            # Wait a moment for FastMCP backend to start
            print(f"⏳ Waiting 3 seconds for FastMCP backend to start...")
            time.sleep(3)
            print(f"✅ Backend should be ready")
            logger.info("FastMCP backend started successfully")
            
            print(f"\n🎯 Now starting OAuth proxy on public port...")
            
            # Start the OAuth proxy on the public port (this blocks)
            run_proxy(host=args.host, port=original_port)
        except Exception as e:
            logger.error(f"Error starting Streamable HTTP server: {e}")
            print(f"Error: Failed to start Streamable HTTP server: {e}")
            return 1
    else:
        # Default stdio transport
        logger.info("Starting MCP server with stdio transport")
        mcp_server.run(transport='stdio') 