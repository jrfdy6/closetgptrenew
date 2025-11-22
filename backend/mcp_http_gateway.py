# mcp_http_gateway.py
# OpenAI Apps SDK Gateway - OAuth and API proxy
import os
import httpx
import secrets
import time
from typing import Optional, Dict, Any
from urllib.parse import quote
from fastapi import FastAPI, Request, Response, HTTPException, Header, Form, Query, Cookie
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
import concurrent.futures

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
firebase_initialized = False
try:
    if not firebase_admin._apps:
        # Check if all required environment variables are present
        required_vars = [
            "FIREBASE_PROJECT_ID", "FIREBASE_PRIVATE_KEY", "FIREBASE_CLIENT_EMAIL",
            "FIREBASE_CLIENT_ID", "FIREBASE_CLIENT_X509_CERT_URL"
        ]
        
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        if missing_vars:
            logger.warning(f"⚠️ FIREBASE INIT: Missing environment variables: {missing_vars}. Firebase Auth will be disabled.")
            firebase_initialized = False
        else:
            # Get private key and handle newlines properly
            private_key = os.environ.get("FIREBASE_PRIVATE_KEY", "")
            if "\\n" in private_key:
                private_key = private_key.replace("\\n", "\n")
            
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
                "private_key": private_key,
                "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL"),
            })
            
            firebase_admin.initialize_app(cred)
            firebase_initialized = True
            logger.info("✅ FIREBASE INIT: Firebase Admin SDK initialized successfully")
    else:
        firebase_initialized = True
        logger.info("✅ FIREBASE INIT: Firebase Admin SDK already initialized")
except Exception as e:
    logger.error(f"❌ FIREBASE INIT FAILED: {type(e).__name__}: {str(e)}")
    firebase_initialized = False

MAIN_BACKEND_URL = os.environ.get("MAIN_BACKEND_URL", "https://closetgptrenew-production.up.railway.app")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "https://easyoutfitapp.com")
API_KEY = os.environ.get("API_KEY", "")

# OAuth configuration
OAUTH_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID", "easyoutfit-chatgpt-app")
OAUTH_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET", secrets.token_urlsafe(32))
OAUTH_REDIRECT_URI = "https://chat.openai.com/aip/oauth/callback"
GATEWAY_URL = os.environ.get("GATEWAY_URL", "https://closetgptrenewopenaisdk-production.up.railway.app")

# In-memory token store (for MVP - use Redis/DB in production)
oauth_codes = {}  # {code: {state, redirect_uri, user_id, expires_at}}
oauth_tokens = {}  # {access_token: {user_id, firebase_token, expires_at, refresh_token}}

app = FastAPI(
    title="Easy Outfit OpenAI Apps SDK Gateway",
    description="OAuth gateway for OpenAI Apps SDK integration with Easy Outfit",
    version="1.0.0"
)

