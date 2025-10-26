"""
Standalone GPT Store Service for ClosetGPT
This is a separate FastAPI app that handles ONLY GPT Store integration.
Run independently from your main app to avoid conflicts.

Deploy on Railway as a separate service OR run on a different port.
"""

from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import secrets
import time
import jwt
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
OAUTH_CLIENT_ID = os.getenv("GPT_OAUTH_CLIENT_ID", "closetgpt-custom-gpt")
OAUTH_CLIENT_SECRET = os.getenv("GPT_OAUTH_CLIENT_SECRET", secrets.token_urlsafe(32))
JWT_SECRET = os.getenv("JWT_SECRET", secrets.token_urlsafe(32))
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:3002")
MAIN_API_URL = os.getenv("MAIN_API_URL", "https://closetgptrenew-production.railway.app")
COMPANY_NAME = os.getenv("COMPANY_NAME", "ClosetGPT")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "support@closetgpt.app")

# In-memory storage (use Redis in production)
oauth_codes = {}
oauth_tokens = {}

# Create FastAPI app
app = FastAPI(
    title="ClosetGPT GPT Store Service",
    description="OAuth and GPT Actions for OpenAI Custom GPT integration",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# PYDANTIC MODELS
# ============================================

class TokenRequest(BaseModel):
    grant_type: str
    code: Optional[str] = None
    refresh_token: Optional[str] = None
    client_id: str
    client_secret: str
    redirect_uri: Optional[str] = None

class WardrobeItemSummary(BaseModel):
    id: str
    name: str
    type: str
    color: str
    style: List[str] = []
    season: List[str] = []
    occasion: List[str] = []
    image_url: Optional[str] = None
    wear_count: int = 0

class AddClothingRequest(BaseModel):
    name: str = Field(..., description="Name of the clothing item")
    type: str = Field(..., description="Type (e.g., shirt, pants, dress)")
    color: str = Field(..., description="Primary color")
    style: List[str] = Field(default=[], description="Style tags")
    season: List[str] = Field(default=["all"], description="Seasons")
    occasion: List[str] = Field(default=[], description="Occasions")
    image_url: Optional[str] = Field(None, description="URL of the item image")

class OutfitRequest(BaseModel):
    occasion: Optional[str] = None
    season: Optional[str] = None
    style: Optional[str] = None
    color_preference: Optional[str] = None

# ============================================
# OAUTH ENDPOINTS
# ============================================

@app.get("/oauth/authorize")
async def oauth_authorize(
    response_type: str,
    client_id: str,
    redirect_uri: str,
    state: str,
    scope: Optional[str] = "wardrobe:read wardrobe:write outfits:read outfits:write"
):
    """OAuth 2.0 Authorization endpoint"""
    logger.info(f"OAuth authorize: client_id={client_id}, state={state}")
    
    if client_id != OAUTH_CLIENT_ID:
        raise HTTPException(status_code=400, detail="Invalid client_id")
    
    if response_type != "code":
        raise HTTPException(status_code=400, detail="Unsupported response_type")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Authorize {COMPANY_NAME}</title>
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
            <h1>🎨 Authorize {COMPANY_NAME}</h1>
            <p>ChatGPT wants to access your wardrobe</p>
            
            <div class="permissions">
                <strong>This will allow ChatGPT to:</strong>
                <div class="permission">View your wardrobe items</div>
                <div class="permission">Add new clothing items</div>
                <div class="permission">Generate outfit recommendations</div>
                <div class="permission">Track your style preferences</div>
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
                window.location.href = '/oauth/consent?client_id={client_id}&redirect_uri={redirect_uri}&state={state}&scope={scope}';
            }}
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

@app.get("/oauth/consent")
async def oauth_consent(client_id: str, redirect_uri: str, state: str, scope: str):
    """Handle user consent and generate authorization code"""
    logger.info(f"OAuth consent: client_id={client_id}")
    
    # Generate authorization code
    auth_code = secrets.token_urlsafe(32)
    
    oauth_codes[auth_code] = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "created_at": time.time(),
        "expires_at": time.time() + 600,
        "user_id": "demo_user"  # TODO: Get from actual auth
    }
    
    logger.info(f"Generated auth code: {auth_code[:10]}...")
    
    redirect_url = f"{redirect_uri}?code={auth_code}&state={state}"
    return RedirectResponse(url=redirect_url)

