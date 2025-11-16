"""
OAuth Authentication Proxy for Meta Ads MCP

This proxy sits in front of the FastMCP server and enforces Bearer token authentication
for all /mcp and /sse requests before forwarding them to the backend MCP server.
"""

from flask import Flask, request, Response, jsonify
import requests
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Backend MCP server configuration
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = 10001
BACKEND_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}"


def check_bearer_token(auth_header):
    """Check if Authorization header contains a Bearer token"""
    if not auth_header:
        logger.warning("Missing Authorization header")
        return False
    
    if not auth_header.lower().startswith('bearer '):
        logger.warning(f"Invalid Authorization format: {auth_header[:20]}...")
        return False
    
    token = auth_header[7:].strip()  # Remove 'Bearer ' prefix
    if not token:
        logger.warning("Empty Bearer token")
        return False
    
    logger.info(f"Valid Bearer token present (length: {len(token)})")
    return True


@app.route('/mcp', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@app.route('/mcp/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy_mcp(path):
    """Proxy /mcp requests with Bearer token authentication"""
    logger.info(f"🔍 Proxy intercepted: {request.method} /mcp/{path}")
    
    # Check for Bearer token
    auth_header = request.headers.get('Authorization')
    if not check_bearer_token(auth_header):
        logger.warning("❌ Authentication failed - returning 401")
        return jsonify({
            "jsonrpc": "2.0",
            "error": {
                "code": -32600,
                "message": "Authentication required",
                "data": "Please authenticate using OAuth. Bearer token required."
            }
        }), 401, {
            'WWW-Authenticate': 'Bearer realm="MCP Server", error="invalid_token"',
            'Content-Type': 'application/json'
        }
    
    # Forward request to backend MCP server
    # Backend runs streamable_http_app() which serves on /mcp
    backend_url = f"{BACKEND_URL}/mcp/{path}" if path else f"{BACKEND_URL}/mcp"
    logger.info(f"✅ Auth valid - forwarding to {backend_url}")
    
    try:
        # Forward all headers except Host
        headers = {key: value for key, value in request.headers if key.lower() != 'host'}
        
        # Make request to backend
        resp = requests.request(
            method=request.method,
            url=backend_url,
            headers=headers,
            data=request.get_data(),
            params=request.args,
            cookies=request.cookies,
            allow_redirects=False,
            stream=True  # Stream the response for SSE
        )
        
        # Create response with same status and headers
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [
            (name, value) for name, value in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]
        
        # Stream response back to client
        return Response(
            resp.iter_content(chunk_size=1024),
            status=resp.status_code,
            headers=response_headers
        )
    
    except requests.exceptions.ConnectionError:
        logger.error("❌ Cannot connect to backend MCP server")
        return jsonify({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Backend server unavailable",
                "data": "The MCP server is not responding"
            }
        }), 503
    except Exception as e:
        logger.error(f"❌ Proxy error: {e}")
        return jsonify({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Internal proxy error",
                "data": str(e)
            }
        }), 500


@app.route('/sse', defaults={'path': ''}, methods=['GET', 'POST', 'OPTIONS'])
@app.route('/sse/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
def proxy_sse(path):
    """Proxy /sse requests with Bearer token authentication"""
    logger.info(f"🔍 Proxy intercepted: {request.method} /sse/{path}")
    
    # Check for Bearer token
    auth_header = request.headers.get('Authorization')
    if not check_bearer_token(auth_header):
        logger.warning("❌ Authentication failed - returning 401")
        return jsonify({
            "error": "Authentication required. Bearer token required."
        }), 401, {
            'WWW-Authenticate': 'Bearer realm="MCP Server", error="invalid_token"',
            'Content-Type': 'application/json'
        }
    
    # Forward request to backend MCP server
    backend_url = f"{BACKEND_URL}/sse/{path}" if path else f"{BACKEND_URL}/sse"
    logger.info(f"✅ Auth valid - forwarding to {backend_url}")
    
    try:
        # Forward all headers except Host
        headers = {key: value for key, value in request.headers if key.lower() != 'host'}
        
        # Make request to backend
        resp = requests.request(
            method=request.method,
            url=backend_url,
            headers=headers,
            data=request.get_data(),
            params=request.args,
            cookies=request.cookies,
            allow_redirects=False,
            stream=True
        )
        
        # Create response with same status and headers
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [
            (name, value) for name, value in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]
        
        # Stream response back to client
        return Response(
            resp.iter_content(chunk_size=1024),
            status=resp.status_code,
            headers=response_headers
        )
    
    except Exception as e:
        logger.error(f"❌ Proxy error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/.well-known/oauth-authorization-server', methods=['GET'])
def oauth_discovery():
    """OAuth discovery endpoint - forward to backend"""
    logger.info("OAuth discovery request - forwarding to backend")
    try:
        resp = requests.get(f"{BACKEND_URL}/.well-known/oauth-authorization-server")
        return Response(resp.content, status=resp.status_code, headers=dict(resp.headers))
    except Exception as e:
        logger.error(f"OAuth discovery error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/oauth/authorize', methods=['GET'])
@app.route('/oauth/token', methods=['POST'])
@app.route('/oauth/callback', methods=['GET'])
def oauth_routes():
    """OAuth routes - forward to backend WITHOUT auth check"""
    logger.info(f"OAuth route request: {request.path} - forwarding to backend")
    try:
        backend_url = f"{BACKEND_URL}{request.path}"
        headers = {key: value for key, value in request.headers if key.lower() != 'host'}
        
        resp = requests.request(
            method=request.method,
            url=backend_url,
            headers=headers,
            data=request.get_data(),
            params=request.args,
            allow_redirects=False
        )
        
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        response_headers = [
            (name, value) for name, value in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]
        
        return Response(resp.content, status=resp.status_code, headers=response_headers)
    except Exception as e:
        logger.error(f"OAuth route error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "proxy": "running"}), 200


@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "service": "Meta Ads MCP - OAuth Proxy",
        "status": "running",
        "backend": f"{BACKEND_URL}",
        "authentication": "Bearer token required for /mcp and /sse"
    }), 200


def run_proxy(host="0.0.0.0", port=10000):
    """Run the OAuth proxy server"""
    from waitress import serve
    
    print("\n" + "=" * 80)
    print("🔒 META ADS MCP - OAUTH AUTHENTICATION PROXY")
    print("=" * 80)
    print(f"Proxy listening on: {host}:{port}")
    print(f"Backend MCP server: {BACKEND_URL}")
    print("✅ Bearer token authentication ENFORCED for /mcp and /sse")
    print("=" * 80 + "\n")
    
    logger.info("=" * 80)
    logger.info("🔒 META ADS MCP - OAUTH AUTHENTICATION PROXY")
    logger.info("=" * 80)
    logger.info(f"Proxy listening on: {host}:{port}")
    logger.info(f"Backend MCP server: {BACKEND_URL}")
    logger.info("✅ Bearer token authentication ENFORCED for /mcp and /sse")
    logger.info("=" * 80)
    
    try:
        print(f"🚀 Starting Waitress proxy server on {host}:{port}...")
        print(f"   (Production-ready WSGI server)")
        logger.info(f"Starting Waitress server on {host}:{port}")
        
        # Use Waitress production server instead of Flask dev server
        serve(app, host=host, port=port, threads=6, _quiet=False)
    except Exception as e:
        print(f"❌ Proxy failed to start: {e}")
        logger.error(f"Proxy failed to start: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    run_proxy()