# Helper function to verify Firebase ID token
def verify_firebase_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Firebase ID token and return decoded token data
    Returns None if token is invalid or Firebase is not initialized
    """
    if not firebase_initialized:
        logger.warning("Firebase not initialized, cannot verify token")
        return None
    
    if not token:
        return None
    
    try:
        # Use ThreadPoolExecutor for blocking Firebase call
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(firebase_auth.verify_id_token, token)
            decoded_token = future.result(timeout=10.0)
            
            user_id = decoded_token.get("uid")
            email = decoded_token.get("email")
            name = decoded_token.get("name", email)
            
            if not user_id:
                logger.warning("Token verified but no user_id found")
                return None
            
            return {
                "user_id": user_id,
                "email": email,
                "name": name,
                "token": token
            }
    except concurrent.futures.TimeoutError:
        logger.error("Firebase token verification timed out")
        return None
    except firebase_auth.InvalidIdTokenError as e:
        logger.warning(f"Invalid Firebase token: {e}")
        return None
    except firebase_auth.ExpiredIdTokenError as e:
        logger.warning(f"Expired Firebase token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error verifying Firebase token: {e}")
        return None

# Helper function to get Firebase token from request
def get_firebase_token_from_request(request: Request) -> Optional[str]:
    """
    Extract Firebase ID token from request
    Checks Authorization header, query parameter, or cookie
    """
    # Check Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.replace("Bearer ", "")
    
    # Check query parameter (for OAuth flow)
    token_param = request.query_params.get("firebase_token")
    if token_param:
        return token_param
    
    # Check cookie
    token_cookie = request.cookies.get("firebase_token")
    if token_cookie:
        return token_cookie
    
    return None

# Allow ChatGPT Apps requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For MVP, allow all origins
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/.well-known/ai-plugin.json")
async def ai_plugin_manifest():
    """
    Serve the AI plugin manifest for OpenAI Apps SDK discovery
    """
    # Get verification token from environment (OpenAI provides this after first registration)
    verification_token = os.environ.get("OPENAI_VERIFICATION_TOKEN", "PLACEHOLDER_TOKEN")
    
    return {
        "schema_version": "v1",
        "name_for_human": "Easy Outfit",
        "name_for_model": "easy_outfit",
        "description_for_human": "AI-powered wardrobe manager and outfit generator. Get personalized outfit suggestions for any occasion.",
        "description_for_model": "Easy Outfit helps users manage their digital wardrobe and get personalized outfit suggestions. Use get_wardrobe to view items, suggest_outfits to generate outfit recommendations based on occasion, style, and weather.",
        "auth": {
            "type": "oauth",
            "authorization_type": "code",
            "client_url": f"{GATEWAY_URL}/oauth/authorize",
            "authorization_url": f"{GATEWAY_URL}/oauth/authorize",
            "authorization_content_type": "application/x-www-form-urlencoded",
            "scope": "wardrobe:read outfits:generate",
            "token_url": f"{GATEWAY_URL}/oauth/token",
            "verification_tokens": {
                "openai": verification_token
            }
        },
        "api": {
            "type": "openapi",
            "url": f"{GATEWAY_URL}/openapi.json",
            "is_user_authenticated": True
        },
        "logo_url": "https://easyoutfitapp.com/logo.png",
        "contact_email": "support@easyoutfitapp.com",
        "legal_info_url": "https://easyoutfitapp.com/legal"
    }

@app.get("/openapi.json")
async def openapi_spec():
    """
    Serve OpenAPI specification for OpenAI Apps SDK
    """
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Easy Outfit API",
            "version": "1.0.0",
            "description": "AI-powered wardrobe manager and outfit generator API"
        },
        "servers": [
            {
                "url": GATEWAY_URL,
                "description": "Production server"
            }
        ],
        "paths": {
            "/wardrobe": {
                "get": {
                    "summary": "Get user's wardrobe items",
                    "description": "Retrieve all wardrobe items for the authenticated user",
                    "operationId": "get_wardrobe",
                    "security": [{"oauth": []}],
                    "responses": {
                        "200": {
                            "description": "List of wardrobe items",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "items": {
                                                "type": "array",
                                                "items": {"type": "object"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/suggest-outfits": {
                "post": {
                    "summary": "Generate outfit suggestions",
                    "description": "Get personalized outfit recommendations based on occasion, style, and weather",
                    "operationId": "suggest_outfits",
                    "security": [{"oauth": []}],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "occasion": {"type": "string"},
                                        "style": {"type": "string"},
                                        "weather": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Outfit suggestions",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "outfits": {
                                                "type": "array",
                                                "items": {"type": "object"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "oauth": {
                    "type": "oauth2",
                    "flows": {
                        "authorizationCode": {
                            "authorizationUrl": f"{GATEWAY_URL}/oauth/authorize",
                            "tokenUrl": f"{GATEWAY_URL}/oauth/token",
                            "scopes": {
                                "wardrobe:read": "Read wardrobe items",
                                "outfits:generate": "Generate outfit suggestions"
                            }
                        }
                    }
                }
            }
        }
    }

@app.get("/oauth/authorize")
async def oauth_authorize(
    request: Request,
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    state: str = Query(...),
    response_type: str = Query("code"),
    scope: Optional[str] = Query("wardrobe:read outfits:generate"),
    firebase_token: Optional[str] = Query(None)
):
    """
    OAuth authorization endpoint - shows consent page or redirects to login
    OpenAI Apps SDK calls this to start the OAuth flow
    """
    logger.info(f"OAuth authorize: client_id={client_id}, redirect_uri={redirect_uri[:50]}..., state={state[:20]}...")
    
    # Validate redirect_uri matches OpenAI callback
    if redirect_uri != OAUTH_REDIRECT_URI:
        logger.warning(f"Invalid redirect_uri: {redirect_uri} (expected {OAUTH_REDIRECT_URI})")
        raise HTTPException(status_code=400, detail=f"Invalid redirect_uri. Must be {OAUTH_REDIRECT_URI}")
    
    # Validate client_id
    if client_id != OAUTH_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Invalid client_id")
    
    # Validate response_type
    if response_type != "code":
        raise HTTPException(status_code=400, detail="Unsupported response_type")
    
    # Try to get Firebase token from request
    token = firebase_token or get_firebase_token_from_request(request)
    user_info = None
    
    if token and firebase_initialized:
        # Verify Firebase token
        user_info = verify_firebase_token(token)
        if user_info:
            logger.info(f"User authenticated: {user_info['user_id']} ({user_info['email']})")
        else:
            logger.warning("Firebase token provided but invalid or expired")
    else:
        logger.info("No Firebase token provided or Firebase not initialized")
    
    # If user is not authenticated, show login page
    if not user_info:
        # Build OAuth URL and encode it as returnUrl parameter
        oauth_url = f"{GATEWAY_URL}/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&state={state}&response_type={response_type}&scope={scope}"
        login_url = f"{FRONTEND_URL}/login?returnUrl={quote(oauth_url, safe='')}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Required - Easy Outfit</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    max-width: 600px;
                    margin: 50px auto;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .card {{
                    background: white;
                    border-radius: 16px;
                    padding: 40px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                }}
                h1 {{ color: #1a202c; margin-bottom: 10px; }}
                p {{ color: #4a5568; margin: 20px 0; }}
                .login-button {{
                    display: inline-block;
                    padding: 12px 32px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 600;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>🔐 Login Required</h1>
                <p>You need to be logged into Easy Outfit to authorize ChatGPT access.</p>
                <p>Please log in to continue.</p>
                <a href="{login_url}" class="login-button">Login to Easy Outfit</a>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)
    
    # User is authenticated - show consent page
    user_name = user_info.get("name", user_info.get("email", "User"))
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authorize Easy Outfit</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .card {{
                background: white;
                border-radius: 16px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            }}
            h1 {{ color: #1a202c; margin-bottom: 10px; }}
            .permissions {{
                background: #f7fafc;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .permission {{
                display: flex;
                align-items: center;
                margin: 10px 0;
                color: #2d3748;
            }}
            .permission::before {{
                content: "✓";
                color: #48bb78;
                font-weight: bold;
                margin-right: 10px;
            }}
            .buttons {{ display: flex; gap: 10px; margin-top: 30px; }}
            button {{
                flex: 1;
                padding: 12px 24px;
                border-radius: 8px;
                border: none;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
            }}
            .authorize {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .deny {{ background: #e2e8f0; color: #4a5568; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🎨 Authorize Easy Outfit</h1>
            <p>Logged in as: <strong>{user_name}</strong></p>
            <p>ChatGPT wants to access your wardrobe</p>
            
            <div class="permissions">
                <strong>This will allow ChatGPT to:</strong>
                <div class="permission">View your wardrobe items</div>
                <div class="permission">Generate outfit recommendations</div>
                <div class="permission">Access your style preferences</div>
            </div>
            
            <div class="buttons">
                <button class="deny" onclick="window.location.href='{redirect_uri}?error=access_denied&state={state}'">
                    Deny
                </button>
                <button class="authorize" onclick="authorize()">
                    Authorize
                </button>
            </div>
        </div>
        
        <script>
            function authorize() {{
                // Pass Firebase token to consent endpoint
                const token = '{token}';
                window.location.href = '/oauth/consent?client_id={client_id}&redirect_uri={redirect_uri}&state={state}&scope={scope}&firebase_token=' + encodeURIComponent(token);
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/oauth/consent")
async def oauth_consent(
    request: Request,
    client_id: str = Query(...),
    redirect_uri: str = Query(...),
    state: str = Query(...),
    scope: str = Query("wardrobe:read outfits:generate"),
    firebase_token: Optional[str] = Query(None)
):
    """
    Handle user consent and generate authorization code
    Verifies user is authenticated with Firebase and stores real user_id
    """
    logger.info(f"OAuth consent: client_id={client_id}")
    
    # Get Firebase token from request
    token = firebase_token or get_firebase_token_from_request(request)
    
    if not token:
        logger.error("No Firebase token provided for consent")
        raise HTTPException(status_code=401, detail="Authentication required. Please log in first.")
    
    # Verify Firebase token
    user_info = verify_firebase_token(token)
    if not user_info:
        logger.error("Invalid or expired Firebase token")
        raise HTTPException(status_code=401, detail="Invalid or expired authentication. Please log in again.")
    
    user_id = user_info["user_id"]
    logger.info(f"User {user_id} ({user_info['email']}) authorized ChatGPT access")
    
    # Generate authorization code
    auth_code = secrets.token_urlsafe(32)
    
    # Store authorization code with real user_id (expires in 10 minutes)
    oauth_codes[auth_code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "scope": scope,
        "created_at": time.time(),
        "expires_at": time.time() + 600,  # 10 minutes
        "user_id": user_id,
        "firebase_token": token  # Store Firebase token for later use
    }
    
    logger.info(f"Generated auth code: {auth_code[:10]}... for user: {user_id}, redirect_uri={redirect_uri[:50]}...")
    
    # Redirect back to OpenAI with authorization code
    redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"
    return RedirectResponse(url=redirect_url)

@app.post("/oauth/token")
async def oauth_token(
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None),
    redirect_uri: Optional[str] = Form(None)
):
    """
    OAuth token endpoint - exchanges authorization code for access token
    OpenAI Apps SDK calls this to get an access token
    """
    logger.info(f"OAuth token request: grant_type={grant_type}")
    
    if grant_type == "authorization_code":
        # Validate client credentials
        if client_id != OAUTH_CLIENT_ID:
            raise HTTPException(status_code=401, detail="Invalid client_id")
        
        if client_secret != OAUTH_CLIENT_SECRET:
            raise HTTPException(status_code=401, detail="Invalid client_secret")
        
        # Exchange authorization code for access token
        if not code or code not in oauth_codes:
            raise HTTPException(status_code=400, detail="Invalid authorization code")
        
        code_data = oauth_codes[code]
        
        # Check if code expired
        if time.time() > code_data["expires_at"]:
            del oauth_codes[code]
            raise HTTPException(status_code=400, detail="Authorization code expired")
        
        # Validate redirect_uri matches
        if redirect_uri and redirect_uri != code_data["redirect_uri"]:
            raise HTTPException(status_code=400, detail="Redirect URI mismatch")
        
        # Generate access token
        access_token = secrets.token_urlsafe(32)
        refresh_token_value = secrets.token_urlsafe(32)
        
        # Store tokens with Firebase token from authorization code
        oauth_tokens[access_token] = {
            "type": "access_token",
            "user_id": code_data["user_id"],
            "firebase_token": code_data.get("firebase_token"),  # Store Firebase token for API calls
            "expires_at": time.time() + 3600,
            "scope": code_data["scope"],
            "refresh_token": refresh_token_value
        }
        
        oauth_tokens[refresh_token_value] = {
            "type": "refresh_token",
            "access_token": access_token,
            "user_id": code_data["user_id"]
        }
        
        # Clean up authorization code
        del oauth_codes[code]
        
        logger.info(f"Generated access token for user: {code_data['user_id']}")
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": refresh_token_value,
            "scope": code_data["scope"]
        }
    
    elif grant_type == "refresh_token":
        # Validate client credentials
        if client_id != OAUTH_CLIENT_ID:
            raise HTTPException(status_code=401, detail="Invalid client_id")
        
        if client_secret != OAUTH_CLIENT_SECRET:
            raise HTTPException(status_code=401, detail="Invalid client_secret")
        
        # Refresh access token
        if not refresh_token or refresh_token not in oauth_tokens:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
        
        refresh_token_data = oauth_tokens[refresh_token]
        
        if refresh_token_data["type"] != "refresh_token":
            raise HTTPException(status_code=400, detail="Invalid token type")
        
        # Generate new access token
        new_access_token = secrets.token_urlsafe(32)
        old_access_token = refresh_token_data["access_token"]
        user_id = refresh_token_data["user_id"]
        
        # Clean up old access token
        if old_access_token in oauth_tokens:
            old_token_data = oauth_tokens[old_access_token]
            scope = old_token_data.get("scope", "wardrobe:read outfits:generate")
        else:
            scope = "wardrobe:read outfits:generate"
        
        oauth_tokens[new_access_token] = {
            "type": "access_token",
            "user_id": user_id,
            "firebase_token": None,
            "expires_at": time.time() + 3600,
            "scope": scope,
            "refresh_token": refresh_token
        }
        
        logger.info(f"Refreshed access token for user: {user_id}")
        
        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": scope
        }
    
    raise HTTPException(status_code=400, detail="Unsupported grant_type")

def verify_oauth_token(authorization: Optional[str] = Header(None)) -> dict:
    """
    Verify OAuth access token from OpenAI Apps SDK
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    if token not in oauth_tokens:
        raise HTTPException(status_code=401, detail="Invalid access token")
    
    token_data = oauth_tokens[token]
    
    if token_data["type"] != "access_token":
        raise HTTPException(status_code=401, detail="Invalid token type")
    
    # Check if token expired
    if "expires_at" in token_data and time.time() > token_data["expires_at"]:
        raise HTTPException(status_code=401, detail="Access token expired")
    
    return token_data