@app.post("/oauth/token")
async def oauth_token(token_request: TokenRequest):
    """Exchange authorization code for access token"""
    logger.info(f"Token request: grant_type={token_request.grant_type}")
    
    if token_request.client_id != OAUTH_CLIENT_ID:
        raise HTTPException(status_code=401, detail="Invalid client_id")
    
    if token_request.client_secret != OAUTH_CLIENT_SECRET:
        raise HTTPException(status_code=401, detail="Invalid client_secret")
    
    if token_request.grant_type == "authorization_code":
        auth_code = token_request.code
        
        if not auth_code or auth_code not in oauth_codes:
            raise HTTPException(status_code=400, detail="Invalid authorization code")
        
        code_data = oauth_codes[auth_code]
        
        if time.time() > code_data["expires_at"]:
            del oauth_codes[auth_code]
            raise HTTPException(status_code=400, detail="Authorization code expired")
        
        if token_request.redirect_uri != code_data["redirect_uri"]:
            raise HTTPException(status_code=400, detail="Redirect URI mismatch")
        
        access_token = jwt.encode(
            {
                "user_id": code_data["user_id"],
                "scope": code_data["scope"],
                "exp": datetime.utcnow() + timedelta(hours=1),
                "iat": datetime.utcnow(),
                "type": "access"
            },
            JWT_SECRET,
            algorithm="HS256"
        )
        
        refresh_token = jwt.encode(
            {
                "user_id": code_data["user_id"],
                "exp": datetime.utcnow() + timedelta(days=30),
                "iat": datetime.utcnow(),
                "type": "refresh"
            },
            JWT_SECRET,
            algorithm="HS256"
        )
        
        oauth_tokens[access_token] = {
            "user_id": code_data["user_id"],
            "scope": code_data["scope"],
            "expires_at": time.time() + 3600
        }
        
        del oauth_codes[auth_code]
        
        logger.info(f"Generated tokens for user: {code_data['user_id']}")
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": refresh_token,
            "scope": code_data["scope"]
        }
    
    elif token_request.grant_type == "refresh_token":
        try:
            payload = jwt.decode(token_request.refresh_token, JWT_SECRET, algorithms=["HS256"])
            
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=400, detail="Invalid token type")
            
            access_token = jwt.encode(
                {
                    "user_id": payload["user_id"],
                    "exp": datetime.utcnow() + timedelta(hours=1),
                    "iat": datetime.utcnow(),
                    "type": "access"
                },
                JWT_SECRET,
                algorithm="HS256"
            )
            
            return {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": 3600
            }
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported grant_type")

@app.get("/oauth/.well-known/oauth-authorization-server")
async def oauth_metadata():
    """OAuth 2.0 Authorization Server Metadata"""
    return {
        "issuer": API_BASE_URL,
        "authorization_endpoint": f"{API_BASE_URL}/oauth/authorize",
        "token_endpoint": f"{API_BASE_URL}/oauth/token",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code", "refresh_token"],
        "token_endpoint_auth_methods_supported": ["client_secret_post"],
        "scopes_supported": ["wardrobe:read", "wardrobe:write", "outfits:read", "outfits:write"]
    }

# ============================================
# GPT ACTIONS - PROXY TO MAIN API
# ============================================

