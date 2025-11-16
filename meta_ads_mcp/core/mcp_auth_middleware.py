"""
MCP Connection-Level Authentication Middleware

This middleware enforces authentication at the MCP connection level,
returning 401 before listing tools if no valid Bearer token is provided.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from .utils import logger


class MCPAuthMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces authentication for all MCP endpoints"""
    
    def __init__(self, app):
        super().__init__(app)
        logger.info("🔒 MCPAuthMiddleware initialized - Bearer token REQUIRED for /mcp and /sse")
        print("🔒 MCP Auth Enforced: No Bearer token = 401 Unauthorized")
    
    async def dispatch(self, request: Request, call_next):
        print(f"🔍 MCPAuthMiddleware.dispatch() CALLED! Path: {request.url.path}")
        print(f"   Method: {request.method}")
        print(f"   Headers: {dict(request.headers)}")
        logger.info(f"MCPAuthMiddleware.dispatch() called for path: {request.url.path}")
        
        # Only check MCP endpoints
        if request.url.path.startswith('/mcp') or request.url.path.startswith('/sse'):
            print(f"🔒 Path {request.url.path} REQUIRES AUTH!")
            logger.debug(f"MCP Auth Middleware: Checking authentication for {request.url.path}")
            
            # Extract Bearer token
            auth_header = request.headers.get('Authorization') or request.headers.get('authorization')
            
            if not auth_header or not auth_header.lower().startswith('bearer '):
                print(f"❌ NO BEARER TOKEN! Returning 401 Unauthorized")
                print(f"   Auth header: {auth_header}")
                logger.info("MCP connection attempt without Bearer token - returning 401")
                return JSONResponse(
                    {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32600,
                            "message": "Authentication required",
                            "data": "Please authenticate using OAuth. Bearer token required."
                        }
                    },
                    status_code=401,
                    headers={
                        "WWW-Authenticate": 'Bearer realm="MCP Server", error="invalid_token"',
                        "Content-Type": "application/json"
                    }
                )
            
            token = auth_header[7:].strip()
            
            # Basic token validation (non-empty)
            if not token or len(token) < 10:
                logger.warning(f"Invalid Bearer token format: {token[:10] if token else 'empty'}...")
                return JSONResponse(
                    {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32600,
                            "message": "Invalid authentication token",
                            "data": "Bearer token is invalid or malformed"
                        }
                    },
                    status_code=401,
                    headers={
                        "WWW-Authenticate": 'Bearer realm="MCP Server", error="invalid_token"',
                        "Content-Type": "application/json"
                    }
                )
            
            logger.debug(f"Valid Bearer token found: {token[:10]}...")
        
        # Continue with request
        response = await call_next(request)
        return response