@app.get("/test-proxy")
async def test_proxy():
    """
    Test endpoint to verify gateway can reach main backend
    """
    async with httpx.AsyncClient() as client:
        try:
            # Test connection to main backend
            r = await client.get(f"{MAIN_BACKEND_URL}/health")
            return {
                "gateway_status": "ok",
                "backend_url": MAIN_BACKEND_URL,
                "backend_reachable": True,
                "backend_status": r.status_code,
                "backend_response": r.json() if r.status_code == 200 else None
            }
        except httpx.RequestError as e:
            return {
                "gateway_status": "ok",
                "backend_url": MAIN_BACKEND_URL,
                "backend_reachable": False,
                "error": str(e)
            }

@app.get("/wardrobe")
async def get_wardrobe(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """
    Forward GET /wardrobe requests to main backend
    Requires OAuth token from OpenAI Apps SDK
    """
    # Verify OAuth token
    token_data = verify_oauth_token(authorization)
    user_id = token_data.get("user_id")
    
    logger.info(f"Wardrobe request from user: {user_id}")
    
    # Build headers for main backend
    # Use Firebase token from OAuth token data if available, otherwise use API_KEY
    headers = {}
    firebase_token = token_data.get("firebase_token")
    
    # Use Firebase token for authentication with main backend
    if firebase_token:
        headers["Authorization"] = f"Bearer {firebase_token}"
    elif API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    # Add user ID as header
    if user_id:
        headers["X-User-Id"] = user_id
    
    async with httpx.AsyncClient() as client:
        try:
            # Forward to main backend API
            r = await client.get(
                f"{MAIN_BACKEND_URL}/api/wardrobe",
                headers=headers,
                timeout=30.0
            )
            return JSONResponse(content=r.json(), status_code=r.status_code)
        except httpx.RequestError as e:
            logger.error(f"Error forwarding wardrobe request: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/suggest-outfits")
async def suggest_outfits(
    request: Request,
    authorization: Optional[str] = Header(None)
):
    """
    Forward POST /suggest-outfits requests to main backend
    Requires OAuth token from OpenAI Apps SDK
    """
    # Verify OAuth token
    token_data = verify_oauth_token(authorization)
    user_id = token_data.get("user_id")
    
    logger.info(f"Suggest outfits request from user: {user_id}")
    
    payload = await request.json()
    
    # Build headers for main backend
    headers = {"Content-Type": "application/json"}
    firebase_token = token_data.get("firebase_token")
    
    # Use Firebase token for authentication with main backend
    if firebase_token:
        headers["Authorization"] = f"Bearer {firebase_token}"
    elif API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    
    # Add user ID as header
    if user_id:
        headers["X-User-Id"] = user_id
    
    async with httpx.AsyncClient() as client:
        try:
            # Forward to main backend API
            r = await client.post(
                f"{MAIN_BACKEND_URL}/api/outfit/generate",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            return JSONResponse(content=r.json(), status_code=r.status_code)
        except httpx.RequestError as e:
            logger.error(f"Error forwarding suggest-outfits request: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Easy Outfit OpenAI Apps SDK Gateway",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "oauth": {
                "authorize": "/oauth/authorize",
                "token": "/oauth/token"
            },
            "api": {
                "wardrobe": "/wardrobe",
                "suggest_outfits": "/suggest-outfits"
            },
            "metadata": {
                "manifest": "/.well-known/ai-plugin.json",
                "openapi": "/openapi.json"
            }
        }
    }

# Optional: add more endpoints later (add item, mark worn, etc.)

