# mcp_http_gateway.py
import os
import httpx
import secrets
from typing import Optional
from fastapi import FastAPI, Request, Response, HTTPException, Header, Form
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

MAIN_BACKEND_URL = "https://closetgptrenew-production.up.railway.app"
API_KEY = os.environ.get("API_KEY", "")

# OAuth configuration
OAUTH_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID", "closetgpt-chatgpt-app")
OAUTH_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET", secrets.token_urlsafe(32))
OAUTH_REDIRECT_URI = "https://chat.openai.com/aip/oauth/callback"

# In-memory token store (for MVP - use Redis/DB in production)
oauth_tokens = {}  # {access_token: {user_id, firebase_token, expires_at}}

app = FastAPI(title="ClosetGPT ChatGPT App Gateway")

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

@app.get("/oauth/authorize")
async def oauth_authorize(
    client_id: str,
    redirect_uri: str,
    state: str,
    response_type: str = "code"
):
    """
    OAuth authorization endpoint - redirects to Firebase Auth
    ChatGPT calls this to start the OAuth flow
    """
    # In production, validate client_id and redirect_uri
    # For MVP, redirect to Firebase Auth
    firebase_auth_url = f"{MAIN_BACKEND_URL}/auth/firebase-login"
    
    # Store state for validation
    # TODO: Implement proper state storage
    
    # For MVP, redirect to a consent page or directly approve
    # Generate authorization code
    auth_code = secrets.token_urlsafe(32)
    
    # Store auth code temporarily (in production, use Redis with expiration)
    oauth_tokens[auth_code] = {
        "type": "authorization_code",
        "state": state,
        "redirect_uri": redirect_uri
    }
    
    # Redirect back to ChatGPT with authorization code
    return RedirectResponse(f"{redirect_uri}?code={auth_code}&state={state}")

@app.post("/oauth/token")
async def oauth_token(
    grant_type: str = Form(...),
    code: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    client_id: Optional[str] = Form(None),
    client_secret: Optional[str] = Form(None)
):
    """
    OAuth token endpoint - exchanges authorization code for access token
    ChatGPT calls this to get an access token
    """
    if grant_type == "authorization_code":
        # Exchange authorization code for access token
        if code not in oauth_tokens:
            raise HTTPException(status_code=400, detail="Invalid authorization code")
        
        # Generate access token
        access_token = secrets.token_urlsafe(32)
        refresh_token_value = secrets.token_urlsafe(32)
        
        # Store tokens (in production, use proper storage)
        oauth_tokens[access_token] = {
            "type": "access_token",
            "user_id": "test_user",  # TODO: Get real user from Firebase
            "firebase_token": None,  # TODO: Get Firebase token
            "expires_in": 3600
        }
        
        oauth_tokens[refresh_token_value] = {
            "type": "refresh_token",
            "access_token": access_token
        }
        
        # Clean up authorization code
        del oauth_tokens[code]
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": refresh_token_value
        }
    
    elif grant_type == "refresh_token":
        # Refresh access token
        if refresh_token not in oauth_tokens:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
        
        # Generate new access token
        new_access_token = secrets.token_urlsafe(32)
        
        oauth_tokens[new_access_token] = {
            "type": "access_token",
            "user_id": "test_user",
            "firebase_token": None,
            "expires_in": 3600
        }
        
        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": 3600
        }
    
    raise HTTPException(status_code=400, detail="Unsupported grant_type")

def verify_oauth_token(authorization: Optional[str] = Header(None)) -> dict:
    """
    Verify OAuth access token from ChatGPT
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
async def get_wardrobe(request: Request, authorization: Optional[str] = Header(None)):
    """
    Forward GET /wardrobe requests to main backend
    Requires OAuth token from ChatGPT
    """
    # Verify OAuth token
    token_data = verify_oauth_token(authorization)
    
    # For MVP, use API_KEY to call main backend
    # TODO: Use Firebase token from token_data
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(f"{MAIN_BACKEND_URL}/wardrobe", headers=headers)
            return JSONResponse(content=r.json(), status_code=r.status_code)
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/suggest-outfits")
async def suggest_outfits(request: Request, authorization: Optional[str] = Header(None)):
    """
    Forward POST /suggest-outfits requests to main backend
    Requires OAuth token from ChatGPT
    """
    # Verify OAuth token
    token_data = verify_oauth_token(authorization)
    
    payload = await request.json()
    
    # For MVP, use API_KEY to call main backend
    # TODO: Use Firebase token from token_data
    headers = {"Authorization": f"Bearer {API_KEY}"}
    
    async with httpx.AsyncClient() as client:
        try:
            r = await client.post(f"{MAIN_BACKEND_URL}/suggest-outfits", json=payload, headers=headers)
            return JSONResponse(content=r.json(), status_code=r.status_code)
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))

# Optional: add more endpoints later (add item, mark worn, etc.)