def verify_token(authorization: Optional[str] = Header(None)):
    """Verify OAuth token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/gpt/wardrobe")
async def get_wardrobe(
    user: dict = Depends(verify_token),
    type: Optional[str] = None,
    limit: int = 50
):
    """Proxy to main API - Get wardrobe items"""
    import httpx
    
    # Forward request to main API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MAIN_API_URL}/api/wardrobe",
            params={"type": type, "limit": limit} if type else {"limit": limit},
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            # Transform to GPT-friendly format
            items = data.get("items", [])
            return [
                WardrobeItemSummary(
                    id=item["id"],
                    name=item.get("name", "Unknown"),
                    type=item.get("type", "unknown"),
                    color=item.get("color", "unknown"),
                    style=item.get("style", []),
                    season=item.get("season", []),
                    occasion=item.get("occasion", []),
                    image_url=item.get("imageUrl"),
                    wear_count=item.get("wearCount", 0)
                )
                for item in items[:limit]
            ]
        else:
            raise HTTPException(status_code=response.status_code, detail="Main API error")

@app.get("/gpt/stats")
async def get_stats(user: dict = Depends(verify_token)):
    """Get wardrobe statistics"""
    import httpx
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MAIN_API_URL}/api/wardrobe",
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            
            types = {}
            colors = {}
            for item in items:
                item_type = item.get("type", "unknown")
                types[item_type] = types.get(item_type, 0) + 1
                
                color = item.get("color", "unknown")
                colors[color] = colors.get(color, 0) + 1
            
            return {
                "total_items": len(items),
                "types": types,
                "colors": colors,
                "most_common_type": max(types.items(), key=lambda x: x[1])[0] if types else "none",
                "most_common_color": max(colors.items(), key=lambda x: x[1])[0] if colors else "none"
            }
        else:
            raise HTTPException(status_code=response.status_code, detail="Main API error")

# ============================================
# LEGAL PAGES
# ============================================

@app.get("/privacy", response_class=HTMLResponse)
async def privacy_policy():
    """Privacy Policy"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Privacy Policy - {COMPANY_NAME}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
                line-height: 1.6;
            }}
            h1 {{ color: #1a202c; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        </style>
    </head>
    <body>
        <h1>Privacy Policy</h1>
        <p><em>Last Updated: {datetime.now().strftime("%B %d, %Y")}</em></p>
        <h2>Your Privacy Matters</h2>
        <p>{COMPANY_NAME} respects your privacy. We collect and use your wardrobe data solely to provide personalized outfit recommendations through ChatGPT.</p>
        <h2>What We Collect</h2>
        <ul>
            <li>Wardrobe items you add</li>
            <li>Your style preferences</li>
            <li>Usage patterns</li>
        </ul>
        <h2>How We Use It</h2>
        <p>Your data is used exclusively to generate outfit recommendations and improve our AI models.</p>
        <h2>Contact</h2>
        <p>Questions? Email us at <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a></p>
    </body>
    </html>
    """

@app.get("/terms", response_class=HTMLResponse)
async def terms_of_service():
    """Terms of Service"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Terms of Service - {COMPANY_NAME}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 40px auto;
                padding: 20px;
                line-height: 1.6;
            }}
            h1 {{ color: #1a202c; border-bottom: 3px solid #667eea; padding-bottom: 10px; }}
        </style>
    </head>
    <body>
        <h1>Terms of Service</h1>
        <p><em>Last Updated: {datetime.now().strftime("%B %d, %Y")}</em></p>
        <h2>Agreement</h2>
        <p>By using {COMPANY_NAME}, you agree to these terms.</p>
        <h2>Service</h2>
        <p>We provide AI-powered wardrobe management and outfit recommendations through ChatGPT.</p>
        <h2>Your Responsibilities</h2>
        <ul>
            <li>Provide accurate information</li>
            <li>Use the service lawfully</li>
            <li>Respect intellectual property</li>
        </ul>
        <h2>Contact</h2>
        <p>Questions? Email us at <a href="mailto:{SUPPORT_EMAIL}">{SUPPORT_EMAIL}</a></p>
    </body>
    </html>
    """

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ClosetGPT GPT Store Service",
        "status": "running",
        "endpoints": {
            "oauth": "/oauth/authorize",
            "gpt_actions": "/gpt/wardrobe",
            "legal": ["/privacy", "/terms"]
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3002))
    uvicorn.run(app, host="0.0.0.0", port=port)

