"""
Meta Ads MCP - Main Entry Point

This module allows the package to be executed directly via `python -m meta_ads_mcp`
"""

# CRITICAL: Patch uvicorn.run() BEFORE any imports that might use it
import uvicorn

_original_uvicorn_run = uvicorn.run

def _patched_uvicorn_run(app, **kwargs):
    """Wrap the ASGI app to add auth middleware at the uvicorn level"""
    print("🔧 Uvicorn.run() intercepted! Wrapping app...")
    print(f"   App type: {type(app)}")
    
    # Define raw ASGI middleware
    async def mcp_auth_asgi_middleware(scope, receive, send):
        """Raw ASGI middleware that enforces Bearer token auth"""
        from starlette.responses import JSONResponse
        
        # Only check HTTP requests to /mcp or /sse
        if scope["type"] == "http" and (
            scope["path"].startswith("/mcp") or scope["path"].startswith("/sse")
        ):
            print(f"🔍 UVICORN-LEVEL ASGI Middleware: {scope['method']} {scope['path']}")
            
            # Extract Authorization header
            headers = dict(scope.get("headers", []))
            auth_header = None
            for header_name, header_value in headers.items():
                if header_name.lower() == b"authorization":
                    auth_header = header_value.decode("utf-8")
                    break
            
            # Check for Bearer token
            if not auth_header or not auth_header.lower().startswith("bearer "):
                print(f"❌ NO BEARER TOKEN! Returning 401")
                
                # Return 401 Unauthorized
                response = JSONResponse(
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
                        "WWW-Authenticate": 'Bearer realm="MCP Server", error="invalid_token"'
                    }
                )
                await response(scope, receive, send)
                return
            
            print(f"✅ Bearer token present, allowing request")
        
        # Call the original app
        await app(scope, receive, send)
    
    print("✅ App wrapped at uvicorn level - ALL /mcp requests will be auth-checked")
    return _original_uvicorn_run(mcp_auth_asgi_middleware, **kwargs)

# Replace uvicorn.run with our patched version
uvicorn.run = _patched_uvicorn_run
print("🔒 Uvicorn.run() patched at module import time - auth will be enforced!")

from meta_ads_mcp.core.server import main

if __name__ == "__main__":
    main() 